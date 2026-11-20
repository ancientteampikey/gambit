@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo Python 3.11+ is required.& pause & exit /b 1)
where node >nul 2>nul || (echo Node.js 20+ is required.& pause & exit /b 1)

if not exist ".venv\Scripts\python.exe" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt

if not exist "frontend\node_modules" call npm.cmd --prefix frontend install

if exist "stockfish\stockfish.exe" set "GAMBIT_STOCKFISH_PATH=%CD%\stockfish\stockfish.exe"
if exist "stockfish\Stockfish-master\src\stockfish.exe" set "GAMBIT_STOCKFISH_PATH=%CD%\stockfish\Stockfish-master\src\stockfish.exe"

start "GAMBIT Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload"
start "GAMBIT Frontend" cmd /k "npm.cmd --prefix frontend run dev"
echo.
echo GAMBIT is starting at http://localhost:5173
echo Configure Stockfish from Settings after opening the app.
endlocal
