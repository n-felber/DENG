output "gcs_bucket_url" {
  value       = google_storage_bucket.data_lake.url
  description = "Die URL des erstellten GCS Buckets"
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.dataset.dataset_id
  description = "Die ID des erstellten BigQuery Datasets"
}