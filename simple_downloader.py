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
    """
    print("=" * 60)
    print("沪深A股所有股票历史数据完整下载程序")
    print("=" * 60)

    # 1. 初始化更新器
    print("\n[步骤1/4] 初始化股票数据更新器...")
    data_dir = "data_all"
    updater = StockDataUpdater(data_dir)
    print(f"数据将保存到: {os.path.abspath(data_dir)}")

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

        # 4. 下载所有股票的历史数据
        print("\n[步骤4/4] 开始下载所有股票的历史数据...")
        print("=" * 60)
        print("重要提示：下载所有股票数据需要较长时间")
        print("每只股票下载完成后会显示进度信息")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        for i, stock_code in enumerate(all_stocks, 1):
            try:
                print(f"\n[{i}/{len(all_stocks)}] 正在下载 {stock_code}...")

                # 下载完整历史数据（从2000-01-01开始）
                df = updater.fetch_stock_data(stock_code, "2000-01-01")

                if not df.empty:
                    # 创建股票文件
                    updater.create_new_stock_file(stock_code, df)
                    success_count += 1
                    print(f"✓ {stock_code} 下载成功 ({len(df)} 条记录)")
                else:
                    fail_count += 1
                    print(f"✗ {stock_code} 无数据")

                # 添加延迟，避免请求过于频繁
                time.sleep(0.1)

            except Exception as e:
                fail_count += 1
                print(f"✗ {stock_code} 下载失败: {e}")
                continue

        # 下载完成总结
        print("\n" + "=" * 60)
        print("下载完成！")
        print(f"成功下载: {success_count} 只股票")
        print(f"失败: {fail_count} 只股票")
        print(f"总计: {len(all_stocks)} 只股票")
        print("=" * 60)

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