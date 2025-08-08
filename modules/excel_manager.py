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


def get_date_from_first_row(df: pd.DataFrame) -> date:
    """
    Получает дату из первой строки данных в колонке "ДатаБезВремени".

    Args:
        df: DataFrame с данными

    Returns:
        date: Дата из первой строки данных
    """
    if "ДатаБезВремени" not in df.columns:
        logger.error("❌ Колонка 'ДатаБезВремени' не найдена в данных")
        raise ValueError("Колонка 'ДатаБезВремени' обязательна для автоматического определения даты")

    # Получаем первую непустую дату
    first_date = None
    for idx, row in df.iterrows():
        date_value = row['ДатаБезВремени']
        if pd.notna(date_value) and str(date_value).strip() != '':
            try:
                if isinstance(date_value, str):
                    first_date = datetime.strptime(date_value, "%d.%m.%Y").date()
                elif isinstance(date_value, datetime):
                    first_date = date_value.date()
                else:
                    first_date = pd.to_datetime(date_value).date()
                break
            except Exception as e:
                logger.warning(f"⚠️ Не удалось распарсить дату '{date_value}' в строке {idx}: {e}")
                continue

    if first_date is None:
        logger.error("❌ Не найдена валидная дата в колонке 'ДатаБезВремени'")
        raise ValueError("Не найдена валидная дата в данных")

    logger.info(f"✅ Автоматически определена дата: {first_date.strftime('%d.%m.%Y')}")
    return first_date


