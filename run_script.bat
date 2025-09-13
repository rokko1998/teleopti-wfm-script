@echo off
chcp 65001 >nul
title WFM Traffic Script

echo ========================================
echo  WFM Traffic Script - Запуск скрипта
echo ========================================
echo.

REM Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [ИНФОРМАЦИЯ] Виртуальное окружение не найдено, создаем...
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
    echo [ИНФОРМАЦИЯ] Виртуальное окружение создано
)

REM Активируем виртуальное окружение
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)

echo [INFO] Виртуальное окружение активировано
echo.

REM Проверяем и устанавливаем зависимости
echo [INFO] Проверка зависимостей...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости!
    echo Проверьте файл requirements.txt
    pause
    exit /b 1
)
echo [INFO] Зависимости установлены
echo.

REM Проверяем наличие файла test08.xlsx
if not exist "test08.xlsx" (
    echo [ПРЕДУПРЕЖДЕНИЕ] Файл test08.xlsx не найден в текущей папке
    echo Убедитесь, что файл находится в папке со скриптом
    echo.
)

REM Запускаем скрипт с параметрами
echo [INFO] Запуск скрипта с параметрами...
echo Команда: python main.py test08.xlsx --auto-date-processing
echo.

python main.py test08.xlsx --auto-date-processing

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Скрипт завершился с ошибкой!
    echo Проверьте логи выше для получения подробной информации.
) else (
    echo.
    echo [УСПЕХ] Скрипт выполнен успешно!
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
