@echo off
setlocal

REM --- 0) (опц.) русская/UTF-8 кодировка вывода ---
REM chcp 65001 >nul

REM --- 1) Перейти в папку .bat (pushd сам смонтирует UNC на временную букву) ---
pushd "%~dp0" || (
  echo [ERROR] Не удалось перейти в папку скрипта: "%~dp0"
  echo Возможно, путь недоступен или нет прав.
  pause
  exit /b 1
)

REM --- 2) Проверки артефактов ---
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Не найден интерпретатор venv: ".venv\Scripts\python.exe"
  echo Создай окружение: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  popd & pause & exit /b 2
)

if not exist "main.py" (
  echo [ERROR] Не найден main.py рядом со скриптом
  popd & pause & exit /b 3
)

REM Разрешим переопределить входной файл первым аргументом, иначе по умолчанию:
set "INPUT_FILE=%~1"
if "%INPUT_FILE%"=="" set "INPUT_FILE=test08.xlsx"

if not exist "%INPUT_FILE%" (
  echo [ERROR] Не найден входной файл: "%INPUT_FILE%"
  popd & pause & exit /b 4
)

REM --- 3) (опц.) Активировать venv. Даже если не получится — ниже мы зовем python по полному пути. ---
call ".venv\Scripts\activate.bat" 2>nul >nul

REM --- 4) Запуск строго интерпретатором из venv (без двусмысленности) ---
echo [INFO] Running: .venv\Scripts\python.exe "main.py" "%INPUT_FILE%" %*
".venv\Scripts\python.exe" "main.py" "%INPUT_FILE%" %*
set "EC=%ERRORLEVEL%"

REM --- 5) Вернуться и выйти с тем же кодом ---
popd
if not "%EC%"=="0" (
  echo [ERROR] Python завершился с кодом %EC%
) else (
  echo [OK] Готово
)
pause
exit /b %EC%
