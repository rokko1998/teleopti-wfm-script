#!/usr/bin/env python3
"""
python new_site_report.py — Основной скрипт для выгрузки отчета по причинам обращений с нового сайта.
Использует модульную архитектуру для лучшей организации кода.
"""

import sys
import argparse
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

# Импортируем наши модули
from modules.selenium_helpers import get_driver, apply_cdp_download_settings, setup_proxy
from modules.new_site_handler import NewSiteReportHandler
from modules.page_analyzer import PageAnalyzer


# Константы
NEW_SITE_URL = (
    "http://t2ru-crmdb-03/Reports/report/%D0%9E%D1%82%D1%87%D0%B5%D1%82%D1%8B%20%D0%9A%A6/"
    "%D0%9E%D1%82%D1%87%D0%B5%D1%82%20%D0%BF%D0%BE%20%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0%D0%BC%20"
    "%D0%BE%D0%B1%D1%80%D0%B0%D1%89%D0%B5%D0%BD%D0%B8%D0%B9%20(%D1%81%D0%BE%20%D1%81%D1%86%D0%B5%D0%BD%D0%B0%D1%80%D0%B8%D1%8F%D0%BC%D0%B8%20"
    "%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8"
)

# Настройки по умолчанию
DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")
DEFAULT_START_DAYS_AGO = 30
DEFAULT_PERIOD = "произвольный"


def setup_logging(level=logging.INFO):
    """
    Настраивает логирование.

    Args:
        level: Уровень логирования
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('new_site_report.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """
    Парсит аргументы командной строки.

    Returns:
        argparse.Namespace: Парсированные аргументы
    """
    parser = argparse.ArgumentParser(
        description="Скрипт для выгрузки отчета по причинам обращений с нового сайта"
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Запуск в headless режиме (без GUI)'
    )

    parser.add_argument(
        '--download-dir',
        default=DEFAULT_DOWNLOAD_DIR,
        help=f'Директория для загрузки файлов (по умолчанию: {DEFAULT_DOWNLOAD_DIR})'
    )

    parser.add_argument(
        '--start-days-ago',
        type=int,
        default=DEFAULT_START_DAYS_AGO,
        help=f'Количество дней назад для начала отчета (по умолчанию: {DEFAULT_START_DAYS_AGO})'
    )

    parser.add_argument(
        '--period',
        default=DEFAULT_PERIOD,
        choices=['произвольный', 'день', 'неделя', 'месяц', '7_дней', 'сегодня'],
        help=f'Период отчета (по умолчанию: {DEFAULT_PERIOD})'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Только анализ страницы без загрузки отчета'
    )

    parser.add_argument(
        '--wait-time',
        type=int,
        default=10,
        help='Время ожидания загрузки отчета в секундах (по умолчанию: 10)'
    )

    return parser.parse_args()


def open_new_site(driver, url, logger):
    """
    Открывает новый сайт.

    Args:
        driver: WebDriver экземпляр
        url: URL для открытия
        logger: Логгер

    Returns:
        bool: True если успешно, False в случае ошибки
    """
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
    """
    Ждет инструкций от пользователя.

    Args:
        driver: WebDriver экземпляр
        logger: Логгер
    """
    logger.info("⏸️ Ожидание инструкций от пользователя...")
    logger.info("💡 Для продолжения работы закройте браузер или нажмите Ctrl+C")

    try:
        # Ждем пока браузер открыт
        while True:
            try:
                # Проверяем, что браузер еще работает
                driver.current_url
                time.sleep(1)
            except:
                break
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")


def main():
    """Основная функция."""
    # Парсим аргументы
    args = parse_arguments()

    # Настраиваем логирование
    logger = setup_logging()
    logger.info("🚀 Запуск скрипта для работы с новым сайтом отчетов")

    # Проверяем директорию для загрузки
    download_dir = Path(args.download_dir)
    if not download_dir.exists():
        logger.error(f"❌ Директория для загрузки не существует: {download_dir}")
        return 1

    logger.info(f"📁 Директория для загрузки: {download_dir}")

    # Настраиваем прокси (как в основном скрипте)
    setup_proxy()
    logger.info("✅ Прокси настроен")

    # Создаем WebDriver
    try:
        driver = get_driver(headless=args.headless)
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

            if args.analyze_only:
                # Только анализ, ждем инструкций пользователя
                logger.info("📊 Режим анализа завершен")
                wait_for_user_instructions(driver, logger)
            else:
                # Полная обработка отчета
                logger.info("📊 Начинаем обработку отчета...")

                # Создаем обработчик отчетов
                report_handler = NewSiteReportHandler(driver, logger)

                # Рассчитываем даты
                end_date = datetime.now()
                start_date = end_date - timedelta(days=args.start_days_ago)

                logger.info(f"📅 Период отчета: с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}")
                logger.info(f"📊 Тип периода: {args.period}")

                # Обрабатываем отчет
                downloaded_file = report_handler.process_report(
                    start_date=start_date,
                    end_date=end_date,
                    download_dir=str(download_dir),
                    period=args.period
                )

                if downloaded_file:
                    logger.info(f"🎉 Отчет успешно загружен: {downloaded_file}")

                    # Здесь можно добавить дальнейшую обработку файла
                    # Например, загрузку в базу данных, анализ данных и т.д.

                else:
                    logger.error("❌ Не удалось загрузить отчет")

                # Ждем инструкций пользователя для анализа результатов
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
