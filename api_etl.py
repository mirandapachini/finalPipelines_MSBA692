import os
from datetime import date, timedelta
import pandas as pd
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. Load environment variables from .env
# ---------------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ---------------------------------------------------------
# 2. Build dynamic date range (today → +7 days)
# ---------------------------------------------------------
today = date.today()
end_date = today + timedelta(days=7)

start_str = today.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# ---------------------------------------------------------
# 3. Call Open-Meteo API
# ---------------------------------------------------------
API_URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 38.2527,
    "longitude": -85.7585,
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "soil_temperature_0cm",
        "soil_moisture_0_1cm",
        "pm10",
        "pm2_5",
        "grass_pollen",
        "tree_pollen",
        "weed_pollen"
    ],
    "start_date": start_str,
    "end_date": end_str,
    "timezone": "America/New_York"
}

response = requests.get(API_URL, params=params)
data = response.json()

if "hourly" not in data:
    raise RuntimeError("❌ API returned no hourly data. Check API parameters.")

hourly = data["hourly"]

# ---------------------------------------------------------
# 4. Convert API JSON → DataFrame
# ---------------------------------------------------------
df = pd.DataFrame(hourly)

# Convert time column
df["datetime_local"] = pd.to_datetime(df["time"])
df.drop(columns=["time"], inplace=True)

# Add keys
df["datetime_id"] = df["datetime_local"].astype("int64") // 10**9
df["env_id"] = 1  # static environment key

# Reorder columns to match your fact table
fact_cols = [
    "datetime_id",
    "env_id",
    "datetime_local",
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "soil_temperature_0cm",
    "soil_moisture_0_1cm",
    "pm10",
    "pm2_5",
    "grass_pollen",
    "tree_pollen",
    "weed_pollen"
]

df = df[fact_cols]

# ---------------------------------------------------------
# 5. Load into Supabase (truncate + insert)
# ---------------------------------------------------------
print("🗑️ Clearing old rows...")
supabase.table("fact_environmental_conditions").delete().neq("datetime_id", -1).execute()

print(f"📤 Inserting {len(df)} new rows...")
rows = df.to_dict(orient="records")
supabase.table("fact_environmental_conditions").insert(rows).execute()

print("✅ ETL complete — Supabase updated with fresh API data.")
