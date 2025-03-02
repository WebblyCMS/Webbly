@echo off
setlocal EnableDelayedExpansion

:: Set script directory
set "SCRIPT_DIR=%~dp0"

:: Default values
set "TEST_TYPE=all"
set "COVERAGE=false"
set "REPORT=false"
set "PARALLEL=false"
set "VERBOSE=false"
set "QUIET=false"
set "FAILFAST=false"

:: Print usage
:usage
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help
goto :parse_args

:help
echo Usage: %0 [options] [test_type]
echo.
echo Test Types:
echo   all          Run all tests (default)
echo   unit         Run unit tests
echo   integration  Run integration tests
echo   functional   Run functional tests
echo   performance  Run performance tests
echo   security     Run security tests
echo.
echo Options:
echo   -h, --help       Show this help message
echo   -c, --coverage   Generate coverage report
echo   -r, --report     Generate HTML test report
echo   -p, --parallel   Run tests in parallel
echo   -v, --verbose    Show verbose output
echo   -q, --quiet      Show minimal output
echo   -f, --failfast   Stop on first failure
echo.
exit /b 1

:: Parse command line arguments
:parse_args
if "%1"=="" goto :run_tests
if "%1"=="-c" (
    set "COVERAGE=true"
    shift
    goto :parse_args
)
if "%1"=="--coverage" (
    set "COVERAGE=true"
    shift
    goto :parse_args
)
if "%1"=="-r" (
    set "REPORT=true"
    shift
    goto :parse_args
)
if "%1"=="--report" (
    set "REPORT=true"
    shift
    goto :parse_args
)
if "%1"=="-p" (
    set "PARALLEL=true"
    shift
    goto :parse_args
)
if "%1"=="--parallel" (
    set "PARALLEL=true"
    shift
    goto :parse_args
)
if "%1"=="-v" (
    set "VERBOSE=true"
    shift
    goto :parse_args
)
if "%1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto :parse_args
)
if "%1"=="-q" (
    set "QUIET=true"
    shift
    goto :parse_args
)
if "%1"=="--quiet" (
    set "QUIET=true"
    shift
    goto :parse_args
)
if "%1"=="-f" (
    set "FAILFAST=true"
    shift
    goto :parse_args
)
if "%1"=="--failfast" (
    set "FAILFAST=true"
    shift
    goto :parse_args
)
if "%1"=="unit" (
    set "TEST_TYPE=unit"
    shift
    goto :parse_args
)
if "%1"=="integration" (
    set "TEST_TYPE=integration"
    shift
    goto :parse_args
)
if "%1"=="functional" (
    set "TEST_TYPE=functional"
    shift
    goto :parse_args
)
if "%1"=="performance" (
    set "TEST_TYPE=performance"
    shift
    goto :parse_args
)
if "%1"=="security" (
    set "TEST_TYPE=security"
    shift
    goto :parse_args
)
if "%1"=="all" (
    set "TEST_TYPE=all"
    shift
    goto :parse_args
)
echo Unknown option: %1
goto :help

:: Run tests
:run_tests
:: Build pytest command
set "PYTEST_CMD=pytest"

:: Add test type
if "%TEST_TYPE%"=="all" (
    set "PYTEST_CMD=!PYTEST_CMD! tests/"
) else (
    set "PYTEST_CMD=!PYTEST_CMD! tests/%TEST_TYPE%/"
)

:: Add options
if "%COVERAGE%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! --cov=webbly --cov-report=term-missing"
    if "%REPORT%"=="true" (
        set "PYTEST_CMD=!PYTEST_CMD! --cov-report=html"
    )
)

if "%REPORT%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! --html=tests/reports/report.html"
)

if "%PARALLEL%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! -n auto"
)

if "%VERBOSE%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! -v"
)

if "%QUIET%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! -q"
)

if "%FAILFAST%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! -x"
)

:: Activate virtual environment
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
)

:: Print test configuration
echo ==============================
echo Webbly CMS Test Runner
echo ==============================
echo.
echo Configuration:
echo Test Type: %TEST_TYPE%
echo Coverage: %COVERAGE%
echo Report: %REPORT%
echo Parallel: %PARALLEL%
echo Verbose: %VERBOSE%
echo Quiet: %QUIET%
echo Failfast: %FAILFAST%
echo.
echo Command:
echo %PYTEST_CMD%
echo.

:: Run tests
echo Running tests...
echo.
%PYTEST_CMD%
set TEST_RESULT=%ERRORLEVEL%

:: Generate reports if enabled
if "%COVERAGE%"=="true" if "%REPORT%"=="true" (
    echo.
    echo Generating coverage report...
    coverage html
)

:: Print results
echo.
if %TEST_RESULT%==0 (
    echo All tests passed successfully!
) else (
    echo Tests failed with exit code %TEST_RESULT%
)

:: Print report locations if generated
if "%REPORT%"=="true" (
    echo.
    echo Test report generated: tests/reports/report.html
)

if "%COVERAGE%"=="true" if "%REPORT%"=="true" (
    echo Coverage report generated: tests/reports/coverage/index.html
)

:: Deactivate virtual environment
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    deactivate
)

exit /b %TEST_RESULT%
