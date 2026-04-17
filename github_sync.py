#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 同步脚本 - stock-data-updater 项目

功能：
1. 上传项目到 GitHub (push)
2. 从 GitHub 下载项目 (pull)
3. 查看项目状态 (status)
4. 一键同步 (sync)

GitHub 仓库：https://github.com/frankwu510/stock-data-updater
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """执行命令行命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return None


def check_git_installed():
    """检查Git是否安装"""
    result = run_command("git --version", check=False)
    if result and result.returncode == 0:
        print(f"✓ Git 已安装: {result.stdout.strip()}")
        return True
    else:
        print("✗ Git 未安装或未添加到系统路径")
        print("请先安装 Git: https://git-scm.com/downloads")
        return False


def check_git_repo():
    """检查当前目录是否为Git仓库"""
    result = run_command("git rev-parse --is-inside-work-tree", check=False)
    if result and result.returncode == 0:
        return True
    return False


def init_git_repo():
    """初始化Git仓库"""
    if not check_git_installed():
        return False

    if check_git_repo():
        print("✓ 已经是Git仓库")
        return True

    print("初始化Git仓库...")
    commands = [
        "git init",
        "git remote add origin https://github.com/frankwu510/stock-data-updater.git"
    ]

    for cmd in commands:
        result = run_command(cmd)
        if not result:
            return False

    print("✓ Git仓库初始化成功")
    return True


def git_status():
    """查看Git状态"""
    print("\n" + "=" * 60)
    print("查看 Git 状态")
    print("=" * 60)
    run_command("git status")


def git_add():
    """添加文件到暂存区"""
    print("\n添加文件到暂存区...")
    # 添加所有文件，排除大文件和敏感信息
    result = run_command("git add .")
    if result:
        print("✓ 文件已添加到暂存区")
    return result is not None


def git_commit(message="Update project"):
    """提交更改"""
    print("\n提交更改...")
    result = run_command(f'git commit -m "{message}"')
    if result:
        print("✓ 提交成功")
    return result is not None


def git_push():
    """推送更改到GitHub"""
    print("\n推送到 GitHub...")
    print("可能需要输入GitHub用户名和密码/令牌")
    result = run_command("git push -u origin master")
    if result:
        print("✓ 推送成功")
    else:
        print("✗ 推送失败，可能需要身份验证")
        print("建议：使用 Personal Access Token 进行认证")
    return result is not None


def git_pull():
    """从GitHub拉取更改"""
    print("\n从 GitHub 拉取更新...")
    result = run_command("git pull origin master")
    if result:
        print("✓ 拉取成功")
    else:
        print("✗ 拉取失败，请检查网络连接")
    return result is not None


def git_sync():
    """同步GitHub仓库（拉取+推送）"""
    print("\n" + "=" * 60)
    print("同步 GitHub 仓库")
    print("=" * 60)

    # 先拉取更新
    if not git_pull():
        print("⚠ 拉取更新失败，继续推送...")

    # 推送本地更改
    if git_push():
        print("✓ 同步完成")
        return True
    else:
        print("✗ 同步失败")
        return False


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("GitHub 同步工具 - stock-data-updater")
    print("仓库: https://github.com/frankwu510/stock-data-updater")
    print("=" * 60)
    print("1. 查看状态 (status)")
    print("2. 推送到 GitHub (push)")
    print("3. 从 GitHub 拉取 (pull)")
    print("4. 一键同步 (pull + push)")
    print("5. 提交并推送")
    print("0. 退出")
    print("=" * 60)


def interactive_mode():
    """交互模式"""
    if not check_git_installed():
        return

    if not check_git_repo():
        print("当前目录不是Git仓库")
        if input("是否初始化Git仓库？(y/N): ").lower() == 'y':
            if not init_git_repo():
                return
        else:
            return

    while True:
        show_menu()
        choice = input("请选择操作: ").strip()

        if choice == "1":
            git_status()
        elif choice == "2":
            if git_add():
                git_commit()
                git_push()
        elif choice == "3":
            git_pull()
        elif choice == "4":
            git_sync()
        elif choice == "5":
            message = input("输入提交信息 (默认: Update project): ").strip()
            if not message:
                message = "Update project"
            if git_add():
                git_commit(message)
                git_push()
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")

        input("\n按 Enter 键继续...")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GitHub 同步工具 - stock-data-updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python github_sync.py          # 进入交互模式
  python github_sync.py --push   # 直接推送
  python github_sync.py --pull   # 直接拉取
  python github_sync.py --sync   # 一键同步
        """
    )

    parser.add_argument(
        "--push",
        action="store_true",
        help="直接推送到GitHub"
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="直接从GitHub拉取"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="一键同步（拉取+推送）"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="查看仓库状态"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化Git仓库"
    )

    args = parser.parse_args()

    # 命令行模式
    if args.init:
        init_git_repo()
    elif args.status:
        git_status()
    elif args.push:
        if git_add():
            git_commit()
            git_push()
    elif args.pull:
        git_pull()
    elif args.sync:
        git_sync()
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"工作目录: {os.getcwd()}")

    main()