@echo off
REM Change to network drive Z:
cd /d "Z:\!_ Папки сотрудников\Шева\Ебота(\МР ебола\teleopti-wfm-script-main"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the script using Python from virtual environment explicitly
.venv\Scripts\python.exe main.py test08.xlsx --auto-date-processing

pause
