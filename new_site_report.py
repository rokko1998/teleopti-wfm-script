#!/usr/bin/env python3
"""
new_site_report.py — Скрипт для выгрузки отчета по причинам обращений с нового сайта.

Этот скрипт:
1. Открывает сайт http://t2ru-crmdb-03/Reports/report/...
2. Работает в no-headless режиме для удобства отладки
3. Готов к настройке конкретных действий (кнопки, поля, загрузка)
4. Использует существующую инфраструктуру selenium_helpers

ИСПОЛЬЗОВАНИЕ:
    python new_site_report.py [--headless] [--debug]

ПАРАМЕТРЫ:
    --headless     Запуск в headless режиме (по умолчанию no-headless)
    --debug        Включить подробное логирование
"""

from __future__ import annotations

import sys
import argparse
import time
import json
from pathlib import Path
from loguru import logger

# Импорты из наших модулей
from modules.selenium_helpers import get_driver, setup_proxy, apply_cdp_download_settings

# Константы
BASE_DIR = Path(__file__).resolve().parent
NEW_SITE_URL = (
    "http://t2ru-crmdb-03/Reports/report/%D0%9E%D1%82%D1%87%D0%B5%D1%82%D1%8B%20%D0%9A%D0%A6/"
    "%D0%9E%D1%82%D1%87%D0%B5%D1%82%20%D0%BF%D0%BE%20%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0%D0%BC%20"
    "%D0%BE%D0%B1%D1%80%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D0%B9%20(%D1%81%D0%BE%20%D1%81%D1%86%D0%B5%D0%BD%D0%B8%D1%8F%D0%BC%D0%B8%20"
    "%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8"
)


def setup_logging(debug: bool = False):
    """Настраивает логирование."""
    if debug:
        logger.remove()
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>"
        )
    else:
        logger.remove()
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<level>{message}</level>"
        )


def open_new_site(driver, url: str):
    """Открывает новый сайт и ждет загрузки."""
    logger.info(f"🌐 Открываем сайт: {url}")

    try:
        driver.get(url)
        logger.info("✅ Сайт открыт успешно")

        # Ждем загрузки страницы
        time.sleep(3)

        # Показываем информацию о странице
        logger.info(f"📄 Заголовок страницы: {driver.title}")
        logger.info(f"🔗 Текущий URL: {driver.current_url}")

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при открытии сайта: {e}")
        return False


def analyze_page_structure(driver):
    """Анализирует структуру страницы для понимания доступных элементов."""
    logger.info("🔍 Анализируем структуру страницы...")

    try:
        # Ищем все кнопки
        buttons = driver.find_elements("tag name", "button")
        logger.info(f"🔘 Найдено кнопок: {len(buttons)}")
        for i, btn in enumerate(buttons[:10]):  # Показываем первые 10
            try:
                text = btn.text.strip()
                btn_id = btn.get_attribute("id") or "без ID"
                btn_class = btn.get_attribute("class") or "без класса"
                logger.info(f"  {i+1}. Кнопка: '{text}' (ID: {btn_id}, класс: {btn_class})")
            except:
                logger.info(f"  {i+1}. Кнопка: [не удалось прочитать]")

        # Ищем все поля ввода
        inputs = driver.find_elements("tag name", "input")
        logger.info(f"📝 Найдено полей ввода: {len(inputs)}")
        for i, inp in enumerate(inputs[:10]):  # Показываем первые 10
            try:
                inp_type = inp.get_attribute("type") or "без типа"
                inp_id = inp.get_attribute("id") or "без ID"
                inp_name = inp.get_attribute("name") or "без имени"
                inp_placeholder = inp.get_attribute("placeholder") or "без placeholder"
                logger.info(f"  {i+1}. Поле: тип={inp_type}, ID={inp_id}, name={inp_name}, placeholder='{inp_placeholder}'")
            except:
                logger.info(f"  {i+1}. Поле: [не удалось прочитать]")

        # Ищем все ссылки
        links = driver.find_elements("tag name", "a")
        logger.info(f"🔗 Найдено ссылок: {len(links)}")
        for i, link in enumerate(links[:10]):  # Показываем первые 10
            try:
                text = link.text.strip()
                href = link.get_attribute("href") or "без href"
                logger.info(f"  {i+1}. Ссылка: '{text}' -> {href}")
            except:
                logger.info(f"  {i+1}. Ссылка: [не удалось прочитать]")

        # Ищем все таблицы
        tables = driver.find_elements("tag name", "table")
        logger.info(f"📊 Найдено таблиц: {len(tables)}")

        # Ищем все формы
        forms = driver.find_elements("tag name", "form")
        logger.info(f"📋 Найдено форм: {len(forms)}")

        # Ищем все iframe
        iframes = driver.find_elements("tag name", "iframe")
        logger.info(f"🖼️ Найдено iframe: {len(iframes)}")

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при анализе страницы: {e}")
        return False


