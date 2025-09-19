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

REM === 2) Автоматическое определение Python и настройка venv ===
call :FindPython
if "%PYTHON_PATH%"=="" (
  echo [ERROR] Python не найден в системе
  echo Проверьте установку Python или добавьте его в PATH
  popd & pause & exit /b 2
)

echo [INFO] Найден Python: "%PYTHON_PATH%"

REM Указываем интерпретатор из venv и целевые файлы
set "PY=%CURR%\.venv\Scripts\python.exe"
set "ACT=%CURR%\.venv\Scripts\activate.bat"
set "MAIN=%CURR%\main.py"

REM Входной XLSX: первый аргумент или test08.xlsx по умолчанию
set "INPUT=%~1"
if "%INPUT%"=="" set "INPUT=%CURR%\test08.xlsx"
REM Если пришёл относительный путь или имя файла без пути — добавим текущую папку
if not exist "%INPUT%" if exist "%CURR%\%~1" set "INPUT=%CURR%\%~1"

REM === 3) Проверки наличия и создание/исправление venv ===
if not exist "%PY%" (
  echo [INFO] venv не найден, создаем новое окружение...
  call :CreateVenv
  if errorlevel 1 (
    echo [ERROR] Не удалось создать venv
    popd & pause & exit /b 2
  )
) else (
  echo [INFO] Проверяем корректность существующего venv...
  call :CheckVenv
  if errorlevel 1 (
  echo [INFO] venv поврежден, исправляем пути...
  call :RecreateVenv
  if errorlevel 1 (
    echo [ERROR] Не удалось исправить venv
    popd & pause & exit /b 2
  )
  )
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
echo [INFO] RUN = "%PY%" "%MAIN%" "%INPUT%" --auto-date-processing --log-level ERROR %*
echo [INFO] ВНИМАНИЕ: После выгрузки будет выполнена постобработка данных
echo [INFO] - Поиск дубликатов в колонке "Потерянные"
echo [INFO] - Сравнение регионов и заметок
echo [INFO] - Зануление строк с отрицательным "Превышение"

REM Запускаем с обработкой ошибки 103
call :RunWithErrorHandling
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

REM === ФУНКЦИИ ===

:FindPython
REM Поиск Python в различных местах
set "PYTHON_PATH="

REM 1. Проверяем PATH
python --version >nul 2>&1
if not errorlevel 1 (
  for /f "tokens=*" %%i in ('where python 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto :FoundPython
  )
)

REM 2. Проверяем стандартные места установки
for %%p in (
  "C:\py\python.exe"
  "C:\Python39\python.exe"
  "C:\Python310\python.exe"
  "C:\Python311\python.exe"
  "C:\Python312\python.exe"
  "C:\Python313\python.exe"
  "C:\Program Files\Python39\python.exe"
  "C:\Program Files\Python310\python.exe"
  "C:\Program Files\Python311\python.exe"
  "C:\Program Files\Python312\python.exe"
  "C:\Program Files\Python313\python.exe"
  "C:\Program Files (x86)\Python39\python.exe"
  "C:\Program Files (x86)\Python310\python.exe"
  "C:\Program Files (x86)\Python311\python.exe"
  "C:\Program Files (x86)\Python312\python.exe"
  "C:\Program Files (x86)\Python313\python.exe"
) do (
  if exist %%p (
    set "PYTHON_PATH=%%p"
    goto :FoundPython
  )
)

REM 3. Поиск в реестре (если доступен)
for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore" /s /v "ExecutablePath" 2^>nul ^| findstr "ExecutablePath"') do (
  if exist "%%b" (
    set "PYTHON_PATH=%%b"
    goto :FoundPython
  )
)

REM 4. Поиск в пользовательском реестре
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\SOFTWARE\Python\PythonCore" /s /v "ExecutablePath" 2^>nul ^| findstr "ExecutablePath"') do (
  if exist "%%b" (
    set "PYTHON_PATH=%%b"
    goto :FoundPython
  )
)

:FoundPython
exit /b 0

:CreateVenv
REM Создание нового venv
echo [INFO] Создаем venv с Python: "%PYTHON_PATH%"
"%PYTHON_PATH%" -m venv .venv
if errorlevel 1 exit /b 1

echo [INFO] Устанавливаем зависимости...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 exit /b 1

echo [INFO] venv создан успешно
exit /b 0

:CheckVenv
REM Проверка корректности существующего venv
echo [INFO] Проверяем venv...
.venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 exit /b 1

REM Проверяем наличие основных пакетов
.venv\Scripts\python.exe -c "import selenium, pandas, openpyxl, loguru, tqdm" >nul 2>&1
if errorlevel 1 exit /b 1

echo [INFO] venv корректен
exit /b 0

:RecreateVenv
REM Исправление путей в существующем venv
echo [INFO] Исправляем пути в существующем venv...

REM Обновляем pyvenv.cfg
if exist .venv\pyvenv.cfg (
  echo [INFO] Обновляем pyvenv.cfg...
  echo home = %PYTHON_PATH% > .venv\pyvenv.cfg
  echo include-system-site-packages = false >> .venv\pyvenv.cfg
  echo version = 3.13 >> .venv\pyvenv.cfg
)

REM Обновляем python.exe (копируем правильный Python)
if exist "%PYTHON_PATH%" (
  echo [INFO] Копируем правильный Python в venv...
  copy /Y "%PYTHON_PATH%" .venv\Scripts\python.exe >nul 2>&1
  copy /Y "%PYTHON_PATH%" .venv\Scripts\pythonw.exe >nul 2>&1
)

REM Обновляем pip
if exist .venv\Scripts\python.exe (
  echo [INFO] Обновляем pip...
  .venv\Scripts\python.exe -m ensurepip --upgrade >nul 2>&1
)

echo [INFO] Пути в venv исправлены успешно
exit /b 0

:RunWithErrorHandling
REM Запуск с обработкой ошибки 103
"%PY%" "%MAIN%" "%INPUT%" --auto-date-processing --log-level ERROR %*
set "RUN_EC=%ERRORLEVEL%"

REM Если получили ошибку 103, пытаемся исправить
if "%RUN_EC%"=="103" (
  echo [WARNING] Обнаружена ошибка 103 - проблема с путем к Python
  echo [INFO] Исправляем пути в venv...

  call :RecreateVenv
  if errorlevel 1 (
    echo [ERROR] Не удалось исправить venv
    exit /b 103
  )

  echo [INFO] Повторный запуск после исправления...
  "%PY%" "%MAIN%" "%INPUT%" --auto-date-processing --log-level ERROR %*
  set "RUN_EC=%ERRORLEVEL%"
)

exit /b %RUN_EC%