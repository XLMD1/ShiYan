@echo off
echo === 启动数据分析系统 ===

echo.
echo [1/2] 启动 Django 后端...
start "Django Backend" cmd /c "cd /d E:\vs code\code\Python\ShiYan\backend && E:\vs code\code\Python\ShiYan\venv\Scripts\activate.bat && python manage.py runserver 8000"

echo [2/2] 启动 Vue 前端...
start "Vue Frontend" cmd /c "cd /d E:\vs code\code\Python\ShiYan\frontend && npm run dev"

echo.
echo ==============================
echo 后端:  http://localhost:8000
echo 前端:  http://localhost:5173
echo ==============================
echo.
echo 在浏览器打开 http://localhost:5173 即可使用
echo 关闭此窗口不会停止服务，请在两个新窗口中分别按 Ctrl+C 停止
pause
