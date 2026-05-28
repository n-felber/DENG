# Setup Guide

This guide explains how to set up, run, and verify the full DENG Team 2 Bike Sharing data pipeline.

The project contains two runnable pipeline paths:

1. **Local pipeline**

   * Kaggle dataset
   * PostgreSQL
   * pgAdmin
   * Airflow orchestration

2. **Cloud pipeline**

   * Kaggle dataset
   * Google Cloud Storage data lake
   * BigQuery raw tables
   * BigQuery analytics and summary tables
   * Airflow orchestration
   * Terraform-managed cloud infrastructure

Use the commands in this guide from the project root directory.

---

## 1. Prerequisites

Before starting the project setup, make sure the following tools and accounts are available.

This guide does not explain how to install these prerequisites. Use the official documentation links below if something is missing.

| Requirement          | Purpose                                                                           | Where to get it / documentation                                                  |
| -------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Docker Desktop       | Runs PostgreSQL, pgAdmin, Airflow, and the pipeline services locally              | [Docker Desktop](https://www.docker.com/products/docker-desktop/)                |
| Docker Compose       | Starts and manages the local multi-container environment                          | [Docker Compose documentation](https://docs.docker.com/compose/)                 |
| Make                 | Runs project commands such as `make up`, `make trigger-local`, and `make cleanup` | [GNU Make documentation](https://www.gnu.org/software/make/)                     |
| Terraform            | Provisions the Google Cloud Storage bucket and BigQuery dataset                   | [Terraform installation docs](https://developer.hashicorp.com/terraform/install) |
| Google Cloud CLI     | Authenticates with Google Cloud and verifies GCS/BigQuery resources               | [Google Cloud CLI docs](https://cloud.google.com/sdk/docs/install)               |
| Google Cloud project | Hosts the cloud data lake and BigQuery warehouse                                  | [Google Cloud console](https://console.cloud.google.com/)                        |
| Kaggle account       | Provides access to the Bike Sharing dataset if Kaggle authentication is required  | [Kaggle](https://www.kaggle.com/)                                                |

After the prerequisites are installed, verify that the required command-line tools are available:

```bash
docker --version
docker compose version
make --version
terraform version
gcloud version
```

Expected result:

* Docker prints a version number
* Docker Compose prints a version number
* Make prints a version number
* Terraform prints a version number
* Google Cloud CLI prints a version number

If one of these commands is not found, install or fix that prerequisite first before continuing with the project setup.

---

## 2. Clone the repository

Clone the repository and enter the project directory:

```bash
git clone git@github.com:n-felber/DENG.git
cd DENG
```

---

## 3. Check the available Make commands

The project includes a `Makefile` with common commands for running, validating, and cleaning the project.

Show all available commands:

```bash
make help
```

---

## 4. Create the local environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and confirm that the local database settings are present:

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

The `.env` file must not be committed to Git.

---

## 5. Optional Kaggle authentication

The project uses the Kaggle Bike Sharing dataset.

Dataset:

```text
lakshmi25npathi/bike-sharing-dataset
```

In some environments, the dataset can be downloaded without explicit Kaggle authentication. If Kaggle authentication is required, create a Kaggle API token.

### Create a Kaggle token

1. Open Kaggle in the browser.
2. Log in to your Kaggle account.
3. Open your account settings.
4. Go to the API section.
5. Click **Create New Token**.
6. Copy the token value.

Then open `.env` and set:

```env
KAGGLE_API_TOKEN=your_token_here
```

Expected result:

The project can download:

```text
hour.csv
day.csv
```

from the Kaggle dataset.

---

## 6. Start the local Docker environment

Start all local services:

```bash
make up
```

Expected result:

Docker starts the following services:

* `postgres`
* `pgadmin`
* `airflow-webserver`
* `airflow-scheduler`

Check service status:

```bash
make ps
```

Expected result:

```text
postgres              Up / healthy
pgadmin               Up
airflow-webserver     Up
airflow-scheduler     Up
```

If Airflow is still starting, run the status command again after waiting for some time:

```bash
make ps
```

The important result is that the services are running and PostgreSQL is healthy.

---

## 7. Open Airflow

Open Airflow in the browser:

```text
http://localhost:8080
```

Log in with:

```text
Username: airflow
Password: airflow
```

Expected result:

The Airflow UI opens successfully.

You should see the local DAG:

```text
bike_sharing_ingestion
```

You should also see the cloud DAG after the cloud DAG file has been added:

```text
bike_sharing_cloud_pipeline
```

---

## 8. Run the local PostgreSQL pipeline

Trigger the local DAG with Make:

```bash
make trigger-local
```

Expected terminal result:

Airflow creates a new DAG run for:

```text
bike_sharing_ingestion
```

Now open Airflow if you haven't already:

```text
http://localhost:8080
```

Expected Airflow result:

* DAG `bike_sharing_ingestion` exists
* A new DAG run appears
* The task `run_batch_ingestion_task` finishes successfully
* The DAG run becomes green

---

## 9. Verify local PostgreSQL tables

List the project tables:

```bash
make verify-local
```

Expected result:

The following tables should exist:

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

Check row counts:

```bash
make verify-local-counts
```

Expected row counts:

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

Check the weather summary table:

```bash
make verify-local-weather
```

Expected result:

The query returns grouped weather demand rows with columns such as:

```text
weather_situation
weather_situation_label
avg_total_rentals
total_rentals
record_count
```

---

## 10. Open pgAdmin

Open pgAdmin in the browser:

```text
http://localhost:5050
```

Log in with:

```text
Email: admin@local.dev
Password: admin
```

Expected result:

The pgAdmin UI opens successfully.

---

## 11. Connect pgAdmin to PostgreSQL

After logging in to pgAdmin:

1. In the left sidebar, right-click **Servers**
2. Click **Register**
3. Click **Server...**

Use these settings.

### General tab

```text
Name: deng
```

### Connection tab

```text
Host name/address: postgres
Port: 5432
Maintenance database: deng
Username: deng
Password: deng_dev_password
```

Enable:

```text
Save password
```

Then click **Save**.

Expected result:

A server named:

```text
deng
```

appears in the pgAdmin sidebar.

Expand:

```text
Servers
  deng
    Databases
      deng
        Schemas
          public
            Tables
```

Expected result:

The following project tables are visible:

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

---

# Cloud Setup

The cloud setup provisions and runs the final pipeline on Google Cloud.

The cloud pipeline uses:

* Terraform
* Google Cloud Storage
* BigQuery
* Airflow
* Service account authentication

---

## 12. Configure Google Cloud values

The project uses these default cloud values:

```text
GCP project ID: deng-team2-bike-sharing
GCP region: europe-west6
GCS bucket: deng-team2-bike-sharing-data-lake
BigQuery dataset: bike_sharing
Service account ID: deng-team2-pipeline-sa
```

The expected GCS paths are:

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
```

The expected BigQuery tables are:

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

Open `.env` and confirm:

```env
GCP_PROJECT_ID=deng-team2-bike-sharing
GCP_REGION=europe-west6
GCS_BUCKET_NAME=deng-team2-bike-sharing-data-lake
BQ_DATASET=bike_sharing
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp/service-account.json
```

If the GCP project ID or bucket name is different, update `.env` and `terraform/terraform.tfvars`.

---

## 13. Log in to Google Cloud

Log in with the Google Cloud CLI:

```bash
gcloud auth login
```

Set the active project:

```bash
gcloud config set project deng-team2-bike-sharing
```

Confirm the active project:

```bash
gcloud config get-value project
```

Expected result:

```text
deng-team2-bike-sharing
```

Enable required Google Cloud APIs:

```bash
gcloud services enable storage.googleapis.com bigquery.googleapis.com iam.googleapis.com cloudresourcemanager.googleapis.com
```

Expected result:

The command finishes without an error.

---

## 14. Create or add the service account key

Create the local folder for the service account key:

```bash
mkdir -p gcp
```

If your team already has a service account JSON key, place it here:

```text
gcp/service-account.json
```

If you need to create the service account, run:

```bash
gcloud iam service-accounts create deng-team2-pipeline-sa \
  --display-name="DENG Team 2 Pipeline Service Account"
```

Grant the required project roles:

```bash
gcloud projects add-iam-policy-binding deng-team2-bike-sharing \
  --member="serviceAccount:deng-team2-pipeline-sa@deng-team2-bike-sharing.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding deng-team2-bike-sharing \
  --member="serviceAccount:deng-team2-pipeline-sa@deng-team2-bike-sharing.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"
```

Create the local JSON key:

```bash
gcloud iam service-accounts keys create gcp/service-account.json \
  --iam-account=deng-team2-pipeline-sa@deng-team2-bike-sharing.iam.gserviceaccount.com
```

Expected result:

The file exists locally:

```bash
ls gcp/service-account.json
```

Expected output:

```text
gcp/service-account.json
```

Important:

```text
gcp/service-account.json
```

contains credentials and must not be committed to Git.

---

## 15. Configure Terraform variables

Copy the Terraform variables example:

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Open:

```text
terraform/terraform.tfvars
```

Confirm that it contains:

```hcl
gcp_project_id  = "deng-team2-bike-sharing"
gcp_region      = "europe-west6"
gcs_bucket_name = "deng-team2-bike-sharing-data-lake"
bq_dataset_name = "bike_sharing"
```

The file:

```text
terraform/terraform.tfvars
```

must not be committed to Git.

---

## 16. Make the service account available to Terraform

From the project root, run:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp/service-account.json"
```

Verify:

```bash
echo "$GOOGLE_APPLICATION_CREDENTIALS"
```

Expected result:

The printed path ends with:

```text
gcp/service-account.json
```

---

## 17. Provision cloud infrastructure with Terraform

Initialize Terraform:

```bash
make terraform-init
```

Expected result:

Terraform initializes successfully and downloads the Google provider.

Plan the infrastructure:

```bash
make terraform-plan
```

Expected result for a fresh setup:

```text
Plan: 2 to add, 0 to change, 0 to destroy.
```

The two resources are:

* Google Cloud Storage bucket
* BigQuery dataset

Apply the infrastructure:

```bash
make terraform-apply
```

When Terraform asks for approval, type:

```text
yes
```

Expected result:

Terraform finishes successfully and prints outputs such as:

```text
gcs_bucket_url = "gs://deng-team2-bike-sharing-data-lake"
bigquery_dataset_id = "bike_sharing"
```

---

## 18. Verify cloud infrastructure

Verify the GCS bucket:

```bash
gcloud storage buckets list --project=deng-team2-bike-sharing
```

Expected result:

The list contains:

```text
deng-team2-bike-sharing-data-lake
```

Verify the BigQuery dataset:

```bash
bq ls --project_id=deng-team2-bike-sharing
```

Expected result:

The list contains:

```text
bike_sharing
```

---

## 19. Restart Docker after cloud configuration

Restart the Docker services so Airflow has the latest `.env` and mounted credentials:

```bash
make restart
```

Check services:

```bash
make ps
```

Expected result:

```text
postgres              Up / healthy
pgadmin               Up
airflow-webserver     Up
airflow-scheduler     Up
```

---

## 20. Validate cloud pipeline configuration

Run the cloud dry run:

```bash
make test-cloud-config
```

Expected result:

The output includes:

```text
Dry run configuration:
Project: deng-team2-bike-sharing
Dataset: bike_sharing
Bucket: gs://deng-team2-bike-sharing-data-lake
Location: europe-west6
```

It should also include:

```text
Dry run finished successfully.
```

This confirms that the cloud pipeline can read the required environment variables and render the BigQuery SQL files.

---

## 21. Run the cloud Airflow pipeline

Trigger the cloud pipeline:

```bash
make trigger-cloud
```

Expected terminal result:

Airflow creates a new DAG run for:

```text
bike_sharing_cloud_pipeline
```

Open Airflow:

```text
http://localhost:8080
```

Log in with:

```text
Username: airflow
Password: airflow
```

Expected Airflow result:

The DAG:

```text
bike_sharing_cloud_pipeline
```

has a new run.

The cloud pipeline tasks should finish successfully, including:

```text
validate_bigquery_pipeline_config
upload_raw_files_to_gcs
run_bigquery_pipeline
```

Expected final Airflow result:

* all tasks are green
* the full DAG run is green

---

## 22. Verify files in Google Cloud Storage

Check the raw files in the GCS bucket:

```bash
gcloud storage ls gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/
```

Expected result:

```text
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/day.csv
gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/hour.csv
```

---

## 23. Verify BigQuery tables

List the BigQuery tables:

```bash
bq ls deng-team2-bike-sharing:bike_sharing
```

Expected result:

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

Check row counts:

```bash
make verify-cloud-counts
```

Expected row counts:

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

Check the weather summary table:

```bash
make verify-cloud-weather
```

Expected result:

The query returns grouped weather demand rows with columns such as:

```text
weather_situation
weather_situation_label
avg_total_rentals
total_rentals
record_count
```

---

## 24. Verify partitioning and clustering

Check the hourly analytics table:

```bash
bq show --format=prettyjson deng-team2-bike-sharing:bike_sharing.bike_hour_analytics
```

Expected result:

The output contains partitioning information for:

```text
event_timestamp
```

or:

```text
DATE(event_timestamp)
```

It should also contain clustering fields:

```text
hour_of_day
is_weekend
weather_situation
```

Check the daily analytics table:

```bash
bq show --format=prettyjson deng-team2-bike-sharing:bike_sharing.bike_day_analytics
```

Expected result:

The output contains partitioning information for:

```text
event_date
```

It should also contain clustering fields:

```text
is_weekend
weather_situation
```

---

## 25. Verify Airflow scheduling and backfills

Open Airflow:

```text
http://localhost:8080
```

Log in with:

```text
Username: airflow
Password: airflow
```

Expected result for the local DAG:

```text
bike_sharing_ingestion
```

The schedule should be:

```text
@daily
```

Expected result for the cloud DAG:

```text
bike_sharing_cloud_pipeline
```

The schedule should be:

```text
@daily
```

Run a local backfill example:

```bash
docker compose exec airflow-webserver airflow dags backfill bike_sharing_ingestion -s 2024-01-01 -e 2024-01-03
```

Expected result:

Airflow creates DAG runs for the selected dates.

The task:

```text
run_batch_ingestion_task
```

should finish successfully for each backfill run.

---

## 26. Troubleshooting

### Airflow UI does not open

Wait a minute, then check services:

```bash
make ps
```

Expected result:

```text
airflow-webserver     Up
airflow-scheduler     Up
postgres              Up / healthy
```

Check logs:

```bash
make logs
```

Look for errors in:

```text
airflow-webserver
airflow-scheduler
postgres
```

---

### Airflow login does not work

Use:

```text
Username: airflow
Password: airflow
```

The user is created automatically when the Airflow webserver container starts.

---

### PostgreSQL is not healthy

Check services:

```bash
make ps
```

Check logs:

```bash
docker compose logs postgres
```

Expected database values from `.env`:

```env
POSTGRES_USER=deng
POSTGRES_PASSWORD=deng_dev_password
POSTGRES_DB=deng
```

---

### pgAdmin cannot connect to PostgreSQL

Use these pgAdmin connection settings:

```text
Host name/address: postgres
Port: 5432
Maintenance database: deng
Username: deng
Password: deng_dev_password
```

Do not use:

```text
localhost
```

as the pgAdmin host, because pgAdmin runs inside Docker and must connect to the Compose service name:

```text
postgres
```

---

### Kaggle download fails

Set a Kaggle API token in `.env`:

```env
KAGGLE_API_TOKEN=your_token_here
```

Then restart services:

```bash
make restart
```

Trigger the pipeline again:

```bash
make trigger-local
```

---

### Terraform cannot authenticate

Confirm that the service account key exists:

```bash
ls gcp/service-account.json
```

Then export the credential path:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp/service-account.json"
```

Run Terraform again:

```bash
make terraform-plan
```

---

### Cloud DAG cannot find Google credentials

Confirm that `.env` contains:

```env
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp/service-account.json
```

Confirm that the local file exists:

```bash
ls gcp/service-account.json
```

Restart Docker:

```bash
make restart
```

Run the dry run:

```bash
make test-cloud-config
```

Expected result:

```text
Dry run finished successfully.
```

---

### BigQuery tables are missing

First confirm that the cloud DAG finished successfully in Airflow.

Then check GCS:

```bash
gcloud storage ls gs://deng-team2-bike-sharing-data-lake/raw/bike_sharing/
```

Expected result:

```text
day.csv
hour.csv
```

Then list BigQuery tables:

```bash
bq ls deng-team2-bike-sharing:bike_sharing
```

Expected result:

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

---

## 27. Cleanup

Cleanup is documented separately because it deletes local runtime data and can also destroy cloud infrastructure.

See [Cleanup Guide](cleanup.md).

For full cleanup including cloud infrastructure:

```bash
make cleanup-all
```

For removing local secrets:

```bash
make cleanup-secrets
```

Only run full cleanup after all screenshots and verification evidence have been collected.
