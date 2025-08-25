"""
Основной класс для работы с новым сайтом отчетов
Использует модульную архитектуру для лучшей организации кода
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .form_elements import FormElements
from .iframe_handler import IframeHandler
from .form_filler import FormFiller
from .excel_exporter import ExcelExporter


class NewSiteHandler:
    """Основной класс для работы с новым сайтом отчетов"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

        # Инициализируем модули
        self.form_elements = FormElements()
        self.iframe_handler = IframeHandler(driver, logger)
        self.form_filler = FormFiller(driver, logger, self.iframe_handler, self.form_elements)
        self.excel_exporter = ExcelExporter(driver, logger)

    def process_report(self):
        """Обработать отчет - основная логика"""
        try:
            self.logger.info("[new_site_handler] 📊 Начинаем обработку отчета...")
            
            # 1. Устанавливаем период отчета
            if not self.form_filler.set_report_period():
                self.logger.error("[new_site_handler] ❌ Не удалось установить период отчета")
                return False
            
            # 2. Устанавливаем дату начала
            if not self.form_filler.set_start_date():
                self.logger.error("[new_site_handler] ❌ Не удалось установить дату начала")
                return False
            
            # 3. Устанавливаем дату окончания
            if not self.form_filler.set_end_date():
                self.logger.error("[new_site_handler] ❌ Не удалось установить дату окончания")
                return False
            
            # 4. Устанавливаем причину обращения
            if not self.form_filler.set_reason():
                self.logger.error("[new_site_handler] ❌ Не удалось установить причину обращения")
                return False
            
            # 5. Отправляем запрос на формирование отчета
            if not self.form_filler.submit_report():
                self.logger.error("[new_site_handler] ❌ Не удалось отправить запрос на формирование отчета")
                return False
            
            # 6. Экспортируем в Excel
            if not self.excel_exporter.export_to_excel():
                self.logger.error("[new_site_handler] ❌ Не удалось экспортировать отчет в Excel")
                return False
            
            self.logger.info("[new_site_handler] ✅ Отчет успешно обработан и экспортирован в Excel")
            return True
            
        except Exception as e:
            self.logger.error(f"[new_site_handler] ❌ Критическая ошибка при обработке отчета: {e}")
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
