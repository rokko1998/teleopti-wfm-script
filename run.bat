@echo off
REM Use pushd to automatically map UNC path to a drive letter
pushd "Z:\!_ Папки сотрудников\Шева\Ебота(\МР ебола\teleopti-wfm-script-main"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the script using Python from virtual environment explicitly
.venv\Scripts\python.exe main.py test08.xlsx --auto-date-processing

REM Return to original directory and unmount drive
popd

pause
