#!/usr/bin/env python3
"""wfm_single.py — one‑file версия скрипта выгрузки «потерянных» и «превышения» из Teleopti.
python main.py test.xlsx --out-csv result.csv --no-headless

"""
from __future__ import annotations

import sys
import time
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from typing import List, Tuple

import os

import pytz
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_parameter_input(driver, label: str, timeout: int = 10):
    """
    Находит <input type="text"> в том же <tr>, где <td> содержит label.
    """
    xpath = (
        f"//td[contains(normalize-space(.), '{label}')]"
        "/following-sibling::td"
        "//input[@type='text']"
    )

    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
    except Exception as e:
        logger.error(f"❌ Не удалось найти поле '{label}'")
        logger.info("🔍 Попытка найти все доступные поля...")

        # Показываем все доступные поля для отладки
        try:
            all_td_elements = driver.find_elements(By.TAG_NAME, "td")
            field_labels = [td.text.strip() for td in all_td_elements if td.text.strip() and len(td.text.strip()) < 50]
            logger.info(f"Доступные поля на странице: {field_labels[:20]}")
        except:
            logger.warning("Не удалось получить список полей")

        raise e

# === timezone setup ===
tz_utc   = pytz.UTC
tz_local = datetime.now().astimezone().tzinfo

# ваш корпоративный прокси
os.environ['HTTP_PROXY']  = 'http://fg-proxy.corp.tele2.ru:8080'
os.environ['HTTPS_PROXY'] = 'http://fg-proxy.corp.tele2.ru:8080'

# обязательно — не проксировать локалхост!
os.environ['NO_PROXY']   = 'localhost,127.0.0.1'
os.environ['no_proxy']   = 'localhost,127.0.0.1'


import pandas as pd
import numpy as np
import argparse
import yaml
from dateutil import tz
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# --- Selenium helpers ------------------------------------------------------

REPORT_URL = (
    "http://t2ru-optiweb-02/TeleoptiWFM/Web/Areas/Reporting/"
    "Index.aspx?ReportID=8d8544e4-6b24-4c1c-8083-cbe7522dd0e0&UseOpenXml=true"
)


def get_driver(headless: bool = True) -> webdriver.Chrome:
    """Создает и настраивает Chrome WebDriver с автоматической установкой драйвера."""
    opts = webdriver.ChromeOptions()

    # Основные опции
    # Включаем headless режим для стабильности и обхода защиты (как предложил пользователь)
    if headless:
        opts.add_argument("--headless=new")
        logger.info("🔒 Включен headless режим для стабильности и обхода защиты")
    opts.add_argument("--auth-server-whitelist=*")  # NTLM/SSO
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")

    # Дополнительные опции для Chrome 138+
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-features=TranslateUI")
    opts.add_argument("--disable-ipc-flooding-protection")

    # КРИТИЧЕСКИ ВАЖНЫЕ настройки для ПРИНУДИТЕЛЬНОГО скачивания Excel файлов
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR.absolute()),
        "download.prompt_for_download": False,  # НЕ спрашивать где сохранить
        "download.directory_upgrade": True,

        # КЛЮЧЕВЫЕ настройки для обхода блокировок (предложены пользователем)
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,  # Включаем но отключаем защиту
        "safebrowsing.disable_download_protection": True,  # КРИТИЧНО для Excel!

        # Автоматические скачивания
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,

        # Дополнительные настройки для Excel
        "plugins.always_open_pdf_externally": True,  # PDF открывать внешне
        "download.open_pdf_in_system_reader": True,
        "plugins.plugins_disabled": ["Chrome PDF Viewer"]  # Отключить встроенный PDF
    }
    opts.add_experimental_option("prefs", prefs)

    # Убираем детекцию автоматизации
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    # дополнительные флаги для отключения блокировок
    opts.add_argument("--safebrowsing-disable-download-protection")
    opts.add_argument("--disable-extensions")

    # КРИТИЧЕСКИ ВАЖНО: флаги для обхода блокировок скачивания
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")  # Предложено пользователем
    opts.add_argument("--ignore-certificate-errors")      # Предложено пользователем
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_argument("--trusted-download-sources=*")
    opts.add_argument("--disable-download-quarantine")
    opts.add_argument("--allow-downloads-from-secure-origin")
    opts.add_argument("--disable-safebrowsing")
    opts.add_argument("--disable-safebrowsing-disable-download-protection")

    # ДОПОЛНИТЕЛЬНЫЕ флаги для принудительного разрешения скачивания
    opts.add_argument("--allow-downloads")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-extensions-file-access-check")
    opts.add_argument("--disable-file-system")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument("--disable-download-protection")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--test-type")

    try:
        # Автоматическая установка ChromeDriver для Chrome 138+
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

        # Убираем индикатор автоматизации
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # КРИТИЧЕСКИ ВАЖНО: Настройка поведения скачивания через CDP (предложено пользователем)
        logger.info("🔧 Настраиваем скачивание через Chrome DevTools Protocol...")
        try:
            params = {
                "behavior": "allow",              # Разрешаем скачивание без вопросов
                "downloadPath": str(DOWNLOAD_DIR.absolute())  # Путь, куда скачивать файлы
            }
            driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
            logger.info(f"✅ CDP настройки скачивания применены: {DOWNLOAD_DIR}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось применить CDP настройки: {e}")
            logger.info("📝 Продолжаем с обычными настройками Chrome...")

        driver.set_window_size(1600, 1000)
        logger.info(f"Chrome WebDriver инициализирован успешно")
        return driver

    except Exception as e:
        logger.error(f"Ошибка инициализации Chrome WebDriver: {e}")
        logger.info("Попробуйте:")
        logger.info("1. Обновить Chrome до последней версии")
        logger.info("2. Перезапустить скрипт (webdriver-manager попробует снова)")
        logger.info("3. Очистить кэш: rm -rf ~/.wdm/ (Mac/Linux) или del %USERPROFILE%\\.wdm\\ (Windows)")
        raise




