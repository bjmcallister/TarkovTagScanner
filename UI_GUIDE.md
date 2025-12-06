# Tarkov Price Checker - UI Version Guide

## 🎮 What's New

The UI version adds:
- **Graphical interface** with dark theme
- **Global hotkey** (Ctrl+Shift+P) to capture and search
- **Real-time status updates**
- **Color-coded price information**
- **Manual search option**

## 🚀 Quick Start

1. Run the program:
   ```
   python tarkov_price_checker_ui.py
   ```

2. Click **"Start Hotkey"** to enable the global hotkey listener

3. In Escape from Tarkov:
   - Hover over an item
   - Press **Ctrl+Shift+P**
   - Enter the item name when prompted
   - View the price instantly!

## 🎯 Features

### Hotkey Mode
- Press **Ctrl+Shift+P** anywhere (even when Tarkov is focused)
- Takes a screenshot automatically
- Prompts you to enter the item name
- Displays full price information

### Manual Search Mode
- Type any item name in the search box
- Press Enter or click "Search"
- Get instant price information

### Screenshot Only
- Click "Take Screenshot Now" to just capture your screen
- Useful for documenting item stats or locations

## 📊 Price Information Displayed

- **Current Price** - Latest flea market price
- **24h Change** - Price trend over 24 hours (green = up, red = down)
- **7d Change** - Price trend over 7 days
- **Trader Price** - Best vendor sell price
- **Average Prices** - 24h and 7d averages

## 💡 Tips

1. **Item Names**: Use full item names for best results
   - ✅ "Physical bitcoin" 
   - ✅ "LEDX Skin Transilluminator"
   - ✅ "Graphics card"
   - ❌ "btc" (might not work)

2. **Hotkey**: The Ctrl+Shift+P hotkey works globally
   - Make sure the UI window stays open
   - Click "Stop Hotkey" to disable it

3. **Screenshots**: All screenshots are saved to the `screenshots/` folder

## 🎨 Color Guide

- **Green** - Success, positive changes
- **Red** - Errors, negative changes
- **Yellow** - Warnings, processing
- **Cyan** - Item information headers
- **Blue** - Manual actions

## ⚠️ Troubleshooting

**Hotkey not working?**
- Make sure you clicked "Start Hotkey"
- Check if another program is using the same hotkey
- Run as administrator if needed

**API connection failed?**
- Check your internet connection
- Verify firewall isn't blocking Python
- Wait a few minutes and try again

**Item not found?**
- Try the exact name from the Tarkov Market website
- Check spelling and capitalization
- Some items have special characters

## 🔧 Customization

To change the hotkey, edit `tarkov_price_checker_ui.py`:
- Find the `on_press` function
- Modify the key combination checking logic
- Current: Ctrl+Shift+P

## 📝 Common Item Names

See `common_items.txt` for a list of frequently searched items with correct names.
