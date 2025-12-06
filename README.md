# ⚡ WABBAJACK TARKOV PRICE CHECKER ⚡

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-00ff41?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-00ff41?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-00ff41?style=for-the-badge)

**Real-time price checking for Escape from Tarkov items with OCR detection**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Hotkeys](#hotkeys) • [FAQ](#faq)

</div>

---

## 📋 Features

- 🎯 **OCR Item Detection** - Automatically detects item names from your screen
- ⚡ **Instant Price Lookup** - Real-time prices from Tarkov Market API
- 🖱️ **Multiple Trigger Options** - Keyboard hotkey (8) or mouse side button
- 📊 **Price Per Slot** - Calculate efficiency for inventory management
- 🎨 **Matrix-Themed UI** - Sleek dark green/black interface
- 🔒 **No Admin Required** - Works without administrator privileges
- 💾 **Lightweight** - Minimal resource usage
- 🆓 **No API Key** - Uses free tarkov.dev GraphQL API
- 🌐 **Real-time Data** - Community-driven, constantly updated

---

## 🚀 Quick Start

### Option 1: Download Executable (Recommended)

1. Download `WabbajackTarkovPriceChecker.exe` from [Releases](../../releases)
2. Run the executable
3. Click **[ACTIVATE]** or press **Shift+K**
4. Hover over items in Tarkov and press **8** or your mouse side button

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- Windows OS

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/Tarkov_project.git
cd Tarkov_project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python tarkov_price_checker_ui.py
```

---

## 🎮 Usage

### Initial Setup

1. **Launch the application**
   - Double-click `WabbajackTarkovPriceChecker.exe` or run `python tarkov_price_checker_ui.py`

2. **First Run**
   - OCR models will download automatically (~100MB)
   - This only happens once

3. **Activate System**
   - Click **[ACTIVATE]** button or press **Shift+K**
   - Status will change to ">>> SYSTEM ACTIVE"

### Scanning Items

1. **In Tarkov**, hover your mouse cursor over any item
2. Press **8** key or your **mouse side button**
3. A green overlay will appear with:
   - Item name
   - Current flea market price
   - 24-hour price change
   - Price per inventory slot
   - Trader sell price

### Manual Search

You can also search items manually:
1. Type item name in the search box
2. Click **[QUERY]** or press **Enter**
3. Results appear in the output window

---

## ⌨️ Hotkeys

| Hotkey | Function |
|--------|----------|
| `Shift+K` | Activate/Deactivate system |
| `8` | Capture item at cursor (requires system active) |
| `Mouse Side Button` | Capture item at cursor (requires system active) |

---

## 🔧 Configuration

### API Source

This application uses the **free tarkov.dev GraphQL API** - no API key required!

- API Endpoint: `https://api.tarkov.dev/graphql`
- Data Source: Community-driven, open source
- Rate Limits: Generous, suitable for personal use
- More Info: [github.com/the-hideout/tarkov-api](https://github.com/the-hideout/tarkov-api)

### OCR Region

The OCR capture region is optimized for Tarkov's default UI. If items aren't detected:

1. Take a screenshot when hovering over an item (saved to `screenshots/` folder)
2. Adjust the `roi_x`, `roi_y`, `roi_width`, `roi_height` values in `extract_item_name_from_image()` method

---

## ❓ FAQ

### Is this detectable by BattleEye?

**No.** This tool:
- Does not read game memory
- Does not inject into the game process
- Only takes screenshots (like pressing Print Screen)
- Runs completely external to Tarkov

It's as safe as using a second monitor with a price website.

### Why do I need admin privileges for keyboard hotkeys?

Windows requires admin rights for global keyboard hooks. However:
- The mouse side button works **without admin**
- You can run as admin to enable keyboard hotkeys
- Or just use the mouse side button

### The OCR isn't detecting items correctly

Common fixes:
- Make sure you hover directly over the item
- Ensure the item name is fully visible
- Try adjusting your in-game UI scale
- Check that OCR models downloaded completely (first run)

### Can I use this during raids?

Yes! The overlay appears quickly and disappears automatically. However:
- Use at your own risk
- Consider using it pre-raid for planning
- Don't let it distract you during combat

### What API does this use?

This uses the free **tarkov.dev GraphQL API** maintained by The Hideout community. No API key needed, real-time data, and open source!

---

## 🛠️ Building from Source

To create your own executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_exe.py
```

The executable will be in the `dist/` folder.

---

## 📦 Dependencies

- `tkinter` - GUI framework
- `pyautogui` - Screenshot capture
- `requests` - API calls
- `Pillow` - Image processing
- `easyocr` - Optical character recognition
- `opencv-python` - Image manipulation
- `numpy` - Array operations
- `pynput` - Mouse event detection
- `keyboard` - Keyboard hotkey support

---

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Try running as administrator

### OCR not working
- First run requires internet to download models
- Check `screenshots/` folder for captured images
- Ensure enough disk space (~200MB)

### Prices not loading
- Check internet connection
- Verify Tarkov Market API is online: https://tarkov-market.com
- Try manual search to test API connection

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational and personal use only. 

- Not affiliated with Battlestate Games, Tarkov.dev, or The Hideout
- Use at your own risk
- Game content and materials are trademarks and copyrights of Battlestate Games

---

## 🙏 Credits

- **Tarkov.dev API** - Free GraphQL API by The Hideout: https://tarkov.dev
- **The Hideout** - Community API: https://github.com/the-hideout/tarkov-api
- **EasyOCR** - Text recognition: https://github.com/JaidedAI/EasyOCR
- Built with ❤️ by the Tarkov community

---

<div align="center">

**⚡ WABBAJACK - Making Tarkov Trading Easier ⚡**

[Report Bug](../../issues) • [Request Feature](../../issues)

</div>
