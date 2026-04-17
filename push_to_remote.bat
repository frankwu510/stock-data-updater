@ECHO OFF
REM GitHub推送批处理文件
REM 用途：一键推送stock-data-updater项目到GitHub
REM 仓库：https://github.com/frankwu510/stock-data-updater

SETLOCAL

REM 设置编码，支持中文
CHCP 65001 > NUL

ECHO ============================================================
ECHO GitHub推送工具 - stock-data-updater
ECHO 仓库: https://github.com/frankwu510/stock-data-updater
ECHO ============================================================
ECHO.

REM 检查Python是否安装
python --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO ✗ Python未安装或未添加到系统路径
    ECHO 请先安装Python: https://www.python.org/downloads/
    ECHO.
    PAUSE
    EXIT /B 1
)

REM 检查github_sync.py是否存在
IF NOT EXIST "github_sync.py" (
    ECHO ✗ 未找到github_sync.py文件
    ECHO 请确保在正确的目录中运行此脚本
    ECHO.
    PAUSE
    EXIT /B 1
)

REM 显示菜单
:MENU
CLS
ECHO ============================================================
ECHO GitHub推送工具 - 请选择操作
ECHO ============================================================
ECHO 1. 查看仓库状态
ECHO 2. 提交并推送代码
ECHO 3. 从GitHub拉取更新
ECHO 4. 一键同步（拉取+推送）
ECHO 5. 初始化Git仓库（首次使用）
ECHO 0. 退出
ECHO ============================================================
ECHO.

SET /P choice="请选择操作 (0-5): "

IF "%choice%"=="1" (
    python github_sync.py --status
    GOTO CONTINUE
) ELSE IF "%choice%"=="2" (
    ECHO.
    SET /P commit_msg="输入提交信息 (默认: Update project): "
    IF "%commit_msg%"=="" SET commit_msg=Update project

    python github_sync.py --push
    GOTO CONTINUE
) ELSE IF "%choice%"=="3" (
    python github_sync.py --pull
    GOTO CONTINUE
) ELSE IF "%choice%"=="4" (
    python github_sync.py --sync
    GOTO CONTINUE
) ELSE IF "%choice%"=="5" (
    python github_sync.py --init
    GOTO CONTINUE
) ELSE IF "%choice%"=="0" (
    ECHO.
    ECHO 退出程序...
    EXIT /B 0
) ELSE (
    ECHO.
    ECHO 无效选择，请重新输入！
    ECHO.
    PAUSE
    GOTO MENU
)

:CONTINUE
ECHO.
ECHO 操作完成！
ECHO.
PAUSE
GOTO MENU

ENDLOCAL