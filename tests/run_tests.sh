#!/bin/bash

# Test runner script for Webbly CMS

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=false
REPORT=false
PARALLEL=false
VERBOSE=false
QUIET=false
FAILFAST=false

# Print usage
usage() {
    echo -e "${BLUE}Usage: $0 [options] [test_type]${NC}"
    echo
    echo "Test Types:"
    echo "  all          Run all tests (default)"
    echo "  unit         Run unit tests"
    echo "  integration  Run integration tests"
    echo "  functional   Run functional tests"
    echo "  performance  Run performance tests"
    echo "  security    Run security tests"
    echo
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -c, --coverage   Generate coverage report"
    echo "  -r, --report     Generate HTML test report"
    echo "  -p, --parallel   Run tests in parallel"
    echo "  -v, --verbose    Show verbose output"
    echo "  -q, --quiet      Show minimal output"
    echo "  -f, --failfast   Stop on first failure"
    echo
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -r|--report)
            REPORT=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -f|--failfast)
            FAILFAST=true
            shift
            ;;
        unit|integration|functional|performance|security)
            TEST_TYPE=$1
            shift
            ;;
        all)
            TEST_TYPE="all"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

# Add test type
case $TEST_TYPE in
    "all")
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
    *)
        PYTEST_CMD="$PYTEST_CMD tests/$TEST_TYPE/"
        ;;
esac

# Add options
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=webbly --cov-report=term-missing"
    if [ "$REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
    fi
fi

if [ "$REPORT" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --html=tests/reports/report.html"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$QUIET" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -q"
fi

if [ "$FAILFAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Activate virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Print test configuration
echo -e "${BLUE}=============================="
echo "Webbly CMS Test Runner"
echo -e "==============================${NC}"
echo
echo -e "${YELLOW}Configuration:${NC}"
echo "Test Type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo "Report: $REPORT"
echo "Parallel: $PARALLEL"
echo "Verbose: $VERBOSE"
echo "Quiet: $QUIET"
echo "Failfast: $FAILFAST"
echo
echo -e "${YELLOW}Command:${NC}"
echo "$PYTEST_CMD"
echo

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo
eval $PYTEST_CMD
TEST_RESULT=$?

# Generate reports if enabled
if [ "$COVERAGE" = true ] && [ "$REPORT" = true ]; then
    echo
    echo -e "${YELLOW}Generating coverage report...${NC}"
    coverage html
fi

# Print results
echo
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
else
    echo -e "${RED}Tests failed with exit code $TEST_RESULT${NC}"
fi

# Print report locations if generated
if [ "$REPORT" = true ]; then
    echo
    echo -e "${BLUE}Test report generated: tests/reports/report.html${NC}"
fi

if [ "$COVERAGE" = true ] && [ "$REPORT" = true ]; then
    echo -e "${BLUE}Coverage report generated: tests/reports/coverage/index.html${NC}"
fi

# Deactivate virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    deactivate
fi

exit $TEST_RESULT
