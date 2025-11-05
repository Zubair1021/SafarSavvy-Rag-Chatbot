@echo off
REM SafarSavvy RAG - Start Application Script
echo ========================================
echo SafarSavvy RAG - Starting Application
echo ========================================
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: .\install_deps.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting SafarSavvy AI...
echo.
python start.py

pause

