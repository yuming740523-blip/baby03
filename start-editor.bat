@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  ==============================
echo   baby03 網頁編輯器
echo  ==============================
echo.
echo  啟動中，請稍候...
python deploy-server.py
pause
