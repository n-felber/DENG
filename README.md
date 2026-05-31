# DENG

End-to-end batch data pipeline for the Bike Sharing dataset.

## Start here

To set up, run, and verify the project, follow the setup guide:

[docs/setup.md](docs/setup.md)

It explains how to run the local pipeline, provision cloud infrastructure, run the cloud pipeline, and verify the results.

Cleanup is documented separately:

[docs/cleanup.md](docs/cleanup.md)

Use `make cleanup-all` only after screenshots and final verification evidence have been collected.

## Project overview

This project ingests the Kaggle Bike Sharing dataset in batch mode, stores raw data locally and in the cloud, transforms it into analytics-ready tables, and serves summary outputs for demand analysis.

Dataset:

```text
lakshmi25npathi/bike-sharing-dataset
```

Source files:

```text
hour.csv
day.csv
```

The detailed use case is documented in:

[docs/use_case.md](docs/use_case.md)

## Architecture

### Local pipeline

```text
Kaggle dataset
  -> Airflow
  -> PostgreSQL
  -> analytics and summary tables
  -> pgAdmin / SQL inspection
```

### Cloud pipeline

```text
Kaggle dataset
  -> Airflow
  -> Google Cloud Storage raw data lake
  -> BigQuery raw tables
  -> BigQuery analytics and summary tables
```

## Main technologies

* Python
* Docker Compose
* PostgreSQL
* pgAdmin
* Apache Airflow
* Terraform
* Google Cloud Storage
* BigQuery

## Documentation

| Document | Purpose |
| --- | --- |
| [docs/setup.md](docs/setup.md) | Setup, run, and verification steps |
| [docs/use_case.md](docs/use_case.md) | Dataset, user persona, analytics use case, and transformation motivation |
| [docs/ingestion.md](docs/ingestion.md) | Local and cloud ingestion pipeline details |
| [docs/final_verification.md](docs/final_verification.md) | Final verification checklist and commands |
| [docs/screenshots.md](docs/screenshots.md) | Screenshot checklist for submission evidence |
| [docs/cleanup.md](docs/cleanup.md) | Local, cloud, and secrets cleanup |

## Repository structure

```text
.
├── dags/                  # Airflow DAG definitions
├── docs/                  # Project documentation
├── gcp/                   # Local service account key location, not committed
├── sql/                   # BigQuery transformation SQL files
├── src/                   # Python pipeline source code
├── terraform/             # Terraform cloud infrastructure
├── compose.yaml           # Docker Compose services
├── Makefile               # Common run, verify, Terraform, and cleanup commands
├── requirements.txt       # Python dependencies
└── README.md              # Project entry point
```

## Common commands

```bash
make help
make up
make ps
make trigger-local
make verify-local
make verify-local-counts
make verify-local-weather
make terraform-init
make terraform-plan
make terraform-apply
make test-cloud-config
make trigger-cloud
make verify-cloud-counts
make verify-cloud-weather
make cleanup
make cleanup-all
```

## Expected outputs

Local PostgreSQL and BigQuery should contain:

```text
bike_hour_raw
bike_day_raw
bike_hour_analytics
bike_day_analytics
bike_hourly_demand_summary
bike_weekday_weekend_summary
bike_weather_demand_summary
bike_daily_trend_summary
bike_monthly_trend_summary
```

Raw cloud files should exist at:

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
```
