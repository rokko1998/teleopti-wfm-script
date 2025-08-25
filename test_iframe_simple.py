#!/usr/bin/env python3
"""
Простой тестовый скрипт для проверки работы с iframe и выбора периода отчета
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from modules.selenium_helpers import get_driver

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_iframe_period_selection():
    """Тестирует выбор периода отчета в iframe"""

    # URL для тестирования
    url = "http://t2ru-crmdb-03/Reports/report/%D0%9E%D1%82%D1%87%D0%B5%D1%82%D1%8B%20%D0%9A%D0%A6/%D0%9E%D1%82%D1%87%D0%B5%D1%82%20%D0%BF%D0%BE%20%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0%D0%BC%20%D0%BE%D0%B1%D1%80%D0%B0%D1%89%D0%B5%D0%BD%D0%B8%D0%B9%20(%D1%81%D0%BE%20%D1%81%D1%86%D0%B5%D0%BD%D0%B0%D1%80%D0%B8%D1%8F%D0%BC%D0%B8%20%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8)"

    driver = None
    try:
        # Создаем драйвер
        logger.info("🚀 Создаем WebDriver...")
        driver = get_driver(headless=False)  # Всегда в GUI режиме для тестирования

        # Открываем страницу
        logger.info(f"🌐 Открываем страницу: {url}")
        driver.get(url)

        # Ждем загрузки страницы
        logger.info("⏳ Ждем 15 секунд для полной загрузки страницы...")
        time.sleep(15)

        # Ищем iframe
        logger.info("🔍 Ищем iframe...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        logger.info(f"📋 Найдено iframe: {len(iframes)}")

        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute('src')
                logger.info(f"📋 Iframe {i}: src='{src}'")
            except:
                logger.info(f"📋 Iframe {i}: src не доступен")

        # Выбираем первый iframe (обычно это основной)
        if len(iframes) > 0:
            iframe = iframes[0]
            logger.info("✅ Выбираем первый iframe")

            # Переключаемся на iframe
            logger.info("🔄 Переключаемся на iframe...")
            driver.switch_to.frame(iframe)
            logger.info("✅ Переключились на iframe")

            # Ждем еще немного для загрузки содержимого iframe
            time.sleep(5)

            # Ищем поле периода отчета
            logger.info("🔍 Ищем поле периода отчета...")
            try:
                period_dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ReportViewerControl_ctl04_ctl03_ddValue"))
                )
                logger.info("✅ Поле периода отчета найдено")

                # Проверяем текущее состояние
                current_value = period_dropdown.get_attribute('value')
                current_text = period_dropdown.get_attribute('text')
                classes = period_dropdown.get_attribute('class')
                disabled = period_dropdown.get_attribute('disabled')

                logger.info(f"📋 Текущее значение: {current_value}")
                logger.info(f"📋 Текущий текст: {current_text}")
                logger.info(f"📋 Классы: {classes}")
                logger.info(f"📋 Заблокировано: {disabled}")

                # Получаем все опции
                period_select = Select(period_dropdown)
                options = period_select.options
                logger.info(f"📋 Доступно опций: {len(options)}")

                for i, option in enumerate(options):
                    logger.info(f"  {i}: value='{option.get_attribute('value')}', text='{option.text}'")

                # Пытаемся установить значение '900'
                logger.info("🔄 Устанавливаем период '900'...")
                period_select.select_by_value('900')

                # Проверяем результат
                new_value = period_dropdown.get_attribute('value')
                new_text = period_select.first_selected_option.text
                logger.info(f"✅ Новое значение: {new_value}")
                logger.info(f"✅ Новый текст: {new_text}")

                # Проверяем поля дат
                logger.info("🔍 Проверяем поля дат...")
                time.sleep(3)

                start_date_field = driver.find_element(By.ID, "ReportViewerControl_ctl04_ctl05_txtValue")
                if start_date_field:
                    start_disabled = start_date_field.get_attribute('disabled')
                    start_classes = start_date_field.get_attribute('class')
                    logger.info(f"📅 Дата начала - заблокировано: {start_disabled}, классы: {start_classes}")

                end_date_field = driver.find_element(By.ID, "ReportViewerControl_ctl04_ctl07_txtValue")
                if end_date_field:
                    end_disabled = end_date_field.get_attribute('disabled')
                    end_classes = end_date_field.get_attribute('class')
                    logger.info(f"📅 Дата окончания - заблокировано: {end_disabled}, классы: {end_classes}")

            except Exception as e:
                logger.error(f"❌ Ошибка при работе с полем периода: {e}")

        else:
            logger.error("❌ Iframe не найден")

        # Возвращаемся в основной документ
        driver.switch_to.default_content()
        logger.info("✅ Вернулись в основной документ")

        # Ждем пользователя
        logger.info("⏳ Нажмите Enter для закрытия браузера...")
        input()

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

    finally:
        if driver:
            driver.quit()
            logger.info("🔒 Браузер закрыт")

if __name__ == "__main__":
    test_iframe_period_selection()
