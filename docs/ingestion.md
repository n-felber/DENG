# Ingestion Pipeline

## Purpose

This project includes a **batch ingestion pipeline** that downloads the Bike Sharing dataset from Kaggle, loads the raw source data into PostgreSQL, and creates analytics-ready transformed and summary tables.

The ingestion script is located at:

```bash
src/main.py
```

---

## Source

Dataset:

- `lakshmi25npathi/bike-sharing-dataset`

Files ingested:

- `hour.csv`
- `day.csv`

## Target Storage

The pipeline writes data into PostgreSQL.

Raw tables:

- `bike_hour_raw`
- `bike_day_raw`

Analytics tables:

- `bike_hour_analytics`
- `bike_day_analytics`

Summary tables:

- `bike_hourly_demand_summary`
- `bike_weekday_weekend_summary`
- `bike_weather_demand_summary`
- `bike_daily_trend_summary`
- `bike_monthly_trend_summary`

Each pipeline run replaces the existing raw tables so that the database reflects a fresh batch load from the source dataset.  
The transformed and summary tables are also recreated on each run.

## Why This Is a Batch Pipeline

This ingestion process is batch-based because it:

- downloads complete source files
- processes them as full datasets
- writes them into PostgreSQL in one pipeline run

It does not stream individual records in real time.

## Runtime Configuration

The pipeline requires:

- `DATABASE_URL`

The pipeline may also use:

- `KAGGLE_API_TOKEN`

The dataset is public, so in some environments the download may work without explicit authentication. If Kaggle requires authentication, provide a Kaggle API token through an environment variable.

## Secure Handling of Kaggle Credentials

Kaggle credentials are **not committed** to the repository.

The recommended setup is to provide the token at runtime using an environment variable:

```bash
export KAGGLE_API_TOKEN='your_real_token_here'
docker compose up --build
```

A second clean option is to store the token in a local `.env` file that is ignored by Git.

Example `.env`:

```env
KAGGLE_API_TOKEN=your_real_token_here
```

Because `.env` is ignored by Git, the token stays local to the developer machine and is not committed to the repository.

## What the Script Does

The script performs the following steps:

1. Validates required runtime configuration
2. Waits until PostgreSQL is available
3. Downloads the source files from Kaggle
4. Loads the source data into PostgreSQL raw tables
5. Verifies that the raw tables were written successfully
6. Creates analytics-ready daily and hourly tables
7. Creates summary tables for recurring analysis questions

## Implemented Transformation Logic

The transformation layer includes the following types of logic:

- creation of proper date and timestamp fields
- derived calendar features such as:
  - `event_date`
  - `event_timestamp`
  - `day_name`
  - `month_name`
  - `is_weekend`
- demand-oriented derived metrics such as:
  - `total_rentals`
  - `casual_share`
  - `registered_share`
- convenience fields for analysis such as:
  - `weather_situation`
  - `weather_situation_label`
  - `humidity`
  - `hour_of_day`

## Summary Outputs

The pipeline also creates summary tables that support recurring business questions:

- `bike_hourly_demand_summary` for average rentals by hour of day
- `bike_weekday_weekend_summary` for weekday vs. weekend demand
- `bike_weather_demand_summary` for demand by weather situation
- `bike_daily_trend_summary` for daily rental trends
- `bike_monthly_trend_summary` for monthly rental trends

## Expected Result

After a successful pipeline run:

- PostgreSQL contains the raw tables `bike_hour_raw` and `bike_day_raw`
- PostgreSQL contains the analytics tables `bike_hour_analytics` and `bike_day_analytics`
- PostgreSQL contains the summary tables:
  - `bike_hourly_demand_summary`
  - `bike_weekday_weekend_summary`
  - `bike_weather_demand_summary`
  - `bike_daily_trend_summary`
  - `bike_monthly_trend_summary`
- all tables are queryable
- the row counts for raw and transformed tables are logged in the pipeline output
- the transformed and summary tables can be inspected through SQL or pgAdmin

This raw, transformed, and summarized layer is the input for the later analysis and orchestration parts of the project.
