"""
Модуль для управления скачиванием отчетов.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .selenium_helpers import (
    find_parameter_input,
    wait_download,
    apply_cdp_download_settings,
    prepare_download_js,
    REPORT_URL,
    switch_to_report_frame,
)
from .date_time_utils import format_time_intervals, get_time_format_variations
from .regions import setup_regions


def setup_date_range(driver, start_dt: datetime, end_dt: datetime):
    """
    Настраивает диапазон дат в форме отчета.

    Args:
        driver: WebDriver instance
        start_dt: Дата начала
        end_dt: Дата окончания
    """
    date_fmt = "%d.%m.%Y"

    # Дата от (с увеличенными паузами)
    logger.info(f"📅 Устанавливаем дату от: {start_dt.strftime(date_fmt)}")
    date_from = find_parameter_input(driver, "Дата от")
    time.sleep(2)  # Увеличили паузу
    date_from.click()
    time.sleep(2)  # Увеличили паузу
    date_from.send_keys(Keys.CONTROL, "a")
    time.sleep(2)  # Увеличили паузу
    date_from.send_keys(start_dt.strftime(date_fmt))
    time.sleep(2)  # Увеличили паузу
    date_from.send_keys(Keys.TAB)  # подтвердить дату
    time.sleep(3)  # Увеличили паузу для применения изменений
    logger.info(f"✅ Дата от установлена: {start_dt.strftime(date_fmt)}")

    # Дата до (с увеличенными паузами)
    logger.info(f"📅 Устанавливаем дату до: {end_dt.strftime(date_fmt)}")
    date_to = find_parameter_input(driver, "Дата до")
    time.sleep(2)  # Увеличили паузу
    date_to.click()
    time.sleep(2)  # Увеличили паузу
    date_to.send_keys(Keys.CONTROL, "a")  # Очистить поле
    time.sleep(2)  # Увеличили паузу
    date_to.send_keys(end_dt.strftime(date_fmt))
    time.sleep(2)  # Увеличили паузу
    date_to.send_keys(Keys.TAB)  # подтвердить дату
    time.sleep(3)  # Увеличили паузу для применения изменений
    logger.info(f"✅ Дата до установлена: {end_dt.strftime(date_fmt)}")


def setup_time_intervals(driver, start_dt: datetime, end_dt: datetime):
    """
    Настраивает временные интервалы в форме отчета.

    Args:
        driver: WebDriver instance
        start_dt: Время начала
        end_dt: Время окончания
    """
    try:
        # Получаем отформатированные временные интервалы
        start_time_str, end_time_str = format_time_intervals(start_dt, end_dt)

        logger.info(f"🕒 Исходное время: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}")
        logger.info(f"⏰ Округленное время (15-мин интервалы): {start_time_str} - {end_time_str}")
        logger.info(f"   📍 Начало округлено ВНИЗ: {start_dt.strftime('%H:%M')} → {start_time_str}")
        logger.info(f"   📍 Конец округлен ВВЕРХ: {end_dt.strftime('%H:%M')} → {end_time_str}")

        # Интервал от
        logger.info("Выбираем интервал ОТ...")
        interval_from_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//td[contains(normalize-space(.),'Интервал от')]/following-sibling::td//select"
            ))
        )

        interval_from_select = Select(interval_from_element)

        # Получаем все доступные опции для отладки
        available_options = [option.text.strip() for option in interval_from_select.options if option.text.strip()]
        logger.info(f"Доступные варианты времени ОТ: {available_options[:10]}")

        # Пробуем разные форматы времени (убираем ведущие нули для Windows)
        time_formats_to_try = get_time_format_variations(start_time_str)

        selected = False
        for time_format in time_formats_to_try:
            try:
                interval_from_select.select_by_visible_text(time_format)
                logger.info(f"✅ Выбран интервал ОТ: {time_format}")
                selected = True
                break
            except:
                continue

        if not selected:
            logger.warning(f"Не удалось выбрать время {start_time_str}, выбираем первый доступный")
            try:
                interval_from_select.select_by_index(0)
                logger.info(f"✅ Выбрана первая опция: {interval_from_select.first_selected_option.text}")
            except Exception as e:
                logger.error(f"Ошибка выбора времени ОТ: {e}")

        time.sleep(1)

        # Интервал до
        logger.info("Выбираем интервал ДО...")
        interval_to_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//td[contains(normalize-space(.),'Интервал до')]/following-sibling::td//select"
            ))
        )

        interval_to_select = Select(interval_to_element)

        # Получаем все доступные опции для отладки
        available_options_to = [option.text.strip() for option in interval_to_select.options if option.text.strip()]
        logger.info(f"Доступные варианты времени ДО: {available_options_to[:10]}")

        # Пробуем разные форматы времени (убираем ведущие нули для Windows)
        time_formats_to_try_end = get_time_format_variations(end_time_str)

        selected_end = False
        for time_format in time_formats_to_try_end:
            try:
                interval_to_select.select_by_visible_text(time_format)
                logger.info(f"✅ Выбран интервал ДО: {time_format}")
                selected_end = True
                break
            except:
                continue

        if not selected_end:
            logger.warning(f"Не удалось выбрать время {end_time_str}, выбираем последний доступный")
            try:
                # Выбираем последний элемент (максимальное время)
                interval_to_select.select_by_index(len(interval_to_select.options) - 1)
                logger.info(f"✅ Выбрана последняя опция: {interval_to_select.first_selected_option.text}")
            except Exception as e:
                logger.error(f"Ошибка выбора времени ДО: {e}")

        time.sleep(1)

        # Финальная проверка что время выбрано корректно
        try:
            current_from = interval_from_select.first_selected_option.text.strip()
            current_to = interval_to_select.first_selected_option.text.strip()
            logger.info(f"✅ ВРЕМЯ УСПЕШНО НАСТРОЕНО:")
            logger.info(f"   📍 Интервал ОТ: {current_from}")
            logger.info(f"   📍 Интервал ДО: {current_to}")
        except:
            logger.warning("⚠️ Не удалось проверить выбранное время")

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА с интервалами времени: {e}")
        logger.error("❌ ОСТАНОВКА: Без корректного времени отчет не может быть сгенерирован!")
        raise


def trigger_excel_download(driver) -> float:
    """
    Запускает скачивание Excel отчета.

    Args:
        driver: WebDriver instance

    Returns:
        float: Timestamp начала скачивания
    """
    ts = time.time()
    logger.info("🔄 Нажимаем кнопку генерации Excel отчета...")

    # УБЕЖДАЕМСЯ что кликаем именно по EXCEL кнопке, а не PDF!
    try:
        excel_button = driver.find_element(By.ID, "buttonShowExcel")
        button_text = excel_button.get_attribute("value") or excel_button.text or "N/A"
        logger.info(f"✅ Найдена кнопка Excel: ID=buttonShowExcel, текст='{button_text}'")

        # ПРИНУДИТЕЛЬНО устанавливаем нужные настройки через JavaScript
        prepare_download_js(driver)

        # ФИНАЛЬНОЕ применение CDP настроек прямо перед скачиванием
        apply_cdp_download_settings(driver)

        # Кликаем по кнопке Excel
        excel_button.click()
        logger.info("✅ Клик по кнопке Excel выполнен")

        return ts

    except Exception as e:
        logger.error(f"❌ Ошибка при поиске/клике кнопки Excel: {e}")
        # Показываем все доступные кнопки для отладки
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "input")
            button_info = []
            for btn in all_buttons:
                btn_id = btn.get_attribute("id") or "N/A"
                btn_value = btn.get_attribute("value") or "N/A"
                btn_type = btn.get_attribute("type") or "N/A"
                button_info.append(f"ID={btn_id}, value={btn_value}, type={btn_type}")
            logger.info(f"🔍 Доступные кнопки на странице: {button_info}")
        except:
            pass
        raise


def download_report(
    driver: webdriver.Chrome,
    region_ids: List[str],
    start_dt: datetime,
    end_dt: datetime,
) -> Path:
    """
    Открывает форму, выставляет фильтры, скачивает отчёт.

    Args:
        driver: WebDriver instance
        region_ids: Список ID регионов
        start_dt: Дата и время начала
        end_dt: Дата и время окончания

    Returns:
        Path: Путь к скачанному файлу
    """
    logger.info(f"🌐 Переходим на страницу отчета: {REPORT_URL}")
    driver.get(REPORT_URL)

    # ДОПОЛНИТЕЛЬНО: Повторно применяем CDP настройки на странице отчета
    apply_cdp_download_settings(driver)

    # Переходим в правильный фрейм, если он используется
    logger.info("⏳ Ждем загрузки страницы отчета (до 30с)...")
    switch_to_report_frame(driver, timeout=30)

    time.sleep(1)  # Небольшая пауза для стабильности

    # --- 1) даты / время -------------------------------------------------------
    setup_date_range(driver, start_dt, end_dt)

    # --- 2) Интервалы часов -------------------------------------------------
    setup_time_intervals(driver, start_dt, end_dt)

    # --- 3) Рабочая нагрузка (регионы) -------------------------------------------------
    logger.info("🔧 Настраиваем рабочую нагрузку...")
    if not setup_regions(driver, region_ids):
        raise Exception("Не удалось настроить регионы")

    logger.info("✅ Рабочая нагрузка настроена успешно")
    time.sleep(1)  # Пауза перед генерацией отчета

    # --- 4) Excel --------------------------------------------------------------
    logger.info("📊 Все параметры настроены, генерируем отчет...")
    ts = trigger_excel_download(driver)

    # Простое ожидание скачивания файла (без агрессивных попыток)
    logger.info("⏳ Ожидаем скачивание файла...")
    return wait_download(ts, driver=driver, timeout=60)  # Нормальный таймаут