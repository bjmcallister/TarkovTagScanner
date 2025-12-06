"""
Build script for Wabbajack Tarkov Price Checker
Creates a standalone executable using PyInstaller
"""

import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("Building Wabbajack Tarkov Price Checker executable...")
print("This may take several minutes...")

# PyInstaller configuration
PyInstaller.__main__.run([
    'tarkov_price_checker_ui.py',
    '--name=WabbajackTarkovPriceChecker',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=screenshots;screenshots',
    '--hidden-import=easyocr',
    '--hidden-import=cv2',
    '--hidden-import=PIL',
    '--hidden-import=numpy',
    '--hidden-import=pynput',
    '--hidden-import=keyboard',
    '--collect-all=easyocr',
    '--clean',
])

print("\n" + "="*60)
print("Build complete!")
print("="*60)
print(f"Executable location: {os.path.abspath('dist/WabbajackTarkovPriceChecker.exe')}")
print("\nNote: First run will download OCR models (~100MB)")
print("="*60)
