"""
Модуль для определения элементов формы отчета
Использует data-parametername атрибуты для точного поиска полей
"""

class FormElements:
    """Класс для определения элементов формы по ID (на основе диагностики)"""

    # Элементы формы по ID (точный поиск на основе диагностики)
    ELEMENT_SELECTORS = {
        'period_dropdown': '#ReportViewerControl_ctl04_ctl03_ddValue',           # Период отчета (SELECT)
        'start_date_field': 'input[name="ReportViewerControl$ctl04$ctl05$txtValue"]',  # Дата начала (INPUT)
        'end_date_field': 'input[name="ReportViewerControl$ctl04$ctl09$txtValue"]',    # Дата окончания (INPUT)
        'reason_field': 'input[name="ReportViewerControl$ctl04$ctl23$txtValue"]',       # Причина обращения (INPUT)
        'submit_button': '#ReportViewerControl_ctl04_ctl00',                     # Кнопка отправки (INPUT)
    }
    
    # Селекторы для выпадающих списков и чекбоксов
    DROPDOWN_SELECTORS = {
        'reason_dropdown_toggle': '#ReportViewerControl_ctl04_ctl23_divDropDown_ctl00',  # Кнопка выпадающего списка причины
        'reason_checkbox': '#ReportViewerControl_ctl04_ctl23_divDropDown_ctl372',        # Чекбокс "Низкая скорость в 3G/4G"
    }

    # Значения для периода отчета
    PERIOD_VALUES = {
        'произвольный': '900'
    }

    # Тестовые даты (фиксированные для тестирования)
    TEST_DATES = {
        'start_date': '01.08.2025',
        'end_date': '02.08.2025'
    }

    # Значение для причины обращения
    REASON_VALUE = 'Низкая скорость в 3G/4G'

    @classmethod
    def get_element_selector(cls, element_name):
        """Получить CSS селектор для элемента по имени"""
        return cls.ELEMENT_SELECTORS.get(element_name)

    @classmethod
    def get_period_value(cls, period_name):
        """Получить значение периода по названию"""
        return cls.PERIOD_VALUES.get(period_name)

    @classmethod
    def get_test_date(cls, date_type):
        """Получить тестовую дату по типу"""
        return cls.TEST_DATES.get(date_type)
    
    @classmethod
    def get_dropdown_selector(cls, dropdown_name):
        """Получить CSS селектор для выпадающего списка по имени"""
        return cls.DROPDOWN_SELECTORS.get(dropdown_name)
