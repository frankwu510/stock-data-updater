# 快速开始指南

本指南将帮助您快速上手使用股票数据更新工具。

## 1. 环境准备

### 安装 Python
确保您已安装 Python 3.7 或更高版本：

```bash
python --version
# 或
python3 --version
```

### 安装依赖

```bash
# 进入项目目录
cd stock-data-updater

# 安装依赖包
pip install -r requirements.txt
```

## 2. 首次运行

### 测试模式
建议首次运行时使用测试模式：

```bash
python src/stock_data_updater/main.py --test
```

或者在 VS Code 中使用调试配置 "Python: 测试模式"

### 正式模式

```bash
python src/stock_data_updater/main.py --production
```

或者在 VS Code 中使用调试配置 "Python: 正式模式"

### 交互式模式

```bash
python src/stock_data_updater/main.py
```

程序会提示您选择运行模式。

## 3. 项目结构说明

```
stock-data-updater/
├── src/                           # 源代码目录
│   └── stock_data_updater/       # 主程序包
│       ├── __init__.py          # 包初始化文件
│       └── main.py              # 主程序文件
├── data/                        # 正式数据目录（自动生成）
├── data_test/                   # 测试数据目录（自动生成）
├── tests/                       # 测试代码
│   └── test_stock_data_updater.py
├── .vscode/                     # VS Code 配置文件
├── setup.py                     # 项目安装脚本
├── requirements.txt             # 依赖包列表
├── README.md                    # 项目说明
└── QUICK_START.md               # 快速开始指南（本文件）
```

## 4. VS Code 开发环境设置

### 推荐的扩展

1. **Python** - Microsoft 官方 Python 扩展
2. **Pylance** - Python 语言服务器
3. **Python Test Explorer** - 测试运行器

### 调试配置

项目已预配置了以下调试选项：

- **Python: 股票数据更新器** - 默认调试配置
- **Python: 测试模式** - 直接运行测试模式
- **Python: 正式模式** - 直接运行正式模式
- **Python: 当前文件** - 调试当前打开的文件

### 代码格式化

项目已配置自动代码格式化：
- 保存时自动格式化
- 使用 autopep8 格式化器
- 最大行长度 120 字符

## 5. 常见问题

### Q: 运行时提示 "ModuleNotFoundError: No module named 'baostock'"

A: 请确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### Q: CSV 文件中文显示乱码

A: 程序使用 GBK 编码保存 CSV 文件。使用 Excel 打开时选择 GBK 编码，或使用支持 GBK 的文本编辑器。

### Q: 如何添加新的股票数据字段？

A: 修改 `src/stock_data_updater/main.py` 中的 `fields_mapping` 字典和 `fetch_stock_data` 方法中的查询字段。

### Q: 程序运行很慢

A: 程序内置了请求延迟（0.1秒/次）以避免过于频繁的请求。您可以根据需要调整延迟时间。

## 6. 下一步

- 查看 [README.md](README.md) 了解完整功能说明
- 运行测试确保环境正常：`python -m pytest tests/`
- 根据需求修改配置和代码
- 设置定时任务自动更新数据

## 7. 开发提示

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_stock_data_updater.py::TestStockDataUpdater::test_init -v
```

### 代码检查

```bash
# 检查代码风格
python -m pylint src/

# 类型检查
python -m mypy src/
```

### 打包发布

```bash
# 创建分发包
python setup.py sdist bdist_wheel

# 安装到本地
pip install -e .
```

---

祝您使用愉快！如有问题，请查看项目文档或联系开发者。