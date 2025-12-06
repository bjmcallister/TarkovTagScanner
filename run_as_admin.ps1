# Tarkov Price Checker - Run as Administrator
# This script ensures proper permissions for global hotkey detection

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tarkov Price Checker with OCR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting with administrator privileges..." -ForegroundColor Yellow
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Not running as Administrator!" -ForegroundColor Red
    Write-Host "Restarting with Administrator privileges..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-File", "$PSCommandPath"
    exit
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""
Write-Host "Launching Tarkov Price Checker..." -ForegroundColor Cyan
Write-Host ""

# Navigate to script directory
Set-Location $PSScriptRoot

# Run the Python script
python tarkov_price_checker_ui.py

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
