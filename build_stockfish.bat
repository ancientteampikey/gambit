@echo off
setlocal
cd /d "%~dp0stockfish\Stockfish-master\src"

where nmake >nul 2>nul
if errorlevel 1 (
  echo Microsoft C++ Build Tools were not found in this command prompt.
  echo Install "Build Tools for Visual Studio 2022" with the "Desktop development with C++" workload.
  echo Then run this file from an "x64 Native Tools Command Prompt for VS 2022".
  pause
  exit /b 1
)

echo Building Stockfish for modern 64-bit Windows CPUs...
nmake -f Makefile build ARCH=x86-64-avx2 COMP=msvc
if errorlevel 1 (
  echo Build failed. Try ARCH=x86-64-sse41-popcnt for older CPUs.
  pause
  exit /b 1
)

if exist stockfish.exe (
  copy /y stockfish.exe "%~dp0stockfish\stockfish.exe" >nul
  echo Success: %~dp0stockfish\stockfish.exe
) else (
  echo Build completed but stockfish.exe was not found.
)
pause
