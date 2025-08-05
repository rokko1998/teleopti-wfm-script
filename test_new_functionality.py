#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового функционала с фильтрацией по дате.
"""

import sys
from pathlib import Path
from loguru import logger

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from modules.excel_manager import get_user_date, filter_problems_by_date, calculate_time_window_for_date
from modules.data_processing import process_excel_data


def test_date_filtering():
    """Тестирует фильтрацию по дате."""
    logger.info("🧪 Тестируем новый функционал фильтрации по дате")

    # Путь к тестовому файлу (замените на реальный путь)
    test_file = Path("test.xlsx")  # Замените на реальный файл

    if not test_file.exists():
        logger.error(f"❌ Тестовый файл {test_file} не найден")
        logger.info("💡 Создайте тестовый Excel файл или укажите правильный путь")
        return

    try:
        # Загружаем данные
        logger.info(f"📂 Загружаем данные из {test_file}")
        df = process_excel_data(test_file)

        # Тестируем запрос даты (закомментируйте для автоматического тестирования)
        # target_date = get_user_date()

        # Для автоматического тестирования используем фиксированную дату
        from datetime import date
        target_date = date(2025, 5, 4)  # 04.05.2025
        logger.info(f"📅 Тестовая дата: {target_date.strftime('%d.%m.%Y')}")

        # Фильтруем проблемы
        filtered_df = filter_problems_by_date(df, target_date)

        logger.info(f"✅ Тест завершен успешно!")
        logger.info(f"📊 Найдено {len(filtered_df)} проблем для даты {target_date.strftime('%d.%m.%Y')}")

        # Показываем временные окна для первых нескольких проблем
        for idx, row in filtered_df.head(3).iterrows():
            win_start, win_end = calculate_time_window_for_date(row, target_date)
            logger.info(f"   📋 {row['Номер массовой']}: {win_start.strftime('%H:%M')} - {win_end.strftime('%H:%M')}")

    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")
        logger.exception("Полный traceback:")


if __name__ == "__main__":
    test_date_filtering()