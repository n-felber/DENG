# Setup

## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)

## Optional Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

## Kaggle API Token

For the official Kaggle API documentation, including authentication details and usage, see the Kaggle Public API docs: https://www.kaggle.com/docs/api.

This project downloads a dataset from Kaggle.  
To access the dataset, you may need a personal Kaggle API token.

### Step 1 – Create a Kaggle account

1. Go to https://www.kaggle.com
2. Create an account or log in

### Step 2 – Open the account settings

1. Open https://www.kaggle.com/settings
2. Scroll to the **API** section

### Step 3 – Create a new token

1. Click **Create New Token**

### Step 4 – Copy the token

After creating the token, Kaggle will show it once.  
Copy the token directly.

### Step 5 – Create a `.env` file

1. Copy the file `.env.example` in the project
2. Rename the copy to:

```text
.env
```

3. Open `.env`
4. Paste your token:

```env
KAGGLE_API_TOKEN=your_token_here
```

**Important:**  
The token is only shown once. If you do not copy it, you will need to create a new one.

The `.env` file contains sensitive credentials and must **not be committed** to GitHub.

## Start the system

Start the project with Docker:

```bash
docker compose up -d
```

Expected result:

- the `postgres` container starts and becomes healthy
- the `pgadmin` container starts
- the `airflow-webserver` container starts
- the `airflow-scheduler` container starts

## Open Airflow

Open in your browser:

```text
http://localhost:8080
```

If http://localhost:8080 is not available yet, Airflow may still be starting up, so wait a few minutes and then try again.

Log in with:

- Username: `airflow`
- Password: `airflow`

### Expected result

The DAG `bike_sharing_ingestion` is visible in the Airflow UI.

## Run the pipeline

Trigger the DAG once from the Airflow UI, or run:

```bash
docker compose exec airflow-webserver airflow dags trigger bike_sharing_ingestion
```

### Expected result

A DAG run starts, and the task `run_batch_ingestion_task` finishes successfully.

## Verify that PostgreSQL is populated

### Check services

```bash
docker compose ps
```

Expected result:

- `postgres` is `Up` and healthy
- `pgadmin` is `Up`
- `airflow-webserver` is `Up`
- `airflow-scheduler` is `Up`

### Check project tables in PostgreSQL

Airflow stores its own metadata tables in the same PostgreSQL database. To inspect only the tables created by this project, run:

```bash
docker compose exec postgres psql -U deng -d deng -c "\dt public.bike_*"
```

The following tables should exist:

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

### Check row counts

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

## Open pgAdmin

Open in your browser:

```text
http://localhost:5050
```

Log in with:

- Email: `admin@local.dev`
- Password: `admin`

## Add the PostgreSQL server in pgAdmin

After logging in, add the database server manually:

1. In the left sidebar, right-click **Servers**
2. Click **Register**
3. Click **Server...**

A window with multiple tabs will open.

### General tab

Fill in:

- **Name**: `deng`

### Connection tab

Fill in:

- **Host name/address**: `postgres`
- **Port**: `5432`
- **Maintenance database**: `deng`
- **Username**: `deng`
- **Password**: `deng_dev_password`

Optional but recommended:

- Enable **Save password**

Then:

1. Click **Save**

### Expected result

After saving, the server `deng` appears under **Servers** in the left sidebar.

Expand the items in this order:

1. **Servers**
2. `deng`
3. **Databases**
4. `deng`
5. **Schemas**
6. `public`
7. **Tables**

Inside **Tables**, you should see:

- `bike_hour_raw`
- `bike_day_raw`
- `bike_hour_analytics`
- `bike_day_analytics`
- `bike_hourly_demand_summary`
- `bike_weekday_weekend_summary`
- `bike_weather_demand_summary`
- `bike_daily_trend_summary`
- `bike_monthly_trend_summary`

## Verify backfills

Airflow supports backfills. Example:

```bash
docker compose exec airflow-webserver airflow dags backfill bike_sharing_ingestion -s 2024-01-01 -e 2024-01-03
```

A successful backfill creates past DAG runs for the selected date range.
