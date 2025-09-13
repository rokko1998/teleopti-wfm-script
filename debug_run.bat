@echo off
chcp 65001 >nul
title WFM Traffic Script - DEBUG

echo ========================================
echo  WFM Traffic Script - ОТЛАДОЧНЫЙ РЕЖИМ
echo ========================================
echo.

echo [DEBUG] Шаг 1: Проверяем текущую папку
echo Текущая папка: %CD%
echo.

echo [DEBUG] Шаг 2: Проверяем наличие Python
python --version
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Нажмите любую клавишу для выхода...
    pause
    exit /b 1
)
echo [OK] Python найден
echo.

echo [DEBUG] Шаг 3: Проверяем наличие файлов
if exist "main.py" (
    echo [OK] main.py найден
) else (
    echo [ОШИБКА] main.py не найден!
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo [OK] requirements.txt найден
) else (
    echo [ОШИБКА] requirements.txt не найден!
    pause
    exit /b 1
)

if exist "test08.xlsx" (
    echo [OK] test08.xlsx найден
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] test08.xlsx не найден
)
echo.

echo [DEBUG] Шаг 4: Проверяем виртуальное окружение
if exist "venv\Scripts\activate.bat" (
    echo [OK] Виртуальное окружение найдено
    echo [DEBUG] Активируем окружение...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось активировать окружение!
        pause
        exit /b 1
    )
    echo [OK] Окружение активировано
) else (
    echo [ИНФОРМАЦИЯ] Виртуальное окружение не найдено, создаем...
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать окружение!
        pause
        exit /b 1
    )
    echo [OK] Окружение создано
    echo [DEBUG] Активируем окружение...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось активировать окружение!
        pause
        exit /b 1
    )
    echo [OK] Окружение активировано
)
echo.

echo [DEBUG] Шаг 5: Устанавливаем зависимости
echo [DEBUG] Выполняем: pip install -r requirements.txt
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости!
    pause
    exit /b 1
)
echo [OK] Зависимости установлены
echo.

echo [DEBUG] Шаг 6: Запускаем скрипт
echo [DEBUG] Выполняем: python main.py test08.xlsx --auto-date-processing
echo ========================================
echo.

python main.py test08.xlsx --auto-date-processing

echo.
echo ========================================
if errorlevel 1 (
    echo [ОШИБКА] Скрипт завершился с ошибкой!
) else (
    echo [УСПЕХ] Скрипт выполнен успешно!
)

echo.
echo Нажмите любую клавишу для выхода...
pause
