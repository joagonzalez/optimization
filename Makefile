# Makefile for VM Placement Optimization Tests

# Python interpreter
PYTHON = python3

# Directories
WITHOUT_HOSTS_DIR = without_hosts
WITH_HOSTS_DIR = with_hosts
TEST_RESULTS_DIR = test_results

# Main test runner files
WITHOUT_HOSTS_TEST = $(WITHOUT_HOSTS_DIR)/test_runner.py
WITH_HOSTS_TEST = $(WITH_HOSTS_DIR)/test_runner.py

# Ruff configuration
RUFF_FLAGS = --fix --exit-non-zero-on-fix

# Default target
.PHONY: all
all: setup test-without-hosts

# Create necessary directories
.PHONY: setup
setup:
	@mkdir -p $(TEST_RESULTS_DIR)

# Run tests without hosts
.PHONY: test-without-hosts
test-without-hosts: setup
	@echo "Running tests without hosts..."
	$(PYTHON) $(WITHOUT_HOSTS_TEST)

# Run tests without hosts (no visualization)
.PHONY: test-without-hosts-no-viz
test-without-hosts-no-viz: setup
	@echo "Running tests without hosts (no visualization)..."
	$(PYTHON) $(WITHOUT_HOSTS_TEST) --no-viz

# Run tests with hosts (when implemented)
.PHONY: test-with-hosts
test-with-hosts: setup
	@echo "Running tests with hosts..."
	$(PYTHON) $(WITH_HOSTS_TEST)

# Run all tests
.PHONY: test-all
test-all: test-without-hosts test-with-hosts

# Clean test results
.PHONY: clean
clean:
	@echo "Cleaning test results..."
	rm -rf $(TEST_RESULTS_DIR)/*

# Clean all generated files and cache
.PHONY: clean-all
clean-all: clean
	@echo "Cleaning all generated files..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +

# Install dependencies
.PHONY: install
install:
	pip install -r requirements.txt

# Run tests and generate coverage report
.PHONY: coverage
coverage:
	coverage run -m pytest
	coverage report
	coverage html

# Format and lint code with ruff
.PHONY: format
format:
	ruff format $(WITHOUT_HOSTS_DIR) $(WITH_HOSTS_DIR)
	ruff check $(WITHOUT_HOSTS_DIR) $(WITH_HOSTS_DIR) $(RUFF_FLAGS)

# Check code with ruff (no fixes)
.PHONY: lint
lint:
	ruff check $(WITHOUT_HOSTS_DIR) $(WITH_HOSTS_DIR)

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all                    - Setup and run tests without hosts (default)"
	@echo "  test-without-hosts     - Run tests without hosts"
	@echo "  test-without-hosts-no-viz - Run tests without hosts (no visualization)"
	@echo "  test-with-hosts        - Run tests with hosts"
	@echo "  test-all              - Run all tests"
	@echo "  clean                 - Clean test results"
	@echo "  clean-all             - Clean all generated files and cache"
	@echo "  install               - Install dependencies"
	@echo "  coverage              - Run tests and generate coverage report"
	@echo "  format                - Format and lint code using ruff"
	@echo "  lint                  - Check code using ruff (no fixes)"
	@echo "  help                  - Show this help message"
