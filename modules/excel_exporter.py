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
            self.logger.info("[excel_exporter] ⏳ Ждем готовности отчета...")

            # Проверяем каждые 5 секунд в течение timeout
            check_interval = 5
            max_checks = timeout // check_interval

            # Ищем кнопку экспорта по различным селекторам
            export_selectors = [
                # Основные селекторы по onclick
                "a[onclick*='exportReport']",
                "a[onclick*='EXCELOPENXML']",
                "a[onclick*='Excel']",

                # Селекторы по ID
                "a[id*='Export']",
                "a[id*='ctl04'][id*='ctl00']",
                "a[id*='ctl04'][id*='ctl100']",

                # Селекторы по классам
                "a[class*='ActiveLink']",
                "a[class*='Export']",
                "a[class*='Button']",

                # Селекторы по title и alt
                "a[title*='Экспорт']",
                "a[title*='Export']",
                "a[alt*='Excel']",
                "a[alt*='Экспорт']",

                # Селекторы по структуре
                "div[id*='Export'] a",
                "div[class*='ToolbarExport'] a",
                "div[class*='WidgetSet'] a",
                "table[id*='Button'] a",

                # Селекторы по содержимому
                "a:contains('Excel')",
                "a:contains('Экспорт')"
            ]

            for check_num in range(max_checks):
                self.logger.info(f"[excel_exporter] 🔍 Проверка {check_num + 1}/{max_checks} - ищем кнопку экспорта...")

                # Сначала пробуем найти по тексту (более надежно)
                export_button = self.find_export_button_by_text()
                if export_button:
                    self.logger.info("[excel_exporter] ✅ Кнопка экспорта найдена по тексту")
                    self.logger.info("[excel_exporter] ✅ Отчет готов к экспорту")
                    return True

                # Если не найдено по тексту, пробуем CSS селекторы
                for selector in export_selectors:
                    try:
                        export_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if export_button.is_displayed() and export_button.is_enabled():
                            self.logger.info(f"[excel_exporter] ✅ Кнопка экспорта найдена: {selector}")
                            self.logger.info("[excel_exporter] ✅ Отчет готов к экспорту")
                            return True
                    except:
                        continue

                # Если кнопка не найдена, ждем и проверяем снова
                if check_num < max_checks - 1:  # Не ждем после последней проверки
                    self.logger.info(f"[excel_exporter] ⏳ Кнопка экспорта не найдена, ждем {check_interval} секунд...")
                    time.sleep(check_interval)

            self.logger.error(f"[excel_exporter] ❌ Отчет не загрузился за {timeout} секунд")
            return False

        except Exception as e:
            self.logger.error(f"[excel_exporter] ❌ Ошибка при ожидании готовности отчета: {e}")
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
        """Выбрать формат Excel из выпадающего списка"""
        try:
            self.logger.info("[excel_exporter] 📊 Выбираем формат Excel...")

            # Ищем ссылку Excel в выпадающем меню
            excel_selectors = [
                "a[onclick*='EXCELOPENXML']",
                "a[onclick*='Excel']",
                "a[alt*='Excel']",
                "a:contains('Excel')",
                "a[title*='Excel']"
            ]

            excel_link = None
            for selector in excel_selectors:
                try:
                    excel_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if excel_link.is_displayed() and excel_link.is_enabled():
                        break
                except:
                    continue

            if not excel_link:
                self.logger.error("[excel_exporter] ❌ Ссылка Excel не найдена в выпадающем меню")
                return False

            # Кликаем по ссылке Excel
            self.logger.info("[excel_exporter] 💾 Выбираем формат Excel...")
            excel_link.click()

            self.logger.info("[excel_exporter] ✅ Формат Excel выбран")
            return True

        except Exception as e:
            self.logger.error(f"[excel_exporter] ❌ Ошибка при выборе формата Excel: {e}")
            return False

    def export_to_excel(self, wait_time=120):
        """Экспортировать отчет в Excel"""
        try:
            self.logger.info("[excel_exporter] 📤 Начинаем экспорт отчета в Excel...")

            # Ждем готовности отчета (кнопка экспорта уже найдена)
            if not self.wait_for_report_ready(timeout=wait_time):
                return False

            # Ищем кнопку экспорта (которая уже была найдена в wait_for_report_ready)
            export_selectors = [
                "a[onclick*='exportReport']",
                "a[onclick*='EXCELOPENXML']",
                "a[onclick*='Excel']",
                "a[id*='Export']",
                "a[id*='ctl04'][id*='ctl00']",
                "a[id*='ctl04'][id*='ctl100']",
                "a[class*='ActiveLink']",
                "a[class*='Export']",
                "a[class*='Button']",
                "a[title*='Экспорт']",
                "a[title*='Export']",
                "a[alt*='Excel']",
                "a[alt*='Экспорт']",
                "div[id*='Export'] a",
                "div[class*='ToolbarExport'] a",
                "div[class*='WidgetSet'] a",
                "table[id*='Button'] a",
                "a:contains('Excel')",
                "a:contains('Экспорт')"
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
                self.logger.error("[excel_exporter] ❌ Кнопка экспорта не найдена")
                return False

            # Кликаем по кнопке экспорта
            self.logger.info("[excel_exporter] 💾 Нажимаем кнопку экспорта...")
            export_button.click()

            # Ждем появления выпадающего меню
            time.sleep(2)

            # Выбираем формат Excel
            if not self.select_excel_format():
                return False

            self.logger.info("[excel_exporter] ✅ Экспорт в Excel завершен успешно")
            return True

        except Exception as e:
            self.logger.error(f"[excel_exporter] ❌ Ошибка при экспорте в Excel: {e}")
            return False

    def find_export_button_by_text(self):
        """Найти кнопку экспорта по тексту содержимого (более надежный способ)"""
        try:
            # Ищем все ссылки на странице
            all_links = self.driver.find_elements(By.TAG_NAME, "a")

            for link in all_links:
                try:
                    # Проверяем текст ссылки
                    link_text = link.text.strip().lower()
                    link_title = link.get_attribute('title') or ''
                    link_alt = link.get_attribute('alt') or ''
                    link_onclick = link.get_attribute('onclick') or ''

                    # Ищем признаки кнопки экспорта
                    if any(keyword in link_text for keyword in ['excel', 'экспорт', 'export']):
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"[excel_exporter] ✅ Кнопка экспорта найдена по тексту: '{link_text}'")
                            return link

                    # Проверяем title и alt
                    if any(keyword in link_title.lower() for keyword in ['excel', 'экспорт', 'export']):
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"[excel_exporter] ✅ Кнопка экспорта найдена по title: '{link_title}'")
                            return link

                    # Проверяем onclick
                    if 'exportReport' in link_onclick or 'EXCELOPENXML' in link_onclick:
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"[excel_exporter] ✅ Кнопка экспорта найдена по onclick: '{link_onclick}'")
                            return link

                except:
                    continue

            return None

        except Exception as e:
            self.logger.error(f"[excel_exporter] ❌ Ошибка при поиске кнопки экспорта по тексту: {e}")
            return False
