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

Follow the setup guide:

[docs/setup.md](docs/setup.md)

## Verify local storage

After starting the project, verify that PostgreSQL contains the expected tables.

### Expected PostgreSQL tables

The pipeline should create:

- `bike_hour_raw`
- `bike_day_raw`
- `bike_day_analytics`

### Verify with Docker + psql

Check that the tables exist:

```bash
docker compose exec db psql -U deng -d deng -c "\dt"
```

Check row counts:

```bash
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hour_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_analytics;"
```

Preview transformed data:

```bash
docker compose exec db psql -U deng -d deng -c "SELECT dteday, cnt, total_rentals, is_weekend, casual_share, registered_share FROM bike_day_analytics LIMIT 5;"
```

### Verify with pgAdmin

Open pgAdmin in the browser:

```text
http://localhost:5050
```

Login:

* Email: `admin@local.dev`
* Password: `admin`

Register a new server with these values:

* Name: `deng-postgres`

Connection tab:

* Host name/address: `db`
* Port: `5432`
* Maintenance database: `deng`
* Username: `deng`
* Password: `deng_dev_password`

After connecting, open:

`Servers -> deng-postgres -> Databases -> deng -> Schemas -> public -> Tables`

You should see:

* `bike_hour_raw`
* `bike_day_raw`
* `bike_day_analytics`

## Repository note

The file `.env.example` is included as a template for local Kaggle API token setup.
