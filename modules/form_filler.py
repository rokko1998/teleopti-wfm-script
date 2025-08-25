"""
Модуль для заполнения формы отчета
"""

from selenium.webdriver.support.ui import Select
import logging
import time


class FormFiller:
    """Класс для заполнения формы отчета"""

    def __init__(self, driver, logger, iframe_handler, form_elements):
        self.driver = driver
        self.logger = logger
        self.iframe_handler = iframe_handler
        self.form_elements = form_elements

    def set_report_period(self):
        """Установить период отчета"""
        try:
            self.logger.info("[form_filler] 📊 Устанавливаем период отчета: произвольный")
            
            # Получаем селектор и значение для периода
            period_selector = self.form_elements.get_element_selector('period_dropdown')
            period_value = self.form_elements.get_period_value('произвольный')
            
            if not period_selector or not period_value:
                self.logger.error("[form_filler] ❌ Не удалось получить селектор или значение для периода отчета")
                return False
            
            # Ищем поле периода отчета
            period_field = self.iframe_handler.find_element_in_iframe(period_selector)
            
            if not period_field:
                self.logger.error("[form_filler] ❌ Поле периода отчета не найдено")
                return False
            
            # Проверяем, что это select элемент
            if period_field.tag_name != 'select':
                self.logger.error(f"[form_filler] ❌ Элемент периода отчета не является select (тег: {period_field.tag_name})")
                return False
            
            # Создаем объект Select и выбираем значение
            period_select = Select(period_field)
            period_select.select_by_value(period_value)
            
            self.logger.info(f"[form_filler] ✅ Период отчета установлен: произвольный (значение: {period_value})")
            
            # Ждем завершения postback (ASP.NET WebForms)
            self.logger.info("[form_filler] ⏳ Ждем завершения postback после выбора периода...")
            time.sleep(3)
            
            # После postback ищем элементы заново (избегаем stale element reference)
            self.logger.info("[form_filler] 🔍 Проверяем готовность элементов после postback...")
            
            # Проверяем, что поля дат стали доступными
            start_date_selector = self.form_elements.get_element_selector('start_date_field')
            start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)
            
            if start_date_field and not start_date_field.get_attribute('disabled') and 'aspNetDisabled' not in start_date_field.get_attribute('class'):
                self.logger.info("[form_filler] ✅ Поля дат разблокированы после выбора периода")
            else:
                self.logger.warning("[form_filler] ⚠️ Поля дат все еще заблокированы, возможно нужна дополнительная задержка")
                time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[form_filler] ❌ Ошибка при установке периода отчета: {e}")
            return False

    def set_start_date(self):
        """Установить дату начала отчета"""
        try:
            self.logger.info("[form_filler] 📅 Устанавливаем дату начала отчета...")

            # Получаем селектор и тестовую дату
            start_date_selector = self.form_elements.get_element_selector('start_date_field')
            start_date = self.form_elements.get_test_date('start_date')

            # Ищем поле даты начала
            start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

            if not start_date_field:
                self.logger.error("[form_filler] ❌ Поле даты начала не найдено")
                return False

            # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
            self.logger.info(f"[form_filler] 📝 Устанавливаем дату через JavaScript: {start_date}")
            self.driver.execute_script("arguments[0].value = arguments[1];", start_date_field, start_date)

            # У поля даты начала есть onchange обработчик, вызываем его
            self.logger.info("[form_filler] 🔄 Вызываем onchange событие...")
            self.driver.execute_script("arguments[0].onchange();", start_date_field)

            # Ждем завершения postback (ASP.NET WebForms)
            self.logger.info("[form_filler] ⏳ Ждем завершения postback после установки даты...")
            time.sleep(3)

            # После postback ищем элемент заново (избегаем stale element reference)
            start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

            # Проверяем, что значение установилось
            actual_value = start_date_field.get_attribute('value')
            if actual_value == start_date:
                self.logger.info(f"[form_filler] ✅ Дата начала установлена: {actual_value}")
            else:
                self.logger.warning(f"[form_filler] ⚠️ Дата установлена, но значение отличается: {actual_value}")

            return True

        except Exception as e:
            self.logger.error(f"[form_filler] ❌ Ошибка при установке даты начала: {e}")
            return False

    def set_end_date(self):
        """Установить дату окончания отчета"""
        try:
            self.logger.info("[form_filler] 📅 Устанавливаем дату окончания отчета...")

            # Получаем селектор и тестовую дату
            end_date_selector = self.form_elements.get_element_selector('end_date_field')
            end_date = self.form_elements.get_test_date('end_date')

            # Ищем поле даты окончания
            end_date_field = self.iframe_handler.find_element_in_iframe(end_date_selector)

            if not end_date_field:
                self.logger.error("[form_filler] ❌ Поле даты окончания не найдено")
                return False

            # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
            self.logger.info(f"[form_filler] 📝 Устанавливаем дату через JavaScript: {end_date}")
            self.driver.execute_script("arguments[0].value = arguments[1];", end_date_field, end_date)

            # У поля даты окончания нет onchange обработчика, просто ждем
            self.logger.info("[form_filler] ⏳ Ждем применения изменений...")
            time.sleep(2)

            # Проверяем, что значение установилось
            actual_value = end_date_field.get_attribute('value')
            if actual_value == end_date:
                self.logger.info(f"[form_filler] ✅ Дата окончания установлена: {actual_value}")
            else:
                self.logger.warning(f"[form_filler] ⚠️ Дата установлена, но значение отличается: {actual_value}")

            return True

        except Exception as e:
            self.logger.error(f"[form_filler] ❌ Ошибка при установке даты окончания: {e}")
            return False

    def set_reason(self):
        """Установить причину обращения через выпадающий список с чекбоксами"""
        try:
            self.logger.info("[form_filler] 🔍 Устанавливаем причину обращения")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # 1. Сначала нажимаем на кнопку выпадающего списка
                dropdown_toggle_selector = self.form_elements.get_dropdown_selector('reason_dropdown_toggle')
                if not dropdown_toggle_selector:
                    self.logger.error("[form_filler] ❌ Селектор кнопки выпадающего списка не найден")
                    return False

                dropdown_toggle = self.iframe_handler.find_element_in_iframe(dropdown_toggle_selector)
                if not dropdown_toggle:
                    self.logger.error("[form_filler] ❌ Кнопка выпадающего списка не найдена")
                    return False

                self.logger.info("[form_filler] 📋 Открываем выпадающий список причины обращения...")
                dropdown_toggle.click()

                # Ждем появления выпадающего списка
                time.sleep(2)

                # 2. Теперь нажимаем "Выделить все" чтобы снять все галочки
                select_all_selector = self.form_elements.get_dropdown_selector('reason_select_all')
                if not select_all_selector:
                    self.logger.error("[form_filler] ❌ Селектор 'Выделить все' не найден")
                    return False

                select_all_checkbox = self.iframe_handler.find_element_in_iframe(select_all_selector)
                if not select_all_checkbox:
                    self.logger.error("[form_filler] ❌ Чекбокс 'Выделить все' не найден")
                    return False

                self.logger.info("[form_filler] 🗑️ Снимаем все галочки через 'Выделить все'...")
                select_all_checkbox.click()

                # Ждем применения изменений
                time.sleep(1)

                # 3. Теперь выбираем нужный чекбокс
                checkbox_selector = self.form_elements.get_dropdown_selector('reason_checkbox')
                if not checkbox_selector:
                    self.logger.error("[form_filler] ❌ Селектор чекбокса не найден")
                    return False

                checkbox = self.iframe_handler.find_element_in_iframe(checkbox_selector)
                if not checkbox:
                    self.logger.error("[form_filler] ❌ Чекбокс 'Низкая скорость в 3G/4G' не найден")
                    return False

                # Проверяем, не выбран ли уже чекбокс
                if not checkbox.is_selected():
                    self.logger.info("[form_filler] ✅ Выбираем чекбокс 'Низкая скорость в 3G/4G'...")
                    checkbox.click()
                else:
                    self.logger.info("[form_filler] ✅ Чекбокс 'Низкая скорость в 3G/4G' уже выбран")

                # Ждем применения выбора
                time.sleep(1)

                self.logger.info("[form_filler] ✅ Причина обращения установлена: Низкая скорость в 3G/4G")
                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"[form_filler] ❌ Ошибка при установке причины обращения: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def submit_report(self):
        """Отправить запрос на формирование отчета"""
        try:
            self.logger.info("[form_filler] 🚀 Отправляем запрос на формирование отчета...")

            # Получаем селектор кнопки отправки
            submit_selector = self.form_elements.get_element_selector('submit_button')

            # Ищем кнопку отправки
            submit_button = self.iframe_handler.find_element_in_iframe(submit_selector)

            if not submit_button:
                self.logger.error("[form_filler] ❌ Кнопка отправки отчета не найдена")
                return False

            # Проверяем, что кнопка активна
            if not submit_button.is_enabled():
                self.logger.error("[form_filler] ❌ Кнопка отправки отчета неактивна")
                return False

            # Кликаем по кнопке
            self.logger.info("[form_filler] 💾 Нажимаем кнопку 'Просмотр отчета'...")
            submit_button.click()

            self.logger.info("[form_filler] ✅ Запрос на формирование отчета отправлен")
            return True

        except Exception as e:
            self.logger.error(f"[form_filler] ❌ Ошибка при отправке отчета: {e}")
            return False
