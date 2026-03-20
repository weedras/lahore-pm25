@echo off
:: ============================================================
::  Lahore PM2.5 - One-Time Setup Script (Windows)
::  Run this ONCE to install everything
:: ============================================================

echo.
echo ============================================================
echo  Lahore PM2.5 Setup - Installing dependencies
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python 3.10+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install dependencies
echo Installing packages (this takes 2-5 minutes)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Package installation failed.
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

:: Create required directories
echo Creating project directories...
if not exist data\raw      mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist data\live     mkdir data\live
if not exist data\forecast mkdir data\forecast
if not exist models        mkdir models
if not exist logs          mkdir logs

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env template...
    echo NASA_FIRMS_KEY=your_key_here > .env
    echo IQAIR_API_KEY=your_key_here >> .env
    echo OPENAQ_KEY=optional >> .env
)

:: Run initial demo pipeline
echo.
echo Running initial demo pipeline to verify everything works...
python scripts\07_iqair_live.py --use-screenshot
if errorlevel 1 (
    echo WARNING: Demo run failed - check the error above.
) else (
    echo Demo pipeline succeeded!
)

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Edit .env and add your API keys (see API_KEYS_SETUP.md)
echo  2. Run the dashboard:  streamlit run app.py
echo  3. Schedule daily runs: see SETUP_GUIDE.md Step 4
echo ============================================================
echo.
pause
