@echo off
echo ========================================================
echo   NeuroReport AI - Environment Reset Script
echo ========================================================
echo.

echo 1. Removing old broken virtual environment...
if exist venv (
    rmdir /s /q venv
)
echo Done.

echo.
echo 2. Creating a fresh, clean virtual environment with Python 3.10...
py -3.10 -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create venv. Make sure Python 3.10 is installed.
    echo Try running: py -3.10 --version
    pause
    exit /b 1
)
echo Done.

echo.
echo 3. Activating and installing perfectly locked dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   SUCCESS! The clean environment is ready.
echo   You can now use run_backend.bat and run_frontend.bat!
echo ========================================================
pause
