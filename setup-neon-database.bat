@echo off
echo ========================================
echo 🚀 CuraGenie Neon PostgreSQL Setup
echo ========================================
echo.

echo This script will help you set up your Neon PostgreSQL database.
echo.

echo Please enter your Neon PostgreSQL URL:
echo (Format: postgresql://username:password@host:port/database)
echo.
set /p DATABASE_URL="Enter DATABASE_URL: "

if "%DATABASE_URL%"=="" (
    echo ❌ No DATABASE_URL provided. Exiting.
    pause
    exit /b 1
)

echo.
echo Setting DATABASE_URL environment variable...
setx DATABASE_URL "%DATABASE_URL%"

echo.
echo ✅ DATABASE_URL environment variable set successfully!
echo.
echo Note: You may need to restart your terminal/command prompt
echo for the environment variable to take effect.
echo.

echo Testing database connection...
cd backend
python test_database_connection.py

echo.
echo ========================================
echo 🎯 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your terminal/command prompt
echo 2. Start the backend: python main.py
echo 3. Check the logs for database connection status
echo.
pause
