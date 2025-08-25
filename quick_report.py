#!/usr/bin/env python3
"""
Простой скрипт для быстрого вывода отчета без анализа страницы
"""

import sys
import logging
import time
from datetime import datetime
from pathlib import Path

# Импортируем наши модули
from modules.selenium_helpers import get_driver, apply_cdp_download_settings, setup_proxy
from modules.new_site_handler import NewSiteReportHandler

# Константы
NEW_SITE_URL = (
    "http://t2ru-crmdb-03/Reports/report/%D0%9E%D1%82%D1%87%D0%B5%D1%82%D1%8B%20%D0%9A%D0%A6/%D0%9E%D1%82%D1%87%D0%B5%D1%82%20%D0%BF%D0%BE%20%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0%D0%BC%20%D0%BE%D0%B1%D1%80%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D0%B9%20(%D1%81%D0%BE%20%D1%81%D1%86%D0%B5%D0%BD%D0%B0%D1%80%D0%B8%D1%8F%D0%BC%D0%B8%20%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8)"
)

# Настройки по умолчанию
DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")

def setup_logging(level=logging.INFO):
    """Настраивает логирование."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('quick_report.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def open_new_site(driver, url, logger):
    """Открывает новый сайт."""
    try:
        logger.info(f"🌐 Открываем сайт: {url}")
        driver.get(url)
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
        while True:
            try:
                driver.current_url
                time.sleep(1)
            except:
                break
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")

def main():
    """Основная функция."""
    # Настраиваем логирование
    logger = setup_logging()
    logger.info("🚀 Запуск простого скрипта для вывода отчета")

    # Проверяем директорию для загрузки
    download_dir = Path(DEFAULT_DOWNLOAD_DIR)
    if not download_dir.exists():
        logger.error(f"❌ Директория для загрузки не существует: {download_dir}")
        return 1

    logger.info(f"📁 Директория для загрузки: {download_dir}")

    # Настраиваем прокси
    setup_proxy()
    logger.info("✅ Прокси настроен")

    # Создаем WebDriver
    try:
        driver = get_driver(headless=False)  # Всегда в GUI режиме для отладки
        logger.info("✅ WebDriver инициализирован успешно")

        # Применяем CDP настройки для скачивания
        apply_cdp_download_settings(driver)
        logger.info("✅ CDP настройки для скачивания применены")

        # Открываем новый сайт
        if open_new_site(driver, NEW_SITE_URL, logger):
            # Полная обработка отчета
            logger.info("📊 Начинаем обработку отчета...")

            # Создаем обработчик отчетов
            report_handler = NewSiteReportHandler(driver, logger)

            # Запрашиваем даты у пользователя
            logger.info("📅 Введите даты для отчета:")

            # Дата начала
            while True:
                try:
                    start_date_str = input("Введите дату начала (формат ДД.ММ.ГГГГ, например 01.01.2025): ").strip()
                    start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
                    break
                except ValueError:
                    logger.error("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")

            # Дата окончания
            while True:
                try:
                    end_date_str = input("Введите дату окончания (формат ДД.ММ.ГГГГ, например 31.01.2025): ").strip()
                    end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
                    if end_date < start_date:
                        logger.error("❌ Дата окончания не может быть раньше даты начала")
                        continue
                    break
                except ValueError:
                    logger.error("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")

            logger.info(f"📅 Период отчета: с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}")
            logger.info(f"📊 Тип периода: произвольный (всегда)")
            logger.info(f"🔍 Причина обращения: низкая_скорость_3g_4g")

            # Обрабатываем отчет
            downloaded_file = report_handler.process_report(
                start_date=start_date,
                end_date=end_date,
                download_dir=str(download_dir),
                period='произвольный',
                reason='низкая_скорость_3g_4g'
            )

            if downloaded_file:
                logger.info(f"🎉 Отчет успешно загружен: {downloaded_file}")
            else:
                logger.error("❌ Не удалось загрузить отчет")

            # Ждем инструкций пользователя
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

    logger.info("✅ Скрипт завершен успешно")
    return 0

if __name__ == "__main__":
    sys.exit(main())
