# Setup Guide

This guide explains how to set up, run, and verify the DENG Team 2 Bike Sharing data pipeline.

The project has two runnable paths:

1. Local pipeline: Kaggle -> Airflow -> PostgreSQL -> analytics tables
2. Cloud pipeline: Kaggle -> Airflow -> GCS -> BigQuery -> analytics tables

Run all commands from the project root.

---

## 1. Prerequisites

Install or prepare:

* Docker Desktop
* Docker Compose
* Make
* Terraform
* Google Cloud CLI
* BigQuery CLI
* Google Cloud project
* Kaggle account, if Kaggle authentication is required

Verify the tools:

```bash
docker --version
docker compose version
make --version
terraform version
gcloud version
bq version
```

---

## 2. Clone the repository

```bash
git clone git@github.com:n-felber/DENG.git
cd DENG
```

Check available commands:

```bash
make help
```

---

## 3. Create local environment file

```bash
cp .env.example .env
```

Confirm the local values in `.env`:

```env
POSTGRES_USER=deng
POSTGRES_PASSWORD=deng_dev_password
POSTGRES_DB=deng
DATABASE_URL=postgresql://deng:deng_dev_password@postgres:5432/deng
PGADMIN_DEFAULT_EMAIL=admin@local.dev
PGADMIN_DEFAULT_PASSWORD=admin
AIRFLOW_UID=50000
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://deng:deng_dev_password@postgres:5432/deng
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

Optional Kaggle token:

```env
KAGGLE_API_TOKEN=your_token_here
```

Do not commit `.env`.

---

## 4. Start local services

```bash
make up
make ps
```

Expected services:

```text
postgres
pgadmin
airflow-webserver
airflow-scheduler
```

Open Airflow:

```text
http://localhost:8080
```

Login:

```text
Username: airflow
Password: airflow
```

Open pgAdmin:

```text
http://localhost:5050
```

Login:

```text
Email: admin@local.dev
Password: admin
```

---

## 5. Run and verify local pipeline

Trigger the local Airflow DAG:

```bash
make trigger-local
```

Then open Airflow at:

```text
http://localhost:8080
```

Log in with:

```text
Username: airflow
Password: airflow
```

In Airflow, look for the DAG named:

```text
bike_sharing_ingestion
```

The pipeline worked if:

* the DAG exists in the Airflow UI
* a new DAG run was created after `make trigger-local`
* the task `run_batch_ingestion_task` is green/successful
* the full DAG run is green/successful

Now verify the PostgreSQL output from the terminal.

### 5.1 Verify that the local tables exist

Run:

```bash
make verify-local
```

Expected result:

The output should list the project tables in PostgreSQL, including:

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

### 5.2 Verify local table row counts

Run:

```bash
make verify-local-counts
```

Expected result:

```text
bike_hour_raw                    17379
bike_day_raw                       731
bike_hour_analytics              17379
bike_day_analytics                 731
bike_hourly_demand_summary          24
bike_weekday_weekend_summary         2
bike_daily_trend_summary           731
bike_monthly_trend_summary          24
```

### 5.3 Verify the local weather summary

Run:

```bash
make verify-local-weather
```

Expected result:

The output should return grouped weather-demand rows. It should include these columns:

```text
weather_situation
weather_situation_label
avg_total_rentals
total_rentals
record_count
```

The rows should include weather groups such as:

```text
Clear/Partly cloudy
Mist/Cloudy
Light rain/snow
```



---

## 6. Connect pgAdmin to PostgreSQL

In pgAdmin, register a server with these values.

General:

```text
Name: deng
```

Connection:

```text
Host name/address: postgres
Port: 5432
Maintenance database: deng
Username: deng
Password: deng_dev_password
```

Tick `Save password` and then click `Save`.

Expected result: the `deng` database shows the `bike_*` tables under the public schema.

---

## 7. Configure cloud values

Confirm these values in `.env`:

```env
GCP_PROJECT_ID=deng-team2-bike-sharing
GCP_REGION=europe-west6
GCS_BUCKET_NAME=deng-team2-bike-sharing-data-lake
BQ_DATASET=bike_sharing
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp/service-account.json
```

Create the local credentials folder:

```bash
mkdir -p gcp
```

Place the service account key here:

```text
gcp/service-account.json
```

Do not commit this file.

---

## 8. Authenticate Google Cloud

```bash
gcloud auth login
gcloud config set project deng-team2-bike-sharing
gcloud config get-value project
```

Important:  
`If you have any problems with authentication, ask your preferred LLM for help.`

Enable required APIs:

```bash
gcloud services enable storage.googleapis.com bigquery.googleapis.com iam.googleapis.com cloudresourcemanager.googleapis.com
```

For Terraform from the host machine:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp/service-account.json"
```

---

## 9. Configure and apply Terraform

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Confirm:

```hcl
gcp_project_id  = "deng-team2-bike-sharing"
gcp_region      = "europe-west6"
gcs_bucket_name = "deng-team2-bike-sharing-data-lake"
bq_dataset_name = "bike_sharing"
```

Run Terraform:

```bash
make terraform-init
make terraform-plan
make terraform-apply
```

Expected infrastructure:

* GCS bucket: `deng-team2-bike-sharing-data-lake`
* BigQuery dataset: `bike_sharing`

Verify:

Go to `https://console.cloud.google.com` and see if the bucket is created.

---

## 10. Restart Docker after cloud config

```bash
make restart
make ps
```

Validate the cloud pipeline configuration:

```bash
make test-cloud-config
```

Expected result includes:

```text
Dry run finished successfully.
```

---

## 11. Run and verify cloud pipeline

Trigger the cloud DAG:

```bash
make trigger-cloud
```

Expected Airflow DAG:

```text
bike_sharing_cloud_pipeline
```

Expected tasks:

```text
validate_bigquery_pipeline_config
upload_raw_files_to_gcs
run_bigquery_pipeline
```

Verify GCS files:

```bash
gcloud storage ls gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/
```

Expected result:

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
```

Verify BigQuery tables:

```bash
bq ls deng-team2-bike-sharing:bike_sharing
make verify-cloud-counts
make verify-cloud-weather
```

---

## 12. Verify partitioning and clustering

Hourly analytics table:

```bash
bq show --format=prettyjson deng-team2-bike-sharing:bike_sharing.bike_hour_analytics
```

Expected:

* partitioned by `DATE(event_timestamp)`
* clustered by `hour_of_day`, `is_weekend`, `weather_situation`

Daily analytics table:

```bash
bq show --format=prettyjson deng-team2-bike-sharing:bike_sharing.bike_day_analytics
```

Expected:

* partitioned by `event_date`
* clustered by `is_weekend`, `weather_situation`

---

## 13. Backfill check

Run a local backfill example:

```bash
docker compose exec airflow-webserver airflow dags backfill bike_sharing_ingestion -s 2024-01-01 -e 2024-01-03
```

Expected result: Airflow creates historical DAG runs and the task finishes successfully.

---

## 14. Cleanup

Local cleanup:

```bash
make cleanup
```

Full cleanup, including Terraform-managed cloud infrastructure:

```bash
make cleanup-all
```

Secrets cleanup:

```bash
make cleanup-secrets
```

See:

[cleanup.md](cleanup.md)
