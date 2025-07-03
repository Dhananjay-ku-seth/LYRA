@echo off
echo ============================================================
echo 🚀 LYRA 3.0 Production Build Script
echo ============================================================

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 📦 Installing Node.js dependencies...
npm install

echo.
echo 🔧 Creating directories...
if not exist "config" mkdir config
if not exist "logs" mkdir logs
if not exist "resources" mkdir resources

echo.
echo 🏗️ Building Electron application...
npm run build

echo.
echo ✅ Build complete! 
echo 📁 Check the 'dist' folder for installation files:
echo    - LYRA-3.0-Setup-3.0.0.exe (Installer)
echo    - LYRA-3.0-Portable-3.0.0.exe (Portable)

echo.
echo 🎯 To run LYRA 3.0 in development mode:
echo    npm start

echo.
pause
