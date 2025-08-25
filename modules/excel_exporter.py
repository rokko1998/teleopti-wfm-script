"""
Модуль для экспорта отчета в Excel
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time


class ExcelExporter:
    """Класс для экспорта отчета в Excel"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def wait_for_report_ready(self, timeout=120):
        """Дождаться готовности отчета через проверку по промежуткам"""
        try:
            self.logger.info("⏳ Ждем готовности отчета...")
            
            # Проверяем каждые 5 секунд в течение timeout
            check_interval = 5
            max_checks = timeout // check_interval
            
            for check_num in range(max_checks):
                self.logger.info(f"🔍 Проверка {check_num + 1}/{max_checks} - ищем кнопку экспорта...")
                
                # Ищем кнопку экспорта по различным селекторам
                export_selectors = [
                    "a[onclick*='exportReport']",
                    "a[onclick*='EXCELOPENXML']",
                    "a[title*='Экспорт']",
                    "a[title*='Export']",
                    "a[alt*='Excel']",
                    "a[class*='ActiveLink']",
                    "div[id*='Export'] a",
                    "div[class*='ToolbarExport'] a"
                ]
                
                for selector in export_selectors:
                    try:
                        export_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if export_button.is_displayed() and export_button.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена: {selector}")
                            self.logger.info("✅ Отчет готов к экспорту")
                            return True
                    except:
                        continue
                
                # Если кнопка не найдена, ждем и проверяем снова
                if check_num < max_checks - 1:  # Не ждем после последней проверки
                    self.logger.info(f"⏳ Кнопка экспорта не найдена, ждем {check_interval} секунд...")
                    time.sleep(check_interval)
            
            self.logger.error(f"❌ Отчет не загрузился за {timeout} секунд")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании готовности отчета: {e}")
            return False

    def find_save_button(self):
        """Найти кнопку сохранения"""
        try:
            # Ищем кнопку сохранения по различным селекторам
            save_selectors = [
                "a[title*='Сохранить']",
                "a[title*='Save']",
                "button[title*='Сохранить']",
                "button[title*='Save']",
                "input[value*='Сохранить']",
                "input[value*='Save']",
                "[class*='save']",
                "[id*='save']"
            ]

            for selector in save_selectors:
                try:
                    save_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if save_button.is_displayed() and save_button.is_enabled():
                        self.logger.info(f"✅ Кнопка сохранения найдена: {selector}")
                        return save_button
                except:
                    continue

            self.logger.error("❌ Кнопка сохранения не найдена")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске кнопки сохранения: {e}")
            return None

    def click_save_button(self):
        """Нажать кнопку сохранения"""
        try:
            save_button = self.find_save_button()
            if not save_button:
                return False

            self.logger.info("💾 Нажимаем кнопку сохранения...")
            save_button.click()

            # Ждем появления выпадающего меню
            time.sleep(2)

            self.logger.info("✅ Кнопка сохранения нажата")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при нажатии кнопки сохранения: {e}")
            return False

    def select_excel_format(self):
        """Выбрать формат Excel из выпадающего меню"""
        try:
            self.logger.info("📊 Выбираем формат Excel...")

            # Ищем ссылку на Excel в выпадающем меню
            excel_selectors = [
                "a[href*='Excel']",
                "a[title*='Excel']",
                "a[title*='excel']",
                "a[title*='Эксель']",
                "a[title*='эксель']"
            ]

            for selector in excel_selectors:
                try:
                    excel_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if excel_link.is_displayed():
                        self.logger.info("✅ Ссылка Excel найдена")
                        excel_link.click()
                        self.logger.info("✅ Формат Excel выбран")
                        return True
                except:
                    continue

            # Поиск по XPath (более надежный)
            try:
                excel_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Excel') or contains(text(), 'excel') or contains(text(), 'Эксель') or contains(text(), 'эксель')]")
                if excel_link.is_displayed():
                    self.logger.info("✅ Ссылка Excel найдена по XPath")
                    excel_link.click()
                    self.logger.info("✅ Формат Excel выбран")
                    return True
            except:
                pass

            # Поиск по частичному совпадению href
            try:
                excel_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'Excel') or contains(@href, 'excel')]")
                if excel_link.is_displayed():
                    self.logger.info("✅ Ссылка Excel найдена по href")
                    excel_link.click()
                    self.logger.info("✅ Формат Excel выбран")
                    return True
            except:
                pass

            self.logger.error("❌ Ссылка Excel не найдена в выпадающем меню")
            return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при выборе формата Excel: {e}")
            return False

    def export_to_excel(self, wait_time=120):
        """Экспортировать отчет в Excel"""
        try:
            self.logger.info("📤 Начинаем экспорт отчета в Excel...")
            
            # Ждем готовности отчета (кнопка экспорта уже найдена)
            if not self.wait_for_report_ready(timeout=wait_time):
                return False
            
            # Ищем кнопку экспорта (которая уже была найдена в wait_for_report_ready)
            export_selectors = [
                "a[onclick*='exportReport']",
                "a[onclick*='EXCELOPENXML']",
                "a[title*='Экспорт']",
                "a[title*='Export']",
                "a[alt*='Excel']",
                "a[class*='ActiveLink']",
                "div[id*='Export'] a",
                "div[class*='ToolbarExport'] a"
            ]
            
            export_button = None
            for selector in export_selectors:
                try:
                    export_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if export_button.is_displayed() and export_button.is_enabled():
                        break
                except:
                    continue
            
            if not export_button:
                self.logger.error("❌ Кнопка экспорта не найдена")
                return False
            
            # Кликаем по кнопке экспорта
            self.logger.info("💾 Нажимаем кнопку экспорта...")
            export_button.click()
            
            # Ждем появления выпадающего меню
            time.sleep(2)
            
            # Выбираем формат Excel
            if not self.select_excel_format():
                return False
            
            self.logger.info("✅ Экспорт в Excel завершен успешно")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при экспорте в Excel: {e}")
            return False
