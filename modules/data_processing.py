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
    Читает 2-й лист отчёта и возвращает (lost, excess),
    исключая строки 'Итого:' и любые строки, где в 'Период' не время.
    """
    df = pd.read_excel(path, sheet_name=1, header=4)  # заголовки на 5-й строке
    df.columns = [c.strip() for c in df.columns]

    # 1) Убираем строку ИТОГО и прочий «мусор» в периоде
    if "Период" in df.columns:
        mask_total = df["Период"].astype(str).str.contains("итого", case=False, na=False)
        df = df[~mask_total].copy()

    # 2) Приводим к числам (если вдруг были строки/пробелы) и заполняем NaN
    cols = ["Расчетные звонки", "Спрогнозированные звонки", "Отвеченные звонки"]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    calc = df["Расчетные звонки"].to_numpy()
    fcst = df["Спрогнозированные звонки"].to_numpy()
    answ = df["Отвеченные звонки"].to_numpy()

    # 3) РЕАЛИЗАЦИЯ ТОЧНО КАК В ТВОЕЙ ФОРМУЛЕ ПО СТРОКЕ
    lost_per_row = np.where(
        (calc - fcst) > 0,
        np.where((answ - fcst) > 0, calc - answ, (calc - answ) - (fcst - answ)),
        0
    )
    # при желании можно подстраховаться от отрицательных: lost_per_row = np.maximum(lost_per_row, 0)

    lost = int(lost_per_row.sum())

    # 4) excess как раньше: суммарный (calc - fcst) / суммарный fcst
    fcst_sum = fcst.sum()
    excess = round(float(((calc - fcst).sum()) / fcst_sum), 4) if fcst_sum else 0.0

    return lost, excess

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
    # ВАЖНО: допускаем пустое "Окончание" (незакрытые проблемы). Отбрасываем только без "Старт".
    invalid_start = df[df["Старт"].isna()]
    if not invalid_start.empty:
        logger.warning(f"Найдено {len(invalid_start)} строк без даты 'Старт' — будут исключены")
        logger.warning(
            f"Строки с проблемами: {invalid_start[['Номер массовой', 'Старт', 'Окончание']].to_dict('records')}"
        )
        df = df.dropna(subset=["Старт"]).copy()

    # Информируем о пустых 'Окончание', но НЕ исключаем их
    open_issues = df[df["Окончание"].isna()]
    if not open_issues.empty:
        logger.info(f"Обнаружено {len(open_issues)} строк без 'Окончание' — считаем их открытыми и обрабатываем")

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