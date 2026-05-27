from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Wir fügen den src-Ordner des Containers zum Python-Pfad hinzu,
# damit Airflow dein neues Skript finden und importieren kann.
sys.path.insert(0, '/opt/airflow/src')
from cloud_ingestion import upload_kaggle_to_gcs

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1), # Auf das aktuelle Jahr 2026 angepasst
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bike_sharing_cloud_pipeline',
    default_args=default_args,
    description='CLOUD PATH (Person 1): Ingest Kaggle data into Google Cloud Storage',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Startet deine Python-Funktion für den GCS Upload
    gcs_ingestion_task = PythonOperator(
        task_id='upload_kaggle_to_gcs_task',
        python_callable=upload_kaggle_to_gcs,
    )

    # Hier kann Person 2 später einfach mit "gcs_ingestion_task >> ..." ihre BigQuery-Tasks anhängen!
    gcs_ingestion_task