@echo off
echo Building Windows Health Check Tool...
echo.

:: Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

:: Build the executable
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
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
