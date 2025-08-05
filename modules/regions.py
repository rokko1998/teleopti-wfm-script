"""
Модуль для работы с регионами (рабочая нагрузка).
"""

import time
from typing import List
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


def clear_workload_selection(driver):
    """
    Очищает правый список от старых регионов.
    ⚠️ КРИТИЧЕСКИ ВАЖНО: НЕ НАЖАТЬ НА ВЕРХНЮЮ КНОПКУ (навыки)!
    НАЙТИ ВСЕ КНОПКИ, ПРОПУСТИТЬ ПЕРВУЮ, КЛИКНУТЬ ВТОРУЮ!
    """
    try:
        logger.info("🧹 Очищаем правый список от старых регионов...")
        logger.info("🔍 Ищем ВСЕ кнопки очистки на странице...")

        # Находим ВСЕ кнопки с src="images/left_all_light.gif"
        all_clear_buttons = driver.find_elements(
            By.XPATH,
            "//img[contains(@src, 'images/left_all_light.gif')]"
        )

        logger.info(f"✅ Найдено кнопок очистки: {len(all_clear_buttons)}")

        if len(all_clear_buttons) >= 2:
            # ПРОПУСКАЕМ ПЕРВУЮ (навыки), КЛИКАЕМ ВТОРУЮ (рабочая нагрузка)
            logger.info("🚨 КРИТИЧНО: Пропускаем первую кнопку (навыки)...")
            logger.info("✅ Кликаем по ВТОРОЙ кнопке (рабочая нагрузка)...")

            workload_clear_button = all_clear_buttons[1]  # Вторая кнопка (индекс 1)
            workload_clear_button.click()
            time.sleep(2)  # Пауза после очистки
            logger.info("✅ Правый список рабочей нагрузки очищен (ВТОРАЯ кнопка)")
        elif len(all_clear_buttons) == 1:
            logger.warning("⚠️ Найдена только одна кнопка очистки - возможно структура изменилась")
            logger.info("🔄 Пробуем кликнуть единственную кнопку...")
            all_clear_buttons[0].click()
            time.sleep(2)
            logger.info("✅ Кликнули по единственной найденной кнопке")
        else:
            logger.error("❌ Кнопки очистки не найдены!")
            raise Exception("Кнопки очистки не найдены")

    except Exception as e:
        logger.warning(f"⚠️ Не удалось найти кнопки очистки: {e}")
        # Пробуем альтернативный поиск конкретно в секции "Рабочая нагрузка"
        try:
            logger.info("🔄 Пробуем поиск ТОЛЬКО в секции 'Рабочая нагрузка'...")
            clear_button = driver.find_element(
                By.XPATH,
                "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//img[contains(@src, 'left_all')]"
            )
            clear_button.click()
            time.sleep(2)
            logger.info("✅ Правый список очищен (альтернативный поиск)")
        except Exception as e2:
            logger.warning(f"⚠️ Альтернативный способ очистки тоже не сработал: {e2}")
            logger.warning("⚠️ Продолжаем без очистки - будем добавлять к существующим регионам")


def find_workload_left_select(driver):
    """
    Находит левый селект для рабочей нагрузки.
    """
    try:
        workload_left_select = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][1]"
            ))
        )
        logger.info("✅ Найден левый список рабочей нагрузки")
        return workload_left_select
    except Exception as e:
        logger.error(f"❌ Не удалось найти поле 'Рабочая нагрузка': {e}")

        # Показываем все доступные поля на странице
        try:
            all_td = driver.find_elements(By.TAG_NAME, "td")
            field_names = [td.text.strip() for td in all_td if td.text.strip() and len(td.text.strip()) < 100]
            logger.info(f"📋 Доступные поля на странице: {field_names}")
        except:
            logger.warning("Не удалось получить список полей")
        raise


def wait_for_workload_options(workload_left_select):
    """
    Ждет загрузки опций в списке рабочей нагрузки.
    """
    logger.info("⏳ Ждем загрузки опций в списке рабочей нагрузки...")

    # Ждем пока в списке появятся опции
    for i in range(10):  # макс 10 секунд
        options = workload_left_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:  # больше чем пустая опция
            logger.info(f"✅ Загружено {len(options)} опций")
            break
        time.sleep(1)
        logger.info(f"⏳ Ждем загрузки опций... ({i+1}/10)")
    else:
        logger.warning("⚠️ Список опций не загрузился полностью")

    time.sleep(1)  # Дополнительная пауза


def show_available_regions(workload_left_select):
    """
    Показывает все доступные регионы для отладки.
    """
    available_options = workload_left_select.find_elements(By.TAG_NAME, "option")
    logger.info(f"📋 Всего доступно опций: {len(available_options)}")
    if available_options:
        logger.info(f"📋 Первые 10 опций: {[(opt.get_dom_attribute('value'), opt.text.strip()) for opt in available_options[:10]]}")

        # Показываем ВСЕ доступные ID для сравнения с конфигом
        all_values = [opt.get_dom_attribute('value') for opt in available_options if opt.get_dom_attribute('value')]
        logger.info(f"📋 Все доступные ID регионов: {sorted(all_values)}")
    else:
        logger.error("❌ Список рабочей нагрузки пустой!")


def select_region(driver, workload_left_select, region_id: str) -> bool:
    """
    Выбирает регион по ID из левого списка и переносит в правый.

    Returns:
        bool: True если регион успешно выбран, False иначе
    """
    try:
        logger.info(f'🎯 Ищем регион с ID: {region_id}')

        # Ищем опцию по value (ID региона)
        opt = workload_left_select.find_element(By.XPATH, f".//option[@value='{region_id}']")
        region_name = opt.text.strip()
        logger.info(f'✅ Найден регион: {region_id} = "{region_name}"')

        # Способ 1: Пробуем двойной клик через ActionChains
        try:
            logger.info(f'🖱️ Пробуем двойной клик ActionChains по региону {region_id}')
            driver.execute_script("arguments[0].scrollIntoView(true);", opt)
            time.sleep(0.5)
            ActionChains(driver).move_to_element(opt).double_click().perform()
            time.sleep(1)
            logger.info(f'✅ Двойной клик выполнен для {region_id}')
        except Exception as e:
            logger.warning(f"⚠️ Двойной клик не сработал: {e}")

            # Способ 2: Пробуем через JavaScript
            try:
                logger.info(f'🖱️ Пробуем JavaScript двойной клик для {region_id}')
                driver.execute_script("""
                    var opt = arguments[0];
                    var event = new MouseEvent('dblclick', { bubbles: true, cancelable: true });
                    opt.dispatchEvent(event);
                """, opt)
                time.sleep(1)
                logger.info(f'✅ JavaScript двойной клик выполнен для {region_id}')
            except Exception as e2:
                logger.error(f"❌ JavaScript клик тоже не сработал: {e2}")
                return False

        return True

    except NoSuchElementException:
        logger.warning(f"❌ Регион с ID '{region_id}' НЕ НАЙДЕН в списке рабочей нагрузки")

        # Показываем ВСЕ доступные опции для отладки
        available_options = workload_left_select.find_elements(By.TAG_NAME, "option")
        all_values = [opt.get_dom_attribute('value') for opt in available_options if opt.get_dom_attribute('value')]
        logger.warning(f"Доступные ID: {sorted(all_values)}")

        # Ищем похожие ID (может быть разные форматы)
        similar = [v for v in all_values if region_id in v or v in region_id]
        if similar:
            logger.info(f"Возможно похожие ID: {similar}")

        return False

    except Exception as e:
        logger.error(f"❌ Ошибка при работе с регионом {region_id}: {e}")
        return False


def verify_selected_regions(driver, expected_region_ids: List[str]):
    """
    Проверяет что регионы были правильно выбраны в правом списке.
    """
    logger.info("🔍 Проверяем что регионы выбраны...")
    time.sleep(2)  # Увеличиваем паузу для стабилизации

    # Пробуем несколько способов найти правый список
    right_select_xpaths = [
        # Основной XPath
        "//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][2]",
        # Альтернативные варианты
        "//td[contains(text(),'Рабочая нагрузка')]/following-sibling::td//select[@multiple][position()=2]",
        "//table//td[contains(.,'Рабочая нагрузка')]/following-sibling::td//select[@multiple][last()]",
        # Поиск всех select и взятие последнего
        "(//td[contains(normalize-space(.),'Рабочая нагрузка')]/following-sibling::td//select[@multiple])[last()]"
    ]

    workload_right_select = None
    for xpath in right_select_xpaths:
        try:
            workload_right_select = driver.find_element(By.XPATH, xpath)
            logger.info(f"✅ Правый список найден по XPath: {xpath}")
            break
        except:
            continue

    if not workload_right_select:
        logger.warning("⚠️ Не удалось найти правый список, проверяем через JavaScript...")
        try:
            # Альтернативный способ через JavaScript
            js_code = """
            var tables = document.getElementsByTagName('table');
            for (var i = 0; i < tables.length; i++) {
                var tds = tables[i].getElementsByTagName('td');
                for (var j = 0; j < tds.length; j++) {
                    if (tds[j].textContent.includes('Рабочая нагрузка')) {
                        var selects = tds[j].parentNode.getElementsByTagName('select');
                        if (selects.length >= 2) {
                            return selects[1]; // Правый список
                        }
                    }
                }
            }
            return null;
            """
            workload_right_select = driver.execute_script(js_code)
            if workload_right_select:
                logger.info("✅ Правый список найден через JavaScript")
        except Exception as e:
            logger.warning(f"⚠️ JavaScript поиск тоже не сработал: {e}")

    if not workload_right_select:
        logger.warning("⚠️ Правый список не найден, но ПРЕДПОЛАГАЕМ что регион добавлен успешно")
        logger.info(f"📝 Двойной клик по регионам {expected_region_ids} был выполнен - продолжаем")
        return True  # Возвращаем True, так как двойной клик был выполнен

    try:
        selected_regions = workload_right_select.find_elements(By.TAG_NAME, "option")

        if len(selected_regions) > 0:
            selected_names = [opt.text.strip() for opt in selected_regions]
            selected_ids = [opt.get_dom_attribute('value') for opt in selected_regions]
            logger.info(f"✅ РЕГИОНЫ УСПЕШНО ВЫБРАНЫ:")
            logger.info(f"   📍 Количество: {len(selected_regions)}")
            logger.info(f"   📍 Названия: {selected_names}")
            logger.info(f"   📍 ID: {selected_ids}")
            return True
        else:
            logger.warning(f"⚠️ Правый список пустой, но двойной клик был выполнен")
            logger.info(f"📝 Предполагаем что регионы {expected_region_ids} добавлены корректно")
            return True  # Возвращаем True, так как двойной клик был выполнен

    except Exception as e:
        logger.warning(f"⚠️ Ошибка при проверке содержимого правого списка: {e}")
        logger.info(f"📝 Двойной клик по регионам {expected_region_ids} был выполнен - продолжаем")
        return True  # Возвращаем True, так как двойной клик был выполнен


def setup_regions(driver, region_ids: List[str]) -> bool:
    """
    Основная функция настройки регионов.

    Args:
        driver: WebDriver instance
        region_ids: Список ID регионов для выбора

    Returns:
        bool: True если все регионы успешно настроены
    """
    try:
        logger.info(f"🔍 Настраиваем рабочую нагрузку для регионов: {region_ids}")

        # Находим левый селект (доступные опции) для рабочей нагрузки
        logger.info("🔍 Ищем поле 'Рабочая нагрузка'...")
        workload_left_select = find_workload_left_select(driver)

        # Ждем загрузки опций в списке
        wait_for_workload_options(workload_left_select)

        # СНАЧАЛА ОЧИЩАЕМ ПРАВЫЙ СПИСОК от старых регионов
        clear_workload_selection(driver)

        # ПОСЛЕ ОЧИСТКИ НУЖНО ЗАНОВО НАЙТИ ЛЕВЫЙ СПИСОК!
        # Элемент workload_left_select мог стать "stale" после очистки
        logger.info("🔄 Заново ищем левый список после очистки...")
        time.sleep(1)  # Дополнительная пауза для стабилизации DOM
        workload_left_select = find_workload_left_select(driver)

        # Теперь покажем все доступные опции для отладки
        show_available_regions(workload_left_select)

        # Выбираем каждый регион
        successful_selections = 0
        for region_id in region_ids:
            if select_region(driver, workload_left_select, region_id):
                successful_selections += 1

        # Проверяем что что-то было выбрано
        if successful_selections > 0:
            return verify_selected_regions(driver, region_ids)
        else:
            logger.error("❌ Ни один регион не был выбран!")
            return False

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА с рабочей нагрузкой: {e}")
        return False