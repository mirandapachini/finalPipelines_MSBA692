# Repository Layout

This repository is organized to make the project easy to navigate, understand, and present to hiring managers.

## Top-level files

- `README.md` — project overview, impact summary, and quick start instructions
- `requirements.txt` — Python dependencies for running the dashboard and ETL
- `app.py` — top-level dashboard entrypoint that loads the Dash app from `dashboard/`
- `.env.example` — sample environment variables for secure database credentials

## Directories

- `dashboard/` — Dash application package and visualization logic
  - `dashboard/app.py` contains the main Dash layout, callbacks, and data loading from the database
  - `dashboard/__init__.py` exports the app and server for the top-level entrypoint

- `etl/` — reusable ETL scripts and pipeline modules
  - `etl/openmeteo_etl_pipeline.py` is the main pipeline script for data ingestion, transformation, and export
  - `etl/api_etl.py` and `etl/open_meteo_to_csv.py` support raw data extraction and CSV generation

- `notebooks/` — exploratory notebooks used for analysis, prototyping, and validating the ETL workflow

- `sql/` — database schema and load scripts
  - `sql/schema_environmental.sql` defines the analytical model used by the project
  - `sql/initial_load_script.sql` supports loading transformed data into a database environment

- `data/` — source and processed dataset files that support the pipeline and dashboard

- `docs/` — project documentation and portfolio-facing narrative
  - `docs/ARCHITECTURE.md` explains the system design
  - `docs/SETUP.md` walks through install and run instructions
  - `docs/LINKEDIN_SUMMARY.md` contains a concise, career-ready project summary
  - `docs/PORTFOLIO_SUMMARY.md` captures narrative talking points for interviews

- `tests/` — lightweight smoke tests that verify project entrypoints and app exports

## How to use this repo

1. Create a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and populate database credentials.
4. Run the ETL pipeline from `etl/openmeteo_etl_pipeline.py`.
5. Start the dashboard with `python app.py`.

## Why this layout works for employers

- Separates production-ready pipeline code from exploratory analysis.
- Keeps the dashboard package isolated from notebook research.
- Provides clear onboarding documentation for reviewers.
- Shows a thoughtful structure typical of data product and analytics engineering work.
