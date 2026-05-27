SHELL := /bin/bash

COMPOSE := docker compose
TF := terraform -chdir=terraform

LOCAL_DAG := bike_sharing_ingestion
CLOUD_DAG := bike_sharing_cloud_pipeline

.PHONY: help up down ps logs restart \
	trigger-local trigger-cloud test-cloud-config verify-local \
	terraform-init terraform-plan terraform-apply terraform-destroy \
	cleanup cleanup-local cleanup-python cleanup-terraform-local cleanup-all cleanup-secrets

help: ## Show available commands
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start Docker Compose services
	$(COMPOSE) up -d

down: ## Stop Docker Compose services without deleting volumes
	$(COMPOSE) down --remove-orphans

ps: ## Show Docker Compose service status
	$(COMPOSE) ps

logs: ## Follow Docker Compose logs
	$(COMPOSE) logs -f

restart: down up ## Restart Docker Compose services

trigger-local: ## Trigger the local PostgreSQL Airflow DAG
	$(COMPOSE) exec airflow-webserver airflow dags trigger $(LOCAL_DAG)

trigger-cloud: ## Trigger the cloud GCS + BigQuery Airflow DAG
	$(COMPOSE) exec airflow-webserver airflow dags trigger $(CLOUD_DAG)

test-cloud-config: ## Validate cloud pipeline configuration without loading data
	$(COMPOSE) run --rm airflow-webserver bash -lc \
		'pip install --no-cache-dir -r /opt/airflow/requirements.txt >/dev/null && \
		 python /opt/airflow/src/bigquery_pipeline.py --dry-run'

verify-local: ## List local PostgreSQL project tables
	$(COMPOSE) exec postgres psql -U deng -d deng -c "\dt public.bike_*"

terraform-init: ## Initialize Terraform
	$(TF) init

terraform-plan: ## Show Terraform execution plan
	$(TF) plan

terraform-apply: ## Apply Terraform infrastructure
	$(TF) apply

terraform-destroy: ## Destroy Terraform-managed cloud infrastructure
	$(TF) destroy

cleanup: cleanup-local cleanup-python cleanup-terraform-local ## Clean local runtime and generated files

cleanup-local: ## Stop containers and remove project Docker volumes
	$(COMPOSE) down --volumes --remove-orphans

cleanup-python: ## Remove Python cache and test/cache artifacts
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

cleanup-terraform-local: ## Remove local Terraform runtime/state files
	rm -rf terraform/.terraform
	rm -f terraform/*.tfstate terraform/*.tfstate.*
	rm -f terraform/crash.log terraform/crash.*.log

cleanup-all: terraform-destroy cleanup ## Destroy cloud infrastructure and clean local generated files

cleanup-secrets: ## Remove local secrets; only run before handing in/public sharing
	rm -f .env
	rm -f terraform/terraform.tfvars
	rm -f gcp/*.json