"""
Модуль для работы с датами и временными интервалами.
"""

import pytz
from datetime import datetime, time as dtime, timedelta
from typing import List, Tuple
import pandas as pd


# === Timezone setup ===
tz_utc = pytz.UTC
tz_local = datetime.now().astimezone().tzinfo


def round_to_15_minutes(dt: datetime) -> datetime:
    """Округляет время до ближайших 15 минут."""
    minutes = dt.minute
    rounded_minutes = (minutes // 15) * 15
    return dt.replace(minute=rounded_minutes, second=0, microsecond=0)


def round_to_15_minutes_up(dt: datetime) -> datetime:
    """Округляет время вверх до ближайших 15 минут."""
    minutes = dt.minute
    if minutes % 15 == 0:
        return dt.replace(second=0, microsecond=0)
    rounded_minutes = ((minutes // 15) + 1) * 15
    if rounded_minutes >= 60:
        # Если часы переходят за 23, переносим на следующий день
        if dt.hour >= 23:
            # Переход на следующий день: 23:59 -> 00:00 следующего дня
            return (dt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return dt.replace(hour=dt.hour + 1, minute=0, second=0, microsecond=0)
    return dt.replace(minute=rounded_minutes, second=0, microsecond=0)


def windows_for_row(row) -> List[Tuple[datetime, datetime]]:
    """Разбиваем период массового инцидента на дневные окна с учетом точного времени."""
    import pandas as pd
    
    result = []
    start: datetime = row["Старт"]
    end: datetime = row["Окончание"]

    # Проверяем на NaT значения
    if pd.isna(start) or pd.isna(end):
        logger.warning(f"⚠️ Обнаружены NaT значения в датах: Старт={start}, Окончание={end}")
        return result

    # Если инцидент в рамках одного дня
    if start.date() == end.date():
        result.append((start, end))
        return result

    current_date = start.date()

    while current_date <= end.date():
        if current_date == start.date():
            # Первый день: с точного времени начала до 23:59:59
            window_start = start
            window_end = datetime.combine(current_date, dtime(23, 59, 59))
            result.append((window_start, window_end))
        elif current_date == end.date():
            # Последний день: с 00:00:00 до точного времени окончания
            window_start = datetime.combine(current_date, dtime(0, 0, 0))
            window_end = end
            result.append((window_start, window_end))
        else:
            # Полные дни: с 00:00:00 до 23:59:59
            window_start = datetime.combine(current_date, dtime(0, 0, 0))
            window_end = datetime.combine(current_date, dtime(23, 59, 59))
            result.append((window_start, window_end))

        current_date += timedelta(days=1)

    return result


def prepare_datetime_for_report(dt: datetime) -> datetime:
    """
    Подготавливает datetime для отправки в отчет.
    Преобразует в datetime без изменения часового пояса.
    Время уже в МСК как в Excel файле - НЕ МЕНЯЕМ часовой пояс!
    """
    # Преобразуем в datetime без изменения часового пояса
    dt = pd.to_datetime(dt)

    # Убираем часовую информацию если есть (оставляем только время МСК)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt


def format_time_intervals(start_dt: datetime, end_dt: datetime) -> Tuple[str, str]:
    """
    Форматирует временные интервалы для отчета.
    Округляет время до 15-минутных интервалов.

    Returns:
        Tuple[str, str]: (start_time_str, end_time_str) в формате HH:MM
    """
    # Округляем время до 15-минутных интервалов
    start_rounded = round_to_15_minutes(start_dt)
    end_rounded = round_to_15_minutes_up(end_dt)

    start_time_str = start_rounded.strftime('%H:%M')
    end_time_str = end_rounded.strftime('%H:%M')

    return start_time_str, end_time_str


def get_time_format_variations(time_str: str) -> List[str]:
    """
    Возвращает различные варианты форматирования времени для совместимости.
    Убираем ведущие нули для Windows совместимости.

    Args:
        time_str: Время в формате HH:MM (например, "01:45")

    Returns:
        List[str]: Список вариантов форматирования времени
    """
    # Парсим время
    hour, minute = map(int, time_str.split(':'))

    return [
        time_str,  # 01:45
        time_str.lstrip('0').replace(':0', ':'),  # 1:45
        f"{hour}:{minute:02d}",  # без ведущих нулей в часах: 1:45
        f"{hour}:{minute}"  # совсем без нулей: 1:45
    ]