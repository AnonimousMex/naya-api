@echo off
REM Nayá API E2E Tests - Quick Start Script for Windows

echo ==========================================
echo Nayá API E2E Test Suite - Initialization
echo ==========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Node.js is not installed. Please install it from https://nodejs.org/
    pause
    exit /b 1
)

echo + Node.js version:
node -v

echo.
echo + npm version:
npm -v
echo.

echo Installing dependencies...
npm install

if %ERRORLEVEL% NEQ 0 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo + Dependencies installed successfully
echo.

echo Installing Playwright browsers...
call npx playwright install

if %ERRORLEVEL% NEQ 0 (
    echo X Failed to install browsers
    pause
    exit /b 1
)

echo + Browsers installed successfully
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Configure test data in test-data.json
echo 2. Start your Nayá API server (http://localhost:8000)
echo 3. Run tests:
echo    npm test              - Run all tests
echo    npm run test:report   - View HTML report
echo    npm run test:debug    - Debug mode
echo    npm run test:headed   - See tests running
echo    npm run test:ui       - Interactive UI mode
echo.
pause