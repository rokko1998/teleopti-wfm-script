@echo off
setlocal

REM (опц.) нормальная кодировка
REM chcp 65001 >nul

REM 1) Перейти в папку .bat; pushd сам смонтирует UNC на временную букву
pushd "%~dp0" || (echo [ERROR] pushd "%~dp0" failed & pause & exit /b 1)

REM 2) Проверки
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] venv not found: .venv\Scripts\python.exe
  echo Create it: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  popd & pause & exit /b 2
)
if not exist "main.py" (echo [ERROR] main.py missing & popd & pause & exit /b 3)

set "INPUT_FILE=%~1"
if "%INPUT_FILE%"=="" set "INPUT_FILE=test08.xlsx"
if not exist "%INPUT_FILE%" (echo [ERROR] input "%INPUT_FILE%" missing & popd & pause & exit /b 4)

REM 3) Диагностика: какой python; есть ли tqdm
echo [INFO] Checking venv and tqdm...
".venv\Scripts\python.exe" -c "import sys, pkgutil; print('PY=', sys.executable); print('HAS_TQDM=', any(m.name=='tqdm' for m in pkgutil.iter_modules()))"
if errorlevel 1 (
  echo [ERROR] venv python failed to run
  popd & pause & exit /b 5
)

FOR /F "tokens=2 delims== " %%A IN ('".venv\Scripts\python.exe" -c "import pkgutil; print('HAS_TQDM=', any(m.name=='tqdm' for m in pkgutil.iter_modules()))"') DO set HAS_TQDM=%%A

if /I not "%HAS_TQDM%"=="True" (
  echo [INFO] Installing tqdm into venv...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install tqdm
  if errorlevel 1 (
    echo [ERROR] Failed to install tqdm (check proxy/permissions)
    popd & pause & exit /b 6
  )
)

REM 4) (опц.) activate — не обязателен, но оставим
call ".venv\Scripts\activate.bat" 1>nul 2>nul

REM 5) Запуск строго интерпретатором из venv
echo [INFO] Running: .venv\Scripts\python.exe "main.py" "%INPUT_FILE%" %*
".venv\Scripts\python.exe" "main.py" "%INPUT_FILE%" %*
set "EC=%ERRORLEVEL%"

popd
if not "%EC%"=="0" (echo [ERROR] Python exited %EC%) else (echo [OK] Done)
pause
exit /b %EC%