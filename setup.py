from setuptools import setup, find_packages

setup(
    name="stock-data-updater",
    version="0.1.0",
    description="股票数据更新工具 - 从 Baostock 获取和更新股票数据",
    long_description="""
    这是一个用于从 Baostock 获取和更新股票数据的 Python 工具。
    功能包括：
    - 自动登录 Baostock
    - 获取历史股票数据
    - 更新现有股票数据
    - 创建新股票数据文件
    - 支持测试模式和正式模式
    """,
    author="Frank wu",
    author_email="frankwu510@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.3.0",
        "baostock>=0.8.8",
    ],
    entry_points={
        "console_scripts": [
            "stock-updater=stock_data_updater.main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="stock data baostock finance",
)