@echo off
REM Change to the directory where this batch file is located
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py test08.xlsx --auto-date-processing
pause
