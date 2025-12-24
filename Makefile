.PHONY: help install install-dev clean lint format type-check test test-cov run build clean-pyc clean-build clean-test docs

.DEFAULT_GOAL := help

# Variables
PYTHON := python3
UV := uv
PACKAGE_NAME := autodebugger
SRC_DIR := autodebugger
TEST_DIR := tests

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)'
	@echo '$(GREEN)  Auto Error Debugger Assistant - Makefile Commands$(NC)'
	@echo '$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ''
	@echo '$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)'

install: ## Install production dependencies using uv
	@echo "$(GREEN)Installing production dependencies with uv...$(NC)"
	$(UV) pip install -e .
	@echo "$(GREEN)✓ Installation complete!$(NC)"

install-dev: ## Install all dependencies including dev tools using uv
	@echo "$(GREEN)Installing all dependencies (production + dev) with uv...$(NC)"
	$(UV) pip install -e ".[dev]"
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

sync: ## Synchronize dependencies using uv sync
	@echo "$(GREEN)Synchronizing dependencies with uv...$(NC)"
	$(UV) pip sync
	@echo "$(GREEN)✓ Dependencies synchronized!$(NC)"

clean: clean-pyc clean-build clean-test ## Remove all build, test, coverage and Python artifacts
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

clean-pyc: ## Remove Python file artifacts
	@echo "$(YELLOW)Removing Python artifacts...$(NC)"
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type f -name '*.egg' -delete

clean-build: ## Remove build artifacts
	@echo "$(YELLOW)Removing build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -rf *.egg-info

clean-test: ## Remove test and coverage artifacts
	@echo "$(YELLOW)Removing test artifacts...$(NC)"
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

lint: ## Check code style with ruff
	@echo "$(YELLOW)Running linter (ruff)...$(NC)"
	ruff check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting complete!$(NC)"

lint-fix: ## Fix code style issues automatically with ruff
	@echo "$(YELLOW)Fixing linting issues with ruff...$(NC)"
	ruff check --fix $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting fixes applied!$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code with black...$(NC)"
	black $(SRC_DIR) $(TEST_DIR)
	@echo "$(YELLOW)Sorting imports with isort...$(NC)"
	isort $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Code formatting complete!$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(YELLOW)Checking code formatting...$(NC)"
	black --check $(SRC_DIR) $(TEST_DIR)
	isort --check-only $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Format check complete!$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checker (mypy)...$(NC)"
	mypy $(SRC_DIR)
	@echo "$(GREEN)✓ Type checking complete!$(NC)"

test: ## Run tests with pytest
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest $(TEST_DIR) -v
	@echo "$(GREEN)✓ Tests complete!$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	pytest $(TEST_DIR) -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(YELLOW)Running fast tests...$(NC)"
	pytest $(TEST_DIR) -v -x --no-cov
	@echo "$(GREEN)✓ Fast tests complete!$(NC)"

run: ## Run the Streamlit application
	@echo "$(GREEN)Starting Streamlit application...$(NC)"
	streamlit run autodebugger/app.py

dev: ## Run the application with auto-reload for development
	@echo "$(GREEN)Starting application in development mode...$(NC)"
	STREAMLIT_SERVER_WATCH_FOR_RELOAD=true streamlit run autodebugger/app.py

build: clean ## Build distribution packages
	@echo "$(YELLOW)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build complete! Check dist/ directory$(NC)"

check: lint type-check test ## Run all checks (lint, type-check, tests)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

pre-commit: format lint type-check test ## Run pre-commit checks locally
	@echo "$(GREEN)✓ Pre-commit checks complete!$(NC)"

upgrade-deps: ## Upgrade all dependencies to latest versions
	@echo "$(YELLOW)Upgrading dependencies...$(NC)"
	$(UV) pip install --upgrade -e ".[dev]"
	@echo "$(GREEN)✓ Dependencies upgraded!$(NC)"

show-deps: ## Show installed dependencies
	@echo "$(YELLOW)Installed dependencies:$(NC)"
	$(UV) pip list

init: ## Initialize new development environment
	@echo "$(GREEN)Initializing development environment...$(NC)"
	@command -v $(UV) >/dev/null 2>&1 || { echo "$(RED)Error: uv is not installed. Install from: https://github.com/astral-sh/uv$(NC)"; exit 1; }
	make install-dev
	@echo "$(GREEN)✓ Development environment initialized!$(NC)"

.PHONY: version
version: ## Show package version
	@echo "$(PACKAGE_NAME) version: $$($(PYTHON) -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
