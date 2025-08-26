"""
Модуль для экспорта отчета в Excel
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, WebDriverException
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
                self.logger.info(f"🔍 Проверка {check_num + 1}/{max_checks} - ищем кнопку экспорта...")

                # Сначала пробуем найти по тексту (более надежно)
                export_button = self.find_export_button_by_text()
                if export_button:
                    self.logger.info("✅ Кнопка экспорта найдена по тексту")
                    self.logger.info("✅ Отчет готов к экспорту")
                    return True

                # Если не найдено по тексту, пробуем CSS селекторы
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
        """Экспортировать отчет в Excel (улучшенная версия)"""
        try:
            self.logger.info("📤 Начинаем экспорт отчета в Excel...")

            # Ждем готовности отчета
            if not self.wait_for_report_ready(timeout=wait_time):
                return False

            # 1. Сначала показываем диагностику элементов экспорта
            self.logger.info("🔍 Анализируем доступные элементы экспорта...")
            export_elements = self.find_export_elements_via_js()

            # 2. Пробуем прямой клик через JavaScript (как в вашем тесте)
            self.logger.info("🚀 Пробуем прямой экспорт через JavaScript...")
            if self.click_excel_export_via_js():
                self.logger.info("✅ Экспорт в Excel запущен через JavaScript")
                return True

            # 3. Если JavaScript не сработал, используем стандартный подход
            self.logger.info("🔄 Используем стандартный подход через Selenium...")

            # Ищем кнопку экспорта через обновленный метод
            export_button = self.find_export_button_by_text()
            if not export_button:
                self.logger.error("❌ Кнопка экспорта не найдена всеми методами")
                return False

            # Кликаем по кнопке экспорта
            self.logger.info("💾 Нажимаем кнопку экспорта через Selenium...")
            try:
                export_button.click()
            except Exception as click_error:
                self.logger.warning(f"⚠️ Обычный клик не сработал: {click_error}")
                # Пробуем JavaScript клик
                try:
                    self.driver.execute_script("arguments[0].click();", export_button)
                    self.logger.info("✅ Клик выполнен через JavaScript")
                except Exception as js_click_error:
                    self.logger.error(f"❌ JavaScript клик тоже не сработал: {js_click_error}")
                    return False

            # Ждем появления выпадающего меню (если нужно)
            time.sleep(2)

            # Проверяем, нужно ли выбирать формат Excel из меню
            if not self.select_excel_format():
                self.logger.warning("⚠️ Не удалось выбрать формат Excel из меню, возможно экспорт уже запущен")

            self.logger.info("✅ Экспорт в Excel завершен успешно")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при экспорте в Excel: {e}")
            return False

    def find_excel_export_via_js(self):
        """Найти Excel кнопку через JavaScript (как в тестовом скрипте)"""
        try:
            self.logger.info("🔍 Ищем Excel кнопку через JavaScript...")

            # JavaScript код для поиска Excel кнопки (основан на вашем тесте)
            js_code = """
            // 1. Находим Excel кнопку
            const excelLink = document.querySelector('a.ActiveLink[text="Excel"]') ||
                              Array.from(document.querySelectorAll('a.ActiveLink')).find(el => el.textContent.includes('Excel'));

            if (excelLink) {
                return {
                    found: true,
                    element: excelLink,
                    text: excelLink.textContent,
                    className: excelLink.className,
                    onclick: excelLink.onclick ? excelLink.onclick.toString() : null,
                    isVisible: excelLink.offsetParent !== null &&
                              excelLink.style.display !== 'none' &&
                              excelLink.style.visibility !== 'hidden'
                };
            }

            // 2. Альтернативный поиск по exportReport функциям
            const exportElements = Array.from(document.querySelectorAll('*')).filter(el => {
                const onclick = el.onclick ? el.onclick.toString() : '';
                return onclick.includes('exportReport') && onclick.includes('EXCELOPENXML');
            });

            if (exportElements.length > 0) {
                const excelElement = exportElements.find(el =>
                    el.textContent.includes('Excel') || el.textContent.includes('excel')
                );

                if (excelElement) {
                    return {
                        found: true,
                        element: excelElement,
                        text: excelElement.textContent,
                        className: excelElement.className,
                        onclick: excelElement.onclick.toString(),
                        isVisible: excelElement.offsetParent !== null
                    };
                }
            }

            return { found: false };
            """

            # Выполняем JavaScript
            result = self.driver.execute_script(js_code)

            if result and result.get('found'):
                self.logger.info(f"✅ Excel кнопка найдена через JS: {result.get('text', 'Неизвестно')}")
                self.logger.info(f"📊 Видимость: {result.get('isVisible', False)}")
                self.logger.info(f"📋 OnClick: {result.get('onclick', 'Нет')}")

                # Возвращаем WebElement (JavaScript вернул ссылку на элемент)
                return result.get('element')
            else:
                self.logger.warning("⚠️ Excel кнопка не найдена через JavaScript")
                return None

        except JavascriptException as e:
            self.logger.error(f"❌ Ошибка выполнения JavaScript: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске через JavaScript: {e}")
            return None

    def find_export_elements_via_js(self):
        """Найти все элементы с exportReport через JavaScript"""
        try:
            self.logger.info("🔍 Ищем все элементы с exportReport...")

            js_code = """
            const exportElements = Array.from(document.querySelectorAll('*')).filter(el => {
                const onclick = el.onclick ? el.onclick.toString() : '';
                return onclick.includes('exportReport');
            });

            return exportElements.map((el, i) => ({
                index: i + 1,
                tag: el.tagName,
                text: el.textContent.trim(),
                onclick: el.onclick ? el.onclick.toString() : null,
                className: el.className,
                id: el.id
            }));
            """

            elements = self.driver.execute_script(js_code)

            if elements:
                self.logger.info(f"📋 Найдено {len(elements)} элементов с exportReport:")
                for element in elements:
                    self.logger.info(f"  • {element['index']}: {element['tag']} - '{element['text'][:50]}{'...' if len(element['text']) > 50 else ''}'")

            return elements

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элементов через JavaScript: {e}")
            return []

    def click_excel_export_via_js(self):
        """Нажать на Excel экспорт через JavaScript"""
        try:
            self.logger.info("🖱️ Пытаемся нажать Excel экспорт через JavaScript...")

            js_code = """
            // 1. Находим Excel кнопку
            const excelLink = document.querySelector('a.ActiveLink[text="Excel"]') ||
                              Array.from(document.querySelectorAll('a.ActiveLink')).find(el => el.textContent.includes('Excel'));

            if (excelLink) {
                try {
                    excelLink.click();
                    return { success: true, method: 'ActiveLink', text: excelLink.textContent };
                } catch (e) {
                    return { success: false, error: e.message, method: 'ActiveLink' };
                }
            }

            // 2. Альтернативный способ - поиск по exportReport
            const exportElements = Array.from(document.querySelectorAll('*')).filter(el => {
                const onclick = el.onclick ? el.onclick.toString() : '';
                return onclick.includes('exportReport') && onclick.includes('EXCELOPENXML');
            });

            if (exportElements.length > 0) {
                const excelElement = exportElements.find(el =>
                    el.textContent.includes('Excel') || el.textContent.includes('excel')
                );

                if (excelElement) {
                    try {
                        excelElement.click();
                        return { success: true, method: 'exportReport', text: excelElement.textContent };
                    } catch (e) {
                        return { success: false, error: e.message, method: 'exportReport' };
                    }
                }
            }

            // 3. Прямой вызов exportReport, если есть доступ к ReportViewerControl
            try {
                if (typeof $find !== 'undefined') {
                    const control = $find('ReportViewerControl');
                    if (control && control.exportReport) {
                        control.exportReport('EXCELOPENXML');
                        return { success: true, method: 'direct_call' };
                    }
                }
            } catch (e) {
                // Игнорируем ошибку, пробуем другие способы
            }

            return { success: false, error: 'Excel кнопка не найдена' };
            """

            result = self.driver.execute_script(js_code)

            if result and result.get('success'):
                method = result.get('method', 'unknown')
                text = result.get('text', '')
                self.logger.info(f"✅ Excel экспорт запущен через {method}: '{text}'")
                return True
            else:
                error = result.get('error', 'Неизвестная ошибка') if result else 'Нет результата'
                self.logger.error(f"❌ Не удалось запустить Excel экспорт: {error}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при клике через JavaScript: {e}")
            return False

    def find_export_button_by_text(self):
        """Найти кнопку экспорта по тексту содержимого (обновленная версия)"""
        try:
            # Сначала пробуем через JavaScript (более надежно)
            js_element = self.find_excel_export_via_js()
            if js_element:
                return js_element

            # Если JavaScript не сработал, используем старый метод
            self.logger.info("🔍 Используем стандартный поиск...")

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
                        # УБИРАЕМ проверку is_displayed() - элемент может быть скрыт, но кликабелен
                        if link.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена по тексту: '{link_text}'")
                            return link

                    # Проверяем onclick на наличие exportReport
                    if 'exportReport' in link_onclick and 'EXCELOPENXML' in link_onclick:
                        if link.is_enabled():
                            self.logger.info(f"✅ Кнопка экспорта найдена по onclick: '{link_onclick[:100]}...'")
                            return link

                except:
                    continue

            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске кнопки экспорта по тексту: {e}")
            return None

    def run_excel_export_test(self):
        """Запустить полный тест экспорта Excel (как ваш JavaScript тест)"""
        try:
            self.logger.info("=== 🧪 ТЕСТИРОВАНИЕ EXCEL ЭКСПОРТА ===")

            # Выполняем тот же JavaScript код, что и в вашем тесте
            js_test_code = """
            console.log('=== ТЕСТИРОВАНИЕ EXCEL ЭКСПОРТА ===');

            // 1. Находим Excel кнопку
            const excelLink = document.querySelector('a.ActiveLink[text="Excel"]') ||
                              Array.from(document.querySelectorAll('a.ActiveLink')).find(el => el.textContent.includes('Excel'));

            const result = {
                excelLinkFound: !!excelLink,
                excelLinkInfo: null,
                parentDropdown: null,
                isVisible: false,
                clickResult: null,
                exportElements: []
            };

            if (excelLink) {
                result.excelLinkInfo = {
                    text: excelLink.textContent,
                    className: excelLink.className,
                    onclick: excelLink.onclick ? excelLink.onclick.toString() : null,
                    style: excelLink.style.cssText
                };

                // Проверяем родительский dropdown
                result.parentDropdown = excelLink.closest('[class*="Menu"], [class*="dropdown"], [class*="MenuBar"]');

                // Проверяем видимость
                result.isVisible = excelLink.offsetParent !== null &&
                                 excelLink.style.display !== 'none' &&
                                 excelLink.style.visibility !== 'hidden';
            }

            // Ищем все элементы с exportReport
            const exportElements = Array.from(document.querySelectorAll('*')).filter(el => {
                const onclick = el.onclick ? el.onclick.toString() : '';
                return onclick.includes('exportReport');
            });

            result.exportElements = exportElements.map((el, i) => ({
                index: i + 1,
                tag: el.tagName,
                text: el.textContent.trim(),
                onclick: el.onclick.toString()
            }));

            return result;
            """

            test_result = self.driver.execute_script(js_test_code)

            # Выводим результаты теста
            if test_result:
                self.logger.info(f"📊 Excel ссылка найдена: {test_result.get('excelLinkFound', False)}")

                if test_result.get('excelLinkInfo'):
                    info = test_result['excelLinkInfo']
                    self.logger.info(f"📋 Excel ссылка:")
                    self.logger.info(f"   • Текст: {info.get('text', 'Нет')}")
                    self.logger.info(f"   • Класс: {info.get('className', 'Нет')}")
                    self.logger.info(f"   • OnClick: {info.get('onclick', 'Нет')[:100] if info.get('onclick') else 'Нет'}...")

                self.logger.info(f"👁️ Excel кнопка видима: {test_result.get('isVisible', False)}")

                export_elements = test_result.get('exportElements', [])
                self.logger.info(f"📋 Элементы с exportReport: {len(export_elements)}")

                for element in export_elements[:5]:  # Показываем первые 5
                    text_preview = element['text'][:50] + '...' if len(element['text']) > 50 else element['text']
                    self.logger.info(f"   • {element['index']}: {element['tag']} - '{text_preview}'")

                if len(export_elements) > 5:
                    self.logger.info(f"   ... и еще {len(export_elements) - 5} элементов")

            return test_result

        except Exception as e:
            self.logger.error(f"❌ Ошибка при выполнении теста: {e}")
            return None
