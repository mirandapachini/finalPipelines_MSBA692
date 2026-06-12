# 🌱 **Garden & Allergy Forecast Analytics Platform**  
**Environmental Intelligence · ETL Pipeline · Supabase · Power BI · Dash Dashboard**

A full end‑to‑end analytics system that unifies weather, pollen, soil, air quality, and precipitation data into a single platform for gardeners and allergy‑sensitive users in **Zone 6b (Louisville, KY)**.

This project includes:

- Automated **Python ETL pipeline**  
- **Supabase Postgres** database  
- Clean **star schema**  
- **Power BI prototype**  
- Fully interactive **Dash dashboard**  
- **Planting recommendation engine**  
- **7‑day environmental forecast**  
- **Best‑time‑to‑garden model**

---

## 📌 **Table of Contents**
- [Overview](#overview)  
- [Architecture](#architecture)  
- [Features](#features)  
- [Data Sources](#data-sources)  
- [ETL Pipeline](#etl-pipeline)  
- [Database Schema](#database-schema)  
- [Power BI Prototype](#power-bi-prototype)  
- [Dash Dashboard](#dash-dashboard)  
- [Setup & Installation](#setup--installation)  
- [Lessons Learned](#lessons-learned)  
- [Challenges](#challenges)  
- [Outcome](#outcome)  

---

# 🌿 **Overview**

Gardeners and allergy‑sensitive users often need to check multiple apps for:

- Weather  
- Pollen  
- Soil temperature  
- Rain timing  
- Air quality  
- Seasonal planting windows  

This project solves that by creating a **single, unified analytics platform** that answers:

> **“What’s the best time to garden today — and what should I plant?”**

---

# 🧱 **Architecture**

```
Open-Meteo API
      ↓
Python ETL (hourly)
      ↓
Supabase Postgres (staging + fact tables)
      ↓
Power BI Prototype (initial)
      ↓
Dash Dashboard (final interactive app)
```

---

# 🌦️ **Features**

### **Environmental Forecasting**
- 7‑day hourly weather forecast  
- Pollen levels (grass, ragweed, birch, alder, mugwort, olive)  
- Air Quality Index (US AQI)  
- Soil temperature & moisture  
- Rain probability & precipitation  

### **Planting Recommendation Engine**
Based on:
- Soil temperature  
- Soil moisture  
- Rain probability  
- Wind speed  
- Allergy risk  
- Seasonal planting windows (Zone 6b)  

Outputs:
- What to plant today  
- What to avoid  
- Almanac‑style guidance  
- Best gardening time  

### **Interactive Dash Dashboard**
- KPI cards  
- Trend charts  
- Daily selector  
- Real‑time banners (rain alerts, wind alerts, best gardening time)  

---

# 🌐 **Data Sources**

All data is pulled from **Open‑Meteo**:

- Weather API  
- Pollen API  
- Air Quality API  
- Soil Conditions API  

---

# 🔄 **ETL Pipeline**

### **Extract**
- Hourly API calls  
- Multiple endpoints merged into one dataset  

### **Transform**
- Convert timestamps → local datetime  
- Normalize precipitation (0–1000 → percent)  
- Align hourly data across sources  
- Handle missing values  
- Validate ranges  
- Compute derived fields:
  - `planting_readiness`
  - `allergy_risk`
  - `high_pollen_flag`

### **Load**
- Writes cleaned data into:
  - `staging_environmental_raw`  
  - (Optional) `fact_environmental_conditions`  

---

# 🗄️ **Database Schema**

### **dim_datetime**
- Clean date  
- Day of week  
- Month  
- Season  

### **staging_environmental_raw**
Contains:
- `timestamp_local`  
- `temperature_2m`  
- `relative_humidity_2m`  
- `precipitation_probability`  
- `precipitation`  
- `soil_temperature_0cm`  
- `soil_moisture_0_to_1cm`  
- `us_aqi`  
- Pollen metrics  
- Derived scores  

### **fact_environmental_conditions**
- Daily aggregates  
- Flags  
- Readiness metrics  

---

# 📊 **Power BI Prototype**

The first version of the dashboard was built in Power BI.

### **Included Visuals**
- Best overall day  
- Readiness score  
- Allergy risk  
- Pollen trends  
- AQI bands  
- Soil moisture  
- Precipitation probability  

### **Why It Was Replaced**
Power BI introduced several blockers:
- SSL issues connecting to Supabase  
- Slicers not filtering staging tables  
- Required TREATAS workarounds  
- DAX debugging friction  
- Blank visuals hiding errors  

This led to rebuilding the dashboard in Dash.

---

# ⚡ **Dash Dashboard**

The final dashboard (`app.py`) includes:

### **Header**
- Weather emoji  
- Location  
- Current date  

### **Banners**
- Best time to garden  
- Rain alerts  
- Wind advisories  

### **KPIs**
- Temperature  
- Planting score  
- Allergy risk  
- AQI  
- High‑pollen hours  
- Max wind  

### **Charts**
- Planting readiness vs allergy risk  
- Temperature + humidity  
- Pollen breakdown  
- AQI bars with health bands  
- Soil temperature + moisture  
- Precipitation probability + rainfall  

---

# 🛠️ **Setup & Installation**

### **1. Clone the repo**
```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### **2. Add your `.env`**
```
DB_PASSWORD=your-password
```

### **3. Install dependencies**
```
pip install -r requirements.txt
```

### **4. Run the Dash app**
```
python app.py
```

### **5. Open in browser**
```
http://localhost:8050
```

---

# 🎓 **Lessons Learned**

This project grew far beyond a simple dashboard and became a full end‑to‑end engineering build. Along the way, I learned:

### **About the Data**
- Environmental APIs use inconsistent scales and formats  
- Precipitation required normalization  
- Soil temperature is the strongest planting indicator  
- Pollen data is often sparse or missing  
- Aligning hourly data across multiple endpoints is essential  

### **About the Tools**
- **Power BI** is not ideal for API‑driven, hourly environmental data  
  - SSL issues with Supabase  
  - Slicer limitations  
  - DAX debugging friction  
- **Dash** is dramatically faster for custom logic  
  - Direct SQL connections  
  - Full control over layout and callbacks  
  - Easier debugging and iteration  

### **About Engineering & Debugging**
- Environment setup is fragile — misplaced `.env` files or incorrect paths can break everything  
- Cloud database credentials require precision (URL‑encoding, secure storage, correct formatting)  
- Pandas + SQLAlchemy is the reliable pairing for database reads  
- Git will surface every misstep — merge conflicts, tracked secrets, deleted files  
- Debugging is part of the process — from empty files to cloud outages, each issue revealed how the system really works  
- The project naturally expanded — what began as a simple visualization became a full ETL pipeline, database model, recommendation engine, and interactive app  

---

# 🧨 **Challenges**

A summary of the major issues encountered:

- `app.py` saved empty and had to be rewritten via terminal  
- `.env` and `.gitignore` accidentally created as folders  
- psycopg2 rejected the full Supabase username  
- Password was exposed and had to be reset  
- Supabase outage caused false authentication failures  
- `pd.read_json` treated JSON as a file path  
- SQLAlchemy required for pandas compatibility  
- Power BI slicers failed to filter staging tables  
- SSL issues prevented Power BI from connecting  
- Dash couldn’t find `.env` after moving files  
- Git merge conflicts involving `.env`  
- Data alignment issues across API endpoints  

---

# 🎉 **Outcome**

This project evolved into a complete environmental analytics system:

- Automated ETL  
- Clean database  
- Derived environmental intelligence  
- A full planting recommendation engine  
- A polished, interactive Dash dashboard  

Built quickly, cleanly, and stress‑free.

---

# 🌱 **Garden & Allergy Forecast Dashboard**

## Dash Dashboard
Run `app.py` to launch the interactive weather and allergy dashboard for gardeners.

### Setup
1. Add your database password to `.env`: `DB_PASSWORD=your-password`  
2. Install dependencies: `pip install -r requirements.txt`  
3. Run: `python app.py`  
4. Open browser at `http://localhost:8050`

## Features
- 7‑day weather & pollen forecast  
- Planting recommendations (Farmers' Almanac, Zone 6b)  
- Allergy risk & AQI tracking  
- Best time to garden today  
