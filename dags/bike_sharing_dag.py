from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Pfad zum src-Ordner hinzufügen, damit wir main importieren können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import run_batch_ingestion

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bike_sharing_ingestion',
    default_args=default_args,
    description='Run the Kaggle Bike Sharing ingestion pipeline',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    run_pipeline_task = PythonOperator(
        task_id='run_batch_ingestion_task',
        python_callable=run_batch_ingestion,
    )

    run_pipeline_task