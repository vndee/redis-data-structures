.PHONY: setup test clean build publish install-dev format check lint

# Python and package management settings
PYTHON := python3
UV := uv
PIP := $(UV) pip
PACKAGE_NAME := redis-data-structures

# Test settings
TEST_PATH := tests
COVERAGE_PATH := htmlcov

setup:  ## Install dependencies
	$(UV) venv
	$(PIP) install -e .

setup-dev:  ## Install development dependencies
	$(UV) venv
	$(PIP) install -e ".[dev]"
	$(PIP) install pre-commit
	pre-commit install

test:  ## Run tests
	$(PYTHON) -m unittest discover $(TEST_PATH)

test-coverage:  ## Run tests with coverage report
	$(PIP) install coverage
	coverage run -m unittest discover $(TEST_PATH)
	coverage report
	coverage html
	@echo "HTML coverage report generated in $(COVERAGE_PATH)/"

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(COVERAGE_PATH)/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean  ## Build package
	$(PIP) install build
	$(PYTHON) -m build

publish: build  ## Publish package to PyPI
	$(PIP) install twine
	$(PYTHON) -m twine upload dist/*

publish-test: build  ## Publish package to TestPyPI
	$(PIP) install twine
	$(PYTHON) -m twine upload --repository testpypi dist/*

format:  ## Format code using black and ruff
	$(PIP) install black ruff
	black .
	ruff check --fix .

check:  ## Run code quality checks
	$(PIP) install black ruff mypy
	black --check .
	ruff check .
	mypy .

lint:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

install-dev: setup-dev  ## Install package in development mode
	$(PIP) install -e .

redis-start:  ## Start Redis server using Docker
	docker run --name redis-ds -p 6379:6379 -d redis:latest

redis-stop:  ## Stop Redis server
	docker stop redis-ds
	docker rm redis-ds

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Default target
.DEFAULT_GOAL := help 