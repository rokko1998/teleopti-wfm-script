@echo off
call .venv\Scripts\activate.bat
python main.py test08.xlsx --auto-date-processing
pause