def wait_download(start_ts: float, timeout: int = 60, driver=None) -> Path:
    """Ждём появления xlsx в DOWNLOAD_DIR новее start_ts."""
    deadline = time.time() + timeout
    check_count = 0
    last_status_time = time.time()

    logger.info(f"🔍 Ищем новые .xlsx файлы в папке: {DOWNLOAD_DIR}")

    while time.time() < deadline:
        # ПРОВЕРЯЕМ ИМЕННО .XLSX файлы (НЕ PDF!)
        xlsx_files = list(DOWNLOAD_DIR.glob("*.xlsx"))
        for f in xlsx_files:
            if f.stat().st_mtime > start_ts:
                time.sleep(1)
                logger.info(f"✅ EXCEL файл скачан: {f.name} (размер: {f.stat().st_size} байт)")
                return f

        # ВАЖНО: Проверяем не скачался ли PDF вместо Excel!
        pdf_files = list(DOWNLOAD_DIR.glob("*.pdf"))
        for f in pdf_files:
            if f.stat().st_mtime > start_ts:
                logger.error(f"❌ ОШИБКА: Скачан PDF файл вместо Excel: {f.name}")
                logger.error("❌ Это означает что кликнули по кнопке PDF, а не Excel!")
                logger.error("💡 Проверьте что кликаете именно по кнопке 'buttonShowExcel'")
                # НЕ возвращаем PDF файл - продолжаем ждать Excel

        # Показываем статус каждые 10 секунд
        if time.time() - last_status_time > 10:
            logger.info(f"⏳ Ожидание скачивания... осталось {int(deadline - time.time())} сек. Найдено .xlsx файлов: {len(xlsx_files)}")
            last_status_time = time.time()

            # Показываем что есть в папке
            all_files = list(DOWNLOAD_DIR.glob("*"))
            if all_files:
                recent_files = [f.name for f in all_files if f.stat().st_mtime > start_ts - 60]  # за последнюю минуту
                if recent_files:
                    logger.info(f"📁 Недавние файлы в папке: {recent_files}")

        # Проверяем есть ли активные диалоги
        check_count += 1
        if check_count % 3 == 0 and driver:
            try:
                alert = driver.switch_to.alert
                logger.info(f"🚨 Найден alert: {alert.text}")
                alert.accept()
                logger.info("✅ Alert принят")
            except:
                pass  # Нет алертов

        time.sleep(1)

    logger.error(f"❌ Timeout скачивания файла. Проверьте папку {DOWNLOAD_DIR}")
    # Показываем что есть в папке для отладки
    all_files = list(DOWNLOAD_DIR.glob("*"))
    logger.info(f"📁 Все файлы в папке: {[f.name for f in all_files]}")

    raise TimeoutError("Download timeout")


