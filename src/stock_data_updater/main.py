import os
import pandas as pd
import baostock as bs
import datetime
import time
import random
import logging
from typing import List, Tuple, Dict
from functools import wraps


class StockDataUpdater:
    def __init__(self, data_dir: str = "data"):
        """
        初始化股票数据更新器

        Args:
            data_dir: 数据目录路径
        """
        # 总市值: total_mv, 流通市值: circulating_mv
        self.data_dir = data_dir
        self.fields_mapping = {
            "code": "股票代码",
            "code_name": "股票名称",
            "date": "交易日期",
            "open": "开盘价",
            "high": "最高价",
            "low": "最低价",
            "close": "收盘价",
            "preclose": "前收盘价",
            "volume": "成交量",
            "amount": "成交额",
            "circulating_mv": "流通市值",
            "total_mv": "总市值",
            #"turn": "换手率",
            #"adjustflag": "复权状态",
            #"tradestatus": "交易状态",
            #"pctChg": "涨跌幅",
            #"peTTM": "市盈率",
            #"psTTM": "市销率",
            #"pcfNcfTTM": "市现率",
            #"pbMRQ": "市净率",
            #"isST": "是否ST"
        }

        # 定义统一的字段顺序
        self.column_order = [
            '股票代码', '股票名称', '交易日期', '开盘价', '最高价',
            '最低价', '收盘价', '前收盘价', '成交量', '成交额',
            '流通市值', '总市值'
        ]

        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # 防IP封禁配置
        self.request_delay = 0.5  # 基础延迟时间（秒）
        self.max_retries = 3      # 最大重试次数
        self.timeout = 30         # 请求超时时间（秒）

        # 断点续传配置
        self.progress_file = os.path.join(self.data_dir, "download_progress.json")
        self.failed_file = os.path.join(self.data_dir, "failed_stocks.json")

    @staticmethod
    def anti_ip_block_decorator(func):
        """
        防IP封禁装饰器（静态方法）
        提供重试机制、随机延迟和详细的日志记录
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 执行前延迟（随机延迟避免规律性请求）
            delay = self.request_delay + random.uniform(0.1, 0.5)
            self.logger.info(f"请求前延迟: {delay:.2f}秒")
            time.sleep(delay)

            # 重试机制
            for attempt in range(self.max_retries + 1):
                try:
                    self.logger.info(f"开始执行 {func.__name__} (尝试 {attempt + 1}/{self.max_retries + 1})")
                    result = func(self, *args, **kwargs)

                    # 执行成功后延迟
                    success_delay = self.request_delay + random.uniform(0.1, 0.3)
                    self.logger.info(f"请求成功，执行后延迟: {success_delay:.2f}秒")
                    time.sleep(success_delay)

                    return result

                except Exception as e:
                    self.logger.error(f"第 {attempt + 1} 次尝试失败: {e}")

                    if attempt < self.max_retries:
                        # 计算重试延迟（指数退避）
                        retry_delay = (2 ** attempt) * self.request_delay + random.uniform(0.5, 1.0)
                        self.logger.info(f"等待 {retry_delay:.2f}秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        self.logger.error(f"所有重试均失败，放弃请求")
                        raise e

        return wrapper

    @anti_ip_block_decorator
    def get_stock_name(self, stock_code) -> str:
        """
        通过股票代码获取股票名称
        :param stock_code: 股票代码，如 'sh.600000'
        :return: 股票名称
        """
        try:
            self.logger.info(f"查询股票名称: {stock_code}")
            # 查询股票基本信息
            rs = bs.query_stock_basic(code=stock_code)

            if rs.error_code == '0':
                # 获取查询结果
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())

            if data_list:
                # 返回股票名称（在返回数据的第2个位置）
                stock_name = data_list[0][1]
                self.logger.info(f"成功获取股票名称: {stock_code} -> {stock_name}")
                return stock_name
            else:
                self.logger.error(f"查询股票名称失败: {rs.error_msg}")
                return None

        except Exception as e:
            self.logger.error(f"获取股票名称异常: {e}")
            raise

    @anti_ip_block_decorator
    def login_baostock(self) -> bool:
        """
        登录baostock

        Returns:
            bool: 登录是否成功
        """
        try:
            self.logger.info("正在登录baostock...")
            lg = bs.login()
            if lg.error_code == '0':
                self.logger.info("baostock登录成功")
                return True
            else:
                self.logger.error(f"baostock登录失败: {lg.error_msg}")
                return False
        except Exception as e:
            self.logger.error(f"登录异常: {e}")
            raise

    def logout_baostock(self):
        """退出baostock"""
        try:
            bs.logout()
            self.logger.info("baostock已退出")
        except Exception as e:
            self.logger.error(f"退出baostock时出错: {e}")

    def logout_baostock(self):
        """退出baostock"""
        bs.logout()
        print("baostock已退出")

    def get_existing_stocks(self) -> Dict[str, str]:
        """
        获取现有股票文件列表

        Returns:
            Dict: 股票代码到文件路径的映射
        """
        stock_files = {}
        if not os.path.exists(self.data_dir):
            return stock_files

        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                # 提取股票代码：sh603508 -> 603508
                stock_code = filename[2:-4]  # 去掉交易所前缀和.csv后缀
                stock_files[stock_code] = os.path.join(self.data_dir, filename)

        return stock_files

    def get_latest_trade_date(self, file_path: str) -> str:
        """
        获取文件中最新的交易日期

        Args:
            file_path: 文件路径

        Returns:
            str: 最新交易日期，格式为YYYY-MM-DD
        """
        try:
            if not os.path.exists(file_path):
                return "2000-01-01"  # 如果文件不存在，返回很早的日期

            df = pd.read_csv(file_path, encoding='gbk')
            if df.empty:
                return "2000-01-01"

            # 确保日期列是字符串类型并按日期排序
            df['交易日期'] = pd.to_datetime(df['交易日期']).dt.strftime('%Y-%m-%d')
            latest_date = df['交易日期'].max()
            return latest_date

        except Exception as e:
            print(f"读取文件{file_path}最新日期失败: {e}")
            return "2000-01-01"

    def get_stock_name(self,stock_code) -> str:
        """
        通过股票代码获取股票名称
        :param stock_code: 股票代码，如 'sh.600000'
        :return: 股票名称
        """
        # 查询股票基本信息
        rs = bs.query_stock_basic(code=stock_code)

        if rs.error_code == '0':
            # 获取查询结果
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

        if data_list:
            # 返回股票名称（在返回数据的第2个位置）
            return data_list[0][1]
        else:
            print(f"查询失败: {rs.error_msg}")
            return None

    def get_stock_market_value(self, stock_code: str, date: str) -> tuple:
        """
        获取股票市值信息

        注意：Baostock API 暂不支持直接获取流通市值和总市值，
        这里通过其他方式估算或返回 None

        Args:
            stock_code: 股票代码（带交易所前缀，如 'sh.600000'）
            date: 日期（YYYY-MM-DD）

        Returns:
            tuple: (流通市值, 总市值)
        """
        try:
            print(f"正在尝试获取 {stock_code} 在 {date} 的市值数据...")

            # 由于 Baostock 不支持直接获取市值，我们可以：
            # 1. 通过收盘价和总股本计算（需要额外接口）
            # 2. 返回 None，让用户手动补充
            # 3. 使用其他数据源

            # 目前暂时返回 None，但保留字段结构
            print("Baostock API 暂不支持直接获取市值数据，字段将保持为空")
            return None, None

        except Exception as e:
            print(f"获取{stock_code}市值数据异常: {e}")
            return None, None

    @anti_ip_block_decorator
    def fetch_stock_data(self, stock_code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        从baostock获取股票数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期，默认为当前日期

        Returns:
            pd.DataFrame: 股票数据
        """
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"获取股票数据: {stock_code} ({start_date} 到 {end_date})")

        # 确定交易所前缀
        if stock_code.startswith('6'):
            bs_code = f"sh.{stock_code}"
            file_prefix = "sh"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            bs_code = f"sz.{stock_code}"
            file_prefix = "sz"
        #elif stock_code.startswith('8') or stock_code.startswith('4'):
        #    bs_code = f"bj.{stock_code}"
        #    file_prefix = "bj"
        else:
            self.logger.error(f"无法识别股票代码{stock_code}的交易所")
            return pd.DataFrame()

        try:
            # 查询股票数据
            #rs = bs.query_history_k_data_plus(
            #    bs_code,
            #    "code,code_name,date,open,high,low,close,preclose,volume,amount,turn,adjustflag,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST",
            #    start_date=start_date,
            #    end_date=end_date,
            #    frequency="d",
            #    adjustflag="2"  # 复权类型(1：后复权，2：前复权，3：不复权)
            #)

            rs = bs.query_history_k_data_plus(
                bs_code,
                "code,date,open,high,low,close,preclose,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"  # 复权类型(1：后复权，2：前复权，3：不复权)
            )

            if rs.error_code != '0':
                self.logger.error(f"获取{stock_code}数据失败: {rs.error_msg}")
                return pd.DataFrame()

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                self.logger.warning(f"股票{stock_code}在{start_date}到{end_date}期间无数据")
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(data_list, columns=rs.fields)

            # 重命名列
            df = df.rename(columns=self.fields_mapping)

            # 设置股票代码
            df['股票代码'] = file_prefix + bs_code[3:]

            # 确保所有需要的列都存在
            for col in self.column_order:
                if col not in df.columns:
                    df[col] = None

            # 重新排列列顺序
            df = df[self.column_order]

            # 设置股票名称（从API获取）
            try:
                stock_name = self.get_stock_name(bs_code)
                df['股票名称'] = stock_name
            except Exception as e:
                self.logger.warning(f"获取股票名称失败 {bs_code}: {e}")
                df['股票名称'] = None

            # 修复问题1：价格字段统一保留小数点后两位
            price_columns = ['开盘价', '最高价', '最低价', '收盘价', '前收盘价']
            for col in price_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

            # 修复问题2：设置流通市值和总市值字段
            # 由于 Baostock API 暂不支持直接获取市值数据，
            # 这里保留字段结构但值为空，用户可后续手动补充
            df['流通市值'] = None
            df['总市值'] = None

            self.logger.info(f"成功获取股票数据: {stock_code} ({len(df)} 条记录)")

            return df

        except Exception as e:
            self.logger.error(f"获取{stock_code}数据异常: {e}")
            raise

    def update_existing_stocks(self, existing_stocks: Dict[str, str]):
        """
        更新现有股票数据

        Args:
            existing_stocks: 现有股票字典
        """
        updated_count = 0
        for stock_code, file_path in existing_stocks.items():
            try:
                print(f"正在更新股票 {stock_code}...")

                # 获取最新交易日期
                latest_date = self.get_latest_trade_date(file_path)
                start_date = (pd.to_datetime(latest_date) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                # 如果最新日期已经是今天或未来，跳过
                if pd.to_datetime(start_date) > pd.to_datetime(datetime.datetime.now().strftime('%Y-%m-%d')):
                    print(f"股票{stock_code}数据已是最新")
                    continue

                # 获取新数据
                new_data = self.fetch_stock_data(stock_code, start_date)

                if new_data.empty:
                    print(f"股票{stock_code}无新数据")
                    continue

                # 读取现有数据
                if os.path.exists(file_path):
                    existing_df = pd.read_csv(file_path, encoding='gbk')
                    # 合并数据
                    combined_df = pd.concat([existing_df, new_data], ignore_index=True)
                else:
                    combined_df = new_data

                # 去重并按日期排序
                combined_df = combined_df.drop_duplicates(subset=['交易日期'], keep='last')
                combined_df['交易日期'] = pd.to_datetime(combined_df['交易日期'])
                combined_df = combined_df.sort_values('交易日期')
                combined_df['交易日期'] = combined_df['交易日期'].dt.strftime('%Y-%m-%d')

                # 确保所有数据的价格字段都格式化为小数点后两位
                price_columns = ['开盘价', '最高价', '最低价', '收盘价', '前收盘价']
                for col in price_columns:
                    if col in combined_df.columns:
                        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').round(2)

                # 确保市值字段存在并转换为数值类型
                mv_columns = ['流通市值', '总市值']
                for col in mv_columns:
                    if col in combined_df.columns:
                        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

                # 保存数据
                combined_df.to_csv(file_path, index=False, encoding='gbk')
                updated_count += 1
                print(f"股票{stock_code}更新完成，新增{len(new_data)}条记录")

                # 添加延迟，避免请求过于频繁
                time.sleep(0.1)

            except Exception as e:
                print(f"更新股票{stock_code}失败: {e}")
                continue

        print(f"现有股票更新完成，共更新{updated_count}只股票")

    @anti_ip_block_decorator
    def get_all_a_share_stocks(self) -> List[str]:
        """
        从baostock获取所有沪深A股股票代码

        Returns:
            List: 沪深A股股票代码列表（不带交易所前缀，如 '600000', '000001'）
        """
        try:
            self.logger.info("正在从Baostock获取沪深A股股票列表...")
            rs = bs.query_stock_basic(code='', code_name='')

            if rs.error_code != '0':
                self.logger.error(f"获取股票列表失败: {rs.error_msg}")
                return []

            a_stocks = []
            while (rs.error_code == '0') & rs.next():
                data = rs.get_row_data()
                if data:
                    code = data[0]  # 格式: sh.600000 或 sz.000001
                    # 筛选沪深A股：上证A股(6开头)、深证A股(0或3开头)
                    if code.startswith('sh.6') or code.startswith('sz.0') or code.startswith('sz.3'):
                        # 去掉交易所前缀，只保留股票代码
                        stock_code = code[3:]
                        a_stocks.append(stock_code)

            self.logger.info(f"成功获取 {len(a_stocks)} 只沪深A股股票")
            return a_stocks

        except Exception as e:
            self.logger.error(f"获取沪深A股列表异常: {e}")
            raise

    def find_new_stocks(self, existing_stocks: Dict[str, str]) -> List[str]:
        """
        查找新股（从baostock获取全量股票列表并比较）

        Args:
            existing_stocks: 现有股票字典

        Returns:
            List: 新股代码列表
        """
        # 获取所有沪深A股
        all_stocks = self.get_all_a_share_stocks()

        # 获取现有股票
        existing_codes = set(existing_stocks.keys())

        # 查找新股
        new_stocks = [code for code in all_stocks if code not in existing_codes]

        print(f"发现 {len(new_stocks)} 只新股")
        return new_stocks

    def create_new_stock_file(self, stock_code: str, df: pd.DataFrame):
        """
        创建新的股票数据文件

        Args:
            stock_code: 股票代码
            df: 股票数据
        """
        if df.empty:
            print(f"股票{stock_code}无数据，无法创建文件")
            return

        # 确定文件前缀
        if stock_code.startswith('6'):
            file_prefix = "sh"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            file_prefix = "sz"
        else:
            print(f"无法确定股票代码{stock_code}的交易所")
            return

        filename = f"{file_prefix}{stock_code}.csv"
        file_path = os.path.join(self.data_dir, filename)

        # 保存数据
        df.to_csv(file_path, index=False, encoding='gbk')
        print(f"新建股票文件: {filename}")

    def update_all_stocks(self):
        """更新所有股票数据"""
        # 登录baostock
        if not self.login_baostock():
            return False

        try:
            # 获取现有股票
            existing_stocks = self.get_existing_stocks()
            print(f"找到{len(existing_stocks)}只现有股票")

            # 更新现有股票
            self.update_existing_stocks(existing_stocks)

            # 查找并创建新股（简化处理）
            new_stocks = self.find_new_stocks(existing_stocks)
            if new_stocks:
                print(f"发现{len(new_stocks)}只新股")
                for stock_code in new_stocks:
                    df = self.fetch_stock_data(stock_code, "2000-01-01")
                    if not df.empty:
                        self.create_new_stock_file(stock_code, df)
                        time.sleep(0.1)
            else:
                print("未发现新股")

            return True

        finally:
            # 退出baostock
            self.logout_baostock()


def test_program():
    """测试程序"""
    print("=== 测试模式 ===")
    updater = StockDataUpdater("data_test")

    # 创建测试目录和少量测试文件
    os.makedirs("data_test", exist_ok=True)

    # 创建几个测试文件（如果有的话）
    test_stocks = ['000001', '600000']  # 平安银行, 浦发银行

    success = updater.update_all_stocks()
    if success:
        print("测试完成")
    else:
        print("测试失败")


def main_program():
    """主程序"""
    print("=== 正式模式 ===")
    updater = StockDataUpdater("data")
    success = updater.update_all_stocks()
    if success:
        print("股票数据更新完成")
    else:
        print("股票数据更新失败")


def main():
    """命令行入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description='股票数据更新工具')
    parser.add_argument('--test', action='store_true', help='运行测试模式')
    parser.add_argument('--production', action='store_true', help='运行正式模式')

    args = parser.parse_args()

    if args.test:
        test_program()
    elif args.production:
        main_program()
    else:
        # 交互式模式
        print("请选择运行模式:")
        print("1 - 测试模式 (使用data_test目录)")
        print("2 - 正式模式 (使用data目录)")

        choice = input("请输入选择 (1 或 2): ").strip()

        if choice == "1":
            test_program()
        elif choice == "2":
            main_program()
        else:
            print("无效选择，退出程序")


if __name__ == "__main__":
    main()