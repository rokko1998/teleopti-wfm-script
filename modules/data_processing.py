"""
Модуль для обработки результатов и вычислений.
"""

from pathlib import Path
from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger


def calc_metrics(path: Path) -> Tuple[int, float]:
    """
    Читает 2‑й лист отчёта и возвращает (lost, excess).
    
    Args:
        path: Путь к Excel файлу с отчетом
    
    Returns:
        Tuple[int, float]: (lost_calls, excess_traffic)
    """
    df = pd.read_excel(path, sheet_name=1, header=4)  # строка 5 = header
    df.columns = [c.strip() for c in df.columns]

    calc = df["Расчетные звонки"].fillna(0)
    fcst = df["Спрогнозированные звонки"].fillna(0)
    answ = df["Отвеченные звонки"].fillna(0)

    lost = np.where(
        calc > fcst,
        np.where(answ > fcst, calc - answ, calc - fcst),
        0,
    ).sum()
    excess = ((calc - fcst).sum()) / fcst.sum() if fcst.sum() else 0
    return int(lost), round(float(excess), 4)


def prepare_excel_data(input_xlsx_path: Path) -> pd.DataFrame:
    """
    Читает и подготавливает данные из Excel файла.
    
    Args:
        input_xlsx_path: Путь к входному Excel файлу
    
    Returns:
        pd.DataFrame: Подготовленные данные
    """
    # Читаем данные с листа "отчет"
    try:
        df = pd.read_excel(input_xlsx_path, sheet_name="Отчет")
    except ValueError as e:
        logger.error(f"Не найден лист 'отчет' в файле {input_xlsx_path}. Ошибка: {e}")
        raise

    # Проверяем наличие обязательных колонок
    required_columns = ["Номер массовой", "Регион", "Старт", "Окончание"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Отсутствуют обязательные колонки: {missing_columns}")
        logger.error(f"Доступные колонки: {list(df.columns)}")
        raise ValueError(f"Отсутствуют колонки: {missing_columns}")

    return df


def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Парсит колонки с датами и временем.
    
    Args:
        df: DataFrame с данными
    
    Returns:
        pd.DataFrame: DataFrame с корректно распарсенными датами
    """
    # Убеждаемся что колонки дат парсятся правильно
    try:
        df["Старт"] = pd.to_datetime(df["Старт"], format="%d.%m.%Y %H:%M", errors='coerce')
        df["Окончание"] = pd.to_datetime(df["Окончание"], format="%d.%m.%Y %H:%M", errors='coerce')
    except Exception as e:
        logger.warning(f"Проблема с парсингом дат, пробуем автоматический парсинг: {e}")
        df["Старт"] = pd.to_datetime(df["Старт"], errors='coerce')
        df["Окончание"] = pd.to_datetime(df["Окончание"], errors='coerce')

    # Проверяем на наличие некорректных дат
    invalid_dates = df[df["Старт"].isna() | df["Окончание"].isna()]
    if not invalid_dates.empty:
        logger.warning(f"Найдено {len(invalid_dates)} строк с некорректными датами")
        logger.warning(f"Строки с проблемами: {invalid_dates[['Номер массовой', 'Старт', 'Окончание']].to_dict('records')}")
        df = df.dropna(subset=["Старт", "Окончание"])

    return df


def log_data_summary(df: pd.DataFrame):
    """
    Выводит сводную информацию о загруженных данных.
    
    Args:
        df: DataFrame с данными
    """
    logger.info(f"Загружено {len(df)} строк из Excel файла")
    logger.info(f"Доступные колонки: {list(df.columns)}")
    logger.info(f"Диапазон дат: {df['Старт'].min()} → {df['Окончание'].max()}")

    # Показываем первые несколько записей для проверки
    logger.info(f"Первые записи:\n{df[['Номер массовой', 'Регион', 'Старт', 'Окончание']].head(3).to_string()}")


def validate_region_in_config(region: str, config: Dict[str, Any]) -> bool:
    """
    Проверяет есть ли регион в конфигурации.
    
    Args:
        region: Название региона
        config: Конфигурация из YAML
    
    Returns:
        bool: True если регион найден в конфигурации
    """
    workload_params = config["regions"].get(region)
    
    if not workload_params:
        logger.warning(f"❌ Region '{region}' not found in YAML config → skip")
        logger.info(f"Available regions in config: {list(config['regions'].keys())}")
        return False
    
    logger.info(f"✅ Processing region '{region}' with workload parameters: {workload_params}")
    return True


def create_result_record(
    mass_number: str,
    date_str: str,
    lost_calls: int,
    excess_traffic: float
) -> Dict[str, Any]:
    """
    Создает запись результата для сохранения.
    
    Args:
        mass_number: Номер массового инцидента
        date_str: Дата в ISO формате
        lost_calls: Количество потерянных звонков
        excess_traffic: Коэффициент превышения трафика
    
    Returns:
        Dict[str, Any]: Запись результата
    """
    return {
        "Номер массовой": mass_number,
        "Дата": date_str,
        "LostCalls": lost_calls,
        "ExcessTraffic": excess_traffic,
    }


def save_results_to_csv(results: List[Dict[str, Any]], out_csv_path: Path):
    """
    Сохраняет результаты в CSV файл.
    
    Args:
        results: Список результатов
        out_csv_path: Путь к выходному CSV файлу
    """
    pd.DataFrame(results).to_csv(out_csv_path, index=False, encoding="utf-8")
    logger.success(f"Done → {out_csv_path} ({len(results)} rows)")


def process_excel_data(input_xlsx_path: Path) -> pd.DataFrame:
    """
    Полная обработка Excel данных.
    
    Args:
        input_xlsx_path: Путь к входному Excel файлу
    
    Returns:
        pd.DataFrame: Обработанные данные готовые для использования
    """
    # Читаем данные
    df = prepare_excel_data(input_xlsx_path)
    
    # Парсим даты
    df = parse_datetime_columns(df)
    
    # Выводим сводку
    log_data_summary(df)
    
    return df