def download_report(
    driver: webdriver.Chrome,
    region_ids: List[str],
    start_dt: datetime,
    end_dt: datetime,
) -> Path:
    """Открывает форму, выставляет фильтры, скачивает отчёт."""
    logger.info(f"🌐 Переходим на страницу отчета: {REPORT_URL}")
    driver.get(REPORT_URL)

    # ДОПОЛНИТЕЛЬНО: Повторно применяем CDP настройки на странице отчета
    logger.info("🔧 Повторно применяем CDP настройки скачивания на странице отчета...")
    try:
        params = {
            "behavior": "allow",              # Разрешаем скачивание без вопросов
            "downloadPath": str(DOWNLOAD_DIR.absolute())  # Путь, куда скачивать файлы
        }
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        logger.info("✅ CDP настройки повторно применены на странице отчета")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось повторно применить CDP настройки: {e}")

    # Ждем полной загрузки страницы (сокращенный таймаут)
    wait = WebDriverWait(driver, 10)  # Сократили с 30 до 10 секунд
    logger.info("⏳ Ждем загрузки страницы...")

    # Проверяем что страница загрузилась (ищем любую таблицу с параметрами)
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        logger.info("✅ Страница загружена")
    except Exception as e:
        logger.error(f"❌ Страница не загрузилась: {e}")
        # Показываем что есть на странице
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text[:500]
            logger.info(f"📄 Содержимое страницы: {page_text}")
        except:
            pass
        raise

    time.sleep(2)  # Дополнительная пауза для полной загрузки

    # --- 1) даты / время -------------------------------------------------------
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

    # --- 2) Интервалы часов -------------------------------------------------
    def round_to_15_minutes(dt):
        """Округляет время до ближайших 15 минут."""
        minutes = dt.minute
        rounded_minutes = (minutes // 15) * 15
        return dt.replace(minute=rounded_minutes, second=0, microsecond=0)

    def round_to_15_minutes_up(dt):
        """Округляет время вверх до ближайших 15 минут."""
        minutes = dt.minute
        if minutes % 15 == 0:
            return dt.replace(second=0, microsecond=0)
        rounded_minutes = ((minutes // 15) + 1) * 15
        if rounded_minutes >= 60:
            # Если часы переходят за 23, переносим на следующий день
            if dt.hour >= 23:
                # Переход на следующий день: 23:59 -> 00:00 следующего дня
                from datetime import timedelta
                return (dt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                return dt.replace(hour=dt.hour + 1, minute=0, second=0, microsecond=0)
        return dt.replace(minute=rounded_minutes, second=0, microsecond=0)

    try:
        # Округляем время до 15-минутных интервалов
        start_rounded = round_to_15_minutes(start_dt)
        end_rounded = round_to_15_minutes_up(end_dt)

        start_time_str = start_rounded.strftime('%H:%M')
        end_time_str = end_rounded.strftime('%H:%M')

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
        time_formats_to_try = [
            start_time_str,  # 01:45
            start_time_str.lstrip('0').replace(':0', ':'),  # 1:45
            f"{start_rounded.hour}:{start_rounded.minute:02d}",  # без ведущих нулей в часах: 1:45
            f"{start_rounded.hour}:{start_rounded.minute}"  # совсем без нулей: 1:45
        ]

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
        time_formats_to_try_end = [
            end_time_str,  # 03:00
            end_time_str.lstrip('0').replace(':0', ':'),  # 3:00
            f"{end_rounded.hour}:{end_rounded.minute:02d}",  # без ведущих нулей в часах: 3:00
            f"{end_rounded.hour}:{end_rounded.minute}"  # совсем без нулей: 3:0
        ]

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

    # --- 2) Рабочая нагрузка (регионы) -------------------------------------------------
    try:
        logger.info(f"🔍 Настраиваем рабочую нагрузку для регионов: {region_ids}")

        # Находим левый селект (доступные опции) для рабочей нагрузки
        logger.info("🔍 Ищем поле 'Рабочая нагрузка'...")

        try:
            workload_left_select = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][1]"
                ))
            )
            logger.info("✅ Найден левый список рабочей нагрузки")
        except Exception as e:
            logger.error(f"❌ Не удалось найти поле 'Рабочая нагрузка': {e}")

            # Показываем все доступные поля на странице
            try:
                all_td = driver.find_elements(By.TAG_NAME, "td")
                field_names = [td.text.strip() for td in all_td if td.text.strip() and len(td.text.strip()) < 100]
                logger.info(f"📋 Доступные поля на странице: {field_names}")
            except:
                logger.warning("Не удалось получить список полей")
            raise

        # Ждем загрузки опций в списке
        logger.info("⏳ Ждем загрузки опций в списке рабочей нагрузки...")

        # Ждем пока в списке появятся опции
        for i in range(10):  # макс 10 секунд
            options = workload_left_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:  # больше чем пустая опция
                logger.info(f"✅ Загружено {len(options)} опций")
                break
            time.sleep(1)
            logger.info(f"⏳ Ждем загрузки опций... ({i+1}/10)")
        else:
            logger.warning("⚠️ Список опций не загрузился полностью")

        time.sleep(1)  # Дополнительная пауза

        # СНАЧАЛА ОЧИЩАЕМ ПРАВЫЙ СПИСОК от старых регионов
        # ⚠️ КРИТИЧЕСКИ ВАЖНО: НЕ НАЖАТЬ НА ВЕРХНЮЮ КНОПКУ (навыки)!
        # НАЙТИ ВСЕ КНОПКИ, ПРОПУСТИТЬ ПЕРВУЮ, КЛИКНУТЬ ВТОРУЮ!
        try:
            logger.info("🧹 Очищаем правый список от старых регионов...")
            logger.info("🔍 Ищем ВСЕ кнопки очистки на странице...")

            # Находим ВСЕ кнопки с src="images/left_all_light.gif"
            all_clear_buttons = driver.find_elements(
                By.XPATH,
                "//img[contains(@src, 'images/left_all_light.gif')]"
            )

            logger.info(f"✅ Найдено кнопок очистки: {len(all_clear_buttons)}")

            if len(all_clear_buttons) >= 2:
                # ПРОПУСКАЕМ ПЕРВУЮ (навыки), КЛИКАЕМ ВТОРУЮ (рабочая нагрузка)
                logger.info("🚨 КРИТИЧНО: Пропускаем первую кнопку (навыки)...")
                logger.info("✅ Кликаем по ВТОРОЙ кнопке (рабочая нагрузка)...")

                workload_clear_button = all_clear_buttons[1]  # Вторая кнопка (индекс 1)
                workload_clear_button.click()
                time.sleep(2)  # Пауза после очистки
                logger.info("✅ Правый список рабочей нагрузки очищен (ВТОРАЯ кнопка)")
            elif len(all_clear_buttons) == 1:
                logger.warning("⚠️ Найдена только одна кнопка очистки - возможно структура изменилась")
                logger.info("🔄 Пробуем кликнуть единственную кнопку...")
                all_clear_buttons[0].click()
                time.sleep(2)
                logger.info("✅ Кликнули по единственной найденной кнопке")
            else:
                logger.error("❌ Кнопки очистки не найдены!")
                raise Exception("Кнопки очистки не найдены")

        except Exception as e:
            logger.warning(f"⚠️ Не удалось найти кнопки очистки: {e}")
            # Пробуем альтернативный поиск конкретно в секции "Рабочая нагрузка"
            try:
                logger.info("🔄 Пробуем поиск ТОЛЬКО в секции 'Рабочая нагрузка'...")
                clear_button = driver.find_element(
                    By.XPATH,
                    "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//img[contains(@src, 'left_all')]"
                )
                clear_button.click()
                time.sleep(2)
                logger.info("✅ Правый список очищен (альтернативный поиск)")
            except Exception as e2:
                logger.warning(f"⚠️ Альтернативный способ очистки тоже не сработал: {e2}")
                logger.warning("⚠️ Продолжаем без очистки - будем добавлять к существующим регионам")

        # ПОСЛЕ ОЧИСТКИ НУЖНО ЗАНОВО НАЙТИ ЛЕВЫЙ СПИСОК!
        # Элемент workload_left_select мог стать "stale" после очистки
        logger.info("🔄 Заново ищем левый список после очистки...")
        time.sleep(1)  # Дополнительная пауза для стабилизации DOM
        try:
            workload_left_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][1]"
                ))
            )
            logger.info("✅ Левый список найден заново после очистки")
        except Exception as e:
            logger.error(f"❌ Не удалось заново найти левый список: {e}")
            raise

        # Теперь покажем все доступные опции для отладки
        available_options = workload_left_select.find_elements(By.TAG_NAME, "option")
        logger.info(f"📋 Всего доступно опций: {len(available_options)}")
        if available_options:
            logger.info(f"📋 Первые 10 опций: {[(opt.get_dom_attribute('value'), opt.text.strip()) for opt in available_options[:10]]}")

            # Показываем ВСЕ доступные ID для сравнения с конфигом
            all_values = [opt.get_dom_attribute('value') for opt in available_options if opt.get_dom_attribute('value')]
            logger.info(f"📋 Все доступные ID регионов: {sorted(all_values)}")
        else:
            logger.error("❌ Список рабочей нагрузки пустой!")

        for region_id in region_ids:
            try:
                logger.info(f'🎯 Ищем регион с ID: {region_id}')

                # Ищем опцию по value (ID региона)
                opt = workload_left_select.find_element(By.XPATH, f".//option[@value='{region_id}']")
                region_name = opt.text.strip()
                logger.info(f'✅ Найден регион: {region_id} = "{region_name}"')

                # Способ 1: Пробуем двойной клик через ActionChains
                try:
                    logger.info(f'🖱️ Пробуем двойной клик ActionChains по региону {region_id}')
                    driver.execute_script("arguments[0].scrollIntoView(true);", opt)
                    time.sleep(0.5)
                    ActionChains(driver).move_to_element(opt).double_click().perform()
                    time.sleep(1)
                    logger.info(f'✅ Двойной клик выполнен для {region_id}')
                except Exception as e:
                    logger.warning(f"⚠️ Двойной клик не сработал: {e}")

                    # Способ 2: Пробуем через JavaScript
                    try:
                        logger.info(f'🖱️ Пробуем JavaScript двойной клик для {region_id}')
                        driver.execute_script("""
                            var opt = arguments[0];
                            var event = new MouseEvent('dblclick', { bubbles: true, cancelable: true });
                            opt.dispatchEvent(event);
                        """, opt)
                        time.sleep(1)
                        logger.info(f'✅ JavaScript двойной клик выполнен для {region_id}')
                    except Exception as e2:
                        logger.error(f"❌ JavaScript клик тоже не сработал: {e2}")
                        continue

            except NoSuchElementException:
                logger.warning(f"❌ Регион с ID '{region_id}' НЕ НАЙДЕН в списке рабочей нагрузки")

                # Показываем ВСЕ доступные опции для отладки
                all_values = [opt.get_dom_attribute('value') for opt in available_options if opt.get_dom_attribute('value')]
                logger.warning(f"Доступные ID: {sorted(all_values)}")

                # Ищем похожие ID (может быть разные форматы)
                similar = [v for v in all_values if region_id in v or v in region_id]
                if similar:
                    logger.info(f"Возможно похожие ID: {similar}")

                continue

            except Exception as e:
                logger.error(f"❌ Ошибка при работе с регионом {region_id}: {e}")
                continue

        # Проверяем что что-то было выбрано
        time.sleep(1)
        try:
            # Правый список для проверки
            workload_right_select = driver.find_element(
                By.XPATH,
                "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][2]"
            )
            selected_regions = workload_right_select.find_elements(By.TAG_NAME, "option")

            if len(selected_regions) > 0:
                selected_names = [opt.text.strip() for opt in selected_regions]
                selected_ids = [opt.get_dom_attribute('value') for opt in selected_regions]
                logger.info(f"✅ РЕГИОНЫ УСПЕШНО ВЫБРАНЫ:")
                logger.info(f"   📍 Количество: {len(selected_regions)}")
                logger.info(f"   📍 Названия: {selected_names}")
                logger.info(f"   📍 ID: {selected_ids}")
            else:
                logger.error(f"❌ РЕГИОНЫ НЕ ВЫБРАНЫ! Правый список пустой!")
                logger.error(f"❌ Ожидали регионы: {region_ids}")

        except Exception as e:
            logger.error(f"❌ Не удалось проверить правый список: {e}")
            logger.warning("⚠️ Продолжаем без проверки регионов")

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА с рабочей нагрузкой: {e}")
        raise

    time.sleep(1)  # Пауза перед генерацией отчета

    # --- Excel --------------------------------------------------------------
    ts = time.time()
    logger.info("🔄 Нажимаем кнопку генерации Excel отчета...")

    # УБЕЖДАЕМСЯ что кликаем именно по EXCEL кнопке, а не PDF!
    try:
        excel_button = driver.find_element(By.ID, "buttonShowExcel")
        button_text = excel_button.get_attribute("value") or excel_button.text or "N/A"
        logger.info(f"✅ Найдена кнопка Excel: ID=buttonShowExcel, текст='{button_text}'")

        # ПРИНУДИТЕЛЬНО устанавливаем нужные настройки через JavaScript
        driver.execute_script("""
            // Принудительно отключаем блокировки скачивания
            window.alert = function() { return true; };
            window.confirm = function() { return true; };
            window.prompt = function() { return true; };

            // Принудительно разрешаем скачивание
            if (window.chrome && window.chrome.downloads) {
                window.chrome.downloads.setShelfEnabled(true);
            }
        """)

        # ФИНАЛЬНОЕ применение CDP настроек прямо перед скачиванием
        logger.info("🔧 Финальное применение CDP настроек перед скачиванием...")
        try:
            params = {
                "behavior": "allow",              # Разрешаем скачивание без вопросов
                "downloadPath": str(DOWNLOAD_DIR.absolute())  # Путь, куда скачивать файлы
            }
            driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
            logger.info("✅ Финальные CDP настройки применены перед скачиванием")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось применить финальные CDP настройки: {e}")

        # Кликаем по кнопке Excel
        excel_button.click()
        logger.info("✅ Клик по кнопке Excel выполнен")

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

    # Простое ожидание скачивания файла (без агрессивных попыток)
    logger.info("⏳ Ожидаем скачивание файла...")
    return wait_download(ts, driver=driver, timeout=60)  # Нормальный таймаут

