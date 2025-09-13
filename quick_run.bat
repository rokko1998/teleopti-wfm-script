@echo off
chcp 65001 >nul
title WFM Traffic Script - Quick Run

echo ========================================
echo  WFM Traffic Script - Быстрый запуск
echo ========================================
echo.

REM Активируем окружение и запускаем скрипт
call venv\Scripts\activate.bat
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
