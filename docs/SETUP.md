# Setup Guide

## Prerequisites

- Python 3.10+
- A PostgreSQL-compatible database (Supabase is used in this project)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Environment Variables

Populate the .env file with your database credentials:

```env
DB_PASSWORD=your-password
DB_USER=your-user
DB_HOST=your-host
```

## Run the Dashboard

```bash
python app.py
```

Then open http://localhost:8050.
