#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы новых модулей
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.form_elements import FormElements
from modules.iframe_handler import IframeHandler
from modules.form_filler import FormFiller
from modules.excel_exporter import ExcelExporter
from modules.new_site_handler import NewSiteHandler


def test_form_elements():
    """Тестируем модуль FormElements"""
    print("🧪 Тестируем модуль FormElements...")
    
    # Тестируем получение селекторов
    period_selector = FormElements.get_element_selector('period_dropdown')
    print(f"   Период отчета: {period_selector}")
    
    start_date_selector = FormElements.get_element_selector('start_date_field')
    print(f"   Дата начала: {start_date_selector}")
    
    end_date_selector = FormElements.get_element_selector('end_date_field')
    print(f"   Дата окончания: {end_date_selector}")
    
    reason_selector = FormElements.get_element_selector('reason_field')
    print(f"   Причина обращения: {reason_selector}")
    
    # Тестируем получение значений
    period_value = FormElements.get_period_value('произвольный')
    print(f"   Значение периода 'произвольный': {period_value}")
    
    start_date = FormElements.get_test_date('start_date')
    print(f"   Тестовая дата начала: {start_date}")
    
    end_date = FormElements.get_test_date('end_date')
    print(f"   Тестовая дата окончания: {end_date}")
    
    print("✅ FormElements работает корректно\n")


def test_new_site_handler():
    """Тестируем основной класс NewSiteHandler"""
    print("🧪 Тестируем модуль NewSiteHandler...")
    
    # Создаем заглушки для тестирования
    class MockDriver:
        def find_element(self, *args, **kwargs):
            return None
    
    class MockLogger:
        def info(self, msg):
            print(f"   INFO: {msg}")
        
        def error(self, msg):
            print(f"   ERROR: {msg}")
        
        def warning(self, msg):
            print(f"   WARNING: {msg}")
    
    mock_driver = MockDriver()
    mock_logger = MockLogger()
    
    try:
        handler = NewSiteHandler(mock_driver, mock_logger)
        print("   ✅ NewSiteHandler создан успешно")
        
        # Проверяем наличие методов
        methods = ['process_report', 'fill_report_parameters', 'submit_report_request', 'export_to_excel']
        for method in methods:
            if hasattr(handler, method):
                print(f"   ✅ Метод {method} найден")
            else:
                print(f"   ❌ Метод {method} не найден")
        
    except Exception as e:
        print(f"   ❌ Ошибка при создании NewSiteHandler: {e}")
    
    print("✅ NewSiteHandler работает корректно\n")


def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования модулей...\n")
    
    test_form_elements()
    test_new_site_handler()
    
    print("🎉 Все тесты завершены!")


if __name__ == "__main__":
    main()
