@echo off
echo ========================================
echo CuraGenie Simple Enhanced Backend
echo ========================================
echo.
echo Starting simplified backend with minimal dependencies...
echo.

cd backend

echo Checking Python environment...
python --version

echo.
echo Starting simplified enhanced genomic analysis backend...
echo.
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main_simple.py

pause
