@echo off
echo ================================================================
echo Starting BrandSentinel AI Enterprise Platform
echo ================================================================

cd /d "%~dp0"

echo [1/2] Checking Python and packages...
cd backend
python -c "import fastapi, uvicorn, fitz, docx, cv2, PIL; print('All backend libraries loaded.')"
if %errorlevel% neq 0 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)

echo [2/2] Launching BrandSentinel AI full-stack server on port 8000...
echo Open your browser to: http://localhost:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause

