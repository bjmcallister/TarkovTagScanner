@echo off
echo ========================================
echo Tarkov Price Checker with OCR
echo ========================================
echo.
echo Starting with administrator privileges...
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [ OK ] Running as Administrator
    echo.
    echo Launching Tarkov Price Checker...
    echo.
    python tarkov_price_checker_ui.py
) else (
    echo [WARN] Not running as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
)
