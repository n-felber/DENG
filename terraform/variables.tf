variable "gcp_project_id" {
  description = "Die ID deines GCP Projekts"
  type        = string
  default     = "deng-team2-bike-sharing"
}

variable "gcp_region" {
  description = "Die Region für die Ressourcen"
  type        = string
  default     = "europe-west6" # Zürich 🇨🇭
}

variable "gcp_zone" {
  description = "Die genaue Zone innerhalb der Region"
  type        = string
  default     = "europe-west6-a"
}

variable "gcs_bucket_name" {
  description = "Name des GCS Speicher-Buckets"
  type        = string
  default     = "deng-team2-bike-sharing-data-lake"
}

variable "bq_dataset_name" {
  description = "Name des BigQuery Datasets"
  type        = string
  default     = "bike_sharing"
}