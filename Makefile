# -------------------------------------------------
# Shell & environment
# -------------------------------------------------
SHELL := /bin/bash
-include .env


# -------------------------------------------------
# Project variables
# -------------------------------------------------
WORKDIR := src
PYTHON := python


# -------------------------------------------------
# Phony targets
# -------------------------------------------------
.PHONY: help run format clean db_revise db_upgrade db_downgrade db_history \
	install-dev lint test security ci cluster tls secrets monitoring deploy smoke up rollback grafana cluster-down
.SILENT: clean


# -------------------------------------------------
# Help (self-documenting)
# -------------------------------------------------
help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sed 's/##//'


# -------------------------------------------------
# Run application
# -------------------------------------------------
run:  ## Run FastAPI app locally with reload
	PYTHONPATH=$(WORKDIR) $(PYTHON) -m uvicorn main:app --reload


# -------------------------------------------------
# Formatting
# -------------------------------------------------
format:  ## Format code with Black
	black $(WORKDIR)


# -------------------------------------------------
# Cleanup
# -------------------------------------------------
clean:  ## Remove Python cache files
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -delete
	find . -name '.pytest_cache' -exec rm -rf {} +


# -------------------------------------------------
# Database – Alembic
# -------------------------------------------------
db_revise:  ## Create migration (make db_revise m="message")
	PYTHONPATH=$(WORKDIR) alembic -c $(WORKDIR)/alembic/alembic.ini revision --autogenerate -m "$(m)"

db_upgrade:  ## Apply migrations
	PYTHONPATH=$(WORKDIR) alembic -c $(WORKDIR)/alembic/alembic.ini upgrade head

db_downgrade:  ## Roll back one migration
	PYTHONPATH=$(WORKDIR) alembic -c $(WORKDIR)/alembic/alembic.ini downgrade -1

db_history:  ## Show migration history
	PYTHONPATH=$(WORKDIR) alembic -c $(WORKDIR)/alembic/alembic.ini history


install-dev:
	pip install -r requirements-dev.txt

lint:
	ruff check --select E9,F63,F7,F82 --exclude src/alembic/versions src tests

test:
	pytest -q tests/test_classroom_api_contract.py

security:
	bandit -r src -ll -s B104 -x src/alembic
	pip-audit -r requirements.txt --strict

ci: lint test security

cluster:
	scripts/create-cluster.sh

tls:
	scripts/generate-tls-secret.sh

secrets:
	scripts/create-secrets.sh

monitoring:
	scripts/install-monitoring.sh

deploy:
	VALUES=$(or $(VALUES),values-development.yaml) scripts/deploy.sh

smoke:
	scripts/smoke-test.sh

up: cluster tls secrets monitoring deploy smoke

rollback:
	helm --kube-context k3d-dispositio rollback dispositio -n dispositio --wait

grafana:
	@echo "password: $$(kubectl --context k3d-dispositio -n monitoring get secret kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}' | base64 -d)"
	kubectl --context k3d-dispositio -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80

cluster-down:
	scripts/delete-cluster.sh
