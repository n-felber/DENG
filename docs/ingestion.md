# Ingestion Pipeline

This project contains two batch ingestion paths:

1. Local ingestion into PostgreSQL
2. Cloud ingestion into Google Cloud Storage and BigQuery

Both paths use the Kaggle Bike Sharing dataset.

Dataset:

```text
lakshmi25npathi/bike-sharing-dataset
```

Source files:

```text
hour.csv
day.csv
```

---

## Local pipeline

Local source code:

```text
src/main.py
```

Airflow DAG:

```text
dags/bike_sharing_dag.py
```

DAG ID:

```text
bike_sharing_ingestion
```

The local pipeline runs:

```text
Kaggle dataset
  -> Python ingestion
  -> PostgreSQL raw tables
  -> PostgreSQL analytics tables
  -> PostgreSQL summary tables
```

### Local target tables

Raw tables:

```text
bike_hour_raw
bike_day_raw
```

Analytics tables:

```text
bike_hour_analytics
bike_day_analytics
```

Summary tables:

```text
bike_hourly_demand_summary
bike_weekday_weekend_summary
bike_weather_demand_summary
bike_daily_trend_summary
bike_monthly_trend_summary
```

Each run replaces the existing raw tables and recreates the analytics and summary tables.

---

## Cloud pipeline

Cloud ingestion source code:

```text
src/cloud_ingestion.py
```

BigQuery pipeline source code:

```text
src/bigquery_pipeline.py
```

Airflow DAG:

```text
dags/bike_cloud_pipeline_dag.py
```

DAG ID:

```text
bike_sharing_cloud_pipeline
```

The cloud pipeline runs:

```text
Kaggle dataset
  -> Google Cloud Storage raw files
  -> BigQuery raw tables
  -> BigQuery analytics tables
  -> BigQuery summary tables
```

### Cloud raw file paths

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
```

### BigQuery target tables

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

---

## Runtime configuration

Local pipeline variables:

```env
DATABASE_URL=postgresql://deng:deng_dev_password@postgres:5432/deng
KAGGLE_API_TOKEN=
```

Cloud pipeline variables:

```env
GCP_PROJECT_ID=deng-team2-bike-sharing
GCP_REGION=europe-west6
GCS_BUCKET_NAME=deng-team2-bike-sharing-data-lake
BQ_DATASET=bike_sharing
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp/service-account.json
```

Secrets such as `.env`, `gcp/service-account.json`, and `terraform/terraform.tfvars` must not be committed.

---

## Transformation logic

Both local and cloud transformations create analytics-ready fields such as:

```text
event_date
event_timestamp
year
month
day_name
month_name
is_weekend
weather_situation
weather_situation_label
humidity
total_rentals
casual_share
registered_share
```

The summary tables support repeated analysis questions about:

* hourly demand
* weekday vs. weekend demand
* weather impact
* daily trends
* monthly trends

---

## BigQuery partitioning and clustering

`bike_hour_analytics`:

```text
Partition: DATE(event_timestamp)
Cluster: hour_of_day, is_weekend, weather_situation
```

`bike_day_analytics`:

```text
Partition: event_date
Cluster: is_weekend, weather_situation
```

This matches the main use case queries around time, weekend behavior, and weather effects.

---

## Verification commands

Local:

```bash
make trigger-local
make verify-local
make verify-local-counts
make verify-local-weather
```

Cloud:

```bash
make test-cloud-config
make trigger-cloud
gcloud storage ls gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/
bq ls deng-team2-bike-sharing:bike_sharing
make verify-cloud-counts
make verify-cloud-weather
```
