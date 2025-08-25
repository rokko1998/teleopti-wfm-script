"""
Модули для автоматизации работы с отчетами по трафику.
"""

from .selenium_helpers import get_driver, setup_proxy, apply_cdp_download_settings
from .new_site_handler import NewSiteReportHandler
from .page_analyzer import PageAnalyzer

__all__ = [
    'get_driver',
    'setup_proxy',
    'apply_cdp_download_settings',
    'NewSiteReportHandler',
    'PageAnalyzer'
]