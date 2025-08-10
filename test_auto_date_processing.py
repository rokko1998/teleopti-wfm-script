#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой функциональности автоматической обработки по дате.
"""

import pandas as pd
from pathlib import Path
from modules.excel_manager import get_date_from_first_row, filter_problems_by_date, calculate_time_window_for_date

def test_date_extraction():
    """Тестирует извлечение даты из первой строки данных."""
    print("🧪 Тестируем извлечение даты из первой строки данных...")

    # Создаем тестовые данные
    test_data = {
        'ДатаБезВремени': ['01.08.2025', '01.08.2025', '02.08.2025'],
        'Номер массовой': ['113156', '113157', '113158'],
        'Заметки': [7, 8, 9],
        'Название': ['Проблема 1', 'Проблема 2', 'Проблема 3'],
        'Регион': ['Сахалин', 'Сахалин', 'Москва'],
        'Старт': ['16.07.2025 9:21', '16.07.2025 10:30', '17.07.2025 8:15'],
        'Окончание': ['00.01.1900 0:00', '00.01.1900 0:00', '00.01.1900 0:00'],
        'Макрорегион': ['БиДВ', 'БиДВ', 'ЦФО'],
        'Месяц': [8, 8, 8],
        'Неделя (вс)': [31, 31, 32],
        'Неделя (ISO)': [31, 31, 32]
    }

    df = pd.DataFrame(test_data)

    try:
        # Тестируем извлечение даты
        target_date = get_date_from_first_row(df)
        print(f"✅ Дата успешно извлечена: {target_date.strftime('%d.%m.%Y')}")

        # Тестируем фильтрацию по дате
        filtered_df = filter_problems_by_date(df, target_date)
        print(f"✅ Отфильтровано проблем для даты {target_date.strftime('%d.%m.%Y')}: {len(filtered_df)}")

        # Тестируем расчет временного окна для первой строки
        if len(filtered_df) > 0:
            first_row = filtered_df.iloc[0]
            win_start, win_end = calculate_time_window_for_date(first_row, target_date)
            print(f"✅ Временное окно для первой строки:")
            print(f"   Начало: {win_start}")
            print(f"   Окончание: {win_end}")

        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def test_with_real_file(file_path: str):
    """Тестирует с реальным файлом."""
    print(f"🧪 Тестируем с реальным файлом: {file_path}")

    try:
        # Загружаем данные
        df = pd.read_excel(file_path, sheet_name="Отчет")
        print(f"✅ Файл загружен, строк: {len(df)}")

        # Тестируем извлечение даты
        target_date = get_date_from_first_row(df)
        print(f"✅ Дата извлечена: {target_date.strftime('%d.%m.%Y')}")

        # Тестируем фильтрацию
        filtered_df = filter_problems_by_date(df, target_date)
        print(f"✅ Отфильтровано проблем: {len(filtered_df)}")

        if len(filtered_df) > 0:
            print("📋 Первые 3 проблемы:")
            for idx, row in filtered_df.head(3).iterrows():
                print(f"   {row['Номер массовой']} - {row['Регион']} - {row['ДатаБезВремени']}")

        return True

    except Exception as e:
        print(f"❌ Ошибка при работе с файлом: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов новой функциональности...")

    # Тест с синтетическими данными
    success1 = test_date_extraction()

    # Тест с реальным файлом (если есть)
    success2 = True
    test_file = "test.xlsx"  # Замените на реальный путь к файлу
    if Path(test_file).exists():
        success2 = test_with_real_file(test_file)
    else:
        print(f"⚠️ Файл {test_file} не найден, пропускаем тест с реальными данными")

    if success1 and success2:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли")