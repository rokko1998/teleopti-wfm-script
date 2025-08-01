"""
Модуль для вспомогательных функций Selenium.
"""

import os
import time
from pathlib import Path
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# === Константы ===
BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

REPORT_URL = (
    "http://t2ru-optiweb-02/TeleoptiWFM/Web/Areas/Reporting/"
    "Index.aspx?ReportID=8d8544e4-6b24-4c1c-8083-cbe7522dd0e0&UseOpenXml=true"
)

# === Proxy setup ===
def setup_proxy():
    """Настраивает корпоративный прокси."""
    os.environ['HTTP_PROXY'] = 'http://fg-proxy.corp.tele2.ru:8080'
    os.environ['HTTPS_PROXY'] = 'http://fg-proxy.corp.tele2.ru:8080'
    # обязательно — не проксировать локалхост!
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'


def find_parameter_input(driver, label: str, timeout: int = 10):
    """
    Находит <input type="text"> в том же <tr>, где <td> содержит label.
    """
    xpath = (
        f"//td[contains(normalize-space(.), '{label}')]"
        "/following-sibling::td"
        "//input[@type='text']"
    )

    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
    except Exception as e:
        logger.error(f"❌ Не удалось найти поле '{label}'")
        logger.info("🔍 Попытка найти все доступные поля...")

        # Показываем все доступные поля для отладки
        try:
            all_td_elements = driver.find_elements(By.TAG_NAME, "td")
            field_labels = [td.text.strip() for td in all_td_elements if td.text.strip() and len(td.text.strip()) < 50]
            logger.info(f"Доступные поля на странице: {field_labels[:20]}")
        except:
            logger.warning("Не удалось получить список полей")

        raise e


def get_driver(headless: bool = True) -> webdriver.Chrome:
    """Создает и настраивает Chrome WebDriver с автоматической установкой драйвера."""
    opts = webdriver.ChromeOptions()

    # Основные опции
    # Включаем headless режим для стабильности и обхода защиты (как предложил пользователь)
    if headless:
        opts.add_argument("--headless=new")
        logger.info("🔒 Включен headless режим для стабильности и обхода защиты")
    opts.add_argument("--auth-server-whitelist=*")  # NTLM/SSO
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")

    # Дополнительные опции для Chrome 138+
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-features=TranslateUI")
    opts.add_argument("--disable-ipc-flooding-protection")

    # КРИТИЧЕСКИ ВАЖНЫЕ настройки для ПРИНУДИТЕЛЬНОГО скачивания Excel файлов
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR.absolute()),
        "download.prompt_for_download": False,  # НЕ спрашивать где сохранить
        "download.directory_upgrade": True,

        # КЛЮЧЕВЫЕ настройки для обхода блокировок (предложены пользователем)
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,  # Включаем но отключаем защиту
        "safebrowsing.disable_download_protection": True,  # КРИТИЧНО для Excel!

        # Автоматические скачивания
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,

        # Дополнительные настройки для Excel
        "plugins.always_open_pdf_externally": True,  # PDF открывать внешне
        "download.open_pdf_in_system_reader": True,
        "plugins.plugins_disabled": ["Chrome PDF Viewer"]  # Отключить встроенный PDF
    }
    opts.add_experimental_option("prefs", prefs)

    # Убираем детекцию автоматизации
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    # дополнительные флаги для отключения блокировок
    opts.add_argument("--safebrowsing-disable-download-protection")
    opts.add_argument("--disable-extensions")

    # КРИТИЧЕСКИ ВАЖНО: флаги для обхода блокировок скачивания
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")  # Предложено пользователем
    opts.add_argument("--ignore-certificate-errors")      # Предложено пользователем
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_argument("--trusted-download-sources=*")
    opts.add_argument("--disable-download-quarantine")
    opts.add_argument("--allow-downloads-from-secure-origin")
    opts.add_argument("--disable-safebrowsing")
    opts.add_argument("--disable-safebrowsing-disable-download-protection")

    # ДОПОЛНИТЕЛЬНЫЕ флаги для принудительного разрешения скачивания
    opts.add_argument("--allow-downloads")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-extensions-file-access-check")
    opts.add_argument("--disable-file-system")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument("--disable-download-protection")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--test-type")

    try:
        # Автоматическая установка ChromeDriver для Chrome 138+
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

        # Убираем индикатор автоматизации
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # КРИТИЧЕСКИ ВАЖНО: Настройка поведения скачивания через CDP (предложено пользователем)
        logger.info("🔧 Настраиваем скачивание через Chrome DevTools Protocol...")
        try:
            params = {
                "behavior": "allow",              # Разрешаем скачивание без вопросов
                "downloadPath": str(DOWNLOAD_DIR.absolute())  # Путь, куда скачивать файлы
            }
            driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
            logger.info(f"✅ CDP настройки скачивания применены: {DOWNLOAD_DIR}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось применить CDP настройки: {e}")
            logger.info("📝 Продолжаем с обычными настройками Chrome...")

        driver.set_window_size(1600, 1000)
        logger.info(f"Chrome WebDriver инициализирован успешно")
        return driver

    except Exception as e:
        logger.error(f"Ошибка инициализации Chrome WebDriver: {e}")
        logger.info("Попробуйте:")
        logger.info("1. Обновить Chrome до последней версии")
        logger.info("2. Перезапустить скрипт (webdriver-manager попробует снова)")
        logger.info("3. Очистить кэш: rm -rf ~/.wdm/ (Mac/Linux) или del %USERPROFILE%\\.wdm\\ (Windows)")
        raise


