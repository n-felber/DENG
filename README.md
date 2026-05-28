# DENG

End-to-end batch data pipeline for the Bike Sharing dataset.

## Start here

To set up, run, and verify the project, follow the setup guide:

[docs/setup.md](docs/setup.md)

The setup guide includes:

* prerequisites
* local Docker setup
* Airflow usage
* PostgreSQL and pgAdmin verification
* Terraform setup
* Google Cloud Storage verification
* BigQuery verification
* troubleshooting

Cleanup instructions are documented separately:

[docs/cleanup.md](docs/cleanup.md)

Read the cleanup guide before running destructive cleanup commands, especially `make cleanup-all`.

## Project overview

This project implements a reproducible batch data pipeline for bike-sharing demand analytics.

The pipeline ingests the Bike Sharing dataset, stores raw data, creates analytics-ready tables, and produces summary tables that support demand analysis questions such as:

* At which hours is rental demand highest?
* How does demand differ between weekdays and weekends?
* How does weather affect bike usage?
* How do casual and registered users differ in behavior?
* Which periods require better bike availability and redistribution planning?

The detailed use case is documented here:

[docs/use_case.md](docs/use_case.md)

## Pipeline architecture

The project contains two runnable pipeline paths.

### Local pipeline

```text
Kaggle dataset
   |
   v
Airflow
   |
   v
PostgreSQL
   |
   v
Analytics and summary tables
```

The local pipeline uses:

* Kaggle as the source dataset
* Python for batch ingestion
* PostgreSQL for local storage
* pgAdmin for inspection
* Airflow for orchestration
* Docker Compose for reproducibility

### Cloud pipeline

```text
Kaggle dataset
   |
   v
Airflow
   |
   v
Google Cloud Storage
   |
   v
BigQuery raw tables
   |
   v
BigQuery analytics and summary tables
```

The cloud pipeline uses:

* Terraform for cloud infrastructure
* Google Cloud Storage as the data lake
* BigQuery as the data warehouse
* Airflow for orchestration
* SQL transformations for analytics-ready outputs

## Documentation

| Document                               | Purpose                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------ |
| [docs/setup.md](docs/setup.md)         | Full setup, run, and verification guide                                  |
| [docs/use_case.md](docs/use_case.md)   | Dataset, user persona, analytics use case, and transformation motivation |
| [docs/ingestion.md](docs/ingestion.md) | Local batch ingestion pipeline details                                   |
| [docs/cleanup.md](docs/cleanup.md)     | Local, cloud, and secrets cleanup instructions                           |

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
├── Dockerfile             # Pipeline container image
├── Makefile               # Common run, verify, Terraform, and cleanup commands
├── requirements.txt       # Python dependencies
└── README.md              # Project entry point
```

## Main components

### Source dataset

The project uses the Kaggle Bike Sharing dataset:

```text
lakshmi25npathi/bike-sharing-dataset
```

Input files:

```text
hour.csv
day.csv
```

### Local storage

The local pipeline stores raw, transformed, and summary data in PostgreSQL.

Main local tables:

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

### Cloud storage and warehouse

The cloud pipeline stores raw files in Google Cloud Storage and loads transformed outputs into BigQuery.

Default cloud values:

```text
GCP project ID: deng-team2-bike-sharing
GCP region: europe-west6
GCS bucket: deng-team2-bike-sharing-data-lake
BigQuery dataset: bike_sharing
```

Expected GCS paths:

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
```

Expected BigQuery tables:

```text
bike_sharing.bike_hour_raw
bike_sharing.bike_day_raw
bike_sharing.bike_hour_analytics
bike_sharing.bike_day_analytics
bike_sharing.bike_hourly_demand_summary
bike_sharing.bike_weekday_weekend_summary
bike_sharing.bike_weather_demand_summary
bike_sharing.bike_daily_trend_summary
bike_sharing.bike_monthly_trend_summary
```

## Common commands

Show all available commands:

```bash
make help
```

Start the local Docker environment:

```bash
make up
```

Check running services:

```bash
make ps
```

Trigger the local PostgreSQL pipeline:

```bash
make trigger-local
```

Validate the cloud pipeline configuration without loading data:

```bash
make test-cloud-config
```

Trigger the cloud GCS and BigQuery pipeline:

```bash
make trigger-cloud
```

Verify local PostgreSQL tables:

```bash
make verify-local
```

Check local PostgreSQL row counts:

```bash
make verify-local-counts
```

Check BigQuery row counts:

```bash
make verify-cloud-counts
```

Run local cleanup:

```bash
make cleanup
```

Destroy cloud infrastructure and clean local generated files:

```bash
make cleanup-all
```

## Reproducibility

The project is designed to be reproducible from the repository using Docker Compose and documented setup steps.

A reviewer should start with:

[docs/setup.md](docs/setup.md)

The setup guide explains how to:

1. clone the repository
2. configure local environment variables
3. start the Docker Compose services
4. run the local Airflow pipeline
5. verify PostgreSQL outputs
6. provision cloud infrastructure with Terraform
7. run the cloud Airflow pipeline
8. verify GCS and BigQuery outputs

## Cleanup warning

Some cleanup commands delete generated data.

Use:

```bash
make cleanup
```

to remove local runtime resources.

Use:

```bash
make cleanup-all
```

only when the project is finished and cloud resources can be destroyed.

Before full cleanup, collect screenshots or other required evidence for the project submission.

See the full cleanup guide:

[docs/cleanup.md](docs/cleanup.md)
