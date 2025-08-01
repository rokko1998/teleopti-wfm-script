"""
Модуль для работы с навыками.
"""

import time
from typing import List, Dict, Any
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def find_skills_left_select(driver):
    """
    Находит левый селект для навыков (верхний блок).
    """
    try:
        skills_left_select = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][1]"
            ))
        )
        logger.info("✅ Найден левый список навыков")
        return skills_left_select
    except Exception as e:
        logger.error(f"❌ Не удалось найти поле 'Навыки': {e}")
        logger.error("❌ ОСТАНОВКА: Навыки обязательны при флаге --with-skills!")
        raise


def add_skill(driver, skills_left_select, skill_id: str) -> bool:
    """
    Добавляет навык по ID в правый список.
    
    Args:
        driver: WebDriver instance
        skills_left_select: Левый селект навыков
        skill_id: ID навыка для добавления
    
    Returns:
        bool: True если навык успешно добавлен
    """
    try:
        logger.info(f"🎯 Выбираем навык ID: {skill_id}")

        # Находим опцию с нужным value
        skill_option = skills_left_select.find_element(
            By.XPATH, f".//option[@value='{skill_id}']"
        )
        skill_name = skill_option.text.strip()
        logger.info(f"   📍 Найден навык: {skill_name} (ID: {skill_id})")

        # Аналогично регионам: двойной клик для перемещения в правый список
        logger.info(f"   🔄 Двойной клик для переноса навыка...")
        ActionChains(driver).double_click(skill_option).perform()
        time.sleep(1.5)  # Увеличенная пауза для надежности

        # Проверяем что навык перенесся (попробуем найти его в правом списке)
        try:
            skills_right_select = driver.find_element(
                By.XPATH,
                "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][2]"
            )
            # Проверяем есть ли опция с этим ID в правом списке
            right_option = skills_right_select.find_element(
                By.XPATH, f".//option[@value='{skill_id}']"
            )
            logger.info(f"✅ Навык {skill_name} успешно перенесен в правый список")
            return True
        except:
            logger.error(f"❌ Навык {skill_name} НЕ ПЕРЕНЕСЕН в правый список!")
            # НЕ продолжаем если навык не перенесся
            raise Exception(f"Критическая ошибка: навык {skill_name} (ID: {skill_id}) не был добавлен")

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при добавлении навыка ID {skill_id}: {e}")
        logger.error("❌ ОСТАНОВКА: Все навыки должны быть добавлены перед продолжением!")
        raise


def verify_skills_selection(driver, expected_skills_ids: List[str]) -> bool:
    """
    Проверяет что все навыки действительно попали в правый список.
    
    Args:
        driver: WebDriver instance
        expected_skills_ids: Список ожидаемых ID навыков
    
    Returns:
        bool: True если все навыки успешно добавлены
    """
    logger.info("🔍 Проверяем правый список навыков...")
    try:
        skills_right_select = driver.find_element(
            By.XPATH,
            "//td[contains(normalize-space(.),'Навыки') or contains(normalize-space(.),'Skills')]/following-sibling::td//select[@multiple][2]"
        )

        # Получаем выбранные навыки
        selected_options = skills_right_select.find_elements(By.TAG_NAME, "option")

        if selected_options:
            selected_skills = []
            selected_ids = []
            for opt in selected_options:
                skill_value = opt.get_dom_attribute("value") or opt.get_attribute("value")
                skill_text = opt.text.strip()
                selected_skills.append(skill_text)
                selected_ids.append(skill_value)

            logger.info(f"✅ В правом списке навыков: {len(selected_skills)} навыков")
            logger.info(f"   📍 Названия: {selected_skills}")
            logger.info(f"   📍 ID: {selected_ids}")

            # КРИТИЧЕСКАЯ ПРОВЕРКА: все ли навыки добавлены?
            if len(selected_skills) != len(expected_skills_ids):
                logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не все навыки добавлены!")
                logger.error(f"   Ожидали: {len(expected_skills_ids)} навыков: {expected_skills_ids}")
                logger.error(f"   Получили: {len(selected_skills)} навыков: {selected_ids}")
                logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без всех навыков!")
                return False

            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: все ли нужные ID присутствуют?
            missing_skills = [skill_id for skill_id in expected_skills_ids if skill_id not in selected_ids]
            if missing_skills:
                logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Отсутствуют навыки с ID: {missing_skills}")
                logger.error(f"   Ожидали: {expected_skills_ids}")
                logger.error(f"   Получили: {selected_ids}")
                logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без нужных навыков!")
                return False

            logger.info("✅ ВСЕ навыки успешно добавлены - продолжаем к обработке данных!")
            return True

        else:
            logger.error(f"❌ НАВЫКИ НЕ ВЫБРАНЫ! Правый список пустой!")
            logger.error(f"❌ Ожидали навыки: {expected_skills_ids}")
            logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ продолжать без навыков!")
            return False

    except Exception as e:
        logger.error(f"❌ Не удалось проверить правый список навыков: {e}")
        logger.error("❌ ОСТАНОВКА: Невозможно продолжать без проверки навыков!")
        return False


def prepare_skills_from_config(config: Dict[str, Any]) -> List[str]:
    """
    Подготавливает список навыков из конфигурации.
    
    Args:
        config: Конфигурация из YAML файла
    
    Returns:
        List[str]: Плоский список ID навыков
    """
    skills_ids = []
    skills_config = config.get("skills", {})

    for skill_name, ids_list in skills_config.items():
        if ids_list and isinstance(ids_list, list):
            skills_ids.extend(ids_list)
            logger.info(f"   📍 Навык '{skill_name}': {ids_list}")

    logger.info(f"✅ Всего навыков для добавления: {len(skills_ids)}")
    logger.info(f"   🔢 ID навыков: {skills_ids}")
    
    return skills_ids


def setup_skills(driver, skills_ids: List[str]) -> bool:
    """
    Основная функция настройки навыков.
    
    Args:
        driver: WebDriver instance
        skills_ids: Список ID навыков для добавления
    
    Returns:
        bool: True если все навыки успешно настроены
    """
    if not skills_ids:
        logger.info("ℹ️ Список навыков пустой - пропускаем настройку")
        return True

    try:
        logger.info(f"🎯 Настраиваем навыки (БЕЗ ОЧИСТКИ): {skills_ids}")

        # Находим левый селект для навыков (верхний блок)
        logger.info("🔍 Ищем поле 'Навыки'...")
        skills_left_select = find_skills_left_select(driver)

        # Выбираем навыки по ID (БЕЗ ОЧИСТКИ правого списка)
        successfully_added = 0

        for skill_id in skills_ids:
            if add_skill(driver, skills_left_select, skill_id):
                successfully_added += 1

        logger.info(f"📊 Успешно добавлено навыков: {successfully_added}/{len(skills_ids)}")

        # Проверяем что навыки действительно попали в правый список
        return verify_skills_selection(driver, skills_ids)

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при настройке навыков: {e}")
        logger.error("❌ ОСТАНОВКА: Скрипт НЕ МОЖЕТ работать без навыков!")
        return False


def show_page_diagnostics(driver):
    """
    Показывает диагностику содержимого страницы для отладки.
    """
    try:
        logger.info("🔍 Диагностика содержимого страницы...")
        logger.info(f"✅ Title: {driver.title}")
        logger.info(f"✅ URL: {driver.current_url}")

        # Ищем основные элементы
        body_elements = driver.find_elements(By.TAG_NAME, "body")
        div_elements = driver.find_elements(By.TAG_NAME, "div")
        form_elements = driver.find_elements(By.TAG_NAME, "form")
        table_elements = driver.find_elements(By.TAG_NAME, "table")
        input_elements = driver.find_elements(By.TAG_NAME, "input")
        select_elements = driver.find_elements(By.TAG_NAME, "select")

        logger.info(f"📍 Найдено элементов:")
        logger.info(f"   <body>: {len(body_elements)}")
        logger.info(f"   <div>: {len(div_elements)}")
        logger.info(f"   <form>: {len(form_elements)}")
        logger.info(f"   <table>: {len(table_elements)}")
        logger.info(f"   <input>: {len(input_elements)}")
        logger.info(f"   <select>: {len(select_elements)}")

        if len(body_elements) > 0 and len(div_elements) > 0:
            logger.info("✅ Страница загружена (есть основные элементы)")
        else:
            logger.warning("⚠️ Страница может быть не полностью загружена")

    except Exception as e:
        logger.warning(f"⚠️ Ошибка диагностики: {e}")