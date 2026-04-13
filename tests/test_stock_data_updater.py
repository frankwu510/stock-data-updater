import unittest
import os
import sys
import pandas as pd
from unittest.mock import patch, MagicMock

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_data_updater import StockDataUpdater


class TestStockDataUpdater(unittest.TestCase):

    def setUp(self):
        """测试前准备"""
        self.test_data_dir = "test_data"
        self.updater = StockDataUpdater(self.test_data_dir)
        # 确保测试目录存在
        os.makedirs(self.test_data_dir, exist_ok=True)

    def tearDown(self):
        """测试后清理"""
        # 清理测试目录
        import shutil
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.updater.data_dir, self.test_data_dir)
        self.assertIsInstance(self.updater.fields_mapping, dict)
        self.assertTrue(os.path.exists(self.test_data_dir))

    def test_get_existing_stocks_empty(self):
        """测试获取现有股票（空目录）"""
        stocks = self.updater.get_existing_stocks()
        self.assertEqual(stocks, {})

    def test_get_existing_stocks_with_files(self):
        """测试获取现有股票（有文件）"""
        # 创建测试文件
        test_files = ["sh600000.csv", "sz000001.csv"]
        for filename in test_files:
            filepath = os.path.join(self.test_data_dir, filename)
            pd.DataFrame({"交易日期": ["2023-01-01"], "收盘价": [10.0]}).to_csv(filepath, index=False, encoding='gbk')

        stocks = self.updater.get_existing_stocks()
        self.assertEqual(len(stocks), 2)
        self.assertIn("600000", stocks)
        self.assertIn("000001", stocks)

    def test_get_latest_trade_date_file_not_exist(self):
        """测试获取最新交易日期（文件不存在）"""
        latest_date = self.updater.get_latest_trade_date("non_existent_file.csv")
        self.assertEqual(latest_date, "2000-01-01")

    def test_get_latest_trade_date_with_data(self):
        """测试获取最新交易日期（有数据）"""
        # 创建测试文件
        test_file = os.path.join(self.test_data_dir, "test.csv")
        test_data = pd.DataFrame({
            "交易日期": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "收盘价": [10.0, 11.0, 12.0]
        })
        test_data.to_csv(test_file, index=False, encoding='gbk')

        latest_date = self.updater.get_latest_trade_date(test_file)
        self.assertEqual(latest_date, "2023-01-03")

    @patch('baostock.login')
    def test_login_baostock_success(self, mock_login):
        """测试登录成功"""
        mock_result = MagicMock()
        mock_result.error_code = '0'
        mock_login.return_value = mock_result

        result = self.updater.login_baostock()
        self.assertTrue(result)

    @patch('baostock.login')
    def test_login_baostock_failure(self, mock_login):
        """测试登录失败"""
        mock_result = MagicMock()
        mock_result.error_code = '1'
        mock_result.error_msg = '登录失败'
        mock_login.return_value = mock_result

        result = self.updater.login_baostock()
        self.assertFalse(result)

    @patch('baostock.logout')
    def test_logout_baostock(self, mock_logout):
        """测试登出"""
        self.updater.logout_baostock()
        mock_logout.assert_called_once()

    def test_find_new_stocks(self):
        """测试查找新股"""
        existing_stocks = {"600000": "sh600000.csv", "000001": "sz000001.csv"}
        new_stocks = self.updater.find_new_stocks(existing_stocks)
        self.assertEqual(new_stocks, [])  # 简化版本返回空列表


if __name__ == '__main__':
    unittest.main()