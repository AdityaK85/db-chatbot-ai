@echo off
echo Starting Data Chatbot Agent...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies if requirements file exists
if exist "requirements_local.txt" (
    echo Installing dependencies...
    pip install -r requirements_local.txt
)

REM Set API key (replace with your actual key if needed)
set OPENROUTER_API_KEY=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

REM Start the application
echo.
echo Starting Data Chatbot Agent...
echo Your app will open in the browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo.
streamlit run app.py

pause