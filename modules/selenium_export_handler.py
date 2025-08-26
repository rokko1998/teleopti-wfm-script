"""
Модуль с "боевым" сценарием Selenium для экспорта отчетов
Использует клики по меню вместо API-вызовов для максимальной надежности
"""

import re
import time
import json
import os
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from loguru import logger


class SeleniumExportHandler:
    """Класс для надежного экспорта отчетов через Selenium клики"""

    def __init__(self, driver, logger_instance, download_dir=None):
        self.driver = driver
        self.logger = logger_instance
        self.download_dir = Path(download_dir) if download_dir else Path.home() / "Downloads"

        # Создаем директорию для загрузок если её нет
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _dispatch_click_js(self, driver, el):
        """Отправить полную последовательность событий клика через JavaScript"""
        driver.execute_script("""
          const el = arguments[0];
          const ev = (t) => el.dispatchEvent(new MouseEvent(t, {bubbles:true,cancelable:true,view:window}));
          ev('pointerdown'); ev('mousedown'); ev('mouseup'); ev('click');
        """, el)

    def switch_to_frame_with_reportviewer(self, timeout=20) -> bool:
        """Рекурсивный поиск нужного iframe с ReportViewer"""
        try:
            self.driver.switch_to.default_content()
            wait = WebDriverWait(self.driver, timeout)

            def has_rv() -> bool:
                try:
                    return bool(self.driver.execute_script("return !!(window.$find && $find('ReportViewerControl'));"))
                except Exception:
                    return False

            def dfs():
                # текущий контекст
                if has_rv():
                    return True

                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for idx in range(len(iframes)):
                    try:
                        self.driver.switch_to.frame(idx)
                        if dfs():
                            return True
                        self.driver.switch_to.parent_frame()
                    except Exception:
                        self.driver.switch_to.parent_frame()
                        continue
                return False

            result = dfs()
            if result:
                self.logger.info("✅ Найден iframe с ReportViewer")
            else:
                self.logger.warning("⚠️ Iframe с ReportViewer не найден")
            return result

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске iframe с ReportViewer: {e}")
            return False

    def open_menu_and_click_excel(self, driver, wait=WebDriverWait, timeout=15) -> bool:
        """Открытие меню Export и клик по Excel именно как пользователь"""
        try:
            w = wait(driver, timeout)

            # найдём сам выпадающий контейнер меню по известному id
            menu = driver.find_element(By.CSS_SELECTOR, "#ReportViewerControl_ctl05_ctl04_ctl00_Menu")
            # id тогглера = id меню без суффикса _Menu
            toggle_id = menu.get_attribute("id").replace("_Menu", "")

            # сам «Export» — это либо узел с таким id, либо его потомок с title/aria-label
            toggle = None
            try:
                toggle = driver.find_element(By.ID, toggle_id)
            except Exception:
                pass

            if not toggle:
                toggle = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#{toggle_id} *[title*='Export'], #{toggle_id} *[aria-label*='Export'], "
                    "#ReportViewerControl *[title*='Export'], #ReportViewerControl *[aria-label*='Export']"
                )

            self.logger.info(f"🔍 Найдена кнопка Export: {toggle_id}")

            # откроем меню: сначала обычный клик, затем дублируем JS-событиями
            try:
                ActionChains(driver).move_to_element(toggle).click().perform()
                self.logger.info("✅ Меню Export открыто через ActionChains")
            except Exception as e:
                self.logger.warning(f"⚠️ ActionChains клик не сработал: {e}")

            self._dispatch_click_js(driver, toggle)
            self.logger.info("✅ Меню Export открыто через JavaScript")

            # ждём, пока меню станет видимым
            def _menu_visible(d):
                return d.execute_script("""
                    const el = arguments[0];
                    const s = getComputedStyle(el);
                    if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                """, menu)

            try:
                WebDriverWait(driver, 2).until(_menu_visible)
                self.logger.info("✅ Меню Export стало видимым")
            except Exception:
                # форс-раскрытие: иногда UI игнорит клик
                driver.execute_script("arguments[0].style.display='block';", menu)
                self.logger.info("✅ Меню Export принудительно раскрыто")

            # найдём пункт Excel
            def _find_excel(d):
                nodes = d.find_elements(By.CSS_SELECTOR, "a.ActiveLink")
                for n in nodes:
                    txt = (n.text or n.get_attribute("textContent") or "").strip()
                    if "Excel" in txt:
                        return n
                return False

            excel = WebDriverWait(driver, 5).until(_find_excel)
            self.logger.info("✅ Пункт Excel найден в меню")

            # кликаем именно по ссылке Excel
            try:
                ActionChains(driver).move_to_element(excel).click().perform()
                self.logger.info("✅ Excel выбран через ActionChains")
            except Exception as e:
                self.logger.warning(f"⚠️ ActionChains клик по Excel не сработал: {e}")

            self._dispatch_click_js(driver, excel)
            self.logger.info("✅ Excel выбран через JavaScript")

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка при открытии меню и клике по Excel: {e}")
            return False

    def wait_for_download(self, download_dir: Path, pattern=r".*\.xlsx$", timeout=120):
        """Ожидание файла (и запасной анализ «а ушёл ли запрос?»)"""
        try:
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            end = time.time() + timeout
            before = {p.name for p in download_dir.glob("*")}

            self.logger.info(f"⏳ Ждем появления файла по паттерну: {pattern}")
            self.logger.info(f"📁 Директория загрузки: {download_dir}")

            while time.time() < end:
                files = list(download_dir.glob("*"))
                # игнорируем старые
                new_files = [f for f in files if f.name not in before]

                # в процессе загрузки у Chrome бывает .crdownload
                if any(f.suffix.lower() == ".crdownload" for f in new_files):
                    crdownload_files = [f for f in new_files if f.suffix.lower() == ".crdownload"]
                    if crdownload_files:
                        newest = max(crdownload_files, key=lambda p: p.stat().st_mtime)
                        size = newest.stat().st_size
                        self.logger.info(f"📥 Загрузка в процессе: {newest.name} ({size} байт)")
                    time.sleep(0.3)
                    continue

                # ищем готовый .xlsx
                ready = [f for f in new_files if regex.match(f.name)]
                if ready:
                    target = sorted(ready, key=lambda p: p.stat().st_mtime)[-1]
                    if target.stat().st_size > 0:
                        self.logger.info(f"✅ Файл загружен: {target.name} ({target.stat().st_size} байт)")
                        return target

                time.sleep(0.3)

            self.logger.error(f"❌ Файл не появился за {timeout} секунд")

            # Дополнительная диагностика - показываем что есть в папке
            try:
                all_files = list(download_dir.glob("*"))
                recent_files = [f for f in all_files if f.is_file() and (time.time() - f.stat().st_mtime) < 300]  # Файлы за последние 5 минут
                if recent_files:
                    self.logger.info(f"📋 Недавние файлы в папке: {[f.name for f in recent_files[:5]]}")
            except:
                pass

            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании загрузки: {e}")
            return None

    def find_export_url_in_perf_logs(self, driver, timeout=5):
        """Поиск URL экспорта в performance логах браузера"""
        try:
            end = time.time() + timeout
            rx = re.compile(r"Reserved\.ReportViewerWebControl\.axd.*Format=EXCELOPENXML", re.I)

            self.logger.info("🔍 Анализируем performance логи браузера...")

            while time.time() < end:
                for entry in driver.get_log("performance"):
                    try:
                        msg = json.loads(entry["message"])["message"]
                        if msg.get("method") == "Network.requestWillBeSent":
                            url = msg["params"]["request"]["url"]
                            if rx.search(url):
                                self.logger.info(f"✅ Найден URL экспорта в логах: {url}")
                                return url
                    except Exception:
                        continue
                time.sleep(0.2)

            self.logger.warning("⚠️ URL экспорта в performance логах не найден")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при анализе performance логов: {e}")
            return None

    def export_excel_by_click(self, report_url: str, download_dir: Path, overall_timeout=120) -> Path | None:
        """Всё вместе: сценарий экспорта «кликом»"""
        try:
            self.logger.info("🚀 Начинаем экспорт Excel через клики по меню...")

            # 1) найти фрейм с ReportViewer
            if not self.switch_to_frame_with_reportviewer(timeout=30):
                raise RuntimeError("ReportViewer frame not found")

            # 2) Ждем загрузки отчета по XHR (критически важно!)
            self.logger.info("⏳ Ждем полной загрузки отчета по XHR...")
            if not self.wait_for_report_loaded_xhr(timeout=60):
                self.logger.warning("⚠️ Не удалось дождаться загрузки отчета по XHR, продолжаем...")

            # 3) почистить старые хвосты
            self.logger.info("🧹 Очищаем старые файлы загрузок...")
            for p in download_dir.glob("*"):
                if p.suffix.lower() in {".xlsx", ".crdownload"}:
                    try:
                        p.unlink()
                        self.logger.info(f"🗑️ Удален старый файл: {p.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Не удалось удалить {p.name}: {e}")

            # 4) открыть меню и кликнуть Excel
            self.logger.info("🖱️ Открываем меню Export и кликаем Excel...")
            ok = self.open_menu_and_click_excel(self.driver)
            if not ok:
                raise RuntimeError("Failed to click Excel menu item")

            # 5) дождаться файла
            self.logger.info("⏳ Ждем появления файла Excel...")
            target = self.wait_for_download(download_dir, r".*\.xlsx$", timeout=overall_timeout)
            if target:
                self.logger.info(f"🎉 Экспорт завершен успешно: {target}")
                return target

            # 6) если файла нет — просто возвращаем None, не засоряем логи
            self.logger.warning("⚠️ Файл не появился в срок")

            # Пробуем еще раз с увеличенным timeout (180с)
            self.logger.info("🔄 Пробуем еще раз с увеличенным timeout (180с)...")
            result = self.wait_for_download(download_dir, timeout=180)
            if result:
                return result

            return None

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при экспорте Excel: {e}")
            return None

    def cleanup_downloads(self, patterns=(".xlsx", ".crdownload")):
        """Очистка старых файлов загрузок"""
        try:
            for pattern in patterns:
                files = list(self.download_dir.glob(f"*{pattern}"))
                for file_path in files:
                    try:
                        file_path.unlink()
                        self.logger.info(f"🗑️ Удален файл: {file_path.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Не удалось удалить {file_path.name}: {e}")

        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при очистке загрузок: {e}")

    def set_download_directory(self, new_dir):
        """Изменить директорию загрузок"""
        try:
            new_path = Path(new_dir)
            new_path.mkdir(parents=True, exist_ok=True)
            self.download_dir = new_path
            self.logger.info(f"📁 Директория загрузок изменена на: {new_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка при изменении директории загрузок: {e}")
            return False

    def wait_for_report_loaded_xhr(self, timeout=60):
        """Ждать загрузки отчета по завершению XHR запросов"""
        try:
            self.logger.info("🔍 Ждем завершения XHR запросов для загрузки отчета...")

            # Проверяем доступность performance логов
            try:
                self.driver.get_log("performance")
                self.logger.info("✅ Performance логи доступны")
            except Exception:
                self.logger.info("ℹ️ Performance логи недоступны, используем программные признаки загрузки")
                return self._wait_for_report_loaded_by_elements(timeout)

            start_time = time.time()
            last_activity_time = start_time

            while time.time() - start_time < timeout:
                try:
                    # Получаем performance логи
                    logs = self.driver.get_log("performance")

                    # Ищем активные XHR запросы
                    active_requests = []
                    for entry in logs:
                        try:
                            msg = json.loads(entry["message"])["message"]
                            if msg.get("method") == "Network.requestWillBeSent":
                                url = msg["params"]["request"]["url"]
                                request_id = msg["params"]["requestId"]

                                # Фильтруем только запросы к отчетам
                                if any(keyword in url.lower() for keyword in ["report", "reportviewer", "axd"]):
                                    active_requests.append({
                                        "id": request_id,
                                        "url": url,
                                        "time": msg["params"]["timestamp"]
                                    })
                                    last_activity_time = time.time()

                        except Exception:
                            continue

                    # Если нет активных запросов и прошло достаточно времени с последней активности
                    if not active_requests and (time.time() - last_activity_time) > 3:
                        self.logger.info("✅ XHR запросы завершены, отчет загружен")
                        return True

                    # Показываем прогресс
                    if active_requests:
                        self.logger.info(f"⏳ Активных XHR запросов: {len(active_requests)}")
                        for req in active_requests[:2]:  # Показываем первые 2
                            self.logger.info(f"   • {req['url'][:80]}...")

                    time.sleep(1)

                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка при анализе XHR: {e}")
                    time.sleep(1)

            self.logger.warning(f"⚠️ Timeout ожидания XHR ({timeout}с), продолжаем...")
            return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании XHR: {e}")
            return False

    def _wait_for_report_loaded_by_elements(self, timeout=60):
        """Ждать загрузки отчета по структурным узлам ReportViewer и состоянию ASP.NET"""
        try:
            self.logger.info("🔍 Ждем загрузки отчета по структурным узлам ReportViewer...")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Ищем признаки загруженного отчета
                    indicators = []
                    
                    # 1. Проверяем состояние ASP.NET partial postback
                    try:
                        is_async_postback = self.driver.execute_script(
                            "return typeof Sys !== 'undefined' && Sys.WebForms && Sys.WebForms.PageRequestManager && " +
                            "Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack()"
                        )
                        if is_async_postback is False:
                            indicators.append("✅ ASP.NET partial postback завершен")
                        elif is_async_postback is True:
                            indicators.append("⏳ ASP.NET partial postback активен")
                            time.sleep(1)
                            continue
                        else:
                            indicators.append("ℹ️ ASP.NET не обнаружен")
                    except:
                        indicators.append("ℹ️ ASP.NET не обнаружен")
                    
                    # 2. Проверяем структурные узлы ReportViewer (без динамических классов)
                    try:
                        # Ищем рендер-контейнер отчета с role="presentation"
                        report_table = self.driver.find_element("xpath", 
                            "//div[@id='ReportViewerControl']//table[@role='presentation']")
                        if report_table and report_table.is_displayed():
                            # Проверяем размеры
                            size = report_table.size
                            if size['width'] > 0 and size['height'] > 0:
                                indicators.append(f"✅ Рендер-контейнер отчета найден ({size['width']}x{size['height']})")
                            else:
                                indicators.append("⏳ Рендер-контейнер отчета загружается")
                                time.sleep(1)
                                continue
                    except:
                        pass
                    
                    # 3. Проверяем навигацию отчета
                    try:
                        nav_div = self.driver.find_element("xpath", 
                            "//div[@id='ReportViewerControl']//div[@role='navigation']")
                        if nav_div and nav_div.is_displayed():
                            indicators.append("✅ Навигация отчета готова")
                    except:
                        pass
                    
                    # 4. Проверяем готовность страницы
                    ready_state = self.driver.execute_script("return document.readyState")
                    if ready_state == "complete":
                        indicators.append("✅ Страница полностью загружена")
                    else:
                        indicators.append(f"⏳ Состояние страницы: {ready_state}")
                        time.sleep(1)
                        continue
                    
                    # Если нашли все признаки загрузки
                    if len(indicators) >= 2:  # Минимум 2 признака
                        self.logger.info("✅ Отчет загружен по структурным узлам:")
                        for indicator in indicators:
                            self.logger.info(f"   {indicator}")
                        return True
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка при проверке элементов: {e}")
                    time.sleep(1)
            
            self.logger.warning(f"⚠️ Timeout ожидания загрузки отчета ({timeout}с)")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании загрузки отчета: {e}")
            return False
