@echo off
title One-Day Energy Detective Server
cd /d "%~dp0"

echo ==================================================
echo   Starting One-Day Energy Detective Server...
echo ==================================================

set "PYTHON_EXE=C:\Users\DELL\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe"
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" run_server.py
) else (
    python run_server.py
)

pause
