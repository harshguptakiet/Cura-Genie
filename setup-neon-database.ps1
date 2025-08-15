# CuraGenie Neon PostgreSQL Setup Script
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 CuraGenie Neon PostgreSQL Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will help you set up your Neon PostgreSQL database." -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  Warning: This script is not running as Administrator." -ForegroundColor Yellow
    Write-Host "   Environment variables may not be set system-wide." -ForegroundColor Yellow
    Write-Host ""
}

# Get DATABASE_URL from user
Write-Host "Please enter your Neon PostgreSQL URL:" -ForegroundColor White
Write-Host "(Format: postgresql://username:password@host:port/database)" -ForegroundColor Gray
Write-Host ""
$databaseUrl = Read-Host "Enter DATABASE_URL"

if ([string]::IsNullOrEmpty($databaseUrl)) {
    Write-Host "❌ No DATABASE_URL provided. Exiting." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Validate URL format
if (-not $databaseUrl.StartsWith("postgresql://")) {
    Write-Host "⚠️  Warning: DATABASE_URL should start with 'postgresql://'" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "Setting DATABASE_URL environment variable..." -ForegroundColor Green

try {
    # Set environment variable for current session
    $env:DATABASE_URL = $databaseUrl
    
    # Set environment variable system-wide (requires admin)
    if ($isAdmin) {
        [Environment]::SetEnvironmentVariable("DATABASE_URL", $databaseUrl, "Machine")
        Write-Host "✅ DATABASE_URL set system-wide (Machine)" -ForegroundColor Green
    } else {
        [Environment]::SetEnvironmentVariable("DATABASE_URL", $databaseUrl, "User")
        Write-Host "✅ DATABASE_URL set for current user" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "✅ DATABASE_URL environment variable set successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error setting environment variable: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Setting for current session only..." -ForegroundColor Yellow
    $env:DATABASE_URL = $databaseUrl
}

Write-Host ""
Write-Host "Note: You may need to restart your terminal/PowerShell" -ForegroundColor Yellow
Write-Host "for the environment variable to take effect system-wide." -ForegroundColor Yellow
Write-Host ""

# Test database connection
Write-Host "Testing database connection..." -ForegroundColor Green
Write-Host ""

try {
    Set-Location "backend"
    
    if (Test-Path "test_database_connection.py") {
        python test_database_connection.py
    } else {
        Write-Host "⚠️  Database test script not found." -ForegroundColor Yellow
        Write-Host "   Make sure you're running this from the project root directory." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error running database test: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Restart your terminal/PowerShell" -ForegroundColor Yellow
Write-Host "2. Start the backend: python main.py" -ForegroundColor Yellow
Write-Host "3. Check the logs for database connection status" -ForegroundColor Yellow
Write-Host ""

# Return to original directory
Set-Location ".."

Read-Host "Press Enter to continue"
