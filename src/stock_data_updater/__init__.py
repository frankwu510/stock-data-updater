"""
股票数据更新器包

这个包提供了从 Baostock 获取和更新股票数据的功能。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .main import StockDataUpdater, main

__all__ = ["StockDataUpdater", "main"]