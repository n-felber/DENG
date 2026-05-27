# Cleanup

This document explains how to remove everything created by this project.

There are three cleanup levels:

1. Local runtime cleanup
2. Full cleanup including cloud infrastructure
3. Optional local secrets cleanup

Take screenshots/evidence before running the full cleanup, because the cloud data lake and BigQuery tables will be deleted.

---

## Recommended cleanup commands

### Local cleanup

Use this when you want to stop the local environment and remove generated local files:

```bash
make cleanup
```

This removes:

* Docker Compose containers
* Docker Compose project volumes
* Docker Compose project network
* local PostgreSQL data
* Airflow metadata stored in PostgreSQL
* Python cache files such as `__pycache__` and `*.pyc`
* local Terraform runtime files such as `terraform/.terraform`
* local Terraform state files such as `terraform/*.tfstate`

It does **not** delete:

* source code
* documentation
* SQL files
* `.env`
* `gcp/service-account.json`
* Terraform-managed cloud resources

---

### Full cleanup

Use this when the project is finished and the cloud resources should also be deleted:

```bash
make cleanup-all
```

This first runs:

```bash
terraform -chdir=terraform destroy
```

Then it runs the local cleanup.

This removes Terraform-managed cloud resources, including:

* Google Cloud Storage data lake bucket
* files uploaded to the bucket
* BigQuery dataset
* BigQuery tables

The Terraform configuration uses destructive cleanup settings for project teardown:

* the GCS bucket can be destroyed even when it contains files
* the BigQuery dataset can be destroyed together with its tables

---

### Optional secrets cleanup

Use this only when you want to remove local credentials and environment files from your machine:

```bash
make cleanup-secrets
```

This removes:

* `.env`
* `terraform/terraform.tfvars`
* `gcp/*.json`

Do not run this if you still need the local credentials for testing.

---

## Manual cleanup commands

If `make` is not available, run the commands manually.

### Stop and remove local Docker resources

```bash
docker compose down --volumes --remove-orphans
```

### Remove Python cache files

```bash
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
```

### Remove local Terraform runtime files

```bash
rm -rf terraform/.terraform
rm -f terraform/*.tfstate terraform/*.tfstate.*
rm -f terraform/crash.log terraform/crash.*.log
```

### Destroy cloud infrastructure

```bash
terraform -chdir=terraform destroy
```

---

## Verify cleanup

### Check Docker

```bash
docker compose ps
```

Expected result:

* no project services are running

### Check Python cache files

```bash
find . -type d -name "__pycache__"
find . -type f -name "*.pyc"
```

Expected result:

* no output

### Check Terraform local files

```bash
ls terraform/.terraform
ls terraform/*.tfstate
```

Expected result:

* files do not exist

### Check Git status

```bash
git status --short
```

Expected result:

* only intentional documentation or source-code changes are shown
* no generated cache files are shown
* no secrets are shown
