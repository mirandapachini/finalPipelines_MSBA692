import os
from datetime import date, timedelta
import pandas as pd
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
print(f"DB_HOST={DB_HOST!r} DB_PORT={DB_PORT!r} DB_NAME={DB_NAME!r} DB_USER={DB_USER!r}")

# ---------------------------------------------------------
# 1. Initialize connections
# ---------------------------------------------------------
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# 2. Build dynamic date range (today → +7 days)
# ---------------------------------------------------------
today    = date.today()
end_date = today + timedelta(days=7)
start_str = today.strftime("%Y-%m-%d")
end_str   = end_date.strftime("%Y-%m-%d")

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
    "end_date":   end_str,
    "timezone":   "America/New_York"
}

response = requests.get(API_URL, params=params)
data     = response.json()

if "hourly" not in data:
    raise RuntimeError("API returned no hourly data. Check API parameters.")

hourly = data["hourly"]

# ---------------------------------------------------------
# 4. Convert API JSON → DataFrame
# ---------------------------------------------------------
df = pd.DataFrame(hourly)

df["datetime_local"] = pd.to_datetime(df["time"])
df.drop(columns=["time"], inplace=True)

df["datetime_id"] = df["datetime_local"].astype("int64") // 10**9
df["env_id"]      = 1

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
print("Clearing old rows...")
supabase.table("fact_environmental_conditions").delete().neq("datetime_id", -1).execute()

print(f"Inserting {len(df)} new rows...")
rows = df.to_dict(orient="records")
supabase.table("fact_environmental_conditions").insert(rows).execute()

print("ETL complete — Supabase updated with fresh API data.")
