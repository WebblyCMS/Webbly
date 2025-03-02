@echo off
setlocal

:: Set script directory
set "SCRIPT_DIR=%~dp0"

:: Print banner
echo.
echo ==============================
echo Webbly CMS Test Initialization
echo ==============================
echo.

:: Check Python installation
echo Checking Python installation...
where python >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)
echo Python is installed.

:: Check pip installation
echo.
echo Checking pip installation...
where pip >nul 2>&1
if errorlevel 1 (
    echo pip is not installed. Please install pip and try again.
    exit /b 1
)
echo pip is installed.

:: Create virtual environment if it doesn't exist
echo.
echo Setting up virtual environment...
if not exist "%SCRIPT_DIR%venv" (
    python -m venv "%SCRIPT_DIR%venv"
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
echo Virtual environment activated.

:: Install/upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install test dependencies
echo.
echo Installing test dependencies...
pip install -r "%SCRIPT_DIR%requirements-test.txt"
echo Dependencies installed.

:: Run initialization script
echo.
echo Running test environment initialization...
python "%SCRIPT_DIR%init_test_env.py"

:: Create .env.test if it doesn't exist
if not exist "%SCRIPT_DIR%.env.test" (
    echo.
    echo Creating .env.test file...
    copy "%SCRIPT_DIR%.env.test.example" "%SCRIPT_DIR%.env.test" >nul 2>&1 || type nul > "%SCRIPT_DIR%.env.test"
    echo .env.test file created.
)

:: Set up pre-commit hooks if git is available
where git >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Setting up pre-commit hooks...
    
    :: Create pre-commit hook directory if it doesn't exist
    if not exist ".git\hooks" mkdir ".git\hooks"
    
    :: Create pre-commit hook
    (
        echo @echo off
        echo.
        echo :: Run tests before commit
        echo echo Running tests before commit...
        echo call tests\venv\Scripts\activate.bat
        echo pytest tests/unit/
        echo.
        echo :: Check test result
        echo if errorlevel 1 (
        echo     echo Tests failed. Please fix the tests before committing.
        echo     exit /b 1
        echo ^)
    ) > ".git\hooks\pre-commit.bat"
    
    echo Pre-commit hooks set up.
)

:: Final message
echo.
echo ==============================
echo Test environment setup complete!
echo ==============================
echo.
echo Next steps:
echo 1. Configure test settings in .env.test
echo 2. Run tests with: pytest
echo 3. View test reports in tests/reports/
echo.
echo Happy testing! 🚀
echo.

:: Deactivate virtual environment
deactivate

endlocal
