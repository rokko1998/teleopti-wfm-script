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
            'reason_dropdown': 'ReportViewerControl_ctl04_ctl09_ddValue',  # Поле для причины обращения
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

        # Значения для причины обращения
        self.REASON_VALUES = {
            'низкая_скорость_3g_4g': 'Низкая скорость в 3G/4G',
            'низкая_скорость': 'Низкая скорость в 3G/4G',
            '3g_4g': 'Низкая скорость в 3G/4G',
            'default': 'Низкая скорость в 3G/4G'
        }

    def fill_report_parameters(self, start_date, end_date, period='произвольный', reason='низкая_скорость_3g_4g'):
        """
        Заполняет параметры отчета.

        Args:
            start_date: Дата начала отчета
            end_date: Дата окончания отчета
            period: Период отчета (по умолчанию 'произвольный')
            reason: Причина обращения (по умолчанию 'низкая_скорость_3g_4g')

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

            # 4. Устанавливаем "Причина обращения"
            if not self._set_reason(reason):
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

            # Пробуем найти элемент по ID
            try:
                period_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['period_dropdown']))
                )
            except TimeoutException:
                # Если не нашли по ID, пробуем найти по тексту
                self.logger.info("🔍 Период отчета не найден по ID, ищем по тексту...")
                period_dropdown = self._find_element_by_multiple_criteria('period', 'select')

                if not period_dropdown:
                    self.logger.error("❌ Не удалось найти поле 'Период отчета'")
                    return False

            # Ждем готовности элемента
            if not self._wait_for_element_ready(period_dropdown):
                self.logger.error("❌ Элемент 'Период отчета' не готов к взаимодействию")
                return False

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
            # Пробуем найти элемент по ID
            try:
                start_date_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['start_date_field']))
                )
            except TimeoutException:
                # Если не нашли по ID, пробуем найти по тексту
                self.logger.info("🔍 Дата начала не найдена по ID, ищем по тексту...")
                start_date_field = self._find_element_by_multiple_criteria('start_date', 'input')

                if not start_date_field:
                    self.logger.error("❌ Не удалось найти поле 'Дата начала'")
                    return False

            # Ждем готовности элемента
            if not self._wait_for_element_ready(start_date_field):
                self.logger.error("❌ Элемент 'Дата начала' не готов к взаимодействию")
                return False

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
            # Пробуем найти элемент по ID
            try:
                end_date_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['end_date_field']))
                )
            except TimeoutException:
                # Если не нашли по ID, пробуем найти по тексту
                self.logger.info("🔍 Дата окончания не найдена по ID, ищем по тексту...")
                end_date_field = self._find_element_by_multiple_criteria('end_date', 'input')

                if not end_date_field:
                    self.logger.error("❌ Не удалось найти поле 'Дата окончания'")
                    return False

            # Ждем готовности элемента
            if not self._wait_for_element_ready(end_date_field):
                self.logger.error("❌ Элемент 'Дата окончания' не готов к взаимодействию")
                return False

            end_date_field.clear()
            end_date_field.send_keys(end_date.strftime("%d.%m.%Y"))

            self.logger.info(f"✅ Дата окончания установлена: {end_date.strftime('%d.%m.%Y')}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания: {e}")
            return False

    def _set_reason(self, reason):
        """Устанавливает причину обращения."""
        try:
            reason_value = self.REASON_VALUES.get(reason.lower(), self.REASON_VALUES['default'])

            # Пробуем найти элемент по ID
            try:
                reason_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['reason_dropdown']))
                )
            except TimeoutException:
                # Если не нашли по ID, пробуем найти по тексту
                self.logger.info("🔍 Причина обращения не найдена по ID, ищем по тексту...")
                reason_dropdown = self._find_element_by_multiple_criteria('reason', 'select')

                if not reason_dropdown:
                    self.logger.error("❌ Не удалось найти поле 'Причина обращения'")
                    return False

            # Ждем готовности элемента
            if not self._wait_for_element_ready(reason_dropdown):
                self.logger.error("❌ Элемент 'Причина обращения' не готов к взаимодействию")
                return False

            reason_select = Select(reason_dropdown)

            # Пробуем найти опцию по тексту
            try:
                reason_select.select_by_visible_text(reason_value)
            except:
                # Если не получилось, пробуем найти по частичному совпадению
                options = reason_select.options
                for option in options:
                    if "низкая скорость" in option.text.lower() or "3g" in option.text.lower() or "4g" in option.text.lower():
                        reason_select.select_by_visible_text(option.text)
                        self.logger.info(f"✅ Причина обращения установлена: {option.text}")
                        return True

                # Если ничего не нашли, выбираем первую опцию
                reason_select.select_by_index(0)
                self.logger.warning(f"⚠️ Не удалось найти точное совпадение, выбрана первая опция: {reason_select.first_selected_option.text}")

            self.logger.info(f"✅ Причина обращения установлена: {reason_value}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке причины обращения: {e}")
            return False

    def _find_element_by_text(self, text, tag_name=None):
        """
        Ищет элемент по тексту.

        Args:
            text: Текст для поиска
            tag_name: Тип тега (если указан)

        Returns:
            WebElement: Найденный элемент или None
        """
        try:
            if tag_name:
                xpath = f"//{tag_name}[contains(text(), '{text}') or contains(@placeholder, '{text}') or contains(@title, '{text}')]"
            else:
                xpath = f"//*[contains(text(), '{text}') or contains(@placeholder, '{text}') or contains(@title, '{text}')]"

            elements = self.driver.find_elements(By.XPATH, xpath)

            if elements:
                # Возвращаем первый найденный элемент
                return elements[0]

            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элемента по тексту: {e}")
            return None

    def _find_element_by_multiple_criteria(self, field_name, field_type="input"):
        """
        Ищет элемент по нескольким критериям.

        Args:
            field_name: Название поля для поиска
            field_type: Тип элемента (input, select, button)

        Returns:
            WebElement: Найденный элемент или None
        """
        try:
            # Список возможных названий для каждого поля
            field_variants = {
                'period': ['Период отчета', 'Период', 'Тип периода', 'Period'],
                'start_date': ['Дата начала', 'Начало', 'С', 'Start Date', 'From'],
                'end_date': ['Дата окончания', 'Окончание', 'По', 'End Date', 'To'],
                'reason': ['Причина обращения', 'Причина', 'Обращение', 'Reason', 'Issue Type']
            }

            # Получаем варианты названий для поля
            variants = field_variants.get(field_name, [field_name])

            # Пробуем найти по каждому варианту
            for variant in variants:
                element = self._find_element_by_text(variant, field_type)
                if element:
                    self.logger.info(f"✅ Найдено поле '{field_name}' по варианту '{variant}'")
                    return element

            # Если не нашли по тексту, пробуем найти по атрибутам
            if field_type == "input":
                # Ищем по name атрибуту
                elements = self.driver.find_elements(By.XPATH, f"//input[contains(@name, '{field_name}') or contains(@id, '{field_name}')]")
                if elements:
                    self.logger.info(f"✅ Найдено поле '{field_name}' по атрибутам")
                    return elements[0]

            elif field_type == "select":
                # Ищем по name атрибуту
                elements = self.driver.find_elements(By.XPATH, f"//select[contains(@name, '{field_name}') or contains(@id, '{field_name}')]")
                if elements:
                    self.logger.info(f"✅ Найдено поле '{field_name}' по атрибутам")
                    return elements[0]

            self.logger.warning(f"⚠️ Поле '{field_name}' не найдено ни по одному критерию")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элемента '{field_name}' по множественным критериям: {e}")
            return None

    def _wait_for_element_ready(self, element, timeout=5):
        """
        Ждет готовности элемента к взаимодействию.

        Args:
            element: WebElement для проверки
            timeout: Таймаут ожидания в секундах

        Returns:
            bool: True если элемент готов, False в противном случае
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Проверяем, что элемент видим и кликабелен
                    if element.is_displayed() and element.is_enabled():
                        return True
                    time.sleep(0.5)
                except:
                    time.sleep(0.5)

            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании готовности элемента: {e}")
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

            # Пробуем найти кнопку по ID
            try:
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['submit_button']))
                )
            except TimeoutException:
                # Если не нашли по ID, пробуем найти по тексту
                self.logger.info("🔍 Кнопка отправки не найдена по ID, ищем по тексту...")

                # Ищем кнопку по различным вариантам текста
                button_texts = ['Просмотр отчета', 'Сформировать', 'Отправить', 'Просмотр', 'Submit', 'Generate']
                submit_button = None

                for text in button_texts:
                    submit_button = self._find_element_by_text(text, "input")
                    if not submit_button:
                        submit_button = self._find_element_by_text(text, "button")
                    if submit_button:
                        self.logger.info(f"✅ Найдена кнопка отправки по тексту: {text}")
                        break

                if not submit_button:
                    self.logger.error("❌ Не удалось найти кнопку отправки отчета")
                    return False

            # Ждем готовности кнопки
            if not self._wait_for_element_ready(submit_button):
                self.logger.error("❌ Кнопка отправки не готова к взаимодействию")
                return False

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

    def process_report(self, start_date, end_date, download_dir, period='произвольный', reason='низкая_скорость_3g_4g'):
        """
        Основная функция обработки отчета.

        Args:
            start_date: Дата начала отчета
            end_date: Дата окончания отчета
            download_dir: Директория для загрузки
            period: Период отчета
            reason: Причина обращения

        Returns:
            str: Путь к загруженному файлу или None в случае ошибки
        """
        try:
            self.logger.info("🚀 Начинаем обработку отчета с нового сайта")

            # 1. Заполняем параметры отчета
            if not self.fill_report_parameters(start_date, end_date, period, reason):
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
