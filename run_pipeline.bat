@echo off
:: ============================================================
::  Lahore PM2.5 - Daily Pipeline Runner
::  Run manually or via Windows Task Scheduler
:: ============================================================

:: Change this path to wherever you cloned the project
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: Timestamp
echo.
echo ============================================================
echo  Lahore PM2.5 Pipeline - %date% %time%
echo ============================================================
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment.
    echo Make sure you have run setup.bat first.
    pause
    exit /b 1
)

:: Create log directory
if not exist logs mkdir logs
set LOGFILE=logs\run_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log

:: Run pipeline steps
echo [1/4] Fetching live IQAir data...
python scripts\07_iqair_live.py --use-screenshot >> "%LOGFILE%" 2>&1
if errorlevel 1 echo WARNING: Step 1 had errors - check %LOGFILE%

echo [2/4] Running source decomposition...
python scripts\03_pmf_proxy.py >> "%LOGFILE%" 2>&1
if errorlevel 1 echo WARNING: Step 2 had errors - check %LOGFILE%

echo [3/4] Training model...
python scripts\04_train_model.py >> "%LOGFILE%" 2>&1
if errorlevel 1 echo WARNING: Step 3 had errors - check %LOGFILE%

echo [4/4] Generating 7-day forecast...
python scripts\06_forecast.py >> "%LOGFILE%" 2>&1
if errorlevel 1 echo WARNING: Step 4 had errors - check %LOGFILE%

echo.
echo Done! Log saved to %LOGFILE%
echo The Streamlit dashboard will auto-refresh with new data.
echo.
