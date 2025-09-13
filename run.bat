@echo off
REM Use pushd to automatically map UNC path to a drive letter
pushd "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the script using Python from virtual environment explicitly
.venv\Scripts\python.exe main.py test08.xlsx --auto-date-processing

REM Return to original directory and unmount drive
popd

pause
