# Ingestion Pipeline

## Purpose

This project includes a **batch ingestion pipeline** that downloads the Bike Sharing dataset from Kaggle, loads the raw source data into PostgreSQL, and creates a transformed analytics-ready table.

The ingestion script is located at:

```bash
src/main.py
```

---

## Source

Dataset:

* `lakshmi25npathi/bike-sharing-dataset`

Files ingested:

* `hour.csv`
* `day.csv`

## Target Storage

The pipeline writes data into PostgreSQL.

Raw tables:

* `bike_hour_raw`
* `bike_day_raw`

Transformed table:

* `bike_day_analytics`

Each pipeline run replaces the existing raw tables so that the database reflects a fresh batch load from the source dataset.

## Why This Is a Batch Pipeline

This ingestion process is batch-based because it:

* downloads complete source files
* processes them as full datasets
* writes them into PostgreSQL in one pipeline run

It does not stream individual records in real time.

## Runtime Configuration

The pipeline requires:

* `DATABASE_URL`

The pipeline may also use:

* `KAGGLE_API_TOKEN`

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
6. Creates a transformed analytics-ready table

## Expected Result

After a successful pipeline run:

* PostgreSQL contains the raw tables `bike_hour_raw` and `bike_day_raw`
* PostgreSQL contains the transformed table `bike_day_analytics`
* all tables are queryable
* the row counts for raw tables are logged in the pipeline output
* the transformed table can be inspected through SQL or pgAdmin

This raw and transformed layer is the input for the later analysis and orchestration parts of the project.

