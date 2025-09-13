@echo off
chcp 65001 >nul
title WFM Traffic Script

REM Check UNC path and copy to local folder
if "%CD:~0,2%"=="\\" (
    echo [INFO] UNC path detected, copying files to local folder...
    set "LOCAL_DIR=%TEMP%\teleopti-wfm-script"
    if not exist "%LOCAL_DIR%" mkdir "%LOCAL_DIR%"
    echo [INFO] Copying files to: %LOCAL_DIR%
    xcopy /Y /Q "%~dp0*" "%LOCAL_DIR%\" >nul
    cd /d "%LOCAL_DIR%"
    echo [INFO] Switched to local folder: %LOCAL_DIR%
)

echo ========================================
echo  WFM Traffic Script - Запуск скрипта
echo ========================================
echo.
echo [DEBUG] Current folder: %CD%
echo [DEBUG] Checking Python...

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install Python 3.8+ from: https://python.org
    echo Make sure Python is added to PATH
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo [DEBUG] Python found:
python --version

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found, creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo Press any key to exit...
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    echo Press any key to exit...
    pause
    exit /b 1
)

echo [INFO] Virtual environment activated
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    echo Check requirements.txt file
    echo Press any key to exit...
    pause
    exit /b 1
)
echo [INFO] Dependencies installed
echo.

REM Check for test08.xlsx file
if not exist "test08.xlsx" (
    echo [WARNING] File test08.xlsx not found in current folder
    echo Make sure the file is in the script folder
    echo.
)

REM Run script with parameters
echo [INFO] Starting script with parameters...
echo Command: python main.py test08.xlsx --auto-date-processing
echo.
echo [DEBUG] Starting Python script execution...
echo [DEBUG] Console will show progress
echo ========================================
echo.

python main.py test08.xlsx --auto-date-processing

if errorlevel 1 (
    echo.
    echo [ERROR] Script finished with error!
    echo Check logs above for detailed information.
) else (
    echo.
    echo [SUCCESS] Script completed successfully!
)

echo.
echo Press any key to exit...
pause >nul
