#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深A股所有股票历史数据完整下载程序

简单操作脚本：一键下载所有沪深A股的完整历史数据
"""

import os
import sys
import time
import logging
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stock_data_updater import StockDataUpdater

# 增强日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_all_stocks():
    """
    下载所有沪深A股的完整历史数据
    支持断点续传功能
    """
    print("=" * 60)
    print("沪深A股所有股票历史数据完整下载程序")
    print("=" * 60)

    # 1. 初始化更新器
    print("\n[步骤1/4] 初始化股票数据更新器...")
    data_dir = "data_all"
    updater = StockDataUpdater(data_dir)
    print(f"数据将保存到: {os.path.abspath(data_dir)}")

    # 断点续传配置文件
    progress_file = "download_progress.json"
    failed_file = "failed_stocks.json"

    # 2. 登录Baostock
    print("\n[步骤2/4] 登录Baostock...")
    if not updater.login_baostock():
        print("登录失败，程序退出")
        return False

    try:
        # 3. 获取所有沪深A股列表
        print("\n[步骤3/4] 获取沪深A股股票列表...")
        all_stocks = updater.get_all_a_share_stocks()
        print(f"共找到 {len(all_stocks)} 只沪深A股股票")

        if not all_stocks:
            print("获取股票列表失败，程序退出")
            return False

        # 4. 断点续传处理
        print("\n[步骤4/4] 检查断点续传状态...")
        import json

        # 加载进度文件
        completed_stocks = set()
        failed_stocks = set()

        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    completed_stocks = set(progress_data.get('completed', []))
                print(f"找到进度文件，已下载 {len(completed_stocks)} 只股票")
            except Exception as e:
                logger.warning(f"读取进度文件失败: {e}")

        if os.path.exists(failed_file):
            try:
                with open(failed_file, 'r', encoding='utf-8') as f:
                    failed_data = json.load(f)
                    failed_stocks = set(failed_data.get('failed', []))
                print(f"找到失败记录，之前失败 {len(failed_stocks)} 只股票")
            except Exception as e:
                logger.warning(f"读取失败记录文件失败: {e}")

        # 筛选需要下载的股票（排除已完成的）
        stocks_to_download = [code for code in all_stocks if code not in completed_stocks]
        print(f"需要下载的股票数量: {len(stocks_to_download)}/{len(all_stocks)}")

        if not stocks_to_download:
            print("所有股票数据已下载完成！")
            return True

        # 5. 下载股票历史数据
        print("\n开始下载股票的历史数据...")
        print("=" * 60)
        print("重要提示：")
        print("1. 下载所有股票数据需要较长时间")
        print("2. 按 Ctrl+C 可暂停下载，下次运行会自动继续")
        print("3. 如需更换IP，请暂停后手动操作")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        try:
            for i, stock_code in enumerate(stocks_to_download, 1):
                try:
                    print(f"\n[{i}/{len(stocks_to_download)}] 正在下载 {stock_code}...")

                    # 下载完整历史数据（从2000-01-01开始）
                    df = updater.fetch_stock_data(stock_code, "2000-01-01")

                    if not df.empty:
                        # 创建股票文件
                        updater.create_new_stock_file(stock_code, df)
                        success_count += 1
                        print(f"✓ {stock_code} 下载成功 ({len(df)} 条记录)")

                        # 更新进度
                        completed_stocks.add(stock_code)
                        if stock_code in failed_stocks:
                            failed_stocks.remove(stock_code)

                    else:
                        fail_count += 1
                        print(f"✗ {stock_code} 无数据")
                        failed_stocks.add(stock_code)

                    # 保存进度
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump({'completed': list(completed_stocks)}, f, ensure_ascii=False, indent=2)

                    with open(failed_file, 'w', encoding='utf-8') as f:
                        json.dump({'failed': list(failed_stocks)}, f, ensure_ascii=False, indent=2)

                    # 添加随机延迟，避免请求过于频繁
                    delay = 0.5 + (hash(stock_code) % 10) * 0.05  # 0.5-1.0秒随机延迟
                    logger.info(f"延迟 {delay:.2f} 秒后继续...")
                    time.sleep(delay)

                except Exception as e:
                    fail_count += 1
                    print(f"✗ {stock_code} 下载失败: {e}")
                    failed_stocks.add(stock_code)

                    # 保存进度
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump({'completed': list(completed_stocks)}, f, ensure_ascii=False, indent=2)

                    with open(failed_file, 'w', encoding='utf-8') as f:
                        json.dump({'failed': list(failed_stocks)}, f, ensure_ascii=False, indent=2)

                    continue

        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("用户暂停下载！")
            print(f"当前进度: 成功 {success_count} 只，失败 {fail_count} 只")
            print("下次运行程序会自动从断点继续")
            print("=" * 60)
            return True

        # 下载完成总结
        print("\n" + "=" * 60)
        print("下载完成！")
        print(f"成功下载: {success_count} 只股票")
        print(f"失败: {fail_count} 只股票")
        print(f"总计: {len(stocks_to_download)} 只股票")
        print("=" * 60)

        # 清理进度文件（如果全部完成）
        if len(completed_stocks) == len(all_stocks):
            if os.path.exists(progress_file):
                os.remove(progress_file)
            if os.path.exists(failed_file):
                os.remove(failed_file)
            print("所有股票下载完成，清理进度文件")

        return True

    finally:
        # 退出Baostock
        updater.logout_baostock()


def main():
    """主函数"""
    try:
        # 检查是否需要清空数据目录
        data_dir = "data_all"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if files:
                print(f"\n警告：数据目录 {data_dir} 中已存在 {len(files)} 个数据文件")
                choice = input("是否清空现有数据并重新下载？(y/N): ").strip().lower()
                if choice == 'y':
                    import shutil
                    shutil.rmtree(data_dir)
                    print("已清空数据目录")
                else:
                    print("将保留现有数据，继续下载缺失的股票...")

        # 开始下载
        print("\n开始下载所有沪深A股历史数据...")
        input("按 Enter 键继续，或 Ctrl+C 取消...")

        success = download_all_stocks()

        if success:
            print("\n所有股票数据下载完成！")
            print(f"数据保存在: {os.path.abspath('data_all')}")
            print("可以按 Enter 键退出程序...")
        else:
            print("\n下载过程中出现错误，请检查日志文件。")

    except KeyboardInterrupt:
        print("\n\n用户中断程序执行")
    except Exception as e:
        print(f"\n程序执行出错: {e}")


if __name__ == "__main__":
    main()