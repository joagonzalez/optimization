# Makefile for VM Placement Optimization Tests

# Python interpreter
PYTHON = python3

# Directories
SRC_DIR = src
TEST_RESULTS_DIR = test_results

# Main test runner file
TEST_RUNNER = test_runner.py

# Ruff configuration
RUFF_FLAGS = --fix --exit-non-zero-on-fix

# Default target
.PHONY: all
all: setup test

# Create necessary directories
.PHONY: setup
setup:
	@mkdir -p $(TEST_RESULTS_DIR)

# Run tests with visualization
.PHONY: run
run: setup
	@echo "Running tests with visualization..."
	$(PYTHON) $(TEST_RUNNER)

# Run tests without visualization
.PHONY: run-no-viz
run-no-viz: setup
	@echo "Running tests without visualization..."
	$(PYTHON) $(TEST_RUNNER) --no-viz

# Test targets
.PHONY: test-pytest
test:
	pytest src/tests/ -v

.PHONY: test-coverage
test-coverage:
	pytest src/tests/ --cov=src --cov-report=html -v

.PHONY: test-integration
test-integration:
	pytest src/tests/ -v -m "integration"

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
	find . -type d -name "htmlcov" -exec rm -r {} +

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
	ruff format $(SRC_DIR) $(TEST_RUNNER)
	ruff check $(SRC_DIR) $(TEST_RUNNER) $(RUFF_FLAGS)

# Check code with ruff (no fixes)
.PHONY: lint
lint:
	ruff check $(SRC_DIR) $(TEST_RUNNER)

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all                  - Setup and run tests with visualization (default)"
	@echo "  run                - Run tests with visualization"
	@echo "  run-no-viz         - Run tests without visualization"
	@echo "  test                - Run tests using pytest"
	@echo "  test-coverage       - Run tests and generate coverage report"
	@echo "  test-integration    - Run integration tests"
	@echo "  clean               - Clean test results"
	@echo "  clean-all           - Clean all generated files and cache"
	@echo "  install             - Install dependencies"
	@echo "  coverage            - Run tests and generate coverage report"
	@echo "  format              - Format and lint code using ruff"
	@echo "  lint                - Check code using ruff (no fixes)"
	@echo "  help                - Show this help message"
