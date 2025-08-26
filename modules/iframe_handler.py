"""
Модуль для работы с iframe в отчетной форме
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
import time


class IframeHandler:
    """Класс для работы с iframe"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def switch_to_iframe(self):
        """Переключиться на iframe"""
        try:
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            self.driver.switch_to.frame(iframe)
            self.logger.info("✅ Переключились на iframe")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка при переключении на iframe: {e}")
            return False

    def switch_to_main_document(self):
        """Вернуться в основной документ"""
        try:
            self.driver.switch_to.default_content()
            self.logger.info("✅ Вернулись в основной документ")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка при возврате в основной документ: {e}")
            return False

    def find_element_in_iframe(self, selector, timeout=10):
        """Найти элемент в iframe по CSS селектору"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            self.logger.error(f"❌ Элемент не найден в iframe: {selector}, ошибка: {e}")
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
        """Дождаться, пока элемент станет кликабельным"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            self.logger.error(f"❌ Элемент не стал кликабельным: {selector}, ошибка: {e}")
            return None

    def wait_for_fields_unlock(self, wait_time=5):
        """Подождать разблокировки полей после выбора периода"""
        self.logger.info(f"⏳ Ждем {wait_time} секунд для автоматической разблокировки полей...")
        time.sleep(wait_time)
        self.logger.info("✅ Ожидание завершено")
