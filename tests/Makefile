# Webbly CMS Test Suite Makefile

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
COVERAGE := coverage
SHELL := /bin/bash

# Detect OS
ifeq ($(OS),Windows_NT)
	VENV_BIN := venv/Scripts
	PYTHON_CMD := python
	PIP_CMD := pip
	INIT_SCRIPT := init_tests.bat
	RUN_SCRIPT := run_tests.bat
else
	VENV_BIN := venv/bin
	PYTHON_CMD := python3
	PIP_CMD := pip3
	INIT_SCRIPT := ./init_tests.sh
	RUN_SCRIPT := ./run_tests.sh
endif

# Directories
TEST_DIR := .
VENV_DIR := $(TEST_DIR)/venv
REPORT_DIR := $(TEST_DIR)/reports
COVERAGE_DIR := $(REPORT_DIR)/coverage

# Make all scripts executable
.PHONY: chmod
chmod:
	@chmod +x $(TEST_DIR)/init_tests.sh
	@chmod +x $(TEST_DIR)/run_tests.sh
	@chmod +x $(TEST_DIR)/init_test_env.py

# Initialize test environment
.PHONY: init
init: chmod
	@$(INIT_SCRIPT)

# Clean test environment
.PHONY: clean
clean:
	@rm -rf $(VENV_DIR)
	@rm -rf $(REPORT_DIR)
	@rm -rf $(TEST_DIR)/__pycache__
	@rm -rf $(TEST_DIR)/.pytest_cache
	@rm -rf $(TEST_DIR)/.coverage
	@rm -rf $(TEST_DIR)/htmlcov
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +

# Run all tests
.PHONY: test
test:
	@$(RUN_SCRIPT)

# Run unit tests
.PHONY: unit
unit:
	@$(RUN_SCRIPT) unit

# Run integration tests
.PHONY: integration
integration:
	@$(RUN_SCRIPT) integration

# Run functional tests
.PHONY: functional
functional:
	@$(RUN_SCRIPT) functional

# Run performance tests
.PHONY: performance
performance:
	@$(RUN_SCRIPT) performance

# Run security tests
.PHONY: security
security:
	@$(RUN_SCRIPT) security

# Run tests with coverage
.PHONY: coverage
coverage:
	@$(RUN_SCRIPT) --coverage

# Run tests with HTML report
.PHONY: report
report:
	@$(RUN_SCRIPT) --report

# Run tests with coverage and HTML report
.PHONY: coverage-report
coverage-report:
	@$(RUN_SCRIPT) --coverage --report

# Run tests in parallel
.PHONY: parallel
parallel:
	@$(RUN_SCRIPT) --parallel

# Run tests verbosely
.PHONY: verbose
verbose:
	@$(RUN_SCRIPT) --verbose

# Run tests quietly
.PHONY: quiet
quiet:
	@$(RUN_SCRIPT) --quiet

# Run tests with fail-fast
.PHONY: failfast
failfast:
	@$(RUN_SCRIPT) --failfast

# Install test dependencies
.PHONY: install
install:
	@$(PIP_CMD) install -r requirements-test.txt

# Update test dependencies
.PHONY: update
update:
	@$(PIP_CMD) install --upgrade -r requirements-test.txt

# Show help
.PHONY: help
help:
	@echo "Webbly CMS Test Suite"
	@echo
	@echo "Usage:"
	@echo "  make [target]"
	@echo
	@echo "Targets:"
	@echo "  init             Initialize test environment"
	@echo "  clean            Clean test environment"
	@echo "  test             Run all tests"
	@echo "  unit             Run unit tests"
	@echo "  integration      Run integration tests"
	@echo "  functional       Run functional tests"
	@echo "  performance      Run performance tests"
	@echo "  security         Run security tests"
	@echo "  coverage         Run tests with coverage"
	@echo "  report           Run tests with HTML report"
	@echo "  coverage-report  Run tests with coverage and HTML report"
	@echo "  parallel         Run tests in parallel"
	@echo "  verbose          Run tests verbosely"
	@echo "  quiet            Run tests quietly"
	@echo "  failfast         Run tests with fail-fast"
	@echo "  install          Install test dependencies"
	@echo "  update           Update test dependencies"
	@echo "  help             Show this help message"

# Default target
.DEFAULT_GOAL := help
