#!/usr/bin/env python3
"""
page_analyzer.py — Модуль для анализа структуры страницы и HTML элементов.
Содержит функции для анализа элементов страницы и сохранения HTML структуры.
"""

import os
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageAnalyzer:
    """Класс для анализа структуры страницы."""

    def __init__(self, driver, logger=None):
        """
        Инициализация анализатора.

        Args:
            driver: WebDriver экземпляр
            logger: Логгер (если не указан, создается новый)
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)

        # Директория для сохранения файлов анализа
        self.analysis_dir = "analysis"
        self._ensure_analysis_dir()

    def _ensure_analysis_dir(self):
        """Создает директорию для анализа если её нет."""
        if not os.path.exists(self.analysis_dir):
            os.makedirs(self.analysis_dir)
            self.logger.info(f"📁 Создана директория для анализа: {self.analysis_dir}")

    def analyze_form_elements(self):
        """Анализирует элементы форм на странице."""
        try:
            self.logger.info("🔍 Анализируем элементы форм...")

            # 1. Ищем все поля ввода
            input_fields = self.driver.find_elements(By.TAG_NAME, "input")
            self.logger.info(f"✏️ Полей ввода: {len(input_fields)}")

            # 2. Ищем все выпадающие списки
            select_fields = self.driver.find_elements(By.TAG_NAME, "select")
            self.logger.info(f"📋 Выпадающих списков: {len(select_fields)}")

            # 3. Анализируем поля ввода
            for i, field in enumerate(input_fields[:10]):  # Анализируем первые 10 полей
                field_info = self.get_element_info(field)
                if field_info.get('type') in ['text', 'date', 'datetime-local']:
                    self.logger.info(f"📝 Поле {i+1}: {field_info.get('placeholder', 'Без placeholder')} "
                                   f"(ID: {field_info.get('id', 'Нет ID')}, "
                                   f"Name: {field_info.get('name', 'Нет name')})")

            # 4. Анализируем выпадающие списки
            for i, field in enumerate(select_fields[:5]):  # Анализируем первые 5 списков
                field_info = self.get_element_info(field)
                options = field.find_elements(By.TAG_NAME, "option")
                option_texts = [opt.text.strip() for opt in options if opt.text.strip()]

                self.logger.info(f"📋 Список {i+1}: {field_info.get('placeholder', 'Без placeholder')} "
                               f"(ID: {field_info.get('id', 'Нет ID')}, "
                               f"Name: {field_info.get('name', 'Нет name')}, "
                               f"Опций: {len(options)})")

                if option_texts:
                    self.logger.info(f"   Опции: {', '.join(option_texts[:5])}{'...' if len(option_texts) > 5 else ''}")

            # 5. Ищем кнопки отправки
            submit_buttons = self.driver.find_elements(By.XPATH,
                "//input[@type='submit'] | //button[@type='submit'] | //button[contains(text(), 'Просмотр')] | //button[contains(text(), 'Сформировать')]")
            self.logger.info(f"🔘 Кнопок отправки: {len(submit_buttons)}")

            for i, button in enumerate(submit_buttons[:3]):  # Анализируем первые 3 кнопки
                button_info = self.get_element_info(button)
                self.logger.info(f"🔘 Кнопка {i+1}: {button_info.get('text', 'Без текста')} "
                               f"(ID: {button_info.get('id', 'Нет ID')}, "
                               f"Type: {button_info.get('type', 'Нет type')})")

            # Сохраняем результаты анализа форм
            self._save_form_analysis_results({
                'input_fields': len(input_fields),
                'select_fields': len(select_fields),
                'submit_buttons': len(submit_buttons)
            })

            self.logger.info("✅ Анализ элементов форм завершен")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при анализе элементов форм: {e}")

    def _save_form_analysis_results(self, results):
        """Сохраняет результаты анализа форм в файл."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"form_analysis_{timestamp}.txt"
            filepath = os.path.join(self.analysis_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=== РЕЗУЛЬТАТЫ АНАЛИЗА ФОРМ ===\n")
                f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {self.driver.current_url}\n\n")

                for key, value in results.items():
                    f.write(f"{key}: {value}\n")

            self.logger.info(f"✅ Результаты анализа форм сохранены в: {filepath}")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении результатов анализа форм: {e}")

    def find_form_field_by_label(self, label_text):
        """
        Ищет поле формы по связанной метке.

        Args:
            label_text: Текст метки для поиска

        Returns:
            WebElement: Найденное поле или None
        """
        try:
            # Ищем метку
            label = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{label_text}')]")

            # Получаем связанное поле
            field_id = label.get_attribute('for')
            if field_id:
                field = self.driver.find_element(By.ID, field_id)
                self.logger.info(f"✅ Найдено поле по метке '{label_text}' с ID: {field_id}")
                return field

            # Если нет for атрибута, ищем следующее поле
            field = label.find_element(By.XPATH, "following-sibling::*[1]")
            self.logger.info(f"✅ Найдено поле по метке '{label_text}' (следующий элемент)")
            return field

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске поля по метке '{label_text}': {e}")
            return None

    def get_page_html_structure(self, filename=None):
        """
        Получает и сохраняет полную HTML структуру страницы.

        Args:
            filename: Имя файла для сохранения (если не указано, генерируется автоматически)

        Returns:
            str: Путь к сохраненному файлу
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_structure_analysis_{timestamp}.html"

            filepath = os.path.join(self.analysis_dir, filename)

            # Получаем HTML страницы
            html_content = self.driver.page_source

            # Сохраняем в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"✅ HTML структура сохранена в: {filepath}")

            # Анализируем ключевые элементы
            self.analyze_html_elements()

            # Анализируем элементы форм
            self.analyze_form_elements()

            return filepath

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении HTML структуры: {e}")
            return None

    def analyze_html_elements(self):
        """Анализирует ключевые HTML элементы на странице."""
        try:
            self.logger.info("🔍 Анализируем HTML элементы...")

            # 1. Ищем ReportViewer элементы
            report_elements = self.driver.find_elements(By.CLASS_NAME, "ReportViewer")
            self.logger.info(f"📊 ReportViewer элементов: {len(report_elements)}")

            # 2. Ищем таблицы данных
            data_tables = self.driver.find_elements(By.TAG_NAME, "table")
            self.logger.info(f"📋 Таблиц на странице: {len(data_tables)}")

            # 3. Ищем элементы пагинации
            pagination_elements = self.driver.find_elements(By.XPATH,
                "//*[contains(@class, 'pagination') or contains(@id, 'pagination')]")
            self.logger.info(f"📄 Элементов пагинации: {len(pagination_elements)}")

            # 4. Ищем элементы экспорта
            export_elements = self.driver.find_elements(By.XPATH,
                "//*[contains(text(), 'Excel') or contains(text(), 'Export') or contains(text(), 'Выгрузка')]")
            self.logger.info(f"📤 Элементов экспорта: {len(export_elements)}")

            # 5. Ищем скрытые поля
            hidden_fields = self.driver.find_elements(By.XPATH, "//input[@type='hidden']")
            self.logger.info(f"🔒 Скрытых полей: {len(hidden_fields)}")

            # 6. Ищем кнопки
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            submit_buttons = self.driver.find_elements(By.XPATH, "//input[@type='submit']")
            self.logger.info(f"🔘 Кнопок: {len(buttons) + len(submit_buttons)}")

            # 7. Ищем поля ввода
            input_fields = self.driver.find_elements(By.TAG_NAME, "input")
            select_fields = self.driver.find_elements(By.TAG_NAME, "select")
            self.logger.info(f"✏️ Полей ввода: {len(input_fields) + len(select_fields)}")

            # Сохраняем результаты анализа
            self._save_analysis_results({
                'report_elements': len(report_elements),
                'data_tables': len(data_tables),
                'pagination_elements': len(pagination_elements),
                'export_elements': len(export_elements),
                'hidden_fields': len(hidden_fields),
                'buttons': len(buttons) + len(submit_buttons),
                'input_fields': len(input_fields) + len(select_fields)
            })

            self.logger.info("✅ Анализ HTML элементов завершен")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при анализе HTML элементов: {e}")

    def _save_analysis_results(self, results):
        """Сохраняет результаты анализа в файл."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_analysis_{timestamp}.txt"
            filepath = os.path.join(self.analysis_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=== РЕЗУЛЬТАТЫ АНАЛИЗА СТРАНИЦЫ ===\n")
                f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {self.driver.current_url}\n\n")

                for key, value in results.items():
                    f.write(f"{key}: {value}\n")

            self.logger.info(f"✅ Результаты анализа сохранены в: {filepath}")

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении результатов анализа: {e}")

    def find_element_by_text(self, text, tag_name=None):
        """
        Ищет элемент по тексту.

        Args:
            text: Текст для поиска
            tag_name: Тип тега (если указан)

        Returns:
            list: Список найденных элементов
        """
        try:
            if tag_name:
                xpath = f"//{tag_name}[contains(text(), '{text}')]"
            else:
                xpath = f"//*[contains(text(), '{text}')]"

            elements = self.driver.find_elements(By.XPATH, xpath)
            self.logger.info(f"🔍 Найдено элементов с текстом '{text}': {len(elements)}")

            return elements

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элемента по тексту: {e}")
            return []

    def find_element_by_class(self, class_name):
        """
        Ищет элементы по классу.

        Args:
            class_name: Имя класса для поиска

        Returns:
            list: Список найденных элементов
        """
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            self.logger.info(f"🔍 Найдено элементов с классом '{class_name}': {len(elements)}")

            return elements

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске элемента по классу: {e}")
            return []

    def get_element_info(self, element):
        """
        Получает информацию об элементе.

        Args:
            element: WebElement для анализа

        Returns:
            dict: Словарь с информацией об элементе
        """
        try:
            info = {
                'tag_name': element.tag_name,
                'text': element.text.strip() if element.text else '',
                'class': element.get_attribute('class'),
                'id': element.get_attribute('id'),
                'name': element.get_attribute('name'),
                'type': element.get_attribute('type'),
                'value': element.get_attribute('value'),
                'style': element.get_attribute('style'),
                'onclick': element.get_attribute('onclick')
            }

            return info

        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении информации об элементе: {e}")
            return {}

    def wait_for_element(self, by, value, timeout=10):
        """
        Ожидает появления элемента на странице.

        Args:
            by: Способ поиска (By.ID, By.CLASS_NAME, etc.)
            value: Значение для поиска
            timeout: Таймаут ожидания в секундах

        Returns:
            WebElement: Найденный элемент или None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            self.logger.info(f"✅ Элемент найден: {by} = {value}")
            return element

        except Exception as e:
            self.logger.error(f"❌ Элемент не найден: {by} = {value}, ошибка: {e}")
            return None
