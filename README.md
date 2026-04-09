# DENG

## Project Overview

This project implements a local batch data pipeline for the Bike Sharing dataset.

It includes:
- a Python batch ingestion pipeline
- a local PostgreSQL database
- pgAdmin for database inspection
- Kestra for workflow orchestration

## Documentation

- Use case: [docs/use_case.md](docs/use_case.md)
- Ingestion pipeline: [docs/ingestion.md](docs/ingestion.md)
- Setup: [docs/setup.md](docs/setup.md)
- Cleanup: [docs/cleanup.md](docs/cleanup.md)

## Run the project

Continue following the setup instructions in this README, or refer to the detailed setup guide here:

[docs/setup.md](docs/setup.md)


## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)
- [uv](https://github.com/astral-sh/uv)

## Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

If Kaggle authentication is required in your environment, create a local `.env` file based on `.env.example` and set:

```env
KAGGLE_API_TOKEN=your_kaggle_api_token_here
```

## Build and run the system

Build and start all services:

```bash
docker compose up --build
```

This starts:

* PostgreSQL
* pgAdmin
* Kestra
* the Python ingestion pipeline

All services run inside the same Docker Compose network and can communicate using their service names, such as `db`.

## Expected behavior

The `app` service runs the batch ingestion pipeline once.

A successful run should:

* download the Bike Sharing dataset source files
* load `bike_hour_raw` into PostgreSQL
* load `bike_day_raw` into PostgreSQL
* create the transformed table `bike_day_analytics`
* log verification output for the created tables

Because this is a batch pipeline, the `app` container is expected to exit after it finishes.
A successful batch run ends with `Exited (0)`.

## Service URLs

After startup, the following services should be reachable:

* PostgreSQL: `localhost:5432`
* pgAdmin: `http://localhost:5050`
* Kestra: `http://localhost:8081`

## Verify that it works

### 1. Check container status

```bash
docker compose ps -a
```

Expected result:

* `db` is `Up` and healthy
* `pgadmin` is `Up`
* `kestra` is `Up`
* `app` is `Exited (0)`

If `app` exits with a non-zero code, the pipeline failed.

### 2. Check pipeline logs

```bash
docker compose logs app
```

Expected result:

* database connection established
* both raw tables loaded
* transformed table created
* final success message

### 3. Check PostgreSQL tables

```bash
docker compose exec db psql -U deng -d deng -c "\dt"
```

Expected tables:

* `bike_hour_raw`
* `bike_day_raw`
* `bike_day_analytics`

### 4. Check row counts

```bash
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hour_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_analytics;"
```

Expected result:

* `bike_hour_raw` contains `17379` rows
* `bike_day_raw` contains `731` rows
* `bike_day_analytics` contains `731` rows

### 5. Preview transformed data

```bash
docker compose exec db psql -U deng -d deng -c "SELECT dteday, cnt, total_rentals, is_weekend, casual_share, registered_share FROM bike_day_analytics LIMIT 5;"
```

### 6. Verify with pgAdmin

Open in your browser:

```text
http://localhost:5050
```

Log in with:

* Email: `admin@local.dev`
* Password: `admin`

Add a new server with:

General tab:

* Name: `deng`

Connection tab:

* Host name/address: `db`
* Port: `5432`
* Maintenance database: `deng`
* Username: `deng`
* Password: `deng_dev_password`

After connecting, open:

`Servers -> deng -> Databases -> deng -> Schemas -> public -> Tables`

You should see:

* `bike_hour_raw`
* `bike_day_raw`
* `bike_day_analytics`

### 7. Verify Kestra

Open in your browser:

```text
http://localhost:8081
```

Expected result:

* the Kestra UI opens
* the orchestration service is reachable

## Repository note

The file `.env.example` is included as a template for local Kaggle API token setup.

