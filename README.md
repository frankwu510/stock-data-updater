# 股票数据更新工具

这是一个用于从 Baostock 获取和更新股票数据的 Python 工具。

## 功能特性

- 🔐 自动登录 Baostock
- 📊 获取历史股票数据
- 🔄 更新现有股票数据
- 🆕 创建新股票数据文件
- 🧪 支持测试模式和正式模式
- 💾 数据保存为 CSV 格式

## 安装

### 前提条件

- Python 3.7 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载项目到本地
2. 安装依赖：

```bash
pip install -r requirements.txt
```

或者使用 setup.py 安装：

```bash
pip install -e .
```

## 使用方法

### 直接运行

```bash
python src/stock_data_updater/main.py
```

### 作为命令行工具运行

安装后可以使用命令行工具：

```bash
stock-updater
```

### 运行模式

程序启动后会询问运行模式：

- **模式 1 (测试模式)**: 使用 `data_test` 目录，适合测试和开发
- **模式 2 (正式模式)**: 使用 `data` 目录，用于生产环境

## 数据格式

程序会为每只股票创建一个 CSV 文件，包含以下字段：

| 字段名 | 说明 |
|--------|------|
| 股票代码 | 股票完整代码 (如 sh600000) |
| 股票名称 | 股票名称 |
| 交易日期 | 交易日期 (YYYY-MM-DD) |
| 开盘价 | 开盘价格 |
| 最高价 | 最高价格 |
| 最低价 | 最低价格 |
| 收盘价 | 收盘价格 |
| 前收盘价 | 前一交易日收盘价 |
| 成交量 | 成交量 |
| 成交额 | 成交额 |
| 流通市值 | 流通市值 |
| 总市值 | 总市值 |

## 文件结构

```
stock-data-updater/
├── src/
│   └── stock_data_updater/
│       ├── __init__.py
│       └── main.py
├── data/                    # 正式数据目录
├── data_test/              # 测试数据目录
├── tests/                  # 测试代码
├── .vscode/                # VS Code 配置
├── setup.py               # 安装脚本
├── requirements.txt       # 依赖文件
└── README.md             # 项目说明
```

## 配置说明

- **数据目录**: 默认使用 `data` 目录存储正式数据，`data_test` 目录用于测试
- **编码格式**: CSV 文件使用 GBK 编码保存，确保中文字符正常显示
- **请求频率**: 程序会自动添加延迟，避免请求过于频繁

## 注意事项

1. 需要网络连接才能访问 Baostock 服务
2. 数据更新时会自动跳过已经是最新数据的股票
3. 程序会自动创建所需的数据目录
4. 建议在非交易时段运行，避免影响正常交易

## 开发说明

### 项目结构

- `StockDataUpdater` 类: 主要的股票数据更新器
- `login_baostock()`: 登录 Baostock 服务
- `logout_baostock()`: 退出 Baostock 服务
- `fetch_stock_data()`: 获取股票数据
- `update_existing_stocks()`: 更新现有股票数据
- `create_new_stock_file()`: 创建新股票文件

### 扩展功能

可以根据需要扩展以下功能：

- 添加更多股票数据字段
- 支持其他数据源
- 添加数据验证和清理功能
- 实现定时自动更新
- 添加数据可视化功能

## 许可证

MIT License

## 支持

如有问题或建议，请提交 Issue 或联系开发者。