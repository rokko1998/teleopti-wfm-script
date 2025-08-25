#!/usr/bin/env python3
"""
new_site_handler.py — Модуль для работы с новым сайтом отчетов.
Содержит функции для заполнения параметров, отправки запросов и экспорта отчетов.
"""

import time
import logging
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NewSiteReportHandler:
    """Класс для обработки отчетов с нового сайта."""

    def __init__(self, driver, logger=None):
        """
        Инициализация обработчика.

        Args:
            driver: WebDriver экземпляр
            logger: Логгер (если не указан, создается новый)
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)

        # ID элементов на странице
        self.ELEMENT_IDS = {
            'period_dropdown': 'ReportViewerControl_ctl04_ctl03_ddValue',
            'start_date_field': 'ReportViewerControl_ctl04_ctl05_txtValue',
            'end_date_field': 'ReportViewerControl_ctl04_ctl07_txtValue',
            'submit_button': 'ReportViewerControl_ctl04_ctl00',
            'excel_link': "//a[contains(text(), 'Excel') and contains(@class, 'ActiveLink')]"
        }

        # Значения для периода отчета
        self.PERIOD_VALUES = {
            'произвольный': '900',
            'день': '1',
            'неделя': '7',
            'месяц': '30',
            '7_дней': '107',
            'сегодня': '500'
        }

    def fill_report_parameters(self, start_date, end_date, period='произвольный'):
        """
        Заполняет параметры отчета.

        Args:
            start_date: Дата начала отчета
            end_date: Дата окончания отчета
            period: Период отчета (по умолчанию 'произвольный')

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            self.logger.info("🔄 Начинаем заполнение параметров отчета...")

            # 1. Устанавливаем "Период отчета"
            if not self._set_report_period(period):
                return False

            # Ждем активации полей дат
            time.sleep(2)

            # 2. Устанавливаем "Дата начала"
            if not self._set_start_date(start_date):
                return False

            # 3. Устанавливаем "Дата окончания"
            if not self._set_end_date(end_date):
                return False

            self.logger.info("✅ Все параметры отчета заполнены успешно")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при заполнении параметров: {e}")
            return False

    def _set_report_period(self, period):
        """Устанавливает период отчета."""
        try:
            period_value = self.PERIOD_VALUES.get(period.lower())
            if not period_value:
                self.logger.error(f"❌ Неизвестный период: {period}")
                return False

            period_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['period_dropdown']))
            )

            period_select = Select(period_dropdown)
            period_select.select_by_value(period_value)

            self.logger.info(f"✅ Период отчета установлен: {period}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета: {e}")
            return False

    def _set_start_date(self, start_date):
        """Устанавливает дату начала."""
        try:
            start_date_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['start_date_field']))
            )

            start_date_field.clear()
            start_date_field.send_keys(start_date.strftime("%d.%m.%Y"))

            self.logger.info(f"✅ Дата начала установлена: {start_date.strftime('%d.%m.%Y')}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты начала: {e}")
            return False

    def _set_end_date(self, end_date):
        """Устанавливает дату окончания."""
        try:
            end_date_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['end_date_field']))
            )

            end_date_field.clear()
            end_date_field.send_keys(end_date.strftime("%d.%m.%Y"))

            self.logger.info(f"✅ Дата окончания установлена: {end_date.strftime('%d.%m.%Y')}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания: {e}")
            return False

    def submit_report_request(self, wait_time=10):
        """
        Отправляет запрос на формирование отчета.

        Args:
            wait_time: Время ожидания загрузки отчета в секундах

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            self.logger.info("🔄 Отправляем запрос на формирование отчета...")

            # Нажимаем "Просмотр отчета"
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['submit_button']))
            )
            submit_button.click()

            self.logger.info("✅ Запрос на формирование отчета отправлен")

            # Ждем загрузки отчета
            self.logger.info(f"⏳ Ожидание загрузки отчета ({wait_time} сек)...")
            time.sleep(wait_time)

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке запроса: {e}")
            return False

    def export_to_excel(self):
        """
        Экспортирует отчет в Excel.

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            self.logger.info("🔄 Начинаем экспорт в Excel...")

            # Ищем Excel кнопку
            excel_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.ELEMENT_IDS['excel_link']))
            )

            self.logger.info("✅ Excel кнопка найдена")

            # Кликаем по Excel
            excel_link.click()
            self.logger.info("✅ Клик по Excel выполнен")

            # Ждем начала загрузки
            time.sleep(3)

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при экспорте в Excel: {e}")
            return False

    def wait_for_download(self, download_dir, timeout=60):
        """
        Ожидает завершения загрузки файла.

        Args:
            download_dir: Директория для загрузки
            timeout: Таймаут ожидания в секундах

        Returns:
            str: Путь к загруженному файлу или None в случае ошибки
        """
        try:
            self.logger.info(f"⏳ Ожидание загрузки файла в {download_dir}...")

            start_time = time.time()
            while time.time() - start_time < timeout:
                # Проверяем наличие новых файлов
                import os
                files = [f for f in os.listdir(download_dir)
                        if f.endswith('.xlsx') or f.endswith('.xls')]

                if files:
                    # Сортируем по времени изменения
                    files.sort(key=lambda x: os.path.getmtime(
                        os.path.join(download_dir, x)), reverse=True)
                    latest_file = files[0]
                    file_path = os.path.join(download_dir, latest_file)

                    # Проверяем, что файл не заблокирован (загрузка завершена)
                    try:
                        with open(file_path, 'rb') as f:
                            pass
                        self.logger.info(f"✅ Файл загружен: {latest_file}")
                        return file_path
                    except PermissionError:
                        # Файл еще загружается
                        pass

                time.sleep(2)

            self.logger.error("❌ Таймаут ожидания загрузки файла")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании загрузки: {e}")
            return None

    def process_report(self, start_date, end_date, download_dir, period='произвольный'):
        """
        Основная функция обработки отчета.

        Args:
            start_date: Дата начала отчета
            end_date: Дата окончания отчета
            download_dir: Директория для загрузки
            period: Период отчета

        Returns:
            str: Путь к загруженному файлу или None в случае ошибки
        """
        try:
            self.logger.info("🚀 Начинаем обработку отчета с нового сайта")

            # 1. Заполняем параметры отчета
            if not self.fill_report_parameters(start_date, end_date, period):
                return None

            # 2. Отправляем запрос
            if not self.submit_report_request():
                return None

            # 3. Экспортируем в Excel
            if not self.export_to_excel():
                return None

            # 4. Ждем загрузки файла
            downloaded_file = self.wait_for_download(download_dir)
            if not downloaded_file:
                return None

            self.logger.info(f"🎉 Отчет успешно загружен: {downloaded_file}")
            return downloaded_file

        except Exception as e:
            self.logger.error(f"❌ Ошибка при обработке отчета: {e}")
            return None
