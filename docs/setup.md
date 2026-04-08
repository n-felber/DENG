# Setup

## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)
- [uv](https://github.com/astral-sh/uv)

## Optional Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

## Kaggle API Token

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

## Project setup

Start the project with Docker:

```bash
docker compose up --build
```

Expected result:

* Docker builds the `app` image
* The `db` container starts and becomes healthy
* The `pgadmin` container starts
* The `kestra` container starts
* The `app` container runs the ingestion pipeline once
* If the pipeline succeeds, the `app` container exits with status code `0`

## Verify that the local database works

After the containers are running, verify that PostgreSQL is populated.

### Check services

```bash
docker compose ps -a
```

Expected result:

* `db` is `Up` and healthy
* `pgadmin` is `Up`
* `kestra` is `Up`
* `app` is `Exited (0)`

A successful output should look similar to this:

```text
NAME              IMAGE                  COMMAND                  SERVICE    STATUS
deng-db-1         postgres:18            "docker-entrypoint.s…"   db         Up (healthy)
deng-pgadmin-1    dpage/pgadmin4         "/entrypoint.sh"         pgadmin    Up
deng-kestra-1     kestra/kestra:latest   "docker-entrypoint.s…"   kestra     Up
deng-app-1        deng-app               "python src/main.py"     app        Exited (0)
```

If `app` exits with a non-zero code, the pipeline failed.

### Check tables in PostgreSQL

```bash
docker compose exec db psql -U deng -d deng -c "\dt"
```

Expected result:

The following tables should exist:

* `bike_hour_raw`
* `bike_day_raw`
* `bike_day_analytics`

A successful output should look similar to this:

```text
               List of relations
 Schema |        Name         | Type  | Owner
--------+---------------------+-------+-------
 public | bike_day_analytics  | table | deng
 public | bike_day_raw        | table | deng
 public | bike_hour_raw       | table | deng
```

### Check row counts

```bash
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_hour_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_raw;"
docker compose exec db psql -U deng -d deng -c "SELECT COUNT(*) FROM bike_day_analytics;"
```

Expected result:

* `bike_hour_raw` contains `17379` rows
* `bike_day_raw` contains `731` rows
* `bike_day_analytics` contains `731` rows

Example successful outputs:

```text
 count
-------
 17379
(1 row)
```

```text
 count
-------
   731
(1 row)
```

```text
 count
-------
   731
(1 row)
```


### Open pgAdmin

Open in your browser:

```text
http://localhost:5050
````

Log in with:

* Email: `admin@local.dev`
* Password: `admin`

### Add the PostgreSQL server in pgAdmin

After logging in, add the database server manually:

1. In the left sidebar, right-click **Servers**
2. Click **Register**
3. Click **Server...**

A window with multiple tabs will open.

#### General tab

Fill in:

* **Name**: `deng`

#### Connection tab

Fill in:

* **Host name/address**: `db`
* **Port**: `5432`
* **Maintenance database**: `deng`
* **Username**: `deng`
* **Password**: `deng_dev_password`

Optional but recommended:

* Enable **Save password**

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

* `bike_day_analytics`
* `bike_day_raw`
* `bike_hour_raw`


### Optional: Open Kestra

Open:

```text
http://localhost:8081
```

Expected result:

* the Kestra UI opens in the browser
* the Kestra service is reachable
