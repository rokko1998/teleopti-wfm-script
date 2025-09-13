@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM --- (опционально) нормализуем кодировку вывода ---
REM chcp 65001 >nul

REM === 1) Переходим в папку, где лежит батник ===
REM ВАЖНО: pushd сам смонтирует UNC во временную букву; если батник уже на Z:, просто перейдём туда.
pushd "%~dp0" || (
  echo [ERROR] Не удалось перейти в папку скрипта: "%~dp0"
  echo Проверь доступ к сети/правам.
  pause & exit /b 1
)

REM Текущая папка теперь гарантированно на букве диска (не UNC)
set "CURR=%CD%"

REM === 2) Указываем интерпретатор из venv и целевые файлы ===
set "PY=%CURR%\.venv\Scripts\python.exe"
set "ACT=%CURR%\.venv\Scripts\activate.bat"
set "MAIN=%CURR%\main.py"

REM Входной XLSX: первый аргумент или test08.xlsx по умолчанию
set "INPUT=%~1"
if "%INPUT%"=="" set "INPUT=%CURR%\test08.xlsx"
REM Если пришёл относительный путь или имя файла без пути — добавим текущую папку
if not exist "%INPUT%" if exist "%CURR%\%~1" set "INPUT=%CURR%\%~1"

REM === 3) Проверки наличия ===
if not exist "%PY%" (
  echo [ERROR] Не найден интерпретатор venv: "%PY%"
  echo Создай окружение: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  popd & pause & exit /b 2
)

if not exist "%MAIN%" (
  echo [ERROR] Не найден main.py по пути: "%MAIN%"
  popd & pause & exit /b 3
)

if not exist "%INPUT%" (
  echo [ERROR] Не найден входной файл: "%INPUT%"
  popd & pause & exit /b 4
)

REM === 4) (опционально) активируем venv — на случай, если внутри скрипта зовёшь pip/pytest "по имени" ===
if exist "%ACT%" call "%ACT%" 1>nul 2>nul

REM === 5) Запуск строго через интерпретатор из venv (без двусмысленности) ===
echo [INFO] CWD = "%CURR%"
echo [INFO] PY  = "%PY%"
echo [INFO] RUN = "%PY%" "%MAIN%" "%INPUT%" %*
"%PY%" "%MAIN%" "%INPUT%" %*
set "EC=%ERRORLEVEL%"

REM === 6) Возврат в исходную директорию и выход с тем же кодом ===
popd
if not "%EC%"=="0" (
  echo [ERROR] Python завершился с кодом %EC%
  pause & exit /b %EC%
) else (
  echo [OK] Готово
  pause & exit /b 0
)