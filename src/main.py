"""
Batch ingestion pipeline for the Bike Sharing dataset.

This script downloads source data from Kaggle and loads it into a local
PostgreSQL database. Each pipeline run performs a full batch load of the
selected source files and replaces the corresponding raw tables.

Source dataset:
    lakshmi25npathi/bike-sharing-dataset

Source files:
    - hour.csv
    - day.csv

Target tables:
    - bike_hour_raw
    - bike_day_raw
"""

import logging
import os
import time

import kagglehub
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# -----------------------------
# Configuration
# -----------------------------

DATASET_HANDLE = "lakshmi25npathi/bike-sharing-dataset"

SOURCE_FILES = {
    "bike_hour_raw": "hour.csv",
    "bike_day_raw": "day.csv",
}

WRITE_CHUNK_SIZE = 1000
DB_CONNECT_RETRIES = 15
DB_CONNECT_DELAY_SECONDS = 2

DATABASE_URL = os.getenv("DATABASE_URL", "")
KAGGLE_API_TOKEN = os.getenv("KAGGLE_API_TOKEN", "")


# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """
    Validate the required runtime configuration.
    """
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. The ingestion pipeline needs a PostgreSQL "
            "connection string to load data into the database."
        )

    if KAGGLE_API_TOKEN:
        logger.info("Kaggle API token detected via environment variable.")
    else:
        logger.info(
            "No KAGGLE_API_TOKEN detected. Proceeding without explicit Kaggle "
            "authentication. This may still work for public datasets."
        )


def create_db_engine() -> Engine:
    """
    Create a SQLAlchemy engine for the configured PostgreSQL database.
    """
    return create_engine(DATABASE_URL)


def wait_for_db(
    engine: Engine,
    retries: int = DB_CONNECT_RETRIES,
    delay_seconds: int = DB_CONNECT_DELAY_SECONDS,
) -> None:
    """
    Wait until the PostgreSQL database is available.
    """
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            return
        except Exception as exc:
            logger.warning(
                "Database not ready yet (attempt %s/%s): %s",
                attempt,
                retries,
                exc,
            )
            if attempt == retries:
                raise
            time.sleep(delay_seconds)


def download_dataset_file(file_name: str) -> pd.DataFrame:
    """
    Download a single CSV file from the Kaggle dataset into a pandas DataFrame.
    Kompatibel mit kagglehub v0.3.3.
    """
    logger.info("Downloading source file '%s' from Kaggle...", file_name)

    try:
        # Klassischer Download-Weg, der in v0.3.3 stabil funktioniert
        downloaded_path = kagglehub.dataset_download(DATASET_HANDLE, file_name)
        
        # Falls ein Verzeichnis zurückgegeben wird, hängen wir den Dateinamen an
        if os.path.isdir(downloaded_path):
            file_path = os.path.join(downloaded_path, file_name)
        else:
            file_path = downloaded_path
            
        # Manuelles Einlesen via Pandas
        df = pd.read_csv(file_path)
        
    except Exception as exc:
        raise RuntimeError(
            "Failed to download the Kaggle dataset file. "
            "If Kaggle requires authentication in your environment, set "
            "KAGGLE_API_TOKEN in your shell or .env file before running "
            "docker compose up --build."
        ) from exc

    if df.empty:
        raise RuntimeError(f"Downloaded file '{file_name}' is empty.")

    logger.info(
        "Downloaded '%s' successfully with %s rows and %s columns.",
        file_name,
        df.shape[0],
        df.shape[1],
    )

    return df


def log_dataframe_overview(table_name: str, df: pd.DataFrame) -> None:
    """
    Log a compact overview of a DataFrame before writing it to PostgreSQL.
    """
    logger.info("Preparing table '%s'.", table_name)
    logger.info("Columns for '%s': %s", table_name, list(df.columns))
    logger.info("Shape for '%s': %s", table_name, df.shape)


def load_dataframe_to_postgres(
    engine: Engine,
    df: pd.DataFrame,
    table_name: str,
    chunk_size: int = WRITE_CHUNK_SIZE,
) -> None:
    """
    Load a DataFrame into PostgreSQL.
    """
    logger.info("Loading '%s' into PostgreSQL...", table_name)

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=chunk_size,
            method="multi",
        )

    logger.info("Finished loading '%s'.", table_name)


def verify_table_row_count(engine: Engine, table_name: str) -> None:
    """
    Verify that a target table exists and log its row count.
    """
    query = text(f"SELECT COUNT(*) FROM {table_name}")

    with engine.connect() as conn:
        row_count = conn.execute(query).scalar_one()

    logger.info("Verification for '%s': %s rows present.", table_name, row_count)


def transform_bike_day(engine: Engine) -> None:
    """
    Create an analytics-ready version of the daily bike dataset.
    """
    logger.info("Starting transformation for bike_day...")

    query = """
    CREATE TABLE bike_day_analytics AS
    SELECT
        *,
        dteday::date AS event_date,
        2011 + yr AS year,
        mnth AS month,
        TO_CHAR(dteday::date, 'FMDay') AS day_name,
        TO_CHAR(dteday::date, 'FMMonth') AS month_name,

        CASE
            WHEN weekday IN (0, 6) THEN TRUE
            ELSE FALSE
        END AS is_weekend,

        weathersit AS weather_situation,

        CASE
            WHEN weathersit = 1 THEN 'Clear/Partly cloudy'
            WHEN weathersit = 2 THEN 'Mist/Cloudy'
            WHEN weathersit = 3 THEN 'Light rain/snow'
            WHEN weathersit = 4 THEN 'Heavy rain/snow'
            ELSE 'Unknown'
        END AS weather_situation_label,

        hum AS humidity,

        cnt AS total_rentals,

        CASE
            WHEN cnt = 0 THEN 0
            ELSE casual::float / cnt
        END AS casual_share,

        CASE
            WHEN cnt = 0 THEN 0
            ELSE registered::float / cnt
        END AS registered_share

    FROM bike_day_raw;
    """

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS bike_day_analytics"))
        conn.execute(text(query))

    logger.info("Finished transformation for bike_day.")
    verify_table_row_count(engine, "bike_day_analytics")


def transform_bike_hour(engine: Engine) -> None:
    """
    Create an analytics-ready version of the hourly bike dataset.
    """
    logger.info("Starting transformation for bike_hour...")

    query = """
    CREATE TABLE bike_hour_analytics AS
    SELECT
        *,
        dteday::date AS event_date,
        dteday::timestamp + (hr * INTERVAL '1 hour') AS event_timestamp,
        2011 + yr AS year,
        mnth AS month,
        hr AS hour_of_day,
        TO_CHAR(dteday::date, 'FMDay') AS day_name,
        TO_CHAR(dteday::date, 'FMMonth') AS month_name,

        CASE
            WHEN weekday IN (0, 6) THEN TRUE
            ELSE FALSE
        END AS is_weekend,

        weathersit AS weather_situation,

        CASE
            WHEN weathersit = 1 THEN 'Clear/Partly cloudy'
            WHEN weathersit = 2 THEN 'Mist/Cloudy'
            WHEN weathersit = 3 THEN 'Light rain/snow'
            WHEN weathersit = 4 THEN 'Heavy rain/snow'
            ELSE 'Unknown'
        END AS weather_situation_label,

        hum AS humidity,

        cnt AS total_rentals,

        CASE
            WHEN cnt = 0 THEN 0
            ELSE casual::float / cnt
        END AS casual_share,

        CASE
            WHEN cnt = 0 THEN 0
            ELSE registered::float / cnt
        END AS registered_share

    FROM bike_hour_raw;
    """

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS bike_hour_analytics"))
        conn.execute(text(query))

    logger.info("Finished transformation for bike_hour.")
    verify_table_row_count(engine, "bike_hour_analytics")


def create_summary_tables(engine: Engine) -> None:
    """
    Create aggregated summary tables for recurring analytics questions.
    """
    logger.info("Starting creation of summary tables...")

    summary_queries = {
        "bike_hourly_demand_summary": """
            CREATE TABLE bike_hourly_demand_summary AS
            SELECT
                hour_of_day,
                AVG(total_rentals) AS avg_total_rentals,
                SUM(total_rentals) AS total_rentals,
                COUNT(*) AS record_count
            FROM bike_hour_analytics
            GROUP BY hour_of_day
            ORDER BY hour_of_day;
        """,
        "bike_weekday_weekend_summary": """
            CREATE TABLE bike_weekday_weekend_summary AS
            SELECT
                is_weekend,
                CASE
                    WHEN is_weekend THEN 'weekend'
                    ELSE 'weekday'
                END AS day_type,
                AVG(total_rentals) AS avg_total_rentals,
                SUM(total_rentals) AS total_rentals,
                COUNT(*) AS record_count
            FROM bike_day_analytics
            GROUP BY is_weekend
            ORDER BY is_weekend;
        """,
        "bike_weather_demand_summary": """
            CREATE TABLE bike_weather_demand_summary AS
            SELECT
                weather_situation,
                weather_situation_label,
                AVG(total_rentals) AS avg_total_rentals,
                SUM(total_rentals) AS total_rentals,
                COUNT(*) AS record_count
            FROM bike_day_analytics
            GROUP BY weather_situation, weather_situation_label
            ORDER BY weather_situation;
        """,
        "bike_daily_trend_summary": """
            CREATE TABLE bike_daily_trend_summary AS
            SELECT
                event_date,
                day_name,
                month,
                month_name,
                year,
                total_rentals,
                casual,
                registered
            FROM bike_day_analytics
            ORDER BY event_date;
        """,
        "bike_monthly_trend_summary": """
            CREATE TABLE bike_monthly_trend_summary AS
            SELECT
                year,
                month,
                month_name,
                SUM(total_rentals) AS total_rentals,
                AVG(total_rentals) AS avg_daily_rentals,
                SUM(casual) AS casual_rentals,
                SUM(registered) AS registered_rentals,
                COUNT(*) AS day_count
            FROM bike_day_analytics
            GROUP BY year, month, month_name
            ORDER BY year, month;
        """,
    }

    with engine.begin() as conn:
        for table_name, query in summary_queries.items():
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.execute(text(query))

    for table_name in summary_queries:
        verify_table_row_count(engine, table_name)

    logger.info("Finished creation of summary tables.")


def run_batch_ingestion() -> None:
    """
    Run the full batch ingestion process.
    """
    logger.info("--- Starting batch ingestion pipeline ---")

    validate_environment()

    engine = create_db_engine()
    wait_for_db(engine)

    for table_name, file_name in SOURCE_FILES.items():
        df = download_dataset_file(file_name)
        log_dataframe_overview(table_name, df)
        load_dataframe_to_postgres(engine, df, table_name)
        verify_table_row_count(engine, table_name)

    transform_bike_day(engine)
    transform_bike_hour(engine)
    create_summary_tables(engine)

    logger.info("--- Batch ingestion pipeline finished successfully ---")


if __name__ == "__main__":
    run_batch_ingestion()