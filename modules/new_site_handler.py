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
            'reason_dropdown': 'ReportViewerControl_ctl04_ctl09_txtValue',  # Поле для причины обращения
            'submit_button': 'ReportViewerControl_ctl04_ctl00',
            'excel_link': "//a[contains(text(), 'Excel') and contains(@class, 'ActiveLink')]"
        }

        # Значения для периода отчета
        self.PERIOD_VALUES = {
            'произвольный': 'Произвольный',
            'день': 'Произвольный',
            'неделя': 'Произвольный',
            'месяц': 'Произвольный',
            '7_дней': 'Произвольный',
            'сегодня': 'Произвольный'
        }

        # Значения для причины обращения
        self.REASON_VALUES = {
            'низкая_скорость_3g_4g': 'Низкая скорость в 3G/4G',
            'низкая_скорость': 'Низкая скорость в 3G/4G',
            '3g_4g': 'Низкая скорость в 3G/4G',
            'default': 'Низкая скорость в 3G/4G'
        }

        # Флаг для работы с iframe
        self.iframe_mode = True

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

            # Ждем 10 секунд после открытия страницы (она долго загружается)
            self.logger.info("⏳ Ждем 10 секунд для полной загрузки страницы...")
            import time
            time.sleep(10)

            # 1. Устанавливаем "Период отчета"
            if not self._set_report_period(period):
                return False

            # Ждем активации полей дат
            self.logger.info("⏳ Ждем активации полей дат...")
            time.sleep(3)

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

            # Работаем с iframe если включен режим
            if self.iframe_mode:
                return self._set_report_period_in_iframe(period_value)
            else:
                return self._set_report_period_in_main_document(period_value)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета: {e}")
            return False

    def _set_report_period_in_iframe(self, period_value):
        """Устанавливает период отчета в iframe'е."""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe")

            try:
                # Ищем поле периода отчета
                period_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['period_dropdown']))
                )

                # Проверяем, заблокировано ли поле
                if 'aspNetDisabled' in period_dropdown.get_attribute('class') or 'disabled' in period_dropdown.get_attribute('class'):
                    self.logger.info("🔓 Поле 'Период отчета' заблокировано, пытаемся разблокировать...")

                    # Пытаемся разблокировать поле
                    self.driver.execute_script("arguments[0].removeAttribute('disabled');", period_dropdown)
                    self.driver.execute_script("arguments[0].classList.remove('aspNetDisabled');", period_dropdown)
                    self.driver.execute_script("arguments[0].classList.remove('DisabledTextBox');", period_dropdown)

                    # Ждем немного
                    time.sleep(1)

                    # Проверяем, разблокировалось ли поле
                    if 'aspNetDisabled' not in period_dropdown.get_attribute('class'):
                        self.logger.info("✅ Поле 'Период отчета' разблокировано")
                    else:
                        self.logger.warning("⚠️ Не удалось разблокировать поле 'Период отчета'")

                # Устанавливаем значение
                period_select = Select(period_dropdown)

                # Пробуем найти опцию по тексту
                try:
                    period_select.select_by_visible_text(period_value)
                    self.logger.info(f"✅ Период отчета установлен: {period_value}")
                except:
                    # Если не получилось, пробуем найти по частичному совпадению
                    options = period_select.options
                    for option in options:
                        if period_value.lower() in option.text.lower():
                            period_select.select_by_visible_text(option.text)
                            self.logger.info(f"✅ Период отчета установлен: {option.text}")
                            break
                    else:
                        # Если ничего не нашли, выбираем первую опцию
                        period_select.select_by_index(0)
                        self.logger.warning(f"⚠️ Не удалось найти точное совпадение, выбрана первая опция: {period_select.first_selected_option.text}")

                # Ждем разблокировки других полей
                self.logger.info("⏳ Ждем разблокировки полей дат...")
                time.sleep(3)

                return True

            finally:
                # Возвращаемся в основной документ
                self.driver.switch_to.default_content()
                self.logger.info("✅ Вернулись в основной документ")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета в iframe: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _set_report_period_in_main_document(self, period_value):
        """Устанавливает период отчета в основном документе (старый метод)."""
        try:
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

            self.logger.info(f"✅ Период отчета установлен: {period_value}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета: {e}")
            return False

    def _set_start_date(self, start_date):
        """Устанавливает дату начала."""
        try:
            # Работаем с iframe если включен режим
            if self.iframe_mode:
                return self._set_start_date_in_iframe(start_date)
            else:
                return self._set_start_date_in_main_document(start_date)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты начала: {e}")
            return False

    def _set_start_date_in_iframe(self, start_date):
        """Устанавливает дату начала в iframe'е."""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe для установки даты начала")

            try:
                # Ищем поле даты начала
                start_date_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['start_date_field']))
                )

                # Проверяем, заблокировано ли поле
                if 'aspNetDisabled' in start_date_field.get_attribute('class') or 'disabled' in start_date_field.get_attribute('class'):
                    self.logger.warning("⚠️ Поле 'Дата начала' все еще заблокировано. Возможно, нужно сначала выбрать период отчета.")
                    return False

                # Устанавливаем дату
                start_date_field.clear()
                start_date_field.send_keys(start_date.strftime("%d.%m.%Y"))

                self.logger.info(f"✅ Дата начала установлена: {start_date.strftime('%d.%m.%Y')}")
                return True

            finally:
                # Возвращаемся в основной документ
                self.driver.switch_to.default_content()
                self.logger.info("✅ Вернулись в основной документ")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты начала в iframe: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _set_start_date_in_main_document(self, start_date):
        """Устанавливает дату начала в основном документе (старый метод)."""
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
            # Работаем с iframe если включен режим
            if self.iframe_mode:
                return self._set_end_date_in_iframe(end_date)
            else:
                return self._set_end_date_in_main_document(end_date)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания: {e}")
            return False

    def _set_end_date_in_iframe(self, end_date):
        """Устанавливает дату окончания в iframe'е."""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe для установки даты окончания")

            try:
                # Ищем поле даты окончания
                end_date_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['end_date_field']))
                )

                # Проверяем, заблокировано ли поле
                if 'aspNetDisabled' in end_date_field.get_attribute('class') or 'disabled' in end_date_field.get_attribute('class'):
                    self.logger.warning("⚠️ Поле 'Дата окончания' все еще заблокировано. Возможно, нужно сначала выбрать период отчета.")
                    return False

                # Устанавливаем дату
                end_date_field.clear()
                end_date_field.send_keys(end_date.strftime("%d.%m.%Y"))

                self.logger.info(f"✅ Дата окончания установлена: {end_date.strftime('%d.%m.%Y')}")
                return True

            finally:
                # Возвращаемся в основной документ
                self.driver.switch_to.default_content()
                self.logger.info("✅ Вернулись в основной документ")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания в iframe: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _set_end_date_in_main_document(self, end_date):
        """Устанавливает дату окончания в основном документе (старый метод)."""
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
            # Работаем с iframe если включен режим
            if self.iframe_mode:
                return self._set_reason_in_iframe(reason)
            else:
                return self._set_reason_in_main_document(reason)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке причины обращения: {e}")
            return False

    def _set_reason_in_iframe(self, reason):
        """Устанавливает причину обращения в iframe'е."""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe для установки причины обращения")

            try:
                # Ищем поле причины обращения
                reason_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['reason_dropdown']))
                )

                # Проверяем, заблокировано ли поле
                if 'aspNetDisabled' in reason_field.get_attribute('class') or 'disabled' in reason_field.get_attribute('class'):
                    self.logger.warning("⚠️ Поле 'Причина обращения' все еще заблокировано. Возможно, нужно сначала выбрать период отчета.")
                    return False

                # Устанавливаем причину обращения
                reason_field.clear()
                reason_field.send_keys(self.REASON_VALUES.get(reason.lower(), self.REASON_VALUES['default']))

                self.logger.info(f"✅ Причина обращения установлена: {self.REASON_VALUES.get(reason.lower(), self.REASON_VALUES['default'])}")
                return True

            finally:
                # Возвращаемся в основной документ
                self.driver.switch_to.default_content()
                self.logger.info("✅ Вернулись в основной документ")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке причины обращения в iframe: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _set_reason_in_main_document(self, reason):
        """Устанавливает причину обращения в основном документе (старый метод)."""
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

            # Работаем с iframe если включен режим
            if self.iframe_mode:
                return self._submit_report_request_in_iframe(wait_time)
            else:
                return self._submit_report_request_in_main_document(wait_time)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке запроса: {e}")
            return False

    def _submit_report_request_in_iframe(self, wait_time):
        """Отправляет запрос на формирование отчета в iframe'е."""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe для отправки отчета")

            try:
                # Ищем кнопку отправки
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, self.ELEMENT_IDS['submit_button']))
                )

                # Проверяем, готова ли кнопка
                if not self._wait_for_element_ready(submit_button):
                    self.logger.error("❌ Кнопка отправки не готова к взаимодействию")
                    return False

                # Кликаем по кнопке
                submit_button.click()
                self.logger.info("✅ Запрос на формирование отчета отправлен")

                # Ждем загрузки отчета с периодической проверкой
                self.logger.info("⏳ Ожидание загрузки отчета...")
                if not self._wait_for_report_loaded(wait_time):
                    self.logger.error("❌ Таймаут ожидания загрузки отчета")
                    return False

                return True

            finally:
                # Возвращаемся в основной документ
                self.driver.switch_to.default_content()
                self.logger.info("✅ Вернулись в основной документ")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке запроса в iframe: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _submit_report_request_in_main_document(self, wait_time):
        """Отправляет запрос на формирование отчета в основном документе (старый метод)."""
        try:
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

            # Кнопка сохранения находится вне iframe'а, ищем в основном документе
            self.logger.info("🔍 Ищем кнопку сохранения в основном документе...")

            # Ищем кнопку сохранения/экспорта
            save_button_selectors = [
                "//*[contains(text(), 'Сохранить')]",
                "//*[contains(text(), 'Save')]",
                "//*[contains(text(), 'Экспорт')]",
                "//*[contains(text(), 'Export')]",
                "//*[contains(text(), 'Excel')]",
                "//button[contains(text(), 'Сохранить')]",
                "//button[contains(text(), 'Save')]",
                "//a[contains(text(), 'Сохранить')]",
                "//a[contains(text(), 'Save')]",
                "//input[contains(@value, 'Сохранить')]",
                "//input[contains(@value, 'Save')]"
            ]

            save_button = None
            for selector in save_button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        save_button = elements[0]
                        self.logger.info(f"✅ Кнопка сохранения найдена по селектору: {selector}")
                        break
                except:
                    continue

            if not save_button:
                self.logger.error("❌ Кнопка сохранения не найдена")
                return False

            # Кликаем по кнопке сохранения
            self.logger.info("🖱️ Кликаем по кнопке сохранения...")
            save_button.click()

            # Ждем появления выпадающего списка
            self.logger.info("⏳ Ждем появления выпадающего списка...")
            time.sleep(2)

            # Ищем выпадающий список с опциями сохранения
            dropdown_selectors = [
                "//select[contains(@id, 'format') or contains(@id, 'Format')]",
                "//select[contains(@name, 'format') or contains(@name, 'Format')]",
                "//select[contains(@class, 'format') or contains(@class, 'Format')]",
                "//div[contains(@class, 'dropdown')]//select",
                "//div[contains(@class, 'menu')]//select",
                "//ul[contains(@class, 'dropdown')]//select",
                "//ul[contains(@class, 'menu')]//select"
            ]

            format_dropdown = None
            for selector in dropdown_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        format_dropdown = elements[0]
                        self.logger.info(f"✅ Выпадающий список форматов найден по селектору: {selector}")
                        break
                except:
                    continue

            if format_dropdown:
                # Выбираем Excel из выпадающего списка
                try:
                    format_select = Select(format_dropdown)

                    # Ищем опцию Excel
                    excel_options = []
                    for option in format_select.options:
                        if 'excel' in option.text.lower() or 'xlsx' in option.text.lower() or 'xls' in option.text.lower():
                            excel_options.append(option)

                    if excel_options:
                        # Выбираем первую найденную опцию Excel
                        format_select.select_by_visible_text(excel_options[0].text)
                        self.logger.info(f"✅ Выбран формат: {excel_options[0].text}")
                    else:
                        # Если не нашли Excel, выбираем первую опцию
                        format_select.select_by_index(0)
                        self.logger.warning(f"⚠️ Excel не найден, выбрана первая опция: {format_select.first_selected_option.text}")

                except Exception as e:
                    self.logger.warning(f"⚠️ Не удалось выбрать формат из выпадающего списка: {e}")

            # Ищем кнопку подтверждения сохранения
            confirm_selectors = [
                "//*[contains(text(), 'ОК')]",
                "//*[contains(text(), 'OK')]",
                "//*[contains(text(), 'Подтвердить')]",
                "//*[contains(text(), 'Confirm')]",
                "//*[contains(text(), 'Сохранить')]",
                "//*[contains(text(), 'Save')]",
                "//button[contains(text(), 'ОК')]",
                "//button[contains(text(), 'OK')]",
                "//input[contains(@value, 'ОК')]",
                "//input[contains(@value, 'OK')]"
            ]

            confirm_button = None
            for selector in confirm_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        confirm_button = elements[0]
                        self.logger.info(f"✅ Кнопка подтверждения найдена по селектору: {selector}")
                        break
                except:
                    continue

            if confirm_button:
                # Кликаем по кнопке подтверждения
                self.logger.info("🖱️ Кликаем по кнопке подтверждения...")
                confirm_button.click()
                self.logger.info("✅ Экспорт в Excel инициирован")
            else:
                self.logger.info("ℹ️ Кнопка подтверждения не найдена, возможно сохранение началось автоматически")

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
