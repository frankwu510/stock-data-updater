#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深A股所有股票历史数据完整下载程序（增强版）

新功能：
1. 新增通过 akshare 下载股票数据
2. 支持多种数据源（baostock、akshare）
3. 轮动下载规避IP封禁风险
4. 支持断点续传和重新下载参数
5. 配置文件 settings.txt

配置选项：
- enable_baostock: 启用 baostock 数据源
- enable_akshare: 启用 akshare 数据源
- baostock_limit: 连续使用 baostock 下载的股票数量
- akshare_limit: 连续使用 akshare 下载的股票数量
- delay_time: 下载间隔时间(秒)
"""

import os
import sys
import time
import json
import logging
import argparse
import configparser
import random
import pandas as pd
import datetime
from typing import List, Optional
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stock_data_updater import StockDataUpdater


class EnhancedStockDownloader:
    """增强版股票数据下载器"""

    def __init__(self, config_file: str = "settings.txt"):
        """初始化下载器"""
        self.config_file = config_file
        self.config = self.load_config()

        # 配置日志
        self.setup_logging()

        # 初始化数据更新器
        self.data_dir = self.config.get('Download', 'data_dir', fallback='data_all')
        self.updater = StockDataUpdater(self.data_dir)

        # 数据源配置
        self.enable_baostock = self.config.getboolean('DataSources', 'enable_baostock', fallback=True)
        self.enable_akshare = self.config.getboolean('DataSources', 'enable_akshare', fallback=True)

        # 轮动配置
        self.baostock_time_limit = self.config.getint('Rotation', 'baostock_time_limit', fallback=60)  # 秒
        self.akshare_time_limit = self.config.getint('Rotation', 'akshare_time_limit', fallback=60)  # 秒
        self.delay_time = self.config.getfloat('Rotation', 'delay_time', fallback=1.0)

        # 断点续传配置
        self.enable_resume = self.config.getboolean('Resume', 'enable_resume', fallback=True)
        self.progress_file = self.config.get('Resume', 'progress_file', fallback='download_progress.json')
        self.failed_file = self.config.get('Resume', 'failed_file', fallback='failed_stocks.json')

        # 统计信息
        self.stats = {
            'success_count': 0,
            'fail_count': 0,
            'current_source': 'baostock' if self.enable_baostock else 'akshare',
            'baostock_start_time': time.time(),
            'akshare_start_time': time.time()
        }

    def load_config(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                logging.info(f"已加载配置文件: {self.config_file}")
            except Exception as e:
                logging.warning(f"加载配置文件失败: {e}, 使用默认配置")
        else:
            logging.warning(f"配置文件不存在: {self.config_file}, 使用默认配置")

        return config

    def setup_logging(self):
        """设置日志"""
        log_level = self.config.get('Download', 'log_level', fallback='INFO')

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_downloader.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def get_next_data_source(self) -> Optional[str]:
        """获取下一个数据源（时间轮动机制）"""
        if not self.enable_baostock and not self.enable_akshare:
            logging.error("没有可用的数据源！")
            return None

        # 获取当前时间
        current_time = time.time()

        if self.stats['current_source'] == 'baostock':
            # 检查是否达到时间限制
            if current_time - self.stats.get('baostock_start_time', current_time) >= self.baostock_time_limit:
                # 切换到 akshare
                if self.enable_akshare:
                    self.stats['baostock_start_time'] = current_time
                    self.stats['current_source'] = 'akshare'
                    logging.info("切换到 akshare 数据源（时间轮动）")
                    return 'akshare'
                else:
                    # 如果 akshare 不可用，继续使用 baostock
                    logging.warning("akshare 不可用，继续使用 baostock")
                    return 'baostock'
            else:
                return 'baostock'
        else:  # current_source == 'akshare'
            # 检查是否达到时间限制
            if current_time - self.stats.get('akshare_start_time', current_time) >= self.akshare_time_limit:
                # 切换到 baostock
                if self.enable_baostock:
                    self.stats['akshare_start_time'] = current_time
                    self.stats['current_source'] = 'baostock'
                    logging.info("切换到 baostock 数据源（时间轮动）")
                    return 'baostock'
                else:
                    # 如果 baostock 不可用，继续使用 akshare
                    logging.warning("baostock 不可用，继续使用 akshare")
                    return 'akshare'
            else:
                return 'akshare'

    def download_with_baostock(self, stock_code: str) -> Optional[pd.DataFrame]:
        """使用 baostock 下载股票数据"""
        try:
            logging.info(f"[BAOSTOCK] 正在下载 {stock_code}...")
            df = self.updater.fetch_stock_data(stock_code, "2000-01-01")
            if not df.empty:
                logging.info(f"[BAOSTOCK] ✓ {stock_code} 下载成功 ({len(df)} 条记录)")
                return df
            else:
                logging.warning(f"[BAOSTOCK] ✗ {stock_code} 无数据")
                return None
        except Exception as e:
            logging.error(f"[BAOSTOCK] ✗ {stock_code} 下载失败: {e}")
            return None

    def download_with_akshare(self, stock_code: str) -> Optional[pd.DataFrame]:
        """使用 akshare 下载股票数据"""
        try:
            import akshare as ak

            # 确定 akshare 的股票代码格式
            if stock_code.startswith('6'):
                ak_code = f"sh{stock_code}"
            else:
                ak_code = f"sz{stock_code}"

            logging.info(f"[AKSHARE] 正在下载 {stock_code}...")

            # 使用 akshare 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=ak_code,
                period="daily",
                start_date="20000101",
                end_date=datetime.datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )

            if not df.empty:
                # 转换字段格式以匹配主程序
                df = self.convert_akshare_to_standard(df, stock_code)
                logging.info(f"[AKSHARE] ✓ {stock_code} 下载成功 ({len(df)} 条记录)")
                return df
            else:
                logging.warning(f"[AKSHARE] ✗ {stock_code} 无数据")
                return None

        except ImportError:
            logging.error("akshare 库未安装，请先安装: pip install akshare")
            return None
        except Exception as e:
            logging.error(f"[AKSHARE] ✗ {stock_code} 下载失败: {e}")
            return None

    def convert_akshare_to_standard(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """将 akshare 数据转换为标准格式"""
        try:
            # akshare 数据字段：日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
            # 需要转换为：股票代码,股票名称,交易日期,开盘价,最高价,最低价,收盘价,前收盘价,成交量,成交额,流通市值,总市值

            result_df = pd.DataFrame()

            # 基本信息
            result_df['股票代码'] = [f"sh{stock_code}" if stock_code.startswith('6') else f"sz{stock_code}"] * len(df)
            result_df['股票名称'] = [self.get_stock_name_from_akshare(stock_code)] * len(df)
            result_df['交易日期'] = df['日期'].values

            # 价格数据
            result_df['开盘价'] = pd.to_numeric(df['开盘'], errors='coerce').round(2)
            result_df['最高价'] = pd.to_numeric(df['最高'], errors='coerce').round(2)
            result_df['最低价'] = pd.to_numeric(df['最低'], errors='coerce').round(2)
            result_df['收盘价'] = pd.to_numeric(df['收盘'], errors='coerce').round(2)

            # 前收盘价（需要计算）
            result_df['前收盘价'] = result_df['收盘价'].shift(1).fillna(result_df['收盘价'])

            # 成交量成交额
            result_df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
            result_df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')

            # 市值字段（akshare 不提供）
            result_df['流通市值'] = None
            result_df['总市值'] = None

            return result_df

        except Exception as e:
            logging.error(f"转换 akshare 数据失败: {e}")
            return pd.DataFrame()

    def get_stock_name_from_akshare(self, stock_code: str) -> str:
        """从 akshare 获取股票名称"""
        try:
            import akshare as ak

            if stock_code.startswith('6'):
                ak_code = f"sh{stock_code}"
            else:
                ak_code = f"sz{stock_code}"

            # 获取股票基本信息
            stock_info = ak.stock_info_a_code_name()
            name = stock_info.get(ak_code, stock_code)
            return name

        except Exception as e:
            logging.warning(f"获取股票名称失败: {e}")
            return stock_code

    def load_progress(self) -> tuple:
        """加载断点续传进度"""
        completed_stocks = set()
        failed_stocks = set()

        if self.enable_resume:
            # 加载完成进度
            if os.path.exists(self.progress_file):
                try:
                    with open(self.progress_file, 'r', encoding='utf-8') as f:
                        progress_data = json.load(f)
                        completed_stocks = set(progress_data.get('completed', []))
                    logging.info(f"找到进度文件，已下载 {len(completed_stocks)} 只股票")
                except Exception as e:
                    logging.warning(f"读取进度文件失败: {e}")

            # 加载失败记录
            if os.path.exists(self.failed_file):
                try:
                    with open(self.failed_file, 'r', encoding='utf-8') as f:
                        failed_data = json.load(f)
                        failed_stocks = set(failed_data.get('failed', []))
                    logging.info(f"找到失败记录，之前失败 {len(failed_stocks)} 只股票")
                except Exception as e:
                    logging.warning(f"读取失败记录文件失败: {e}")

        return completed_stocks, failed_stocks

    def save_progress(self, completed_stocks: set, failed_stocks: set):
        """保存断点续传进度"""
        try:
            # 保存完成进度
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump({'completed': list(completed_stocks)}, f, ensure_ascii=False, indent=2)

            # 保存失败记录
            with open(self.failed_file, 'w', encoding='utf-8') as f:
                json.dump({'failed': list(failed_stocks)}, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logging.error(f"保存进度失败: {e}")

    def download_stock(self, stock_code: str) -> bool:
        """下载单个股票数据"""
        try:
            # 获取下一个数据源
            data_source = self.get_next_data_source()
            if not data_source:
                return False

            # 根据数据源下载
            if data_source == 'baostock':
                df = self.download_with_baostock(stock_code)
            else:  # akshare
                df = self.download_with_akshare(stock_code)

            if df is not None and not df.empty:
                # 保存数据
                self.updater.create_new_stock_file(stock_code, df)
                self.stats['success_count'] += 1
                return True
            else:
                self.stats['fail_count'] += 1
                logging.warning(f"[{data_source.upper()}] ✗ {stock_code} 下载失败")
                return False

        except Exception as e:
            logging.error(f"[{data_source.upper()}] 下载 {stock_code} 异常: {e}")
            self.stats['fail_count'] += 1
            return False

    def download_all_stocks(self, force_redownload: bool = False):
        """下载所有股票数据"""
        logging.info("=" * 60)
        logging.info("增强版股票数据下载程序")
        logging.info("=" * 60)

        # 1. 登录数据源
        logging.info("登录 baostock...")
        if not self.updater.login_baostock():
            logging.error("baostock 登录失败")
            return False

        try:
            # 2. 获取股票列表
            logging.info("获取沪深A股股票列表...")
            all_stocks = self.updater.get_all_a_share_stocks()
            logging.info(f"共找到 {len(all_stocks)} 只沪深A股股票")

            if not all_stocks:
                logging.error("获取股票列表失败")
                return False

            # 3. 加载断点续传进度
            if force_redownload:
                logging.info("强制重新下载模式，忽略断点续传")
                completed_stocks = set()
                failed_stocks = set()
            else:
                completed_stocks, failed_stocks = self.load_progress()

            # 4. 筛选需要下载的股票
            stocks_to_download = [
                code for code in all_stocks
                if code not in completed_stocks
            ]

            logging.info(f"需要下载的股票数量: {len(stocks_to_download)}/{len(all_stocks)}")

            if not stocks_to_download:
                logging.info("所有股票数据已下载完成！")
                return True

            # 5. 开始下载
            logging.info("开始下载股票数据...")
            logging.info("=" * 60)

            try:
                for i, stock_code in enumerate(stocks_to_download, 1):
                    logging.info(f"[{i}/{len(stocks_to_download)}] 下载 {stock_code}")

                    # 下载股票数据
                    success = self.download_stock(stock_code)

                    if success:
                        completed_stocks.add(stock_code)
                        if stock_code in failed_stocks:
                            failed_stocks.remove(stock_code)
                    else:
                        failed_stocks.add(stock_code)

                    # 保存进度
                    self.save_progress(completed_stocks, failed_stocks)

                    # 添加延迟
                    delay = self.delay_time + random.uniform(0, 0.5)
                    logging.debug(f"延迟 {delay:.2f} 秒")
                    time.sleep(delay)

            except KeyboardInterrupt:
                logging.info("\n用户暂停下载！")
                logging.info(f"当前进度: 成功 {len(completed_stocks)} 只，失败 {len(failed_stocks)} 只")
                return True

            # 6. 下载完成统计
            logging.info("=" * 60)
            logging.info("下载完成！")
            logging.info(f"成功下载: {len(completed_stocks)} 只股票")
            logging.info(f"失败: {len(failed_stocks)} 只股票")
            logging.info(f"总计: {len(all_stocks)} 只股票")
            logging.info("=" * 60)

            # 清理进度文件（如果全部完成）
            if len(completed_stocks) == len(all_stocks):
                if os.path.exists(self.progress_file):
                    os.remove(self.progress_file)
                if os.path.exists(self.failed_file):
                    os.remove(self.failed_file)
                logging.info("所有股票下载完成，清理进度文件")

            return True

        finally:
            # 退出 baostock
            self.updater.logout_baostock()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="增强版股票数据下载程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python enhanced_downloader.py              # 断点续传模式
  python enhanced_downloader.py --force      # 强制重新下载所有股票
  python enhanced_downloader.py --usage      # 显示使用帮助
        """
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新下载所有股票数据"
    )

    parser.add_argument(
        "--usage",
        action="store_true",
        help="显示使用帮助"
    )

    args = parser.parse_args()

    # 显示使用帮助
    if args.usage:
        parser.print_help()
        return

    # 创建下载器
    downloader = EnhancedStockDownloader()

    # 开始下载
    force_redownload = args.force

    try:
        # 检查数据目录
        data_dir = downloader.data_dir
        if os.path.exists(data_dir) and force_redownload:
            import shutil
            shutil.rmtree(data_dir)
            logging.info(f"已清空数据目录: {data_dir}")

        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)

        # 开始下载
        downloader.download_all_stocks(force_redownload=force_redownload)

    except KeyboardInterrupt:
        logging.info("\n用户中断程序执行")
    except Exception as e:
        logging.error(f"\n程序执行出错: {e}")


if __name__ == "__main__":
    main()