@echo off
echo Building Windows Health Check Tool...
echo.

:: Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

:: Verify required packages are installed in the same Python used for packaging
python -c "import customtkinter, psutil, PIL, PyInstaller, win32api" >nul 2>&1
if errorlevel 1 (
    echo Missing Python build dependency.
    echo Run: python -m pip install -r requirements.txt
    echo Then run build.bat again.
    echo.
    pause
    exit /b 1
)

:: Build the executable
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --collect-all customtkinter ^
    --name "Windows Health Check Tool" ^
    --distpath "dist" ^
    main.py

echo.
if exist "dist\Windows Health Check Tool.exe" (
    echo Build successful!
    echo Executable created: dist\Windows Health Check Tool.exe
) else (
    echo Build failed!
)

echo.
pause