def get_page_html_structure(driver):
    """Получает полную HTML структуру страницы для анализа."""
    logger.info("📄 Получаем полную HTML структуру страницы...")

    try:
        # Получаем HTML страницы
        page_source = driver.page_source

        # Сохраняем в файл для анализа
        html_file = BASE_DIR / "page_structure_analysis.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)

        logger.info(f"✅ HTML структура сохранена в файл: {html_file}")

        # Анализируем ключевые элементы
        analyze_html_elements(driver)

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при получении HTML структуры: {e}")
        return False


def analyze_html_elements(driver):
    """Анализирует ключевые HTML элементы для понимания структуры."""
    logger.info("🔍 Анализируем ключевые HTML элементы...")

    try:
        # Ищем элементы ReportViewer
        report_elements = driver.find_elements("xpath", "//*[contains(@id, 'ReportViewer') or contains(@class, 'ReportViewer')]")
        logger.info(f"📊 Найдено элементов ReportViewer: {len(report_elements)}")

        # Ищем таблицы данных
        data_tables = driver.find_elements("xpath", "//table[contains(@class, 'data') or contains(@id, 'data') or contains(@class, 'table')]")
        logger.info(f"📋 Найдено таблиц данных: {len(data_tables)}")

        # Ищем элементы пагинации
        pagination = driver.find_elements("xpath", "//*[contains(@class, 'pagination') or contains(@id, 'pagination') or contains(text(), 'Страница')]")
        logger.info(f"📄 Найдено элементов пагинации: {len(pagination)}")

        # Ищем элементы экспорта
        export_elements = driver.find_elements("xpath", "//*[contains(@class, 'export') or contains(@id, 'export') or contains(text(), 'Экспорт') or contains(text(), 'Excel')]")
        logger.info(f"💾 Найдено элементов экспорта: {len(export_elements)}")

        # Ищем скрытые поля с данными
        hidden_data = driver.find_elements("xpath", "//input[@type='hidden' and contains(@value, 'data')]")
        logger.info(f"🔒 Найдено скрытых полей с данными: {len(hidden_data)}")

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при анализе HTML элементов: {e}")
        return False


def wait_for_user_instructions():
    """Ждет инструкций от пользователя."""
    logger.info("⏸️ Скрипт готов к настройке действий.")
    logger.info("💡 Теперь вы можете:")
    logger.info("  1. Прописать какие кнопки нажимать")
    logger.info("  2. Указать какие поля заполнять")
    logger.info("  3. Настроить что загружать")
    logger.info("  4. Добавить логику обработки отчета")

    input("🔄 Нажмите Enter когда будете готовы продолжить...")
    logger.info("✅ Продолжаем выполнение...")


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Скрипт для выгрузки отчета с нового сайта")
    parser.add_argument("--headless", help="Запуск в headless режиме", action="store_true")
    parser.add_argument("--debug", help="Включить подробное логирование", action="store_true")

    args = parser.parse_args()

    # Настраиваем логирование
    setup_logging(args.debug)

    # Определяем режим запуска (по умолчанию no-headless)
    headless = args.headless
    if headless:
        logger.info("🔒 Запуск в headless режиме")
    else:
        logger.info("👁️ Запуск в no-headless режиме (браузер будет виден)")

    # Настраиваем прокси
    setup_proxy()

    # Создаем WebDriver
    try:
        driver = get_driver(headless=headless)
        logger.info("✅ WebDriver инициализирован успешно")

        # Применяем CDP настройки для скачивания
        apply_cdp_download_settings(driver)

        # Открываем новый сайт
        if open_new_site(driver, NEW_SITE_URL):
            # Анализируем структуру страницы
            analyze_page_structure(driver)

            # Получаем полную HTML структуру
            get_page_html_structure(driver)

            # Ждем инструкций от пользователя
            wait_for_user_instructions()

            # TODO: Здесь будет основная логика работы с сайтом
            # 1. Нажатие кнопок
            # 2. Заполнение полей
            # 3. Загрузка отчета
            # 4. Обработка данных

            logger.info("🎯 Готов к реализации основной логики работы с сайтом")

        else:
            logger.error("❌ Не удалось открыть сайт")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

    finally:
        # Закрываем браузер
        try:
            if 'driver' in locals():
                driver.quit()
                logger.info("🔒 Браузер закрыт")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при закрытии браузера: {e}")

    logger.info("✅ Скрипт завершен успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
