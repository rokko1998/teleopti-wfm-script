"""
Модуль для экспорта отчета в Excel
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, WebDriverException
from loguru import logger
import time
import os


class ExcelExporter:
    """Класс для экспорта отчета в Excel"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

        # Отключаем Google логи в консоли
        self._disable_google_logs()

    def _disable_google_logs(self):
        """Отключить Google логи в консоли"""
        try:
            # Выполняем JavaScript для отключения console.log от Google
            js_code = """
            (function () {
                const originalLog = console.log;
                const originalWarn = console.warn;
                const originalError = console.error;

                const isNoisy = (msg) =>
                    msg.includes('google_apis') ||
                    msg.includes('voice_transcription') ||
                    msg.includes('AiaRequest') ||
                    msg.includes('Registration response error') ||
                    msg.includes('WARNING: All log messages');

                console.log = function (...args) {
                    const message = args.join(' ');
                    if (!isNoisy(message)) originalLog.apply(console, args);
                };

                console.warn = function (...args) {
                    const message = args.join(' ');
                    if (!isNoisy(message)) originalWarn.apply(console, args);
                };

                console.error = function (...args) {
                    const message = args.join(' ');
                    if (!isNoisy(message)) originalError.apply(console, args);
                };
            })();
            """
            self.driver.execute_script(js_code)
            self.logger.info("🔇 Google логи отключены")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось отключить Google логи: {e}")

    def wait_for_report_ready(self, timeout=120):
        """Дождаться готовности отчета через проверку по промежуткам"""
        try:
            self.logger.info("⏳ Ждем готовности отчета...")

            # Сначала ждем полной загрузки страницы
            self.logger.info("⏳ Ждем полной загрузки страницы...")
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                self.logger.info("✅ Страница полностью загружена")
            except:
                self.logger.warning("⚠️ Страница не загрузилась полностью, продолжаем...")

            # Проверяем каждые 5 секунд в течение timeout
            check_interval = 5
            max_checks = timeout // check_interval

            for check_num in range(max_checks):
                self.logger.info(f"🔍 Проверка {check_num + 1}/{max_checks} - ищем кнопку экспорта...")

                # Сначала пробуем найти по тексту (более надежно)
                export_button = self.find_export_button_by_text()
                if export_button:
                    self.logger.info("✅ Кнопка экспорта найдена по тексту")
                    self.logger.info("✅ Отчет готов к экспорту")
                    return True

                # Если не найдено по тексту, пробуем CSS селекторы
                export_selectors = [
                    "a[onclick*='exportReport']",
                    "a[onclick*='EXCELOPENXML']",
                    "a[class*='ActiveLink']",
                    "div[id*='Export'] a",
                    "div[class*='ToolbarExport'] a"
                ]

                for selector in export_selectors:
                    try:
                        export_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if export_button.is_enabled():  # Убрали проверку is_displayed()
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
        """Экспортировать отчет в Excel (исправленная версия)"""
        try:
            self.logger.info("📤 Начинаем экспорт отчета в Excel...")

            # Ждем готовности отчета
            if not self.wait_for_report_ready(timeout=wait_time):
                return False

            # 1. Проверяем iframe и переключаемся в нужный контекст
            self.logger.info("🔍 Проверяем iframe и контекст страницы...")
            iframe_found = self.check_and_switch_iframe()

            # 2. ПРИОРИТЕТ: Пробуем прямой вызов ReportViewer API (самый надежный способ)
            self.logger.info("🚀 Пробуем прямой экспорт через ReportViewer API...")
            if self.export_via_reportviewer("EXCELOPENXML"):
                self.logger.info("✅ Экспорт в Excel запущен через ReportViewer API")
                return True

            # 3. Альтернатива: клик по меню Excel
            self.logger.info("🔄 Пробуем клик по меню Excel...")
            if self.click_excel_menu_item():
                self.logger.info("✅ Экспорт в Excel запущен через меню")
                return True

            # 4. Fallback: старый метод через поиск кнопки
            self.logger.info("🔄 Используем fallback метод...")
            export_button = self.find_export_button_by_text()
            if not export_button:
                self.logger.error("❌ Кнопка экспорта не найдена всеми методами")
                return False

            # Кликаем по кнопке экспорта
            self.logger.info("💾 Нажимаем кнопку экспорта...")
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
        """Найти Excel кнопку через JavaScript (улучшенная версия с диагностикой)"""
        try:
            self.logger.info("🔍 Ищем Excel кнопку через JavaScript...")

            # Сначала проверим, в каком контексте мы находимся
            context_info = self.driver.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    readyState: document.readyState,
                    iframeCount: document.querySelectorAll('iframe').length,
                    activeElement: document.activeElement ? document.activeElement.tagName : 'none'
                };
            """)

            self.logger.info(f"📋 Контекст страницы:")
            self.logger.info(f"   • URL: {context_info.get('url', 'Нет')}")
            self.logger.info(f"   • Title: {context_info.get('title', 'Нет')}")
            self.logger.info(f"   • Ready State: {context_info.get('readyState', 'Нет')}")
            self.logger.info(f"   • Iframe count: {context_info.get('iframeCount', 0)}")

            # Исправленный JavaScript код для поиска Excel кнопки
            js_code = """
            (function () {
                const results = {
                    found: false,
                    method: 'none',
                    details: {},
                    allLinks: [],
                    exportElements: []
                };

                // 1. Находим Excel среди ActiveLink
                const activeLinks = Array.from(document.querySelectorAll('a.ActiveLink'));
                const excelLink = activeLinks.find(el => (el.textContent || '').includes('Excel'));

                if (excelLink) {
                    console.log('✅ Excel найден в ActiveLink!');
                    results.found = true;
                    results.method = 'ActiveLink';
                    results.details = {
                        element: excelLink,
                        text: excelLink.textContent.trim(),
                        className: excelLink.className,
                        onclick: excelLink.onclick ? excelLink.onclick.toString() : null,
                        isVisible: excelLink.offsetParent !== null &&
                                  excelLink.style.display !== 'none' &&
                                  excelLink.style.visibility !== 'hidden'
                    };
                }

                // 2. Собираем все элементы, у кого onclick содержит exportReport
                if (!results.found) {
                    const allElements = Array.from(document.querySelectorAll('*'));
                    const exportElements = allElements.filter(el => {
                        const onclick = el.onclick ? el.onclick.toString() : '';
                        return onclick.includes('exportReport');
                    });

                    results.exportElements = exportElements.map((el, i) => ({
                        index: i + 1,
                        tag: el.tagName,
                        text: (el.textContent || '').trim(),
                        onclick: el.onclick.toString(),
                        className: el.className
                    }));

                    const excelElement = exportElements.find(el => {
                        const text = (el.textContent || '').toLowerCase();
                        return text.includes('excel') || text.includes('экспорт');
                    });

                    if (excelElement) {
                        console.log('✅ Excel найден по exportReport!');
                        results.found = true;
                        results.method = 'exportReport';
                        results.details = {
                            element: excelElement,
                            text: excelElement.textContent.trim(),
                            className: excelElement.className,
                            onclick: excelElement.onclick.toString(),
                            isVisible: excelElement.offsetParent !== null
                        };
                    }
                }

                // 3. Поиск по тексту во всех ссылках
                if (!results.found) {
                    const allLinks = Array.from(document.querySelectorAll('a'));
                    results.allLinks = allLinks.map((link, i) => ({
                        index: i + 1,
                        text: (link.textContent || '').trim(),
                        className: link.className,
                        onclick: link.onclick ? link.onclick.toString() : null
                    }));

                    const excelLink = allLinks.find(link => {
                        const text = (link.textContent || '').toLowerCase();
                        return text.includes('excel') || text.includes('экспорт');
                    });

                    if (excelLink) {
                        console.log('✅ Excel найден по тексту!');
                        results.found = true;
                        results.method = 'text_search';
                        results.details = {
                            element: excelLink,
                            text: excelLink.textContent.trim(),
                            className: excelLink.className,
                            onclick: excelLink.onclick ? excelLink.onclick.toString() : null,
                            isVisible: excelLink.offsetParent !== null
                        };
                    }
                }

                return results;
            })();
            """

            # Выполняем JavaScript
            result = self.driver.execute_script(js_code)

            if result and result.get('found'):
                method = result.get('method', 'unknown')
                details = result.get('details', {})

                self.logger.info(f"✅ Excel кнопка найдена через JS (метод: {method}): {details.get('text', 'Неизвестно')}")
                self.logger.info(f"📊 Видимость: {details.get('isVisible', False)}")
                self.logger.info(f"📋 OnClick: {details.get('onclick', 'Нет')[:100] if details.get('onclick') else 'Нет'}...")

                # Возвращаем WebElement
                return details.get('element')
            else:
                # Показываем детальную диагностику
                self.logger.warning("⚠️ Excel кнопка не найдена через JavaScript")

                if result:
                    export_elements = result.get('exportElements', [])
                    all_links = result.get('allLinks', [])

                    if export_elements:
                        self.logger.info(f"📋 Найдено {len(export_elements)} элементов с exportReport:")
                        for elem in export_elements[:3]:  # Показываем первые 3
                            self.logger.info(f"   • {elem['tag']}: '{elem['text'][:50]}...'")

                    if all_links:
                        excel_links = [link for link in all_links if 'excel' in link['text'].lower()]
                        if excel_links:
                            self.logger.info(f"🔍 Найдено {len(excel_links)} ссылок с 'Excel' в тексте:")
                            for link in excel_links[:3]:
                                self.logger.info(f"   • '{link['text']}' (класс: {link['className']})")

                return None

        except JavascriptException as e:
            self.logger.error(f"❌ Ошибка выполнения JavaScript: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске через JavaScript: {e}")
            return None

    def export_via_reportviewer(self, format_code: str = "EXCELOPENXML", timeout: int = 120) -> bool:
        """
        Самый надежный способ: вызвать JS: $find('ReportViewerControl').exportReport('<FORMAT>')
        """
        try:
            self.logger.info(f"🚀 Прямой экспорт через ReportViewer API: {format_code}")

            # Обязательно проверяем iframe до JS
            self.check_and_switch_iframe()

            # Ждём, пока загрузятся Sys.Application и сам ReportViewer
            self.logger.info("⏳ Ждем загрузки Sys.Application...")
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return !!(window.Sys && Sys.Application);")
                )
                self.logger.info("✅ Sys.Application загружен")
            except:
                self.logger.warning("⚠️ Sys.Application не загрузился, пробуем продолжить...")

            self.logger.info("⏳ Ждем загрузки ReportViewerControl...")
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return !!(window.$find && $find('ReportViewerControl'));")
                )
                self.logger.info("✅ ReportViewerControl загружен")
            except:
                self.logger.error("❌ ReportViewerControl не найден")
                return False

            # Запускаем экспорт
            self.logger.info(f"💾 Запускаем экспорт в формате {format_code}...")
            self.driver.execute_script(
                "$find('ReportViewerControl').exportReport(arguments[0]);",
                format_code
            )

            self.logger.info("✅ Экспорт запущен через ReportViewer API")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при экспорте через ReportViewer API: {e}")
            return False

    def click_excel_menu_item(self) -> bool:
        """Клик по пункту меню Excel (альтернативный способ)"""
        try:
            self.logger.info("🖱️ Пытаемся кликнуть по пункту меню Excel...")

            self.check_and_switch_iframe()

            # Раскрываем меню экспорта (нужен реальный локатор кнопки/иконки «Export» в тулбаре)
            try:
                export_toggle = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[contains(@title,'Export') or contains(@aria-label,'Export') or .='Export']"
                    ))
                )
                export_toggle.click()
                self.logger.info("✅ Меню экспорта раскрыто")
            except:
                self.logger.warning("⚠️ Не удалось найти кнопку раскрытия меню экспорта")
                return False

            # Ждём появления видимого пункта Excel
            def _find_excel_link(drv):
                links = drv.find_elements(By.CSS_SELECTOR, "a.ActiveLink")
                for el in links:
                    try:
                        if "Excel" in (el.text or el.get_attribute("textContent") or "") and el.is_enabled():
                            return el
                    except Exception:
                        continue
                return False

            try:
                excel_link = WebDriverWait(self.driver, 10).until(_find_excel_link)
                self.logger.info("✅ Excel ссылка найдена в меню")

                # Используем JavaScript клик для надежности
                self.driver.execute_script("arguments[0].click();", excel_link)
                self.logger.info("✅ Excel экспорт запущен через клик по меню")
                return True

            except:
                self.logger.error("❌ Excel ссылка не появилась в меню")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при клике по меню Excel: {e}")
            return False

    def check_and_switch_iframe(self):
        """Проверить iframe и переключиться в нужный контекст"""
        try:
            self.logger.info("🔍 Проверяем iframe на странице...")

            # Ищем все iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.logger.info(f"📋 Найдено {len(iframes)} iframe элементов")

            if not iframes:
                self.logger.info("✅ Iframe не найдены, остаемся в основном контексте")
                return True

            # Проверяем каждый iframe на наличие элементов экспорта
            for i, iframe in enumerate(iframes):
                try:
                    self.logger.info(f"🔍 Проверяем iframe {i+1}...")

                    # Переключаемся в iframe
                    self.driver.switch_to.frame(iframe)

                    # Проверяем содержимое iframe
                    iframe_info = self.driver.execute_script("""
                        return {
                            title: document.title,
                            url: window.location.href,
                            hasExportElements: document.querySelectorAll('a[onclick*="exportReport"]').length > 0,
                            hasActiveLinks: document.querySelectorAll('a.ActiveLink').length > 0,
                            hasExcelText: document.querySelector('a:contains("Excel")') !== null
                        };
                    """)

                    self.logger.info(f"   • Title: {iframe_info.get('title', 'Нет')}")
                    self.logger.info(f"   • Has exportReport: {iframe_info.get('hasExportElements', False)}")
                    self.logger.info(f"   • Has ActiveLink: {iframe_info.get('hasActiveLinks', False)}")

                    # Если в этом iframe есть элементы экспорта, остаемся здесь
                    if (iframe_info.get('hasExportElements') or
                        iframe_info.get('hasActiveLinks') or
                        iframe_info.get('hasExcelText')):
                        self.logger.info(f"✅ Найден нужный iframe {i+1}, остаемся здесь")
                        return True

                    # Возвращаемся в основной контекст
                    self.driver.switch_to.default_content()

                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка при проверке iframe {i+1}: {e}")
                    # Возвращаемся в основной контекст
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass

            # Если не нашли нужный iframe, возвращаемся в основной контекст
            self.driver.switch_to.default_content()
            self.logger.info("⚠️ Подходящий iframe не найден, используем основной контекст")
            return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при проверке iframe: {e}")
            # Пытаемся вернуться в основной контекст
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

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
            (function () {
                // 1. Находим Excel кнопку среди ActiveLink
                const activeLinks = Array.from(document.querySelectorAll('a.ActiveLink'));
                const excelLink = activeLinks.find(el => (el.textContent || '').includes('Excel'));

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
                        (el.textContent || '').includes('Excel') || (el.textContent || '').includes('excel')
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
            })();
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
            (function () {
                // 1. Находим Excel кнопку среди ActiveLink
                const activeLinks = Array.from(document.querySelectorAll('a.ActiveLink'));
                const excelLink = activeLinks.find(el => (el.textContent || '').includes('Excel'));

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
                    text: (el.textContent || '').trim(),
                    onclick: el.onclick.toString()
                }));

                return result;
            })();
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
