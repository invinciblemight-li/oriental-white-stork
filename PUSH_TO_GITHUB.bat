@echo off
chcp 65001 >nul
echo ============================================
echo 东方白鹳 - 推送到 GitHub
echo ============================================
echo.

REM 设置 Git 路径
set GIT_PATH=C:\Program Files\Git\bin\git.exe

REM 进入项目目录
cd /d C:\Users\Administrator\WorkBuddy\Claw\oriental-white-stork

echo [1/3] 添加远程仓库...
"%GIT_PATH%" remote add origin https://github.com/invinciblemight-li/oriental-white-stork.git

echo [2/3] 重命名分支为 main...
"%GIT_PATH%" branch -M main

echo [3/3] 推送到 GitHub...
"%GIT_PATH%" push -u origin main

echo.
echo ============================================
echo 完成！请检查 GitHub 仓库。
echo ============================================
pause
