@echo off
cd /d "%~dp0"
echo === Start Data Analysis System ===

echo Starting Django backend...
start "Django-Backend" /D "%~dp0backend" "%~dp0venv\Scripts\python.exe" manage.py runserver 8000

echo Waiting for backend to be ready...
timeout /t 3 /nobreak >nul

echo Starting Vue frontend...
start "Vue-Frontend" /D "%~dp0frontend" npm run dev

echo.
echo ==============================
echo   Frontend:   http://localhost:5173
echo   Backend API: http://localhost:8000/api/
echo   Admin:      http://localhost:8000/admin/
echo ==============================
echo.
echo Opening http://localhost:5173 ...
start http://localhost:5173
pause
