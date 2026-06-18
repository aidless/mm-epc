@echo off
chcp 65001 >nul
title arXiv 采集器 - 100万篇
echo ============================================================
echo   arXiv CS 论文批量采集器
echo   断点续采，关闭此窗口即停止
echo ============================================================
echo.
C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe F:\test\2026-06-14-20-48-36\collect_arxiv_1m.py
echo.
echo ============================================================
echo   完成！按任意键关闭...
pause >nul
