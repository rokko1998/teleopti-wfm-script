"""
Модуль для работы с Excel файлами - чтение и запись данных.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from loguru import logger
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def get_user_date() -> date:
    """
    Запрашивает у пользователя дату для выгрузки.

    Returns:
        date: Выбранная пользователем дата
    """
    while True:
        try:
            date_str = input("📅 Введите дату для выгрузки (формат ДД.ММ.ГГГГ, например 04.05.2025): ").strip()
            user_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            logger.info(f"✅ Выбрана дата: {user_date.strftime('%d.%m.%Y')}")
            return user_date
        except ValueError:
            logger.error("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")
        except KeyboardInterrupt:
            logger.info("🛑 Программа прервана пользователем")
            raise


def filter_problems_by_date(df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    """
    Фильтрует проблемы по дате - оставляет только те, которые были активны в указанную дату.

    Args:
        df: DataFrame с проблемами
        target_date: Целевая дата для фильтрации

    Returns:
        pd.DataFrame: Отфильтрованные проблемы
    """
    logger.info(f"🔍 Фильтруем проблемы для даты {target_date.strftime('%d.%m.%Y')}")

    # Преобразуем target_date в datetime для сравнения
    target_datetime_start = datetime.combine(target_date, datetime.min.time())
    target_datetime_end = datetime.combine(target_date, datetime.max.time())

    # Фильтруем проблемы:
    # 1. Проблема была открыта до или в указанную дату (Старт <= конец дня)
    # 2. Проблема была закрыта после или в указанную дату (Окончание >= начало дня) или не закрыта (Окончание is null)
    # 3. Если есть колонка "Название", исключаем проблемы с названием 'nan'
    time_filter = (
        (df['Старт'] <= target_datetime_end) &
        ((df['Окончание'] >= target_datetime_start) | df['Окончание'].isna())
    )
    
    # Добавляем фильтр по названию если колонка существует
    if 'Название' in df.columns:
        name_filter = ~(df['Название'].astype(str).str.strip().str.lower() == 'nan')
        filtered_df = df[time_filter & name_filter].copy()
        logger.info(f"🔍 Исключены проблемы с названием 'nan'")
    else:
        filtered_df = df[time_filter].copy()

    logger.info(f"📊 Найдено {len(filtered_df)} проблем активных в дату {target_date.strftime('%d.%m.%Y')}")

    if len(filtered_df) == 0:
        logger.warning(f"⚠️ Не найдено проблем для даты {target_date.strftime('%d.%m.%Y')}")
    else:
        logger.info(f"✅ Проблемы для обработки:")
        for idx, row in filtered_df.iterrows():
            start_str = row['Старт'].strftime('%d.%m.%Y %H:%M') if pd.notna(row['Старт']) else 'N/A'
            end_str = row['Окончание'].strftime('%d.%m.%Y %H:%M') if pd.notna(row['Окончание']) else 'N/A'
            logger.info(f"   📋 {row['Номер массовой']} - {row['Регион']}: {start_str} → {end_str}")

    return filtered_df


def calculate_time_window_for_date(row: pd.Series, target_date: date) -> tuple[datetime, datetime]:
    """
    Вычисляет временное окно для указанной даты с учетом времени открытия/закрытия проблемы.

    Args:
        row: Строка с данными проблемы
        target_date: Целевая дата

    Returns:
        tuple[datetime, datetime]: (время начала, время окончания) для указанной даты
    """
    target_datetime_start = datetime.combine(target_date, datetime.min.time())  # 00:00:00
    target_datetime_end = datetime.combine(target_date, datetime.max.time())    # 23:59:59

    problem_start = row['Старт']
    problem_end = row['Окончание']

    # Определяем время начала для указанной даты
    if problem_start.date() == target_date:
        # Проблема была открыта в указанную дату - берем время открытия
        window_start = problem_start
    else:
        # Проблема была открыта раньше - берем начало дня
        window_start = target_datetime_start

    # Определяем время окончания для указанной даты
    if pd.isna(problem_end):
        # Проблема не закрыта - берем конец дня
        window_end = target_datetime_end
    elif problem_end.date() == target_date:
        # Проблема была закрыта в указанную дату - берем время закрытия
        window_end = problem_end
    else:
        # Проблема была закрыта позже - берем конец дня
        window_end = target_datetime_end

    logger.info(f"🕒 Временное окно для {row['Номер массовой']} на {target_date.strftime('%d.%m.%Y')}:")
    logger.info(f"   📍 Начало: {window_start.strftime('%d.%m.%Y %H:%M')}")
    logger.info(f"   📍 Окончание: {window_end.strftime('%d.%m.%Y %H:%M')}")

    return window_start, window_end


def save_results_to_excel(
    results: List[Dict[str, Any]],
    original_file_path: Path,
    target_date: date
) -> None:
    """
    Сохраняет результаты в исходный Excel файл в таблицу "Свод_по_заметкам" в колонку "потерянные".

    Args:
        results: Список результатов
        original_file_path: Путь к исходному Excel файлу
        target_date: Дата для которой были получены результаты
    """
    logger.info(f"💾 Сохраняем результаты в исходный файл: {original_file_path}")

    try:
        # Загружаем рабочую книгу
        workbook = load_workbook(original_file_path)

        # Ищем лист "Отчет"
        if "Отчет" not in workbook.sheetnames:
            logger.error("❌ Лист 'Отчет' не найден в файле")
            return

        report_sheet = workbook["Отчет"]

        # Ищем таблицу "Свод_по_заметкам"
        table_name = "Свод_по_заметкам"
        table = None

        for table_obj in report_sheet.tables.values():
            if table_obj.name == table_name:
                table = table_obj
                break

        if not table:
            logger.error(f"❌ Таблица '{table_name}' не найдена на листе 'Отчет'")
            return

        # Получаем диапазон таблицы
        table_range = table.ref
        logger.info(f"📊 Найдена таблица '{table_name}' в диапазоне {table_range}")

        # Читаем данные таблицы
        table_data = []
        for row in report_sheet[table_range]:
            table_data.append([cell.value for cell in row])

        # Находим заголовки
        headers = table_data[0]
        logger.info(f"📋 Заголовки таблицы: {headers}")

        # Проверяем есть ли колонка "потерянные"
        lost_column_idx = None
        for i, header in enumerate(headers):
            if header and "потерянные" in str(header).lower():
                lost_column_idx = i
                break

        if lost_column_idx is None:
            # Добавляем новую колонку "потерянные" в конец
            lost_column_idx = len(headers)
            headers.append("потерянные")
            logger.info(f"➕ Добавлена новая колонка 'потерянные' в позицию {lost_column_idx}")

        # Создаем словарь для быстрого поиска результатов по номеру массовой
        results_dict = {}
        for result in results:
            mass_number = result["Номер массовой"]
            lost_calls = result["LostCalls"]
            results_dict[mass_number] = lost_calls

        # Находим колонку с номером массовой
        mass_number_col_idx = None
        for i, header in enumerate(headers):
            if header and "номер" in str(header).lower() and "массовой" in str(header).lower():
                mass_number_col_idx = i
                break

        if mass_number_col_idx is None:
            logger.error("❌ Не найдена колонка с номером массовой в таблице")
            return

        # Заполняем данные
        updated_rows = 0
        for row_idx, row_data in enumerate(table_data[1:], start=2):  # Пропускаем заголовок
            if len(row_data) <= mass_number_col_idx:
                continue

            mass_number = row_data[mass_number_col_idx]
            if mass_number in results_dict:
                # Расширяем строку если нужно
                while len(row_data) <= lost_column_idx:
                    row_data.append(None)

                row_data[lost_column_idx] = results_dict[mass_number]
                updated_rows += 1
                logger.info(f"✅ Обновлена строка для {mass_number}: потерянные = {results_dict[mass_number]}")

        # Записываем обновленные данные обратно в таблицу
        for row_idx, row_data in enumerate(table_data):
            for col_idx, value in enumerate(row_data):
                cell = report_sheet.cell(row=row_idx + 1, column=col_idx + 1)
                cell.value = value

        # Обновляем диапазон таблицы если добавили колонку
        if lost_column_idx >= len(headers) - 1:
            # Нужно обновить диапазон таблицы
            new_range = f"{table_range.split(':')[0]}:{chr(ord('A') + lost_column_idx)}{table_range.split(':')[1].split(':')[1]}"
            table.ref = new_range
            logger.info(f"📊 Обновлен диапазон таблицы: {new_range}")

        # Сохраняем файл
        workbook.save(original_file_path)
        logger.success(f"✅ Результаты успешно сохранены в файл {original_file_path}")
        logger.info(f"📝 Обновлено {updated_rows} строк в таблице '{table_name}'")

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении в Excel: {e}")
        raise