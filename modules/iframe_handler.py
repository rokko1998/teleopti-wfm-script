"""
Модуль для работы с iframe в отчетной форме
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time


class IframeHandler:
    """Класс для работы с iframe"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def switch_to_iframe(self):
        """Переключиться на iframe с отчетом"""
        try:
            self.logger.info("[iframe_handler] 🔄 Переключаемся на iframe...")

            # Ищем iframe по различным селекторам
            iframe_selectors = [
                "iframe.viewer",
                "iframe[id*='ReportViewer']",
                "iframe[src*='report']",
                "iframe"
            ]

            iframe = None
            for selector in iframe_selectors:
                try:
                    iframe = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if iframe.is_displayed():
                        break
                except:
                    continue

            if not iframe:
                self.logger.error("[iframe_handler] ❌ Iframe не найден")
                return False

            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            self.logger.info("[iframe_handler] ✅ Переключились на iframe")
            return True

        except Exception as e:
            self.logger.error(f"[iframe_handler] ❌ Ошибка при переключении на iframe: {e}")
            return False

    def switch_to_main_document(self):
        """Вернуться в основной документ"""
        try:
            self.driver.switch_to.default_content()
            self.logger.info("[iframe_handler] ✅ Вернулись в основной документ")
            return True
        except Exception as e:
            self.logger.error(f"[iframe_handler] ❌ Ошибка при возврате в основной документ: {e}")
            return False

    def find_element_in_iframe(self, selector):
        """Найти элемент в iframe по селектору"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element
        except Exception as e:
            self.logger.error(f"[iframe_handler] ❌ Элемент не найден в iframe: {selector} - {e}")
            return None

    def find_element_with_diagnostics(self, selector, timeout=10):
        """Найти элемент в iframe с подробной диагностикой"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )

            # Выводим подробную информацию об элементе
            self.logger.info(f"🔍 Элемент найден: {selector}")
            self.logger.info(f"   Тег: {element.tag_name}")
            self.logger.info(f"   ID: {element.get_attribute('id')}")
            self.logger.info(f"   Классы: {element.get_attribute('class')}")
            self.logger.info(f"   Тип: {element.get_attribute('type')}")
            self.logger.info(f"   Значение: {element.get_attribute('value')}")

            return element

        except Exception as e:
            self.logger.error(f"❌ Элемент не найден в iframe: {selector}, ошибка: {e}")
            return None

    def wait_for_element_clickable(self, selector, timeout=10):
        """Дождаться кликабельности элемента в iframe"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            self.logger.error(f"[iframe_handler] ❌ Элемент не стал кликабельным: {selector} - {e}")
            return None

    def wait_for_fields_unlock(self, wait_time=5):
        """Ждать разблокировки полей"""
        try:
            self.logger.info(f"[iframe_handler] ⏳ Ждем разблокировки полей {wait_time} секунд...")
            time.sleep(wait_time)
            self.logger.info("[iframe_handler] ✅ Ожидание завершено")
            return True
        except Exception as e:
            self.logger.error(f"[iframe_handler] ❌ Ошибка при ожидании разблокировки полей: {e}")
            return False
