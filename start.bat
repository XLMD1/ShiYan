@echo off
echo === Start Data Analysis System ===

echo Starting Django backend...
start "Django-Backend" cmd /c "cd /d E:\vs code\code\Python\ShiYan\backend && E:\vs code\code\Python\ShiYan\venv\Scripts\python.exe manage.py runserver 8000"

echo Starting Vue frontend...
start "Vue-Frontend" cmd /c "cd /d E:\vs code\code\Python\ShiYan\frontend && npm run dev"

echo.
echo ==============================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ==============================
echo   Open http://localhost:5173 in browser
pause
