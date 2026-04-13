# Git 仓库设置指南

本指南介绍如何将本地项目推送到远程 Git 仓库（如 GitHub、GitLab 等）。

## 1. 在远程平台创建仓库

### GitHub
1. 登录 GitHub 账户
2. 点击 "+" -> "New repository"
3. 输入仓库名称：`stock-data-updater`
4. 选择公开或私有
5. **不要**初始化 README、.gitignore 或 LICENSE（项目已包含）
6. 点击 "Create repository"

### GitLab
1. 登录 GitLab 账户
2. 点击 "New project"
3. 选择 "Create blank project"
4. 输入项目名称：`stock-data-updater`
5. 选择可见性级别
6. **不要**初始化项目
7. 点击 "Create project"

## 2. 添加远程仓库地址

### GitHub 示例
```bash
git remote add origin https://github.com/your-username/stock-data-updater.git
```

### GitLab 示例
```bash
git remote add origin https://gitlab.com/your-username/stock-data-updater.git
```

## 3. 推送代码到远程仓库

```bash
# 首次推送，设置上游分支
git push -u origin master

# 后续推送
git push
```

## 4. 验证推送结果

```bash
# 查看远程仓库信息
git remote -v

# 查看分支状态
git status
```

## 5. 后续开发流程

### 日常开发
```bash
# 查看修改状态
git status

# 添加修改到暂存区
git add .

# 提交修改
git commit -m "描述修改内容"

# 推送到远程仓库
git push
```

### 拉取最新代码
```bash
# 拉取远程修改
git pull

# 或者分别执行
git fetch
git merge origin/master
```

## 6. 分支管理（可选）

### 创建功能分支
```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout master

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 7. 项目特定说明

### 已忽略的文件
- `data/` - 股票数据文件（大量数据，不适合版本控制）
- `data_test/` - 测试数据文件
- `*.csv` - 所有 CSV 数据文件
- `__pycache__/` - Python 缓存文件
- `.pytest_cache/` - 测试缓存
- 虚拟环境目录

### 包含的文件
- 源代码 (`src/`)
- 测试代码 (`tests/`)
- 配置文件 (`.vscode/`)
- 文档文件 (`README.md`, `QUICK_START.md` 等)
- 项目配置 (`setup.py`, `requirements.txt`)
- 许可证文件 (`LICENSE`)

## 8. 团队协作设置

### 邀请协作者
1. 在 GitHub/GitLab 项目设置中添加协作者
2. 协作者接受邀请后，可以克隆项目：

```bash
git clone https://github.com/your-username/stock-data-updater.git
cd stock-data-updater
pip install -r requirements.txt
```

### 代码审查流程
1. 创建功能分支
2. 提交代码
3. 创建 Pull Request / Merge Request
4. 团队审查
5. 合并到主分支

## 9. 常见问题

### 认证失败
- GitHub: 使用 Personal Access Token 代替密码
- GitLab: 配置 SSH 密钥或个人访问令牌

### 推送被拒绝
```bash
# 先拉取最新代码
git pull origin master

# 解决冲突后重新推送
git push origin master
```

### 忘记添加文件
```bash
git add 忘记的文件名
git commit --amend
```

## 10. 备份建议

- 定期推送代码到远程仓库
- 重要版本打标签：`git tag v1.0.0`
- 考虑使用多个远程仓库作为备份

---

**注意**: 本项目已经配置了合适的 `.gitignore` 文件，会自动忽略数据文件和临时文件，只跟踪源代码和配置文件。