"""
Модуль для заполнения формы отчета
"""

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from loguru import logger
import time


class FormFiller:
    """Класс для заполнения формы отчета"""

    def __init__(self, driver, logger, iframe_handler, form_elements):
        self.driver = driver
        self.logger = logger
        self.iframe_handler = iframe_handler
        self.form_elements = form_elements

    def set_report_period(self, period_name='произвольный'):
        """Установить период отчета"""
        try:
            self.logger.info(f"📊 Устанавливаем период отчета: {period_name}")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле периода отчета с диагностикой
                period_selector = self.form_elements.get_element_selector('period_dropdown')
                period_field = self.iframe_handler.find_element_with_diagnostics(period_selector)

                if not period_field:
                    self.logger.error("❌ Поле периода отчета не найдено")
                    return False

                # Проверяем, что это SELECT элемент
                if period_field.tag_name.lower() != 'select':
                    self.logger.error(f"❌ Поле периода отчета не является SELECT элементом. Найден: {period_field.tag_name}")
                    self.logger.info(f"   ID элемента: {period_field.get_attribute('id')}")
                    self.logger.info(f"   Классы элемента: {period_field.get_attribute('class')}")
                    return False

                # Получаем значение для периода
                period_value = self.form_elements.get_period_value(period_name)
                if not period_value:
                    self.logger.error(f"❌ Неизвестный период: {period_name}")
                    return False

                # Создаем объект Select и выбираем значение
                period_select = Select(period_field)
                period_select.select_by_value(period_value)

                self.logger.info(f"✅ Период отчета установлен: {period_name} (значение: {period_value})")

                # Ждем завершения postback (ASP.NET WebForms)
                self.logger.info("⏳ Ждем завершения postback после выбора периода...")
                time.sleep(3)

                # После postback ищем элементы заново (избегаем stale element reference)
                self.logger.info("🔍 Проверяем готовность элементов после postback...")

                # Проверяем, что поля дат стали доступными
                start_date_selector = self.form_elements.get_element_selector('start_date_field')
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

                if start_date_field and not start_date_field.get_attribute('disabled') and 'aspNetDisabled' not in start_date_field.get_attribute('class'):
                    self.logger.info("✅ Поля дат разблокированы после выбора периода")
                else:
                    self.logger.warning("⚠️ Поля дат все еще заблокированы, возможно нужна дополнительная задержка")
                    time.sleep(2)

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_start_date(self):
        """Установить дату начала"""
        try:
            self.logger.info("📅 Устанавливаем дату начала")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле даты начала
                start_date_selector = self.form_elements.get_element_selector('start_date_field')
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

                if not start_date_field:
                    self.logger.error("❌ Поле даты начала не найдено")
                    return False

                # Получаем тестовую дату
                start_date = self.form_elements.get_test_date('start_date')

                # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
                self.logger.info(f"📝 Устанавливаем дату через JavaScript: {start_date}")
                self.driver.execute_script("arguments[0].value = arguments[1];", start_date_field, start_date)

                # Триггерим событие onchange для активации JavaScript обработчиков
                self.logger.info("🔄 Триггерим onchange событие...")
                self.driver.execute_script("arguments[0].onchange();", start_date_field)

                # Ждем завершения postback (ASP.NET WebForms)
                self.logger.info("⏳ Ждем завершения postback...")
                time.sleep(3)

                # После postback ищем элемент заново (избегаем stale element reference)
                self.logger.info("🔍 Ищем элемент даты начала заново после postback...")
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)
                if not start_date_field:
                    self.logger.error("❌ Элемент даты начала не найден после postback")
                    return False

                # Проверяем, что значение установилось
                actual_value = start_date_field.get_attribute('value')
                if start_date in actual_value:
                    self.logger.info(f"✅ Дата начала установлена: {start_date}")
                else:
                    self.logger.warning(f"⚠️ Дата установлена, но значение отличается: {actual_value}")

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты начала: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_end_date(self):
        """Установить дату окончания"""
        try:
            self.logger.info("📅 Устанавливаем дату окончания")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле даты окончания
                end_date_selector = self.form_elements.get_element_selector('end_date_field')
                end_date_field = self.iframe_handler.find_element_in_iframe(end_date_selector)

                if not end_date_field:
                    self.logger.error("❌ Поле даты окончания не найдено")
                    return False

                # Получаем тестовую дату
                end_date = self.form_elements.get_test_date('end_date')

                # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
                self.logger.info(f"📝 Устанавливаем дату через JavaScript: {end_date}")
                self.driver.execute_script("arguments[0].value = arguments[1];", end_date_field, end_date)

                # У поля даты окончания нет onchange обработчика, просто ждем
                self.logger.info("⏳ Ждем применения изменений...")
                time.sleep(2)

                # Проверяем, что значение установилось
                actual_value = end_date_field.get_attribute('value')
                if end_date in actual_value:
                    self.logger.info(f"✅ Дата окончания установлена: {end_date}")
                else:
                    self.logger.warning(f"⚠️ Дата установлена, но значение отличается: {actual_value}")

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_reason(self):
        """Установить причину обращения через выпадающий список с чекбоксами"""
        try:
            self.logger.info("🔍 Устанавливаем причину обращения")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # 1. Сначала нажимаем на кнопку выпадающего списка
                dropdown_toggle_selector = self.form_elements.get_dropdown_selector('reason_dropdown_toggle')
                if not dropdown_toggle_selector:
                    self.logger.error("❌ Селектор кнопки выпадающего списка не найден")
                    return False

                dropdown_toggle = self.iframe_handler.find_element_in_iframe(dropdown_toggle_selector)
                if not dropdown_toggle:
                    self.logger.error("❌ Кнопка выпадающего списка не найдена")
                    return False

                # Детальная диагностика кнопки выпадающего списка
                self.logger.info(f"📋 Кнопка выпадающего списка найдена:")
                self.logger.info(f"   • Селектор: {dropdown_toggle_selector}")
                self.logger.info(f"   • Текст: '{dropdown_toggle.text}'")
                self.logger.info(f"   • Класс: {dropdown_toggle.get_attribute('class')}")
                self.logger.info(f"   • ID: {dropdown_toggle.get_attribute('id')}")
                self.logger.info(f"   • Видима: {dropdown_toggle.is_displayed()}")
                self.logger.info(f"   • Кликабельна: {dropdown_toggle.is_enabled()}")

                self.logger.info("📋 Открываем выпадающий список причины обращения...")
                dropdown_toggle.click()

                # Ждем появления выпадающего списка
                time.sleep(2)
                
                # Анализируем все доступные варианты в выпадающем списке
                self.logger.info("🔍 Анализируем все доступные варианты в выпадающем списке...")
                self._analyze_dropdown_options()

                # 2. Теперь нажимаем "Выделить все" чтобы снять все галочки
                select_all_selector = self.form_elements.get_dropdown_selector('reason_select_all')
                if not select_all_selector:
                    self.logger.error("❌ Селектор 'Выделить все' не найден")
                    return False

                select_all_checkbox = self.iframe_handler.find_element_in_iframe(select_all_selector)
                if not select_all_checkbox:
                    self.logger.error("❌ Чекбокс 'Выделить все' не найден")
                    return False

                # Детальная диагностика чекбокса "Выделить все"
                self.logger.info(f"🗑️ Чекбокс 'Выделить все' найден:")
                self.logger.info(f"   • Селектор: {select_all_selector}")
                self.logger.info(f"   • Текст: '{select_all_checkbox.text}'")
                self.logger.info(f"   • Класс: {select_all_checkbox.get_attribute('class')}")
                self.logger.info(f"   • ID: {select_all_checkbox.get_attribute('id')}")
                self.logger.info(f"   • Выбран: {select_all_checkbox.is_selected()}")
                self.logger.info(f"   • Видим: {select_all_checkbox.is_displayed()}")
                self.logger.info(f"   • Кликабелен: {select_all_checkbox.is_enabled()}")

                self.logger.info("🗑️ Снимаем все галочки через 'Выделить все'...")
                select_all_checkbox.click()

                # Ждем применения изменений
                time.sleep(1)

                # 3. Теперь выбираем нужный чекбокс
                checkbox_selector = self.form_elements.get_dropdown_selector('reason_checkbox')
                if not checkbox_selector:
                    self.logger.error("❌ Селектор чекбокса не найден")
                    return False

                checkbox = self.iframe_handler.find_element_in_iframe(checkbox_selector)
                if not checkbox:
                    self.logger.error("❌ Чекбокс 'Низкая скорость в 3G/4G' не найден")
                    return False

                # Детальная диагностика основного чекбокса
                self.logger.info(f"✅ Основной чекбокс найден:")
                self.logger.info(f"   • Селектор: {checkbox_selector}")
                self.logger.info(f"   • Текст: '{checkbox.text}'")
                self.logger.info(f"   • Класс: {checkbox.get_attribute('class')}")
                self.logger.info(f"   • ID: {checkbox.get_attribute('id')}")
                self.logger.info(f"   • Выбран: {checkbox.is_selected()}")
                self.logger.info(f"   • Видим: {checkbox.is_displayed()}")
                self.logger.info(f"   • Кликабелен: {checkbox.is_enabled()}")

                # Проверяем, не выбран ли уже чекбокс
                if not checkbox.is_selected():
                    self.logger.info("✅ Выбираем чекбокс 'Низкая скорость в 3G/4G'...")
                    checkbox.click()
                else:
                    self.logger.info("✅ Чекбокс 'Низкая скорость в 3G/4G' уже выбран")

                # Ждем применения выбора
                time.sleep(1)

                self.logger.info("✅ Причина обращения установлена: Низкая скорость в 3G/4G")
                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке причины обращения: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def submit_report(self):
        """Отправить отчет"""
        try:
            self.logger.info("🚀 Отправляем отчет")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем кнопку отправки
                submit_selector = self.form_elements.get_element_selector('submit_button')
                submit_button = self.iframe_handler.wait_for_element_clickable(submit_selector)

                if not submit_button:
                    self.logger.error("❌ Кнопка отправки не найдена или не кликабельна")
                    return False

                # Нажимаем кнопку
                submit_button.click()

                self.logger.info("✅ Отчет отправлен")
                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке отчета: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def _analyze_dropdown_options(self):
        """Анализировать все доступные варианты в выпадающем списке"""
        try:
            # Ищем все чекбоксы в выпадающем списке
            all_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            if not all_checkboxes:
                self.logger.warning("⚠️ Чекбоксы в выпадающем списке не найдены")
                return
            
            self.logger.info(f"📋 Найдено {len(all_checkboxes)} чекбоксов в выпадающем списке:")
            
            for i, checkbox in enumerate(all_checkboxes):
                try:
                    # Получаем родительский элемент для текста
                    parent = checkbox.find_element(By.XPATH, "./..")
                    text = parent.text.strip() if parent else "Без текста"
                    
                    # Получаем атрибуты чекбокса
                    checkbox_id = checkbox.get_attribute('id') or 'Нет ID'
                    checkbox_class = checkbox.get_attribute('class') or 'Нет класса'
                    is_selected = checkbox.is_selected()
                    is_displayed = checkbox.is_displayed()
                    is_enabled = checkbox.is_enabled()
                    
                    self.logger.info(f"   • Чекбокс {i+1}:")
                    self.logger.info(f"     - Текст: '{text}'")
                    self.logger.info(f"     - ID: {checkbox_id}")
                    self.logger.info(f"     - Класс: {checkbox_class}")
                    self.logger.info(f"     - Выбран: {is_selected}")
                    self.logger.info(f"     - Видим: {is_displayed}")
                    self.logger.info(f"     - Кликабелен: {is_enabled}")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Не удалось проанализировать чекбокс {i+1}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при анализе вариантов выпадающего списка: {e}")
