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

    def set_report_period(self, period_name='произвольный'):
        """Установить период отчета"""
        try:
            self.logger.info(f"📊 Устанавливаем период отчета: {period_name}")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле периода отчета
                period_selector = self.form_elements.get_element_selector('period_dropdown')
                period_field = self.iframe_handler.find_element_in_iframe(period_selector)

                if not period_field:
                    self.logger.error("❌ Поле периода отчета не найдено")
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

                # Ждем автоматической разблокировки полей
                self.iframe_handler.wait_for_fields_unlock(wait_time=5)

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

                # Очищаем поле и вводим дату
                start_date_field.clear()
                start_date_field.send_keys(start_date)

                self.logger.info(f"✅ Дата начала установлена: {start_date}")
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

                # Очищаем поле и вводим дату
                end_date_field.clear()
                end_date_field.send_keys(end_date)

                self.logger.info(f"✅ Дата окончания установлена: {end_date}")
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
        """Установить причину обращения"""
        try:
            self.logger.info("🔍 Устанавливаем причину обращения")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле причины обращения
                reason_selector = self.form_elements.get_element_selector('reason_field')
                reason_field = self.iframe_handler.find_element_in_iframe(reason_selector)

                if not reason_field:
                    self.logger.error("❌ Поле причины обращения не найдено")
                    return False

                # Получаем значение причины
                reason_value = self.form_elements.REASON_VALUE

                # Очищаем поле и вводим причину
                reason_field.clear()
                reason_field.send_keys(reason_value)

                self.logger.info(f"✅ Причина обращения установлена: {reason_value}")
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
