import logging
import os
import kagglehub
from google.cloud import storage

# Logging einrichten, damit wir im Airflow genau sehen, was passiert
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_HANDLE = "lakshmi25npathi/bike-sharing-dataset"
SOURCE_FILES = ["hour.csv", "day.csv"]

def upload_kaggle_to_gcs() -> None:
    # Holt den Bucket-Namen aus den Umgebungsvariablen der .env
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    
    if not bucket_name:
        raise RuntimeError("GCS_BUCKET_NAME ist nicht in den Umgebungsvariablen gesetzt!")

    logger.info("--- Starte Cloud Ingestion zu GCS ---")
    
    # Initialisiert den Google Cloud Storage Client
    # Der Client findet den Service-Account-Key automatisch über die GOOGLE_APPLICATION_CREDENTIALS Variable
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for file_name in SOURCE_FILES:
        logger.info(f"Lade '{file_name}' von Kaggle via kagglehub herunter...")
        
        # Nutzt das bewährte kagglehub (wie im lokalen Skript)
        downloaded_path = kagglehub.dataset_download(DATASET_HANDLE, file_name)
        
        # Falls kagglehub den Ordnerpfad zurückgibt, hängen wir den Dateinamen an
        if os.path.isdir(downloaded_path):
            file_path = os.path.join(downloaded_path, file_name)
        else:
            file_path = downloaded_path

        # Zielpfad im GCS definieren (exakt gemäss Vertrag mit deinem Kumpel!)
        gcs_blob_path = f"raw/bike_sharing/{file_name}"
        blob = bucket.blob(gcs_blob_path)

        logger.info(f"Uploade '{file_name}' zu GCS Bucket '{bucket_name}' unter '{gcs_blob_path}'...")
        blob.upload_from_filename(file_path)
        logger.info(f"Erfolgreich hochgeladen: gs://{bucket_name}/{gcs_blob_path}")

    logger.info("--- Cloud Ingestion erfolgreich beendet ---")

if __name__ == "__main__":
    upload_kaggle_to_gcs()