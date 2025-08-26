#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового функционала экспорта Excel
"""

from loguru import logger
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from excel_exporter import ExcelExporter

def setup_logging():
    """Настройка логирования [[memory:7206334]]"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - test_excel_export.py:%(lineno)d - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_driver():
    """Создание драйвера Chrome"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_excel_export_methods():
    """Тестирование методов экспорта Excel"""
    logger = setup_logging()
    driver = None

    try:
        logger.info("🚀 Запуск тестирования методов экспорта Excel...")

        # Создаем драйвер
        driver = create_driver()

        # Создаем экземпляр ExcelExporter
        exporter = ExcelExporter(driver, logger)

        # Здесь должен быть URL вашей страницы с отчетом
        # test_url = "YOUR_REPORT_URL_HERE"
        # driver.get(test_url)

        logger.info("⚠️ Для полного тестирования нужно:")
        logger.info("1. Раскомментировать строки с test_url")
        logger.info("2. Указать реальный URL страницы с отчетом")
        logger.info("3. Убедиться, что отчет загружен")

                # Когда будет реальная страница, раскомментируйте эти строки:

        # logger.info("📊 Запуск диагностического теста...")
        # test_result = exporter.run_excel_export_test()

        # logger.info("🔍 Поиск элементов через JavaScript...")
        # export_elements = exporter.find_export_elements_via_js()

        # logger.info("🚀 Тестирование прямого экспорта...")
        # success = exporter.click_excel_export_via_js()
        # logger.info(f"Результат прямого экспорта: {'✅ Успех' if success else '❌ Неудача'}")

        # logger.info("🔍 Проверка iframe...")
        # iframe_found = exporter.check_and_switch_iframe()
        # logger.info(f"Результат проверки iframe: {'✅ Найден' if iframe_found else '❌ Не найден'}")

        logger.info("✅ Тестовый скрипт готов к использованию")
        logger.info("🚀 Новые возможности:")
        logger.info("   • Отключение Google логов")
        logger.info("   • Детальная диагностика контекста страницы")
        logger.info("   • Проверка и переключение iframe")
        logger.info("   • Улучшенный JavaScript поиск с детализацией")
        logger.info("   • Принудительное ожидание загрузки страницы")

    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("🔒 Браузер закрыт")

if __name__ == "__main__":
    test_excel_export_methods()
