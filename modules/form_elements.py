"""
Модуль с элементами формы для отчета
"""
from loguru import logger


class FormElements:
    """Класс для хранения селекторов элементов формы"""
    
    # Элементы формы по ID (точный поиск на основе диагностики)
    ELEMENT_SELECTORS = {
        'period_dropdown': '#ReportViewerControl_ctl04_ctl03_ddValue',      # Период отчета
        'start_date_field': '#ReportViewerControl_ctl04_ctl05_txtValue',    # Дата начала
        'end_date_field': '#ReportViewerControl_ctl04_ctl07_txtValue',      # Дата окончания
        'reason_field': '#ReportViewerControl_ctl04_ctl23_ddDropDownButton', # Причина обращения
        'submit_button': '#ReportViewerControl_ctl04_ctl25_btnViewReport'    # Кнопка "Просмотр отчета"
    }
    
    # Селекторы для выпадающих списков и чекбоксов
    DROPDOWN_SELECTORS = {
        'reason_dropdown_toggle': '#ReportViewerControl_ctl04_ctl23_ddDropDownButton',  # Кнопка выпадающего списка причины
        'reason_select_all': '#ReportViewerControl_ctl04_ctl23_divDropDown_ctl00',      # Чекбокс "Выделить все" (снять все галочки)
        'reason_checkbox': '#ReportViewerControl_ctl04_ctl23_divDropDown_ctl372',       # Чекбокс "Низкая скорость в 3G/4G"
    }
    
    # Значения для периода отчета
    PERIOD_VALUES = {
        'произвольный': '900',
        'текущий_месяц': '100',
        'прошлый_месяц': '200',
        'текущий_квартал': '300',
        'прошлый_квартал': '400',
        'текущий_год': '500',
        'прошлый_год': '600'
    }
    
    # Тестовые даты для отладки
    TEST_DATES = {
        'start_date': '01.08.2025',
        'end_date': '02.08.2025'
    }
    
    # Значение причины обращения
    REASON_VALUE = 'Низкая скорость в 3G/4G'
    
    def get_element_selector(self, element_name):
        """Получить селектор элемента по имени"""
        return self.ELEMENT_SELECTORS.get(element_name)
    
    def get_dropdown_selector(self, selector_name):
        """Получить селектор выпадающего списка по имени"""
        return self.DROPDOWN_SELECTORS.get(selector_name)
    
    def get_period_value(self, period_name):
        """Получить значение периода по имени"""
        return self.PERIOD_VALUES.get(period_name)
    
    def get_test_date(self, date_type):
        """Получить тестовую дату по типу"""
        return self.TEST_DATES.get(date_type)
