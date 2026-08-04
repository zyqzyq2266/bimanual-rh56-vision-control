@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found: .venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist "config.left.yaml" (
    echo Missing config.left.yaml. Copy config.left.example.yaml first.
    pause
    exit /b 1
)

if not exist "config.right.yaml" (
    echo Missing config.right.yaml. Copy config.right.example.yaml first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml
echo.
echo The dual-hand tracking program has stopped.
pause
