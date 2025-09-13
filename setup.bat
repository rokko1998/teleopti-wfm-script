@echo off
chcp 65001 >nul
title WFM Traffic Script - Настройка

echo ========================================
echo  WFM Traffic Script - Настройка окружения
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.8+ с официального сайта: https://python.org
    echo Убедитесь, что Python добавлен в PATH
    echo.
    pause
    exit /b 1
)

echo [INFO] Python найден:
python --version

REM Удаляем старое виртуальное окружение если есть
if exist "venv" (
    echo [INFO] Удаляем старое виртуальное окружение...
    rmdir /s /q venv
)

REM Создаем новое виртуальное окружение
echo [INFO] Создание виртуального окружения...
python -m venv venv
if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать виртуальное окружение!
    pause
    exit /b 1
)

REM Активируем виртуальное окружение
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)

REM Обновляем pip
echo [INFO] Обновление pip...
python -m pip install --upgrade pip

REM Устанавливаем зависимости
echo [INFO] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости!
    pause
    exit /b 1
)

echo.
echo [УСПЕХ] Настройка завершена успешно!
echo.
echo Теперь вы можете запустить скрипт командой:
echo   run_script.bat
echo.
echo Или напрямую:
echo   venv\Scripts\activate.bat
echo   python main.py test08.xlsx --auto-date-processing
echo.
pause
