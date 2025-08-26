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

            # 2) почистить старые хвосты
            self.logger.info("🧹 Очищаем старые файлы загрузок...")
            for p in download_dir.glob("*"):
                if p.suffix.lower() in {".xlsx", ".crdownload"}:
                    try:
                        p.unlink()
                        self.logger.info(f"🗑️ Удален старый файл: {p.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Не удалось удалить {p.name}: {e}")

            # 3) открыть меню и кликнуть Excel
            self.logger.info("🖱️ Открываем меню Export и кликаем Excel...")
            ok = self.open_menu_and_click_excel(self.driver)
            if not ok:
                raise RuntimeError("Failed to click Excel menu item")

            # 4) дождаться файла
            self.logger.info("⏳ Ждем появления файла Excel...")
            target = self.wait_for_download(download_dir, r".*\.xlsx$", timeout=overall_timeout)
            if target:
                self.logger.info(f"🎉 Экспорт завершен успешно: {target}")
                return target

            # 5) если файла нет — проверим, ушёл ли запрос экспорта
            self.logger.warning("⚠️ Файл не появился, проверяем performance логи...")
            url = self.find_export_url_in_perf_logs(self.driver, timeout=10)
            if url:
                raise RuntimeError(f"Export request sent, but browser did not save file (URL seen: {url}). Check download policy.")
            else:
                raise RuntimeError("No export request observed. Likely wrong toggle/menu state or blocked click.")

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
