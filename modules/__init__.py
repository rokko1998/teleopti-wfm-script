"""
Модули для автоматизации работы с отчетами по трафику.
"""

from .selenium_helpers import get_driver, setup_proxy, apply_cdp_download_settings
from .new_site_handler import NewSiteReportHandler
from .page_analyzer import PageAnalyzer
from .data_processing import process_data
from .excel_manager import ExcelManager
from .download_manager import DownloadManager
from .date_time_utils import DateUtils
from .regions import RegionManager
from .skills import SkillsManager

__all__ = [
    'get_driver',
    'setup_proxy',
    'apply_cdp_download_settings',
    'NewSiteReportHandler',
    'PageAnalyzer',
    'process_data',
    'ExcelManager',
    'DownloadManager',
    'DateUtils',
    'RegionManager',
    'SkillsManager'
]