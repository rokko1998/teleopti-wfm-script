"""
Модуль для заполнения формы отчета
"""

from selenium.webdriver.support.ui import Select
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

                self.logger.info("📋 Открываем выпадающий список причины обращения...")
                dropdown_toggle.click()

                # Ждем появления выпадающего списка
                time.sleep(2)

                # 2. Теперь нажимаем "Выделить все" чтобы снять все галочки
                select_all_selector = self.form_elements.get_dropdown_selector('reason_select_all')
                if not select_all_selector:
                    self.logger.error("❌ Селектор 'Выделить все' не найден")
                    return False

                # Пробуем найти чекбокс "Выделить все"
                select_all_checkbox = self.iframe_handler.find_element_in_iframe(select_all_selector)
                if not select_all_checkbox:
                    self.logger.warning("⚠️ Чекбокс 'Выделить все' не найден по селектору, пробуем найти по тексту...")

                    # Fallback: ищем по тексту "Выделить все"
                    try:
                        select_all_checkbox = self.iframe_handler.find_element_in_iframe(
                            ("xpath", "//input[@type='checkbox' and following-sibling::label[contains(text(), 'Выделить все')]]")
                        )
                        if select_all_checkbox:
                            self.logger.info("✅ Чекбокс 'Выделить все' найден по тексту")
                        else:
                            self.logger.warning("⚠️ Чекбокс 'Выделить все' не найден даже по тексту, продолжаем...")
                            # Продолжаем без снятия галочек
                    except:
                        self.logger.warning("⚠️ Не удалось найти 'Выделить все', продолжаем...")
                        # Продолжаем без снятия галочек
                else:
                    self.logger.info("🗑️ Снимаем все галочки через 'Выделить все'...")
                    select_all_checkbox.click()

                # Ждем применения изменений
                time.sleep(1)

                                # 3. Теперь выбираем нужный чекбокс (пробуем label, затем fallback)
                self.logger.info("🔍 Ищем чекбокс 'Низкая скорость в 3G/4G'...")

                # Пробуем найти по label тексту (тихо, без ошибок в логах)
                checkbox = None
                try:
                    # Ищем label с ТОЧНЫМ текстом (строго по названию) В IFRAME
                    label_xpath = """//label[
                        normalize-space(text()) = 'Интернет >> Низкая скорость в 3G/4G' or
                        normalize-space(.) = 'Интернет >> Низкая скорость в 3G/4G' or
                        normalize-space(text()) = 'Интернет&nbsp;&gt;&gt;&nbsp;Низкая&nbsp;скорость&nbsp;в&nbsp;3G/4G' or
                        normalize-space(.) = 'Интернет&nbsp;&gt;&gt;&nbsp;Низкая&nbsp;скорость&nbsp;в&nbsp;3G/4G'
                    ]"""

                    # Ищем через iframe_handler, а не через driver напрямую
                    label = self.iframe_handler.find_element_in_iframe(("xpath", label_xpath))
                    if not label:
                        raise Exception("Label не найден в iframe")

                    # Дополнительная проверка - убеждаемся что это именно нужный label
                    label_text = label.text.strip()
                    if "Интернет" in label_text and "Низкая скорость" in label_text and "3G/4G" in label_text:
                        self.logger.info(f"✅ Найден правильный label: '{label_text}'")

                        # Получаем for атрибут и ищем соответствующий input
                        for_attr = label.get_attribute("for")
                        if for_attr:
                            checkbox = self.iframe_handler.find_element_in_iframe(("id", for_attr))
                            if checkbox:
                                self.logger.info(f"✅ Чекбокс найден по label с for='{for_attr}'")
                            else:
                                raise Exception("Чекбокс не найден по for атрибуту")
                        else:
                            # Если нет for, ищем input рядом с label
                            checkbox = label.find_element("xpath", "./following-sibling::input[@type='checkbox']")
                            self.logger.info("✅ Чекбокс найден рядом с label")
                    else:
                        self.logger.warning(f"⚠️ Найден label не подходит: '{label_text}'")
                        raise Exception("Label не содержит нужный текст")

                except Exception:
                    # Тихий fallback без ошибок в логах
                    pass

                    # Fallback: используем старый метод
                    checkbox_selector = self.form_elements.get_dropdown_selector('reason_checkbox')
                    if checkbox_selector:
                        self.logger.info(f"🔄 Fallback: ищем по селектору '{checkbox_selector}'")
                        checkbox = self.iframe_handler.find_element_in_iframe(checkbox_selector)
                        if checkbox:
                            # Проверяем что нашли правильный чекбокс
                            try:
                                # Ищем label для этого чекбокса
                                checkbox_id = checkbox.get_attribute("id")
                                if checkbox_id:
                                    label = self.iframe_handler.find_element_in_iframe(
                                        ("xpath", f"//label[@for='{checkbox_id}']")
                                    )
                                    if label:
                                        label_text = label.text.strip()
                                        self.logger.info(f"✅ Fallback: найден чекбокс с label '{label_text}'")
                                        if "Интернет" in label_text and "Низкая скорость" in label_text:
                                            self.logger.info("✅ Это правильный чекбокс!")
                                        else:
                                            self.logger.warning(f"⚠️ Fallback нашел неправильный чекбокс: '{label_text}'")
                                            checkbox = None
                                    else:
                                        self.logger.info(f"✅ Fallback: найден чекбокс с ID '{checkbox_id}' (без label)")
                                else:
                                    self.logger.info("✅ Fallback: найден чекбокс без ID")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Ошибка при проверке fallback чекбокса: {e}")
                                checkbox = None
                        else:
                            self.logger.warning("⚠️ Fallback селектор не нашел чекбокс")
                    else:
                        self.logger.warning("⚠️ Fallback селектор не определен")

                if not checkbox:
                    self.logger.error("❌ Чекбокс 'Низкая скорость в 3G/4G' не найден ни одним способом")
                    return False

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
