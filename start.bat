@echo off
cd /d "%~dp0"
echo === Start Data Analysis System ===

echo Starting Django backend...
start "Django-Backend" /D "%~dp0backend" "%~dp0venv\Scripts\python.exe" manage.py runserver 8000

echo Starting Vue frontend...
start "Vue-Frontend" /D "%~dp0frontend" npm run dev

echo.
echo ==============================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ==============================
echo   Open http://localhost:5173 in browser
pause
