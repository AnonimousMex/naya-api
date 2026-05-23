#!/bin/bash

# Nayá API E2E Tests - Quick Start Script

echo "=========================================="
echo "Nayá API E2E Test Suite - Initialization"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm version: $(npm -v)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Install browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install browsers"
    exit 1
fi

echo "✅ Browsers installed successfully"
echo ""

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Configure test data in test-data.json"
echo "2. Start your Nayá API server:"
echo "   - Ensure it's running on http://localhost:8000"
echo "3. Run tests:"
echo "   npm test              # Run all tests"
echo "   npm run test:report   # View HTML report"
echo "   npm run test:debug    # Debug mode"
echo "   npm run test:headed   # See tests running"
echo "   npm run test:ui       # Interactive UI mode"
echo ""
