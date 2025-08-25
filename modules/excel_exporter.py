"""
Модуль для экспорта отчета в Excel
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class ExcelExporter:
    """Класс для экспорта отчета в Excel"""

    def __init__(self, driver, logger_instance=None):
        self.driver = driver
        self.logger = logger_instance or logger

    def wait_for_report_ready(self, timeout=120):
        """Дождаться готовности отчета через проверку по промежуткам"""
        try:
            self.logger.info("⏳ Ждем готовности отчета...")

            # Проверяем каждые 5 секунд в течение timeout
            check_interval = 5
            max_checks = timeout // check_interval

            # Ищем кнопку экспорта по различным селекторам
            export_selectors = [
                # Основные селекторы по onclick
                "a[onclick*='exportReport']",
                "a[onclick*='EXCELOPENXML']",
                "a[onclick*='Excel']",
                
                # Селекторы по ID (на основе скриншота)
                "a[id*='ctl05'][id*='ctl104'][id*='ctl100']",
                "a[id*='ctl05'][id*='ctl04'][id*='ctl00']",
                "a[id*='ctl05'][id*='ctl04'][id*='ctl100']",
                "a[id*='Export']",
                "a[id*='ctl04'][id*='ctl00']",
                "a[id*='ctl04'][id*='ctl100']",
                
                # Селекторы по alt атрибуту (на основе скриншота)
                "a[alt='Экспорт раскрывающегося меню']",
                "a[alt*='Экспорт']",
                "a[alt*='Export']",
                "a[alt*='экспорт']",
                "a[alt*='export']",
                
                # Селекторы по title и alt
                "a[title*='Экспорт']",
                "a[title*='Export']",
                "a[title*='экспорт']",
                "a[title*='export']",
                "a[alt*='Excel']",
                "a[alt*='Экспорт']",
                
                # Селекторы по классам
                "a[class*='ActiveLink']",
                "a[class*='Export']",
                "a[class*='Button']",
                "a[class*='DisabledButton']",
                
                # Селекторы по структуре (на основе скриншота)
                "div[id*='ctl05'][id*='ctl104'] a",
                "div[class*='DisabledButton'] a",
                "div[id*='Export'] a",
                "div[class*='ToolbarExport'] a",
                "div[class*='WidgetSet'] a",
                "table[id*='Button'] a",
                
                # Селекторы по содержимому
                "a:contains('Excel')",
                "a:contains('Экспорт')",
                "a:contains('Export')"
            ]

            for check_num in range(max_checks):
                self.logger.info(f"🔍 Проверка {check_num + 1}/{max_checks} - ищем кнопку экспорта...")
                
                # Сначала пробуем найти по изображению (иконка дискеты - самый надежный способ)
                export_button = self.find_export_button_by_image()
                if export_button:
                    self.logger.info("✅ Кнопка экспорта найдена по изображению")
                    self.logger.info("✅ Отчет готов к экспорту")
                    return True
                
                # Затем пробуем найти по тексту
                export_button = self.find_export_button_by_text()
                if export_button:
                    self.logger.info("✅ Кнопка экспорта найдена по тексту")
                    self.logger.info("✅ Отчет готов к экспорту")
                    return True
                
                # Если не найдено по изображению и тексту, пробуем CSS селекторы
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
            save_button = self.driver.find_element(By.CSS_SELECTOR, "a[title*='Сохранить'], a[title*='Save'], button[title*='Сохранить'], button[title*='Save']")
            self.logger.info("✅ Кнопка сохранения найдена")
            return save_button
        except:
            self.logger.error("❌ Кнопка сохранения не найдена")
            return None

    def click_save_button(self):
        """Нажать кнопку сохранения"""
        try:
            save_button = self.find_save_button()
            if save_button:
                save_button.click()
                self.logger.info("✅ Кнопка сохранения нажата")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка при нажатии кнопки сохранения: {e}")
            return False

    def select_excel_format(self):
        """Выбрать формат Excel из выпадающего списка"""
        try:
            # Ищем ссылку Excel по различным селекторам
            excel_selectors = [
                "a[onclick*='EXCELOPENXML']",
                "a[title*='Excel']",
                "a[alt*='Excel']",
                "a:contains('Excel')"
            ]

            for selector in excel_selectors:
                try:
                    excel_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if excel_link.is_displayed() and excel_link.is_enabled():
                        self.logger.info("✅ Ссылка Excel найдена")
                        excel_link.click()
                        self.logger.info("✅ Формат Excel выбран")
                        return True
                except:
                    continue

            self.logger.error("❌ Ссылка Excel не найдена")
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

    def find_export_button_by_text(self):
        """Найти кнопку экспорта по тексту содержимого и изображению (более надежный способ)"""
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
                            self.logger.info(f"✅ Кнопка экспорта найдена по тексту: '{link_text}'")
                            return link
                    
                    # Проверяем title и alt
                    if any(keyword in link_title.lower() for keyword in ['excel', 'экспорт', 'export']):
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена по title: '{link_title}'")
                            return link
                    
                    # Проверяем onclick
                    if 'exportReport' in link_onclick or 'EXCELOPENXML' in link_onclick:
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена по onclick: '{link_onclick}'")
                            return link
                    
                    # Проверяем alt атрибут (на основе скриншота)
                    if any(keyword in link_alt.lower() for keyword in ['экспорт', 'export', 'раскрывающегося меню']):
                        if link.is_displayed() and link.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена по alt: '{link_alt}'")
                            return link
                    
                    # Проверяем изображение внутри ссылки (иконка дискеты)
                    try:
                        img_elements = link.find_elements(By.TAG_NAME, "img")
                        for img in img_elements:
                            img_src = img.get_attribute('src') or ''
                            img_alt = img.get_attribute('alt') or ''
                            
                            # Ищем иконку дискеты по src (на основе скриншота)
                            if 'Icons.Save' in img_src or 'ReportServer/Reserved.ReportV' in img_src:
                                if link.is_displayed() and link.is_enabled():
                                    self.logger.info(f"✅ Кнопка экспорта найдена по изображению: '{img_src}'")
                                    return link
                            
                            # Ищем по alt изображения
                            if any(keyword in img_alt.lower() for keyword in ['экспорт', 'export', 'сохранить', 'save']):
                                if link.is_displayed() and link.is_enabled():
                                    self.logger.info(f"✅ Кнопка экспорта найдена по alt изображения: '{img_alt}'")
                                    return link
                    except:
                        continue
                            
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске кнопки экспорта по тексту: {e}")
            return None

    def find_export_button_by_image(self):
        """Найти кнопку экспорта по изображению иконки дискеты (на основе скриншота)"""
        try:
            self.logger.info("🔍 Ищем кнопку экспорта по изображению иконки дискеты...")
            
            # Ищем все изображения на странице
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in all_images:
                try:
                    img_src = img.get_attribute('src') or ''
                    img_alt = img.get_attribute('alt') or ''
                    img_id = img.get_attribute('id') or ''
                    
                    # Ищем иконку дискеты по src (на основе скриншота)
                    if 'Icons.Save' in img_src or 'ReportServer/Reserved.ReportV' in img_src:
                        self.logger.info(f"✅ Найдена иконка дискеты: {img_src}")
                        
                        # Ищем родительскую ссылку
                        parent_link = img.find_element(By.XPATH, "./ancestor::a")
                        if parent_link and parent_link.is_displayed() and parent_link.is_enabled():
                            self.logger.info("✅ Найдена кнопка экспорта по изображению")
                            return parent_link
                        else:
                            self.logger.warning("⚠️ Иконка найдена, но родительская ссылка неактивна")
                    
                    # Ищем по alt изображения
                    if any(keyword in img_alt.lower() for keyword in ['экспорт', 'export', 'сохранить', 'save', 'дискета']):
                        self.logger.info(f"✅ Найдена иконка по alt: '{img_alt}'")
                        
                        # Ищем родительскую ссылку
                        try:
                            parent_link = img.find_element(By.XPATH, "./ancestor::a")
                            if parent_link and parent_link.is_displayed() and parent_link.is_enabled():
                                self.logger.info("✅ Найдена кнопка экспорта по alt изображения")
                                return parent_link
                        except:
                            self.logger.warning("⚠️ Иконка найдена, но родительская ссылка не найдена")
                    
                    # Ищем по ID изображения (на основе скриншота)
                    if 'ButtonImg' in img_id or 'ctl100' in img_id:
                        self.logger.info(f"✅ Найдена иконка по ID: {img_id}")
                        
                        # Ищем родительскую ссылку
                        try:
                            parent_link = img.find_element(By.XPATH, "./ancestor::a")
                            if parent_link and parent_link.is_displayed() and parent_link.is_enabled():
                                self.logger.info("✅ Найдена кнопка экспорта по ID изображения")
                                return parent_link
                        except:
                            self.logger.warning("⚠️ Иконка найдена, но родительская ссылка не найдена")
                            
                except Exception as e:
                    continue
            
            self.logger.warning("⚠️ Кнопка экспорта по изображению не найдена")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске кнопки экспорта по изображению: {e}")
            return None
