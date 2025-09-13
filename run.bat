@echo off
REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Activate virtual environment with full path
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

REM Run Python script with full path
python "%SCRIPT_DIR%main.py" "%SCRIPT_DIR%test08.xlsx" --auto-date-processing

pause
