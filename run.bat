@echo off
setlocal

REM 1) Перейти в папку с батником; pushd сам смонтирует UNC на временную букву
pushd "%~dp0" || (echo [ERROR] pushd "%~dp0" failed & pause & exit /b 1)

REM 2) Укажем интерпретатор из venv одной переменной
set "PY=.venv\Scripts\python.exe"

REM 3) Простейшие проверки наличия
if not exist "%PY%" (
  echo [ERROR] venv not found: "%PY%"
  echo Create it: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  popd & pause & exit /b 2
)
if not exist "main.py" (
  echo [ERROR] main.py missing
  popd & pause & exit /b 3
)

REM 4) Входной файл: аргумент или test08.xlsx по умолчанию
set "INPUT_FILE=%~1"
if "%INPUT_FILE%"=="" set "INPUT_FILE=test08.xlsx"
if not exist "%INPUT_FILE%" (
  echo [ERROR] Input not found: "%INPUT_FILE%"
  popd & pause & exit /b 4
)

REM 5) (Опционально) быстрая проверка наличия tqdm единым кодом возврата
"%PY%" -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('tqdm') else 1)"
if errorlevel 1 (
  echo [INFO] Installing deps into venv...
  "%PY%" -m pip install --upgrade pip
  "%PY%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Failed to install deps (proxy/rights?). Try:
    echo     %PY% -m pip install tqdm
    popd & pause & exit /b 5
  )
)

REM 6) Запуск строго через venv-питон
echo [INFO] Running: "%PY%" "main.py" "%INPUT_FILE%" %*
"%PY%" "main.py" "%INPUT_FILE%" %*
set "EC=%ERRORLEVEL%"

popd
if not "%EC%"=="0" (echo [ERROR] Python exited %EC%) else (echo [OK] Done)
pause
exit /b %EC%