Green Thumbs & Runny Noses: A Forecasting Tool for Gardeners with Allergies
Open‑Meteo Environmental Analytics Pipeline
Weather • Soil • Air Quality • Pollen • Feature Engineering • Decision Flags

This project builds a complete environmental decision‑support dataset using the Open‑Meteo API suite. It integrates weather, soil, air quality, and pollen data into a single engineered dataset with custom scoring models and operational flags.

Pipeline Flowchart
The diagram below illustrates the full data extraction and transformation workflow used in the Environmental Conditions Database Application. It mirrors the structure demonstrated in the course example and shows how external data sources, API calls, and processing scripts interact to produce the final merged dataset.

The flowchart highlights:

External data sources (Open‑Meteo API and reference files)

User‑defined parameters (time range selection)

The ETL pipeline steps (API requests, transformations, merging)

Scripts
pipelines.ipynb
Purpose:  
End‑to‑end ETL pipeline that fetches environmental data from Open‑Meteo APIs and produces a unified dataset for database loading.

Workflow:

Fetches hourly weather, soil, air quality, and pollen data for Louisville, KY

Converts timestamps to local time (America/New_York)

Normalizes JSON responses into pandas DataFrames

Merges all variables into a single hourly dataset

Engineers composite scores (planting readiness, allergy risk)

Generates boolean environmental risk flags

Exports final dataset to data/merged_open_meteo_final.csv

Key Features:

Uses three Open‑Meteo endpoints (Weather/Soil, Air Quality, Pollen)

Ensures consistent timestamp alignment across APIs

Handles missing values and unit conversions

Produces a clean, analysis‑ready dataset for PostgreSQL loading

Usage:
Code
Run all cells in pipelines.ipynb

schema.ipynb
Purpose:  
Programmatically generates the full SQL schema (documentation + CREATE TABLE statements) and writes it to schema.sql.

Demonstrates:

Constructing SQL schema strings in Python

Embedding documentation directly into SQL files

Writing .sql files from Python

Ensuring reproducible schema generation for database creation

Usage:
Code
Run all cells in schema.ipynb
schema.sql will be created automatically

initial_load.py
Purpose:  
Creates PostgreSQL tables using schema.sql and loads the processed dataset into the fact table.

Workflow:

Connects to PostgreSQL using psycopg2

Executes schema.sql to create all tables

Loads merged_open_meteo_final.csv into pandas

Inserts rows into fact_environmental_conditions

Closes database connection cleanly

Key Features:

Uses parameterized SQL inserts

Includes error handling for database operations

Ensures reproducible table creation and loading

Usage:
Code
python initial_load.py

Learning Outcomes
Students completing this project will:

Understand multi‑API extraction using Open‑Meteo

Learn how to normalize and merge heterogeneous environmental datasets

Practice timestamp handling and timezone conversion

Build a star schema with dimension and fact tables

Generate SQL schema files programmatically

Load structured data into PostgreSQL using Python

Interpret ERDs and relational database design principles

Data Reference
Environmental Dataset
The data/merged_open_meteo_final.csv file contains:

Hourly weather variables (temperature, wind speed, precipitation probability)

Soil conditions (soil temperature, soil moisture)

Air quality metrics (PM2.5, ozone, AQI)

Pollen counts (grass, ragweed, birch, alder, mugwort, olive)

Composite scores (planting readiness, allergy risk)

Boolean environmental flags (high wind, rain expected, poor air quality, etc.)

Reference File
The data/environmental_reference.xlsx file contains:

Variable names

Descriptions

Units of measurement

Source API mapping

This mirrors the structure of the weather code reference file used in the course example.

ERD Reference
The ERD (assets/erd.png) illustrates:

dim_datetime (time dimension)

dim_environmental_factors (location dimension)

fact_environmental_conditions (central fact table)

Relationships follow a star schema with 1‑to‑many cardinality.

Source APIs
All data is sourced from:

👉 Open‑Meteo API  
https://open-meteo.com/en/docs

Free access

No authentication required

High‑resolution hourly environmental data

Supports weather, soil, air quality, and pollen endpoints

Requirements
Install dependencies from requirements.txt:

Code
pip install -r requirements.txt
Key libraries:

requests — API calls

pandas — data transformation

openmeteo_requests — optimized Open‑Meteo client

psycopg2-binary — PostgreSQL connection

numpy — numeric operations

Usage Summary
To reproduce the full pipeline:

Run pipelines.ipynb → generates merged CSV

Run schema.ipynb → generates schema.sql

Run initial_load.py → creates tables + loads data

View ERD in assets/erd.png

Query your PostgreSQL database

Environmental Conditions Dashboard — Power BI
Overview
This Power BI dashboard visualizes environmental conditions using data pulled from a PostgreSQL database. It includes temperature trends, pollen levels (after unpivoting), air quality, and planting readiness. The visuals are designed to stay clean and easy to interpret, and everything updates when the user interacts with the slicer.

Features
KPIs
Avg Planting Readiness

Avg AQI

Avg Pollen

Visuals
Daily Temperature Trend

Daily Pollen Levels (using unpivoted structure)

Weekly Avg Planting Readiness

All visuals respond to the slicer

Interactivity
Day slicer that filters the entire dashboard

KPIs and charts update automatically

Data Integration
Connected to PostgreSQL (Supabase)

Uses fact and dimension tables

Clean joins through datetime_id

Pollen columns reshaped using Power Query (unpivot)

Layout
KPIs at the top

Main visuals centered

Slicer on the left

Simple, readable layout

Tech Stack
Power BI Desktop

PostgreSQL (Supabase)

Power Query

DAX

How to Use
Open the .pbix file

Confirm the PostgreSQL connection string

Refresh the data

Use the slicer to filter by day

Explore the visuals

Business Value
The dashboard gives a quick, practical view of how temperature, pollen, and air quality relate to planting readiness. It helps identify favorable planting days and shows how environmental conditions shift over time. The layout keeps everything straightforward so users can focus on the patterns without getting lost in the details.
