#!/usr/bin/env python3
"""
analyze_page.py — Скрипт для анализа структуры страницы нового сайта отчетов.
Запускает браузер, открывает страницу и выполняет детальный анализ элементов формы.
"""

import sys
import logging
from pathlib import Path

# Импортируем наши модули
from modules.selenium_helpers import get_driver, apply_cdp_download_settings, setup_proxy
from modules.page_analyzer import PageAnalyzer


# Константы
NEW_SITE_URL = (
    "http://t2ru-crmdb-03/Reports/report/%D0%9E%D1%82%D1%87%D0%B5%D1%82%D1%8B%20%D0%9A%D0%A6/%D0%9E%D1%82%D1%87%D0%B5%D1%82%20%D0%BF%D0%BE%20%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0%D0%BC%20%D0%BE%D0%B1%D1%80%D0%B0%D1%89%D0%B5%D0%BD%D0%B8%D0%B9%20(%D1%81%D0%BE%20%D1%81%D1%86%D0%B5%D0%BD%D0%B0%D1%80%D0%B8%D1%8F%D0%BC%D0%B8%20%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8)"
)


def setup_logging(level=logging.INFO):
    """Настраивает логирование."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('page_analysis.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def open_new_site(driver, url, logger):
    """Открывает новый сайт."""
    try:
        logger.info(f"🌐 Открываем сайт: {url}")
        driver.get(url)

        # Ждем загрузки страницы
        driver.implicitly_wait(10)

        logger.info("✅ Сайт успешно открыт")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при открытии сайта: {e}")
        return False


def wait_for_user_instructions(driver, logger):
    """Ждет инструкций от пользователя."""
    logger.info("⏸️ Ожидание инструкций от пользователя...")
    logger.info("💡 Для продолжения работы закройте браузер или нажмите Ctrl+C")

    try:
        # Ждем пока браузер открыт
        while True:
            try:
                # Проверяем, что браузер еще работает
                driver.current_url
                import time
                time.sleep(1)
            except:
                break
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")


def main():
    """Основная функция."""
    # Настраиваем логирование
    logger = setup_logging()
    logger.info("🚀 Запуск скрипта анализа страницы нового сайта отчетов")

    # Настраиваем прокси
    setup_proxy()
    logger.info("✅ Прокси настроен")

    # Создаем WebDriver
    try:
        driver = get_driver(headless=False)  # Всегда запускаем с GUI для анализа
        logger.info("✅ WebDriver инициализирован успешно")

        # Применяем CDP настройки для скачивания
        apply_cdp_download_settings(driver)
        logger.info("✅ CDP настройки для скачивания применены")

        # Открываем новый сайт
        if open_new_site(driver, NEW_SITE_URL, logger):
            # Создаем анализатор страницы
            page_analyzer = PageAnalyzer(driver, logger)

            # Анализируем структуру страницы
            logger.info("🔍 Анализируем структуру страницы...")
            analysis_file = page_analyzer.get_page_html_structure()

            if analysis_file:
                logger.info(f"✅ Анализ страницы сохранен в: {analysis_file}")

            # Выполняем детальный анализ элементов формы
            logger.info("🔍 Выполняем детальный анализ элементов формы...")
            form_elements = page_analyzer.analyze_report_form_elements()

            if form_elements:
                logger.info("✅ Детальный анализ элементов формы завершен")
                # Выводим найденные элементы
                for element_name, element in form_elements.items():
                    if element:
                        logger.info(f"✅ {element_name}: найден")
                    else:
                        logger.warning(f"⚠️ {element_name}: не найден")
            else:
                logger.warning("⚠️ Детальный анализ элементов формы не выполнен")

            # Ждем инструкций пользователя для анализа результатов
            logger.info("📊 Анализ страницы завершен")
            wait_for_user_instructions(driver, logger)
        else:
            logger.error("❌ Не удалось открыть сайт")
            return 1

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

    logger.info("✅ Скрипт анализа завершен успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
