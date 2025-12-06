# TARKOV TAG SCANNER

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-00ff41?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-00ff41?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-00ff41?style=for-the-badge)

**Real-time price tag scanning for Escape from Tarkov items with OCR detection**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Hotkeys](#hotkeys) • [FAQ](#faq)

<a href="https://www.buymeacoffee.com/allisteras" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 45px !important;width: 162px !important;" ></a>

</div>

---

## Features

- **OCR Item Detection** - Automatically detects item names from your screen
- **Instant Price Lookup** - Real-time prices from tarkov.dev API
- **PVP/PVE Mode Toggle** - Switch between regular and PVE economy data
- **Custom Hotkeys** - Configure your own hotkey preferences
- **Price Per Slot** - Calculate loot efficiency for inventory management
- **Matrix-Themed UI** - Sleek dark green/black interface
- **No Admin Required** - Works without administrator privileges
- **No API Key** - Uses free tarkov.dev GraphQL API
- **Loading Screen** - Shows progress during first-time OCR setup

---

## Quick Start

### Download Release Build

1. Download `TarkovTagScanner.exe` from [Releases](../../releases)
2. Run the executable
3. Click **[ACTIVATE]** or configure your hotkey
4. Hover over items in Tarkov and trigger your hotkey

**Note:** Releases are automatically built via GitHub Actions. No need to build locally!

---

## Usage

### Initial Setup

1. **Launch the application**
   - Double-click `TarkovTagScanner.exe`

2. **First Run**
   - Loading screen appears while OCR models download (~100MB)
   - This only happens once and takes up to 60 seconds

3. **Select Game Mode**
   - Choose **PVP** for regular Tarkov or **PVE** for PVE mode economy
   - Mode affects price data from API

4. **Configure Hotkey (Optional)**
   - Click **[CONFIGURE HOTKEY]** to set your preferred hotkey
   - Default: Shift+K to activate, 8 to capture

5. **Activate System**
   - Click **[ACTIVATE]** button or press your toggle hotkey
   - Status will change to ">>> SYSTEM ACTIVE"

### Scanning Items

1. **In Tarkov**, hover your mouse cursor over any item
2. Press your configured capture hotkey (default: **8**)
3. A green overlay will appear with:
   - Item name
   - **Flea market price** (most prominent)
   - **Price per slot** (most prominent)
   - 48-hour price change
   - Best trader sell price

### Manual Search

You can also search items manually:
1. Type item name in the search box
2. Click **[QUERY]** or press **Enter**
3. Results appear in the output window

---

## Hotkeys

**Default Hotkeys:**

| Hotkey | Function |
|--------|----------|
| `Shift+K` | Activate/Deactivate system |
| `8` | Capture item at cursor (requires system active) |
| `Mouse Side Button` | Capture item at cursor (requires system active) |

**Custom Hotkeys:**
- Click **[CONFIGURE HOTKEY]** in the application to set your own preferences
- Supports most keyboard keys and combinations
- Mouse buttons also supported

---

## Configuration

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

## FAQ

### Is this detectable by BattleEye?

**No.** This tool:
- Does not read game memory
- Does not inject into the game process
- Only takes screenshots (like pressing Print Screen)
- Runs completely external to Tarkov

It's as safe as using a second monitor with a price website.

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

## Dependencies

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

## Troubleshooting

### Application won't start
- Make sure you downloaded from official releases
- Check that OCR models have space to download (~200MB)
- Try running the exe again - first run takes longer

### OCR not working
- First run shows loading screen while models download
- Ensure internet connection during first run
- Check `screenshots/` folder in temp directory for captured images
- Ensure enough disk space (~200MB)

### Prices not loading
- Check internet connection
- Verify Tarkov Market API is online: https://tarkov-market.com
- Try manual search to test API connection

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool is for educational and personal use only. 

- Not affiliated with Battlestate Games, Tarkov.dev, or The Hideout
- Use at your own risk
- Game content and materials are trademarks and copyrights of Battlestate Games

---

## Support the Project

If you find this tool useful, consider buying me a coffee!

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-green.png)](https://www.buymeacoffee.com/allisteras)

Your support helps keep the project maintained and updated!

---

## Credits

- **Tarkov.dev API** - Free GraphQL API by The Hideout: https://tarkov.dev
- **The Hideout** - Community API: https://github.com/the-hideout/tarkov-api
- **EasyOCR** - Text recognition: https://github.com/JaidedAI/EasyOCR
- Built by the Tarkov community

---

<div align="center">

**TARKOV TAG SCANNER - Instant Price Checking**

[Report Bug](../../issues) • [Request Feature](../../issues) • [Buy Me a Coffee](https://www.buymeacoffee.com/allisteras)

</div>