def wait_download(start_ts: float, timeout: int = 60, driver=None) -> Path:
    """Ждём появления xlsx в DOWNLOAD_DIR новее start_ts."""
    deadline = time.time() + timeout
    check_count = 0
    last_status_time = time.time()

    logger.info(f"🔍 Ищем новые .xlsx файлы в папке: {DOWNLOAD_DIR}")

    while time.time() < deadline:
        # ПРОВЕРЯЕМ ИМЕННО .XLSX файлы (НЕ PDF!)
        xlsx_files = list(DOWNLOAD_DIR.glob("*.xlsx"))
        for f in xlsx_files:
            if f.stat().st_mtime > start_ts:
                time.sleep(1)
                logger.info(f"✅ EXCEL файл скачан: {f.name} (размер: {f.stat().st_size} байт)")
                return f

        # ВАЖНО: Проверяем не скачался ли PDF вместо Excel!
        pdf_files = list(DOWNLOAD_DIR.glob("*.pdf"))
        for f in pdf_files:
            if f.stat().st_mtime > start_ts:
                logger.error(f"❌ ОШИБКА: Скачан PDF файл вместо Excel: {f.name}")
                logger.error("❌ Это означает что кликнули по кнопке PDF, а не Excel!")
                logger.error("💡 Проверьте что кликаете именно по кнопке 'buttonShowExcel'")
                # НЕ возвращаем PDF файл - продолжаем ждать Excel

        # Показываем статус каждые 10 секунд
        if time.time() - last_status_time > 10:
            logger.info(f"⏳ Ожидание скачивания... осталось {int(deadline - time.time())} сек. Найдено .xlsx файлов: {len(xlsx_files)}")
            last_status_time = time.time()

            # Показываем что есть в папке
            all_files = list(DOWNLOAD_DIR.glob("*"))
            if all_files:
                recent_files = [f.name for f in all_files if f.stat().st_mtime > start_ts - 60]  # за последнюю минуту
                if recent_files:
                    logger.info(f"📁 Недавние файлы в папке: {recent_files}")

        # Проверяем есть ли активные диалоги
        check_count += 1
        if check_count % 3 == 0 and driver:
            try:
                alert = driver.switch_to.alert
                logger.info(f"🚨 Найден alert: {alert.text}")
                alert.accept()
                logger.info("✅ Alert принят")
            except:
                pass  # Нет алертов

        time.sleep(1)

    logger.error(f"❌ Timeout скачивания файла. Проверьте папку {DOWNLOAD_DIR}")
    # Показываем что есть в папке для отладки
    all_files = list(DOWNLOAD_DIR.glob("*"))
    logger.info(f"📁 Все файлы в папке: {[f.name for f in all_files]}")

    raise TimeoutError("Download timeout")


def apply_cdp_download_settings(driver):
    """Применяет CDP настройки скачивания."""
    logger.info("🔧 Применяем CDP настройки скачивания...")
    try:
        params = {
            "behavior": "allow",              # Разрешаем скачивание без вопросов
            "downloadPath": str(DOWNLOAD_DIR.absolute())  # Путь, куда скачивать файлы
        }
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        logger.info("✅ CDP настройки скачивания применены")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось применить CDP настройки: {e}")


def prepare_download_js(driver):
    """Подготавливает JavaScript настройки для скачивания."""
    driver.execute_script("""
        // Принудительно отключаем блокировки скачивания
        window.alert = function() { return true; };
        window.confirm = function() { return true; };
        window.prompt = function() { return true; };

        // Принудительно разрешаем скачивание
        if (window.chrome && window.chrome.downloads) {
            window.chrome.downloads.setShelfEnabled(true);
        }
    """)