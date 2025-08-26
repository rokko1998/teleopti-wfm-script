"""
Основной класс для работы с новым сайтом отчетов
Использует модульную архитектуру для лучшей организации кода
"""

import time
from pathlib import Path
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .form_elements import FormElements
from .iframe_handler import IframeHandler
from .form_filler import FormFiller
from .excel_exporter import ExcelExporter
from .selenium_export_handler import SeleniumExportHandler


class NewSiteHandler:
    """Основной класс для работы с новым сайтом отчетов"""

    def __init__(self, driver, logger, download_dir=None):
        self.driver = driver
        self.logger = logger

        # Инициализируем модули
        self.form_elements = FormElements()
        self.iframe_handler = IframeHandler(driver, logger)
        self.form_filler = FormFiller(driver, logger, self.iframe_handler, self.form_elements)
        self.excel_exporter = ExcelExporter(driver, logger)

                # Новый модуль для "боевого" сценария экспорта
        self.selenium_exporter = SeleniumExportHandler(driver, logger, download_dir)

    def process_report(self, wait_time=60):
        """Основной метод для обработки отчета"""
        try:
            self.logger.info("🚀 Начинаем обработку отчета на новом сайте...")

            # Ждем загрузки страницы
            self.logger.info("⏳ Ждем загрузки страницы...")
            time.sleep(10)

            # 1. Устанавливаем период отчета
            if not self.form_filler.set_report_period('произвольный'):
                self.logger.error("❌ Не удалось установить период отчета")
                return False

            # 2. Устанавливаем дату начала
            if not self.form_filler.set_start_date():
                self.logger.error("❌ Не удалось установить дату начала")
                return False

            # 3. Устанавливаем дату окончания
            if not self.form_filler.set_end_date():
                self.logger.error("❌ Не удалось установить дату окончания")
                return False

            # 4. Устанавливаем причину обращения
            if not self.form_filler.set_reason():
                self.logger.error("❌ Не удалось установить причину обращения")
                return False

            # 5. Отправляем отчет
            if not self.form_filler.submit_report():
                self.logger.error("❌ Не удалось отправить отчет")
                return False

            # 6. Экспортируем в Excel (пробуем "боевой" сценарий, затем fallback)
            self.logger.info("📤 Пробуем экспорт через 'боевой' сценарий...")
            excel_result = self.export_excel_by_click(wait_time=wait_time)

            # Проверяем результат экспорта
            if excel_result and isinstance(excel_result, str):
                # Нормализуем путь для проверки расширения
                file_path = Path(excel_result)
                if file_path.suffix.lower() == '.xlsx':
                    self.logger.info(f"✅ Экспорт через 'боевой' сценарий успешен: {excel_result}")
                    # Файл скачался, останавливаемся здесь
                    return True
                else:
                    self.logger.warning(f"⚠️ Результат не является Excel файлом: {excel_result}")
            elif excel_result is None:
                self.logger.error("❌ Экспорт не удался - файл не появился")
                return False
            elif excel_result is False:
                self.logger.error("❌ Экспорт не удался - ошибка в процессе")
                return False
            else:
                self.logger.warning(f"⚠️ Неожиданный тип результата: {type(excel_result)} = {excel_result}")
                return False

            self.logger.info("🎉 Обработка отчета завершена успешно!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при обработке отчета: {e}")
            return False

    def fill_report_parameters(self):
        """Заполнить параметры отчета (устаревший метод, оставлен для совместимости)"""
        self.logger.warning("⚠️ Метод fill_report_parameters устарел, используйте process_report")
        return self.process_report()

    def submit_report_request(self):
        """Отправить запрос отчета (устаревший метод, оставлен для совместимости)"""
        self.logger.warning("⚠️ Метод submit_report_request устарел, используйте process_report")
        return self.process_report()

    def export_to_excel(self, wait_time=60):
        """Экспортировать в Excel (устаревший метод, оставлен для совместимости)"""
        self.logger.warning("⚠️ Метод export_to_excel устарел, используйте process_report")
        return self.process_report(wait_time)

    def export_excel_by_click(self, report_url: str = None, wait_time=120):
        """Экспорт Excel через "боевой" сценарий - клики по меню"""
        try:
            self.logger.info("🚀 Запускаем 'боевой' сценарий экспорта Excel...")

            # Если URL не передан, используем текущий
            if not report_url:
                report_url = self.driver.current_url
                self.logger.info(f"📄 Используем текущий URL: {report_url}")

            # Запускаем экспорт через клики
            result = self.selenium_exporter.export_excel_by_click(
                report_url=report_url,
                download_dir=self.selenium_exporter.download_dir,
                overall_timeout=wait_time
            )

            if result:
                self.logger.info(f"🎉 Экспорт Excel завершен успешно: {result}")
                return result  # Возвращаем путь к файлу
            else:
                self.logger.error("❌ Экспорт Excel не удался")
                return False

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при экспорте Excel: {e}")
            return False

    def get_download_directory(self):
        """Получить текущую директорию загрузок"""
        return self.selenium_exporter.download_dir

    def set_download_directory(self, new_dir):
        """Изменить директорию загрузок"""
        return self.selenium_exporter.set_download_directory(new_dir)
