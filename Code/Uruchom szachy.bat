@echo off
cd /d "%~dp0"

if not exist "%~dp0models\best.pt" (
    echo Model not found: "%~dp0models\best.pt"
    echo Copy your trained chess model to Code\models\best.pt first.
    pause
    exit /b 1
)

python "%~dp0wykrywaj_ruchy.py" --orientation black --model "%~dp0models\best.pt" --engine-time 1.0
if errorlevel 1 (
    echo.
    echo The chess program stopped with an error.
)
pause
