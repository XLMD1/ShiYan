@echo off
cd /d "%~dp0"
echo === Setup Data Analysis System ===
echo.

if exist "%~dp0venv\Scripts\python.exe" (
    echo [1/3] venv already exists, skipping...
) else (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
    echo Done.
)

echo.
echo [2/3] Installing Python packages...
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0backend\requirements.txt" -q
echo Done.

echo.
if exist "%~dp0frontend\node_modules" (
    echo [3/3] node_modules already exists, skipping...
) else (
    echo [3/3] Installing Node.js packages...
    cd /d "%~dp0frontend"
    call npm install
    echo Done.
)

echo.
echo ==============================
echo   Setup complete!
echo   Now double-click start.bat
echo ==============================
pause
