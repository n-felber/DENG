# 1. Google Cloud Storage Bucket (Data Lake)
resource "google_storage_bucket" "data_lake" {
  name                        = var.gcs_bucket_name
  location                    = var.gcp_region
  storage_class               = "STANDARD"
  force_destroy               = true # Erlaubt das Löschen des Buckets, auch wenn Daten drin sind (wichtig für Testzwecke)
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30 # Löscht Testdaten nach 30 Tagen automatisch, um Kosten zu sparen
    }
    action {
      type = "Delete"
    }
  }
}

# 2. BigQuery Dataset (Data Warehouse)
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.bq_dataset_name
  location                   = var.gcp_region
  delete_contents_on_destroy = true # Löscht alle Tabellen mit, wenn die Infrastruktur abgerissen wird
}