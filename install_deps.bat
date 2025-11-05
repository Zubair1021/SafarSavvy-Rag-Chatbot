@echo off
REM SafarSavvy RAG - Dependency Installation Script for Windows
echo ========================================
echo SafarSavvy RAG - Installing Dependencies
echo ========================================
echo.

REM Check if virtual environment exists, if not create it
if not exist "venv\Scripts\activate.bat" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [4/5] Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt

echo.
echo [5/5] Verifying critical packages...
python -c "import sqlalchemy; print('✓ SQLAlchemy:', sqlalchemy.__version__)" 2>nul || echo ✗ SQLAlchemy not found
python -c "import fastapi; print('✓ FastAPI:', fastapi.__version__)" 2>nul || echo ✗ FastAPI not found
python -c "import uvicorn; print('✓ Uvicorn:', uvicorn.__version__)" 2>nul || echo ✗ Uvicorn not found
python -c "import chromadb; print('✓ ChromaDB installed')" 2>nul || echo ✗ ChromaDB not found

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file: copy env_template.txt .env
echo 2. Edit .env and add your DEEPSEEK_API_KEY
echo 3. Run the application:
echo    - EASY WAY: .\START.bat
echo    - OR activate venv first: venv\Scripts\Activate.ps1
echo      Then run: python start.py
echo.
echo IMPORTANT: Always activate venv before running python start.py!
echo.
pause