# --- Data processing -------------------------------------------------------


def calc_metrics(path: Path) -> Tuple[int, float]:
    """Читает 2‑й лист отчёта и возвращает (lost, excess)."""
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

# --- Main job --------------------------------------------------------------


def windows_for_row(row) -> List[Tuple[datetime, datetime]]:
    """Разбиваем период массового инцидента на дневные окна с учетом точного времени."""
    result = []
    start: datetime = row["Старт"]
    end: datetime = row["Окончание"]

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


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="WFM script for extracting lost calls and excess traffic from Teleopti")
    parser.add_argument("input_xlsx", help="Файл Power Query (Свод.xlsx)")
    parser.add_argument("--yaml-cfg", help="region_skills.yml", default=None)
    parser.add_argument("--out-csv", help="Файл вывода", default="wfm_metrics_daily.csv")
    parser.add_argument("--headless", help="Запуск в headless режиме", action="store_true", default=True)
    parser.add_argument("--no-headless", help="Запуск с видимым браузером", action="store_true")
    parser.add_argument("--with-skills", help="Включить работу с навыками (добавление без очистки)", action="store_true")

    args = parser.parse_args()

    input_xlsx_path = Path(args.input_xlsx)
    yaml_path = Path(args.yaml_cfg) if args.yaml_cfg else BASE_DIR / "region_skills.yml"
    out_csv_path = Path(args.out_csv)
    headless = args.headless and not args.no_headless

    cfg = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    # Подготавливаем навыки, если включен флаг --with-skills
    skills_ids = None
    if args.with_skills:
        logger.info("🎯 Включена работа с навыками (флаг --with-skills)")

        # Собираем все навыки из конфига в один плоский список
        skills_ids = []
        skills_config = cfg.get("skills", {})

        for skill_name, ids_list in skills_config.items():
            if ids_list and isinstance(ids_list, list):
                skills_ids.extend(ids_list)
                logger.info(f"   📍 Навык '{skill_name}': {ids_list}")

        logger.info(f"✅ Всего навыков для добавления: {len(skills_ids)}")
        logger.info(f"   🔢 ID навыков: {skills_ids}")
    else:
        logger.info("ℹ️ Работа с навыками отключена (добавьте флаг --with-skills для включения)")

    # Читаем данные с листа "отчет"
    try:
        df = pd.read_excel(input_xlsx_path, sheet_name="Отчет")
    except ValueError as e:
        logger.error(f"Не найден лист 'отчет' в файле {input_xlsx_path}. Ошибка: {e}")
        return

    # Проверяем наличие обязательных колонок
    required_columns = ["Номер массовой", "Регион", "Старт", "Окончание"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Отсутствуют обязательные колонки: {missing_columns}")
        logger.error(f"Доступные колонки: {list(df.columns)}")
        return

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

    logger.info(f"Загружено {len(df)} строк из Excel файла")
    logger.info(f"Доступные колонки: {list(df.columns)}")
    logger.info(f"Диапазон дат: {df['Старт'].min()} → {df['Окончание'].max()}")

    # Показываем первые несколько записей для проверки
    logger.info(f"Первые записи:\n{df[['Номер массовой', 'Регион', 'Старт', 'Окончание']].head(3).to_string()}")

    # tz_local = tz.gettz(cfg.get("timezone", "Europe/Moscow"))  # НЕ НУЖЕН - время остается как в Excel (МСК)

    driver = get_driver(headless=headless)
    results = []

    # --- НАВЫКИ: Добавляем ОДИН РАЗ В НАЧАЛЕ (если включены) ----------------------------
    if skills_ids:
        logger.info(f"🎯 Настраиваем навыки (БЕЗ ОЧИСТКИ): {skills_ids}")
        logger.info("🔍 Переходим на страницу отчета для настройки навыков...")

        # Переходим на страницу отчета для настройки навыков
        driver.get(REPORT_URL)

        # Применяем CDP настройки
        logger.info("🔧 Применяем CDP настройки скачивания...")
        try:
            params = {
                "behavior": "allow",
                "downloadPath": str(DOWNLOAD_DIR.absolute())
            }
            driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
            logger.info("✅ CDP настройки применены")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось применить CDP настройки: {e}")

        # Ждем загрузки страницы (простое ожидание)
        logger.info("⏳ Ждем загрузки страницы...")
        time.sleep(5)  # Просто ждем 5 секунд

        # Показываем диагностику что загрузилось
        try:
            logger.info("🔍 Диагностика содержимого страницы...")
            logger.info(f"✅ Title: {driver.title}")
            logger.info(f"✅ URL: {driver.current_url}")

            # Ищем основные элементы
            body_elements = driver.find_elements(By.TAG_NAME, "body")
            div_elements = driver.find_elements(By.TAG_NAME, "div")
            form_elements = driver.find_elements(By.TAG_NAME, "form")
            table_elements = driver.find_elements(By.TAG_NAME, "table")
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            select_elements = driver.find_elements(By.TAG_NAME, "select")

            logger.info(f"📍 Найдено элементов:")
            logger.info(f"   <body>: {len(body_elements)}")
            logger.info(f"   <div>: {len(div_elements)}")
            logger.info(f"   <form>: {len(form_elements)}")
            logger.info(f"   <table>: {len(table_elements)}")
            logger.info(f"   <input>: {len(input_elements)}")
            logger.info(f"   <select>: {len(select_elements)}")

            if len(body_elements) > 0 and len(div_elements) > 0:
                logger.info("✅ Страница загружена (есть основные элементы)")
            else:
                logger.warning("⚠️ Страница может быть не полностью загружена")

        except Exception as e:
            logger.warning(f"⚠️ Ошибка диагностики: {e}")

        logger.info("✅ Продолжаем к поиску навыков...")

        try:
            # Находим левый селект для навыков (верхний блок)
            logger.info("🔍 Ищем поле 'Навыки'...")

            try:
                skills_left_select = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][1]"
                    ))
                )
                logger.info("✅ Найден левый список навыков")
            except Exception as e:
                logger.error(f"❌ Не удалось найти поле 'Навыки': {e}")
                logger.error("❌ ОСТАНОВКА: Навыки обязательны при флаге --with-skills!")
                raise

            # Выбираем навыки по ID (БЕЗ ОЧИСТКИ правого списка)
            successfully_added = 0

            for skill_id in skills_ids:
                try:
                    logger.info(f"🎯 Выбираем навык ID: {skill_id}")

                    # Находим опцию с нужным value
                    skill_option = skills_left_select.find_element(
                        By.XPATH, f".//option[@value='{skill_id}']"
                    )
                    skill_name = skill_option.text.strip()
                    logger.info(f"   📍 Найден навык: {skill_name} (ID: {skill_id})")

                    # Аналогично регионам: двойной клик для перемещения в правый список
                    logger.info(f"   🔄 Двойной клик для переноса навыка...")
                    ActionChains(driver).double_click(skill_option).perform()
                    time.sleep(1.5)  # Увеличенная пауза для надежности

                    # Проверяем что навык перенесся (попробуем найти его в правом списке)
                    try:
                        skills_right_select = driver.find_element(
                            By.XPATH,
                            "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][2]"
                        )
                        # Проверяем есть ли опция с этим ID в правом списке
                        right_option = skills_right_select.find_element(
                            By.XPATH, f".//option[@value='{skill_id}']"
                        )
                        logger.info(f"✅ Навык {skill_name} успешно перенесен в правый список")
                        successfully_added += 1
                    except:
                        logger.error(f"❌ Навык {skill_name} НЕ ПЕРЕНЕСЕН в правый список!")
                        # НЕ продолжаем если навык не перенесся
                        raise Exception(f"Критическая ошибка: навык {skill_name} (ID: {skill_id}) не был добавлен")

                except Exception as e:
                    logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при добавлении навыка ID {skill_id}: {e}")
                    logger.error("❌ ОСТАНОВКА: Все навыки должны быть добавлены перед продолжением!")
                    raise

            logger.info(f"📊 Успешно добавлено навыков: {successfully_added}/{len(skills_ids)}")

            # Проверяем что навыки действительно попали в правый список
            logger.info("🔍 Проверяем правый список навыков...")
            try:
                skills_right_select = driver.find_element(
                    By.XPATH,
                    "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][2]"
                )

                # Получаем выбранные навыки
                selected_options = skills_right_select.find_elements(By.TAG_NAME, "option")

                if selected_options:
                    selected_skills = []
                    selected_ids = []
                    for opt in selected_options:
                        skill_value = opt.get_dom_attribute("value") or opt.get_attribute("value")
                        skill_text = opt.text.strip()
                        selected_skills.append(skill_text)
                        selected_ids.append(skill_value)

                    logger.info(f"✅ В правом списке навыков: {len(selected_skills)} навыков")
                    logger.info(f"   📍 Названия: {selected_skills}")
                    logger.info(f"   📍 ID: {selected_ids}")

                    # КРИТИЧЕСКАЯ ПРОВЕРКА: все ли навыки добавлены?
                    if len(selected_skills) != len(skills_ids):
                        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не все навыки добавлены!")
                        logger.error(f"   Ожидали: {len(skills_ids)} навыков: {skills_ids}")
                        logger.error(f"   Получили: {len(selected_skills)} навыков: {selected_ids}")
                        logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без всех навыков!")
                        raise Exception(f"Не все навыки добавлены: {len(selected_skills)}/{len(skills_ids)}")

                    # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: все ли нужные ID присутствуют?
                    missing_skills = [skill_id for skill_id in skills_ids if skill_id not in selected_ids]
                    if missing_skills:
                        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Отсутствуют навыки с ID: {missing_skills}")
                        logger.error(f"   Ожидали: {skills_ids}")
                        logger.error(f"   Получили: {selected_ids}")
                        logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без нужных навыков!")
                        raise Exception(f"Отсутствуют навыки с ID: {missing_skills}")

                    logger.info("✅ ВСЕ навыки успешно добавлены - продолжаем к обработке данных!")

                else:
                    logger.error(f"❌ НАВЫКИ НЕ ВЫБРАНЫ! Правый список пустой!")
                    logger.error(f"❌ Ожидали навыки: {skills_ids}")
                    logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без навыков!")
                    raise Exception("Правый список навыков пустой - все навыки должны быть добавлены")

            except Exception as e:
                logger.error(f"❌ Не удалось проверить правый список навыков: {e}")
                logger.error("❌ ОСТАНОВКА: Невозможно продолжать без проверки навыков!")
                raise

        except Exception as e:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при настройке навыков: {e}")
            logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ работать без навыков!")
            raise

    logger.info("🚀 Начинаем обработку данных из Excel...")

    for idx, row in df.iterrows():
        region = row["Регион"]
        logger.info(f"🔄 Обрабатываем строку #{idx}: {row['Номер массовой']} - {region}")

        # Ищем соответствие региона в конфигурации
        workload_params = cfg["regions"].get(region)

        if not workload_params:
            logger.warning(f"❌ Region '{region}' not found in YAML config → skip")
            logger.info(f"Available regions in config: {list(cfg['regions'].keys())}")
            continue

        logger.info(f"✅ Processing region '{region}' with workload parameters: {workload_params}")

        # ОТЛАДКА: Показываем исходные времена из Excel
        logger.info(f"📅 Исходные данные из Excel:")
        logger.info(f"   Старт: {row['Старт']} (тип: {type(row['Старт'])})")
        logger.info(f"   Окончание: {row['Окончание']} (тип: {type(row['Окончание'])})")

        # Получаем все временные окна для этой строки
        time_windows = list(windows_for_row(row))
        logger.info(f"📊 Создано временных окон: {len(time_windows)}")

        for window_idx, (win_start, win_end) in enumerate(time_windows):
            logger.info(f"🔸 Обрабатываем окно #{window_idx + 1}/{len(time_windows)}")
            logger.info(f"🕒 Временное окно (исходное):")
            logger.info(f"   win_start: {win_start} (тип: {type(win_start)})")
            logger.info(f"   win_end: {win_end} (тип: {type(win_end)})")

            # Преобразуем в datetime без изменения часового пояса
            # Время уже в МСК как в Excel файле - НЕ МЕНЯЕМ часовой пояс!
            win_start = pd.to_datetime(win_start)
            win_end = pd.to_datetime(win_end)

            # Убираем часовую информацию если есть (оставляем только время МСК)
            if win_start.tzinfo is not None:
                win_start = win_start.replace(tzinfo=None)
            if win_end.tzinfo is not None:
                win_end = win_end.replace(tzinfo=None)

            logger.info(f"🕒 Временное окно (финальное МСК):")
            logger.info(f"   win_start: {win_start}")
            logger.info(f"   win_end: {win_end}")

            try:
                logger.info(f"🚀 Запускаем download_report для {row['Номер массовой']} {win_start.date()}")
                xlsx_path = download_report(driver, workload_params, win_start, win_end)
                logger.info(f"📊 Обрабатываем метрики из файла: {xlsx_path}")
                lost, excess = calc_metrics(xlsx_path)
                results.append({
                    "Номер массовой": row["Номер массовой"],
                    "Дата": win_start.date().isoformat(),
                    "LostCalls": lost,
                    "ExcessTraffic": excess,
                })
                logger.info(f"✅ Успешно обработан {row['Номер массовой']} - {region}: lost={lost}, excess={excess}")
            except Exception as exc:
                logger.error(f"❌ ОШИБКА для строки #{idx} MassID {row['Номер массовой']} {region}")
                try:
                    logger.error(f"   Период: {win_start.date()} - {win_end.date()}")
                except:
                    logger.error(f"   Период: не удалось определить")
                logger.error(f"   Детали ошибки: {exc}")
                logger.exception("   Полный traceback:")
                continue

    pd.DataFrame(results).to_csv(out_csv_path, index=False, encoding="utf-8")
    logger.success(f"Done → {out_csv_path} ({len(results)} rows)")
    driver.quit()


if __name__ == "__main__":
    main()