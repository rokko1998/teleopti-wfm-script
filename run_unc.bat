@echo off
title WFM Traffic Script - UNC Path Support

REM This batch file handles UNC paths by copying files to local temp folder
echo ========================================
echo  WFM Traffic Script - UNC Path Support
echo ========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Create local working directory
set "LOCAL_DIR=%TEMP%\teleopti-wfm-script-%RANDOM%"
echo [INFO] Creating local working directory: %LOCAL_DIR%
mkdir "%LOCAL_DIR%" 2>nul

REM Copy all files to local directory
echo [INFO] Copying files from network location...
xcopy /Y /Q /E "%SCRIPT_DIR%*" "%LOCAL_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy files to local directory
    pause
    exit /b 1
)

REM Change to local directory
cd /d "%LOCAL_DIR%"
echo [INFO] Working in local directory: %LOCAL_DIR%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install Python 3.8+ from: https://python.org
    echo Make sure Python is added to PATH
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Create virtual environment if needed
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo [INFO] Dependencies installed
echo.

REM Check for input file
if not exist "test08.xlsx" (
    echo [WARNING] File test08.xlsx not found
    echo Make sure to copy test08.xlsx to the script folder
    echo.
)

REM Run the script
echo [INFO] Starting script...
echo Command: python main.py test08.xlsx --auto-date-processing
echo ========================================
echo.

python main.py test08.xlsx --auto-date-processing

echo.
echo ========================================
if errorlevel 1 (
    echo [ERROR] Script finished with error!
) else (
    echo [SUCCESS] Script completed successfully!
)

REM Copy results back to network location if needed
echo [INFO] Results are saved in: %LOCAL_DIR%
echo [INFO] You can copy results back to network location if needed

echo.
echo Press any key to exit...
pause >nul

REM Cleanup (optional - uncomment to auto-delete temp folder)
REM rmdir /s /q "%LOCAL_DIR%"
