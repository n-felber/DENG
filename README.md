# DENG

## Project Overview

This project implements a local batch data pipeline for the Bike Sharing dataset.

It includes:
- a Python batch ingestion pipeline
- a local PostgreSQL database
- pgAdmin for database inspection
- Airflow for workflow orchestration

## Documentation

- Use case: [docs/use_case.md](docs/use_case.md)
- Ingestion pipeline: [docs/ingestion.md](docs/ingestion.md)
- Setup: [docs/setup.md](docs/setup.md)
- Cleanup: [docs/cleanup.md](docs/cleanup.md)

## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)

## Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

If Kaggle authentication is required in your environment, create a local `.env` file based on `.env.example` and set:

```env
KAGGLE_API_TOKEN=your_kaggle_api_token_here
```

## Build and run the system

Start all services:

```bash
docker compose up -d
```

This starts:

- PostgreSQL
- pgAdmin
- Airflow webserver
- Airflow scheduler

All services run inside the same Docker Compose network and can communicate using their service names, such as `postgres`.

## Airflow UI

Open in your browser:

```text
http://localhost:8080
```

Log in with:

- Username: `airflow`
- Password: `airflow`

The DAG `bike_sharing_ingestion` should be visible in the Airflow UI.

To run the pipeline immediately, trigger the DAG once from the Airflow UI or with:

```bash
docker compose exec airflow-webserver airflow dags trigger bike_sharing_ingestion
```

## Verify that it works

### 1. Check container status

```bash
docker compose ps
```

Expected result:

- `postgres` is `Up` and healthy
- `pgadmin` is `Up`
- `airflow-webserver` is `Up`
- `airflow-scheduler` is `Up`

### 2. Verify the DAG run in Airflow

In the Airflow UI:

- confirm that the DAG `bike_sharing_ingestion` exists
- trigger the DAG once if no recent run is present
- confirm that the task `run_batch_ingestion_task` finishes successfully

### 3. Check PostgreSQL tables

Airflow stores its own metadata tables in the same PostgreSQL database. To inspect only the project tables, run:

```bash
docker compose exec postgres psql -U deng -d deng -c "\dt public.bike_*"
```

Expected tables:

- `bike_hour_raw`
- `bike_day_raw`
- `bike_hour_analytics`
- `bike_day_analytics`
- `bike_hourly_demand_summary`
- `bike_weekday_weekend_summary`
- `bike_weather_demand_summary`
- `bike_daily_trend_summary`
- `bike_monthly_trend_summary`

### 4. Check row counts

```bash
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hour_raw;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_raw;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hour_analytics;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_analytics;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hourly_demand_summary;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_weekday_weekend_summary;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_daily_trend_summary;"
docker compose exec postgres psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_monthly_trend_summary;"
```

Expected result:

- `bike_hour_raw` contains `17379` rows
- `bike_day_raw` contains `731` rows
- `bike_hour_analytics` contains `17379` rows
- `bike_day_analytics` contains `731` rows
- `bike_hourly_demand_summary` contains `24` rows
- `bike_weekday_weekend_summary` contains `2` rows
- `bike_daily_trend_summary` contains `731` rows
- `bike_monthly_trend_summary` contains `24` rows

For the weather summary table, the exact row count depends on how many weather categories are present in the dataset. You can inspect it with:

```bash
docker compose exec postgres psql -U deng -d deng -c "SELECT * FROM bike_weather_demand_summary ORDER BY weather_situation;"
```

### 5. Verify with pgAdmin

Open in your browser:

```text
http://localhost:5050
```

Log in with:

- Email: `admin@local.dev`
- Password: `admin`

Add a new server with:

General tab:

- Name: `deng`

Connection tab:

- Host name/address: `postgres`
- Port: `5432`
- Maintenance database: `deng`
- Username: `deng`
- Password: `deng_dev_password`

After connecting, open:

`Servers -> deng -> Databases -> deng -> Schemas -> public -> Tables`

You should see the project tables listed above.

## Verify orchestration requirements

### Scheduled runs

The DAG is scheduled with `@daily`.

### Future runs

Future runs can be triggered manually from the Airflow UI or with:

```bash
docker compose exec airflow-webserver airflow dags trigger bike_sharing_ingestion
```

### Backfills

Airflow supports backfills for past dates. Example:

```bash
docker compose exec airflow-webserver airflow dags backfill bike_sharing_ingestion -s 2024-01-01 -e 2024-01-03
```

## Reproducibility summary

This repository contains the components required to reproduce the local environment:

- application source code
- Docker Compose configuration
- Airflow DAG definition
- setup and verification documentation

To reproduce the environment independently:

1. clone the repository
2. create `.env` from `.env.example` if Kaggle authentication is required
3. run `docker compose up -d`
4. trigger the DAG in Airflow
5. verify the services and database state using the commands above
