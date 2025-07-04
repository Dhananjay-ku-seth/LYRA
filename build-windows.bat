@echo off
echo ========================================
echo LYRA 3.0 Windows Build Script
echo ========================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and add it to PATH
    pause
    exit /b 1
)

echo ✓ Python and Node.js found

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    echo Trying with --no-deps flag...
    pip install --no-deps -r requirements.txt
)

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)

REM Test Python backend
echo Testing Python backend...
python -c "import flask, flask_socketio; print('✓ Flask modules OK')"
python -c "import psutil; print('✓ System monitoring OK')"
python -c "import pyttsx3; print('✓ Text-to-speech OK')" 2>nul || echo "⚠ TTS may need manual installation"
python -c "import speech_recognition; print('✓ Speech recognition OK')" 2>nul || echo "⚠ Speech recognition may need manual installation"

REM Create application bundle
echo Creating application bundle...
mkdir dist 2>nul
mkdir dist\LYRA-3.0-Windows 2>nul

REM Copy main application files
echo Copying application files...
xcopy /E /I /H /Y gui dist\LYRA-3.0-Windows\gui
xcopy /E /I /H /Y core dist\LYRA-3.0-Windows\core
xcopy /E /I /H /Y data dist\LYRA-3.0-Windows\data
xcopy /E /I /H /Y config dist\LYRA-3.0-Windows\config 2>nul
xcopy /E /I /H /Y logs dist\LYRA-3.0-Windows\logs 2>nul
xcopy /E /I /H /Y resources dist\LYRA-3.0-Windows\resources

copy main.py dist\LYRA-3.0-Windows\
copy launcher.py dist\LYRA-3.0-Windows\
copy start_lyra.py dist\LYRA-3.0-Windows\
copy electron-main.js dist\LYRA-3.0-Windows\
copy package.json dist\LYRA-3.0-Windows\
copy requirements.txt dist\LYRA-3.0-Windows\
copy README.md dist\LYRA-3.0-Windows\

REM Copy virtual environment (portable Python)
echo Creating portable Python environment...
xcopy /E /I /H /Y venv dist\LYRA-3.0-Windows\venv

REM Create startup scripts
echo Creating startup scripts...

REM Create Python startup script
echo @echo off > dist\LYRA-3.0-Windows\start-backend.bat
echo cd /d "%%~dp0" >> dist\LYRA-3.0-Windows\start-backend.bat
echo call venv\Scripts\activate.bat >> dist\LYRA-3.0-Windows\start-backend.bat
echo python start_lyra.py >> dist\LYRA-3.0-Windows\start-backend.bat
echo pause >> dist\LYRA-3.0-Windows\start-backend.bat

REM Create Electron startup script
echo @echo off > dist\LYRA-3.0-Windows\start-gui.bat
echo cd /d "%%~dp0" >> dist\LYRA-3.0-Windows\start-gui.bat
echo npm start >> dist\LYRA-3.0-Windows\start-gui.bat

REM Create main launcher
echo @echo off > dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo title LYRA 3.0 - AI Assistant >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo cd /d "%%~dp0" >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo echo ======================================== >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo echo LYRA 3.0 - AI Assistant System >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo echo ======================================== >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo start "LYRA Backend" start-backend.bat >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo timeout /t 5 /nobreak >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo start "LYRA GUI" start-gui.bat >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo echo LYRA 3.0 is starting... >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo echo Backend: http://localhost:5000 >> dist\LYRA-3.0-Windows\LYRA-3.0.bat
echo pause >> dist\LYRA-3.0-Windows\LYRA-3.0.bat

REM Create installation instructions
echo Creating installation instructions...
echo LYRA 3.0 - Windows Installation > dist\LYRA-3.0-Windows\INSTALL.txt
echo ======================================= >> dist\LYRA-3.0-Windows\INSTALL.txt
echo. >> dist\LYRA-3.0-Windows\INSTALL.txt
echo 1. Extract this folder to your desired location >> dist\LYRA-3.0-Windows\INSTALL.txt
echo 2. Double-click LYRA-3.0.bat to start the application >> dist\LYRA-3.0-Windows\INSTALL.txt
echo 3. Wait for the backend to start, then the GUI will open >> dist\LYRA-3.0-Windows\INSTALL.txt
echo 4. Access the web interface at http://localhost:5000 >> dist\LYRA-3.0-Windows\INSTALL.txt
echo. >> dist\LYRA-3.0-Windows\INSTALL.txt
echo Requirements: >> dist\LYRA-3.0-Windows\INSTALL.txt
echo - Windows 10/11 >> dist\LYRA-3.0-Windows\INSTALL.txt
echo - No additional software needed (all included) >> dist\LYRA-3.0-Windows\INSTALL.txt
echo. >> dist\LYRA-3.0-Windows\INSTALL.txt
echo Troubleshooting: >> dist\LYRA-3.0-Windows\INSTALL.txt
echo - If TTS doesn't work, check Windows audio settings >> dist\LYRA-3.0-Windows\INSTALL.txt
echo - If voice recognition fails, check microphone permissions >> dist\LYRA-3.0-Windows\INSTALL.txt
echo - For support, check the README.md file >> dist\LYRA-3.0-Windows\INSTALL.txt

REM Create ZIP package
echo Creating ZIP package...
powershell -command "Compress-Archive -Path 'dist\LYRA-3.0-Windows' -DestinationPath 'dist\LYRA-3.0-Windows-Portable.zip' -Force"

echo ========================================
echo Windows Build Complete!
echo ========================================
echo.
echo Portable package: dist\LYRA-3.0-Windows-Portable.zip
echo Portable folder: dist\LYRA-3.0-Windows\
echo.
echo To test the build:
echo 1. Go to dist\LYRA-3.0-Windows\
echo 2. Run LYRA-3.0.bat
echo.
pause
