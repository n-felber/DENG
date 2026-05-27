from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cloud_ingestion import upload_kaggle_to_gcs
from bigquery_pipeline import run_pipeline


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="bike_sharing_cloud_pipeline",
    default_args=default_args,
    description="Upload Bike Sharing raw files to GCS, then load and transform them in BigQuery",
    schedule_interval="@daily",
    catchup=False,
    tags=["bike-sharing", "gcs", "bigquery", "cloud"],
) as dag:

    validate_bigquery_pipeline_config = PythonOperator(
        task_id="validate_bigquery_pipeline_config",
        python_callable=run_pipeline,
        op_kwargs={"dry_run": True},
    )

    upload_raw_files_to_gcs = PythonOperator(
        task_id="upload_raw_files_to_gcs",
        python_callable=upload_kaggle_to_gcs,
    )

    run_bigquery_pipeline = PythonOperator(
        task_id="run_bigquery_pipeline",
        python_callable=run_pipeline,
        op_kwargs={"dry_run": False},
    )

    validate_bigquery_pipeline_config >> upload_raw_files_to_gcs >> run_bigquery_pipeline
