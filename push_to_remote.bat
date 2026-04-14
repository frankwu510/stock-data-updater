@echo off
echo 正在推送项目到远程 Git 仓库...

echo 1. 检查当前状态...
git status

echo 2. 添加远程仓库地址...
git remote add origin https://github.com/frankwu510/stock-data-updater.git

echo 3. 推送到远程仓库...
git push -u origin master

echo 4. 验证推送结果...
git remote show origin

echo 推送完成！
pause
