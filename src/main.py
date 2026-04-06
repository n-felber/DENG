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
from kagglehub import KaggleDatasetAdapter
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

    This pipeline strictly requires:
    - DATABASE_URL

    Kaggle authentication is not always required for public datasets,
    so the pipeline does not fail early if KAGGLE_API_TOKEN is missing.
    Instead, it will try the download first and raise a clear error
    message only if Kaggle rejects the request.
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

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    return create_engine(DATABASE_URL)


def wait_for_db(
    engine: Engine,
    retries: int = DB_CONNECT_RETRIES,
    delay_seconds: int = DB_CONNECT_DELAY_SECONDS,
) -> None:
    """
    Wait until the PostgreSQL database is available.

    Args:
        engine: SQLAlchemy engine connected to PostgreSQL.
        retries: Maximum number of connection attempts.
        delay_seconds: Delay between retries in seconds.

    Raises:
        Exception: Re-raises the last connection error if all retries fail.
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

    Args:
        file_name: Name of the file inside the dataset repository.

    Returns:
        pd.DataFrame: Loaded DataFrame.

    Raises:
        RuntimeError: If the file is empty or if Kaggle access fails.
    """
    logger.info("Downloading source file '%s' from Kaggle...", file_name)

    try:
        df = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            DATASET_HANDLE,
            file_name,
        )
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

    Args:
        table_name: Name of the target database table.
        df: DataFrame to be loaded.
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

    Each run replaces the target table so that the batch pipeline produces
    a fresh raw layer from the source files.

    Args:
        engine: SQLAlchemy engine connected to PostgreSQL.
        df: DataFrame to load.
        table_name: Target PostgreSQL table name.
        chunk_size: Number of rows per batch insert.
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

    Args:
        engine: SQLAlchemy engine connected to PostgreSQL.
        table_name: Name of the table to check.
    """
    query = text(f"SELECT COUNT(*) FROM {table_name}")

    with engine.connect() as conn:
        row_count = conn.execute(query).scalar_one()

    logger.info("Verification for '%s': %s rows present.", table_name, row_count)


def run_batch_ingestion() -> None:
    """
    Run the full batch ingestion process.

    Steps:
    1. Validate runtime configuration
    2. Wait for PostgreSQL
    3. Download each source file from Kaggle
    4. Load raw tables into PostgreSQL
    5. Verify row counts
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

    logger.info("--- Batch ingestion pipeline finished successfully ---")


if __name__ == "__main__":
    run_batch_ingestion()
