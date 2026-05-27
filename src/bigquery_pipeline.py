"""
BigQuery pipeline for the Bike Sharing cloud warehouse.

This module:
1. Loads raw CSV files from GCS into BigQuery raw tables.
2. Runs BigQuery SQL transformations.
3. Verifies that expected output tables contain rows.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from google.cloud import bigquery


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"

RAW_FILES = {
    "bike_hour_raw": "raw/bike_sharing/hour.csv",
    "bike_day_raw": "raw/bike_sharing/day.csv",
}

SQL_FILES = [
    "create_bike_hour_analytics.sql",
    "create_bike_day_analytics.sql",
    "create_summary_tables.sql",
]

EXPECTED_TABLES = [
    "bike_hour_raw",
    "bike_day_raw",
    "bike_hour_analytics",
    "bike_day_analytics",
    "bike_hourly_demand_summary",
    "bike_weekday_weekend_summary",
    "bike_weather_demand_summary",
    "bike_daily_trend_summary",
    "bike_monthly_trend_summary",
]


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_config() -> dict[str, str]:
    return {
        "project_id": get_required_env("GCP_PROJECT_ID"),
        "dataset_id": get_required_env("BQ_DATASET"),
        "bucket_name": get_required_env("GCS_BUCKET_NAME"),
        "location": os.getenv("GCP_REGION", "europe-west6").strip(),
    }


def read_sql_file(file_name: str) -> str:
    path = SQL_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"Missing SQL file: {path}")
    return path.read_text(encoding="utf-8")


def render_sql(sql: str, config: dict[str, str]) -> str:
    return sql.format(
        project_id=config["project_id"],
        dataset_id=config["dataset_id"],
    )


def get_bigquery_client(config: dict[str, str]) -> bigquery.Client:
    return bigquery.Client(project=config["project_id"])


def load_csv_from_gcs(
    client: bigquery.Client,
    config: dict[str, str],
    table_name: str,
    gcs_path: str,
) -> None:
    table_id = f"{config['project_id']}.{config['dataset_id']}.{table_name}"
    uri = f"gs://{config['bucket_name']}/{gcs_path}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Loading {uri} into {table_id}...")
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}.")


def run_query(client: bigquery.Client, config: dict[str, str], sql: str) -> None:
    query_job = client.query(sql, location=config["location"])
    query_job.result()


def run_transformations(client: bigquery.Client, config: dict[str, str]) -> None:
    for file_name in SQL_FILES:
        print(f"Running SQL file: {file_name}")
        sql = render_sql(read_sql_file(file_name), config)
        run_query(client, config, sql)


def get_row_count(
    client: bigquery.Client,
    config: dict[str, str],
    table_name: str,
) -> int:
    table_id = f"`{config['project_id']}.{config['dataset_id']}.{table_name}`"
    sql = f"SELECT COUNT(*) AS row_count FROM {table_id}"
    rows = list(client.query(sql, location=config["location"]).result())
    return int(rows[0]["row_count"])


def verify_outputs(client: bigquery.Client, config: dict[str, str]) -> None:
    for table_name in EXPECTED_TABLES:
        row_count = get_row_count(client, config, table_name)
        if row_count <= 0:
            raise RuntimeError(f"Table {table_name} has no rows.")
        print(f"Verified {table_name}: {row_count} rows.")


def run_pipeline(dry_run: bool = False) -> None:
    config = get_config()

    if dry_run:
        print("Dry run configuration:")
        print(f"Project: {config['project_id']}")
        print(f"Dataset: {config['dataset_id']}")
        print(f"Bucket: gs://{config['bucket_name']}")
        print(f"Location: {config['location']}")

        for table_name, gcs_path in RAW_FILES.items():
            print(
                f"Would load gs://{config['bucket_name']}/{gcs_path} "
                f"into {config['project_id']}.{config['dataset_id']}.{table_name}"
            )

        for file_name in SQL_FILES:
            rendered_sql = render_sql(read_sql_file(file_name), config)
            print(f"Validated SQL rendering for {file_name}: {len(rendered_sql)} chars")

        print("Dry run finished successfully.")
        return

    client = get_bigquery_client(config)

    for table_name, gcs_path in RAW_FILES.items():
        load_csv_from_gcs(client, config, table_name, gcs_path)

    run_transformations(client, config)
    verify_outputs(client, config)

    print("BigQuery pipeline finished successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run)