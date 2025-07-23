#!/usr/bin/env python3
"""wfm_single.py — one‑file версия скрипта выгрузки «потерянных» и «превышения» из Teleopti.

Нужен Python 3.11+, Edge (Chromium) + соответствующий msedgedriver.exe в PATH.
Библиотеки: selenium, pandas, numpy, pyyaml, loguru, python‑dateutil, typer.

Запуск:
    python wfm_single.py run --input_xlsx Свод.xlsx [--out_csv out.csv] [--headless false]

Config
------
region_skills.yml лежит рядом с файлом; пример:

    timezone: Europe/Moscow
    interval_minutes: 15
    regions:
      Problem Russia: [67]
      Chelyabinsk_CC: [87, 118]
    aliases:
      Челябинск: Chelyabinsk_CC

"""
from __future__ import annotations

import sys
import time
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import numpy as np
import argparse
import yaml
from dateutil import tz
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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
    if headless:
        opts.add_argument("--headless=new")
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

    # Настройка папки загрузок - КРИТИЧЕСКИ ВАЖНО!
    # Указываем браузеру скачивать файлы в папку проекта downloads/
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR.absolute()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    opts.add_experimental_option("prefs", prefs)

    # Убираем детекцию автоматизации
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    try:
        # Автоматическая установка ChromeDriver для Chrome 138+
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

        # Убираем индикатор автоматизации
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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


def wait_download(start_ts: float, timeout: int = 60) -> Path:
    """Ждём появления xlsx в DOWNLOAD_DIR новее start_ts."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for f in DOWNLOAD_DIR.glob("*.xlsx"):
            if f.stat().st_mtime > start_ts:
                time.sleep(1)
                return f
        time.sleep(1)
    raise TimeoutError("Download timeout")


def download_report(
    driver: webdriver.Chrome,
    skills: List[str],
    start_dt: datetime,
    end_dt: datetime,
) -> Path:
    """Открывает форму, выставляет фильтры, скачивает отчёт."""
    driver.get(REPORT_URL)
    wait = WebDriverWait(driver, 30)

    # --- multiselect skills -------------------------------------------------
    left_select = wait.until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "select[id^=\"ParameterSelector_List\"][size='7']"))
    )
    for skill in skills:
        try:
            opt = left_select.find_element(By.XPATH, f".//option[text()='{skill}']")
            opt.click()
        except NoSuchElementException:
            logger.warning(f"skill {skill} not found in list → skip")
            continue
        # move right
        driver.find_element(By.CSS_SELECTOR,
            "input[id^='ParameterSelector_ButtonOne'][value='>']").click()

    # --- даты / время -------------------------------------------------------
    def _set_input(selector: str, value: str):
        elem = driver.find_element(By.CSS_SELECTOR, selector)
        elem.clear(); elem.send_keys(value)

    fmt = "%d.%m.%Y %H:%M"
    _set_input("input[name*='txtBox1285']", start_dt.strftime(fmt))
    _set_input("input[name*='txtBox3448']", end_dt.strftime(fmt))

    # --- Excel --------------------------------------------------------------
    ts = time.time()
    driver.find_element(By.ID, "buttonShowExcel").click()
    return wait_download(ts)

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

    args = parser.parse_args()

    input_xlsx_path = Path(args.input_xlsx)
    yaml_path = Path(args.yaml_cfg) if args.yaml_cfg else BASE_DIR / "region_skills.yml"
    out_csv_path = Path(args.out_csv)
    headless = args.headless and not args.no_headless

    cfg = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    # Читаем данные с листа "отчет"
    try:
        df = pd.read_excel(input_xlsx_path, sheet_name="отчет")
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

    tz_local = tz.gettz(cfg.get("timezone", "Europe/Moscow"))

    driver = get_driver(headless=headless)
    results = []

    for _, row in df.iterrows():
        region = row["Регион"]
        # Ищем соответствие региона в конфигурации
        workload_params = cfg["regions"].get(region)

        if not workload_params:
            logger.warning(f"Region '{region}' not found in YAML config → skip")
            logger.info(f"Available regions in config: {list(cfg['regions'].keys())}")
            continue

        logger.info(f"Processing region '{region}' with workload parameters: {workload_params}")

        for win_start, win_end in windows_for_row(row):
            win_start = win_start.astimezone(tz_local)
            win_end   = win_end.astimezone(tz_local)

            try:
                xlsx_path = download_report(driver, workload_params, win_start, win_end)
                lost, excess = calc_metrics(xlsx_path)
                results.append({
                    "Номер массовой": row["Номер массовой"],
                    "Дата": win_start.date().isoformat(),
                    "LostCalls": lost,
                    "ExcessTraffic": excess,
                })
            except Exception as exc:
                logger.exception(f"Failed for MassID {row['Номер массовой']} {win_start.date()}: {exc}")
                continue

    pd.DataFrame(results).to_csv(out_csv_path, index=False, encoding="utf-8")
    logger.success(f"Done → {out_csv_path} ({len(results)} rows)")
    driver.quit()


if __name__ == "__main__":
    main()