def filter_problems_by_date(df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    """
    Фильтрует проблемы по дате из колонки "ДатаБезВремени".

    Args:
        df: DataFrame с проблемами
        target_date: Целевая дата для фильтрации

    Returns:
        pd.DataFrame: Отфильтрованные проблемы
    """
    logger.info(f"🔍 Фильтруем проблемы для даты {target_date.strftime('%d.%m.%Y')}")

    # Преобразуем target_date в строку для сравнения
    target_date_str = target_date.strftime('%d.%m.%Y')

    # Фильтруем проблемы:
    # 1. Дата в колонке "ДатаБезВремени" совпадает с указанной датой
    # 2. Исключаем проблемы с регионом 'nan' (отсутствующий регион)
    date_filter = df['ДатаБезВремени'].astype(str) == target_date_str
    region_filter = ~(df['Регион'].astype(str).str.strip().str.lower() == 'nan')

    filtered_df = df[date_filter & region_filter].copy()
    logger.info(f"🔍 Исключены проблемы с регионом 'nan'")

    logger.info(f"📊 Найдено {len(filtered_df)} проблем для даты {target_date.strftime('%d.%m.%Y')}")

    if len(filtered_df) == 0:
        logger.warning(f"⚠️ Не найдено проблем для даты {target_date.strftime('%d.%m.%Y')}")
    else:
        logger.info(f"✅ Проблемы для обработки:")
        for idx, row in filtered_df.iterrows():
            date_str = row['ДатаБезВремени'] if pd.notna(row['ДатаБезВремени']) else 'N/A'
            logger.info(f"   📋 {row['Номер массовой']} - {row['Регион']} (дата: {date_str})")

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
    Сохраняет результаты в отдельный лист Excel файла.
    Создает новый лист с полной таблицей как в исходных данных + колонка "потерянные".

    Args:
        results: Список результатов
        original_file_path: Путь к исходному Excel файлу
        target_date: Дата для которой были получены результаты
    """
    logger.info(f"💾 Сохраняем результаты в отдельный лист: {original_file_path}")

    try:
        # Загружаем рабочую книгу
        workbook = load_workbook(original_file_path)

        # Создаем или получаем лист для результатов
        sheet_name = f"Результаты_{target_date.strftime('%d_%m_%Y')}"
        if sheet_name in workbook.sheetnames:
            result_sheet = workbook[sheet_name]
        else:
            result_sheet = workbook.create_sheet(sheet_name)
            logger.info(f"📋 Создан новый лист: {sheet_name}")

        # Если лист новый, копируем заголовки из исходного листа "Отчет"
        if result_sheet.max_row == 1 and result_sheet.max_column == 1:
            # Копируем заголовки из листа "Отчет"
            report_sheet = workbook["Отчет"]
            for col in range(1, report_sheet.max_column + 1):
                cell_value = report_sheet.cell(row=1, column=col).value
                result_sheet.cell(row=1, column=col, value=cell_value)

            # Добавляем колонку "потерянные"
            lost_col = report_sheet.max_column + 1
            result_sheet.cell(row=1, column=lost_col, value="потерянные")
            logger.info(f"📋 Скопированы заголовки и добавлена колонка 'потерянные'")

        # Находим колонку с номером массовой
        mass_number_col = None
        for col in range(1, result_sheet.max_column + 1):
            header = result_sheet.cell(row=1, column=col).value
            if header and "номер" in str(header).lower() and "массовой" in str(header).lower():
                mass_number_col = col
                break

        if mass_number_col is None:
            logger.error("❌ Не найдена колонка с номером массовой")
            return

        # Создаем словарь результатов
        results_dict = {}
        for result in results:
            mass_number = result["Номер массовой"]
            lost_calls = result["LostCalls"]
            results_dict[mass_number] = lost_calls

        # Обрабатываем каждый результат
        for mass_number, lost_calls in results_dict.items():
            # Ищем строку с нужным номером массовой
            target_row = None
            for row in range(2, result_sheet.max_row + 1):
                cell_value = result_sheet.cell(row=row, column=mass_number_col).value
                if str(cell_value) == str(mass_number):
                    target_row = row
                    break

            if target_row is None:
                # Добавляем новую строку
                target_row = result_sheet.max_row + 1
                logger.info(f"➕ Добавлена новая строка {target_row} для {mass_number}")

            # Копируем данные из исходного листа "Отчет"
            report_sheet = workbook["Отчет"]
            report_row = None
            for row in range(2, report_sheet.max_row + 1):
                cell_value = report_sheet.cell(row=row, column=mass_number_col).value
                if str(cell_value) == str(mass_number):
                    report_row = row
                    break

            if report_row:
                # Копируем все данные из исходной строки
                for col in range(1, report_sheet.max_column + 1):
                    cell_value = report_sheet.cell(row=report_row, column=col).value
                    result_sheet.cell(row=target_row, column=col, value=cell_value)

            # Записываем результат в колонку "потерянные"
            lost_col = result_sheet.max_column
            result_sheet.cell(row=target_row, column=lost_col, value=lost_calls)
            logger.info(f"✅ Сохранен результат: {mass_number} → {lost_calls}")

        # Сохраняем файл
        workbook.save(original_file_path)
        logger.info(f"💾 Все результаты сохранены в лист '{sheet_name}'")

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении результатов: {e}")


def save_single_result_to_original_file(
    mass_number: str,
    lost_calls: int,
    excess_traffic: float,
    original_file_path: Path,
    row_index: int
) -> None:
    """
    Сохраняет результат одной строки в исходный Excel файл.
    Добавляет колонки "Потерянные" и "Полученные" если их нет.

    Args:
        mass_number: Номер массового инцидента
        lost_calls: Количество потерянных звонков
        excess_traffic: Коэффициент превышения трафика (сохраняется как "Полученные")
        original_file_path: Путь к исходному Excel файлу
        row_index: Индекс строки в исходном файле
    """
    logger.info(f"💾 Сохраняем результат для {mass_number}: lost={lost_calls}, excess={excess_traffic}")

    try:
        # Загружаем рабочую книгу
        workbook = load_workbook(original_file_path)
        report_sheet = workbook["Отчет"]

        # Проверяем есть ли колонки "Потерянные" и "Полученные"
        lost_col = None
        received_col = None

        for col in range(1, report_sheet.max_column + 1):
            header = report_sheet.cell(row=1, column=col).value
            if header and "потерянные" in str(header).lower():
                lost_col = col
            elif header and "полученные" in str(header).lower():
                received_col = col

        # Если колонок нет, добавляем их
        if lost_col is None:
            lost_col = report_sheet.max_column + 1
            report_sheet.cell(row=1, column=lost_col, value="Потерянные")
            logger.info(f"➕ Добавлена колонка 'Потерянные' в позицию {lost_col}")

        if received_col is None:
            received_col = report_sheet.max_column + 1
            report_sheet.cell(row=1, column=received_col, value="Полученные")
            logger.info(f"➕ Добавлена колонка 'Полученные' в позицию {received_col}")

        # Находим строку с нужным номером массовой
        mass_number_col = None
        for col in range(1, report_sheet.max_column + 1):
            header = report_sheet.cell(row=1, column=col).value
            if header and "номер" in str(header).lower() and "массовой" in str(header).lower():
                mass_number_col = col
                break

        if mass_number_col is None:
            logger.error("❌ Не найдена колонка с номером массовой")
            return

        # Ищем строку с нужным номером массовой
        target_row = None
        for row in range(2, report_sheet.max_row + 1):
            cell_value = report_sheet.cell(row=row, column=mass_number_col).value
            if str(cell_value) == str(mass_number):
                target_row = row
                break

        if target_row is None:
            logger.error(f"❌ Не найдена строка с номером массовой {mass_number}")
            return

        # Записываем результаты
        report_sheet.cell(row=target_row, column=lost_col, value=lost_calls)
        report_sheet.cell(row=target_row, column=received_col, value=excess_traffic)

        # Сохраняем файл
        workbook.save(original_file_path)
        logger.info(f"✅ Результат сохранен в строку {target_row}: {mass_number} → lost={lost_calls}, received={excess_traffic}")

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении результата для {mass_number}: {e}")
        raise