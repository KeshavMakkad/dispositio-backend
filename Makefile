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
.PHONY: help run format clean db_revise db_upgrade db_downgrade db_history
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
