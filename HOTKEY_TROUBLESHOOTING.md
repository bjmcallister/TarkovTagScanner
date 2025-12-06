# Hotkey Troubleshooting Guide

## 🔧 If the hotkey (Ctrl+Shift+P) isn't working:

### Method 1: Test the Hotkey Detection
1. Click **"Start Hotkey"** button
2. Press Ctrl+Shift+P 
3. Check the log window for any messages
4. Click the **"Test Hotkey"** button to see currently pressed keys

### Method 2: Try Running as Administrator
1. Close the program
2. Right-click on PowerShell or Command Prompt
3. Select "Run as Administrator"
4. Navigate to project folder: `cd "C:\Users\bjmca\OneDrive\Desktop\Tarkov_project"`
5. Run: `python tarkov_price_checker_ui.py`

### Method 3: Check for Conflicting Programs
- Make sure no other program is using Ctrl+Shift+P
- Check Discord, OBS, game overlays, etc.
- Temporarily disable them and try again

### Method 4: Alternative - Use the Manual Button
If hotkey still doesn't work:
1. Click **"Take Screenshot + OCR"** button instead
2. This will capture your screen immediately
3. The OCR will read the item name automatically

### Method 5: Check Firewall/Antivirus
Some security software blocks global keyboard hooks:
1. Add Python to your firewall exceptions
2. Add the script folder to antivirus exceptions
3. Try temporarily disabling security software to test

### Method 6: Use a Different Hotkey
Edit line 264 in `tarkov_price_checker_ui.py`:
- Change `'p'` to another letter (like `'i'` for Ctrl+Shift+I)
- Or change the whole combination

## ✅ What Should Happen:

When hotkey works correctly:
1. You'll see "⚡ Hotkey triggered! Taking screenshot..." in the log
2. Screenshot is captured after 0.3 seconds
3. OCR reads the item name from the top of the screen
4. Price information appears automatically

## 🎯 Best Practice:

1. **Start Hotkey** before going into Tarkov
2. Keep the UI window open (can minimize)
3. In Tarkov, hover over item so name shows at top
4. Press Ctrl+Shift+P
5. Check the UI window for results

## 🐛 Debug Mode:

To see what keys are being detected, uncomment line 260 in the file:
```python
self.log(f"Keys pressed: {self.current_keys}", '#888888')
```

This will show every key press in the log window.
