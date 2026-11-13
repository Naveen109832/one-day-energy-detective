# One-Day Energy Detective - PowerShell Launcher
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pythonExe = "C:\Users\DELL\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting One-Day Energy Detective Server..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

if (Test-Path $pythonExe) {
    & $pythonExe run_server.py
} else {
    python run_server.py
}
