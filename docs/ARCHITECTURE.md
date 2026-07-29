# Architecture Overview

## System Flow

1. The ETL scripts query the Open-Meteo APIs for weather, soil, air quality, and pollen data.
2. The extracted data is transformed into a consistent hourly dataset with derived readiness and allergy metrics.
3. The cleaned dataset is loaded into a PostgreSQL/Supabase-compatible schema for downstream use.
4. The Dash application reads from the database and renders a polished forecasting dashboard.

## Components

- ETL scripts: [notebooks/openmeteo_etl_pipeline.py](../notebooks/openmeteo_etl_pipeline.py)
- Dashboard app: [dashboard/app.py](../dashboard/app.py)
- SQL schema: [sql/schema_environmental.sql](../sql/schema_environmental.sql)
- Data assets: [data/](../data/)

## Design Goals

- Keep the pipeline modular and readable.
- Separate extraction, transformation, and presentation concerns.
- Make the project easy to demo and explain to employers.
