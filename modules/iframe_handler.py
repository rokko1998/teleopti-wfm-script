"""
Модуль для работы с iframe элементами
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class IframeHandler:
    """Класс для работы с iframe элементами"""
    
    def __init__(self, driver, logger_instance=None):
        self.driver = driver
        self.logger = logger_instance or logger
    
    def switch_to_iframe(self, iframe_selector="iframe.viewer"):
        """Переключиться на iframe"""
        try:
            # Ищем iframe
            iframe = self.driver.find_element(By.CSS_SELECTOR, iframe_selector)
            if not iframe:
                self.logger.error("❌ Iframe не найден")
                return False
            
            # Переключаемся на iframe
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
        """Найти элемент в iframe"""
        try:
            # Убеждаемся, что мы в iframe
            if self.driver.current_url == self.driver.get_current_url():
                self.logger.warning("⚠️ Возможно, мы не в iframe")
            
            # Ищем элемент
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            if element:
                self.logger.info(f"✅ Элемент найден: {selector}")
                return element
            else:
                self.logger.error(f"❌ Элемент не найден: {selector}")
                return None
                
        except TimeoutException:
            self.logger.error(f"❌ Таймаут при поиске элемента: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элемента {selector}: {e}")
            return None
    
    def wait_for_element_clickable(self, selector, timeout=10):
        """Дождаться кликабельности элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            self.logger.info(f"✅ Элемент кликабелен: {selector}")
            return element
        except TimeoutException:
            self.logger.error(f"❌ Таймаут ожидания кликабельности: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании кликабельности {selector}: {e}")
            return None
    
    def wait_for_fields_unlock(self, wait_time=5):
        """Ждать разблокировки полей"""
        self.logger.info(f"⏳ Ждем разблокировки полей {wait_time} секунд...")
        time.sleep(wait_time)
        self.logger.info("✅ Ожидание завершено")
    
    def find_element_with_diagnostics(self, selector, timeout=10):
        """Найти элемент с диагностической информацией"""
        try:
            element = self.find_element_in_iframe(selector, timeout)
            if element:
                # Логируем детальную информацию об элементе
                element_id = element.get_attribute('id') or 'Нет ID'
                element_class = element.get_attribute('class') or 'Нет классов'
                element_type = element.get_attribute('type') or 'Нет типа'
                element_value = element.get_attribute('value') or 'Нет значения'
                element_tag = element.tag_name
                
                self.logger.info(f"🔍 Диагностика элемента {selector}:")
                self.logger.info(f"   Тег: {element_tag}")
                self.logger.info(f"   ID: {element_id}")
                self.logger.info(f"   Классы: {element_class}")
                self.logger.info(f"   Тип: {element_type}")
                self.logger.info(f"   Значение: {element_value}")
                
                return element
            else:
                self.logger.error(f"❌ Элемент не найден для диагностики: {selector}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при диагностике элемента {selector}: {e}")
            return None
