# GitHub Upload Instructions

## Step 1: Wait for Build to Complete

The executable is currently being built. Wait for the message:
```
Build complete!
Executable location: dist/WabbajackTarkovPriceChecker.exe
```

This may take 5-10 minutes depending on your system.

## Step 2: Test the Executable

After build completes:
1. Navigate to `dist/` folder
2. Run `WabbajackTarkovPriceChecker.exe`
3. Test all features:
   - Shift+K to activate
   - Press 8 key to capture (if admin)
   - Mouse side button to capture
   - Manual search

## Step 3: Initialize Git Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial release: Wabbajack Tarkov Price Checker v1.0"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Wabbajack-Tarkov-Price-Checker`
3. Description: "Real-time Tarkov item price checker with OCR detection"
4. Choose Public or Private
5. Do NOT initialize with README (we have one)
6. Click "Create repository"

## Step 5: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Wabbajack-Tarkov-Price-Checker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 6: Create a Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0`
4. Release title: `Wabbajack Tarkov Price Checker v1.0`
5. Description:
```markdown
# ⚡ Wabbajack Tarkov Price Checker v1.0

Real-time price checking for Escape from Tarkov items with OCR detection.

## Features
- 🎯 OCR Item Detection
- ⚡ Instant Price Lookup  
- 🖱️ Multiple Trigger Options
- 📊 Price Per Slot Calculation
- 🎨 Matrix-Themed UI

## Download
Download `WabbajackTarkovPriceChecker.exe` below and run it!

**Note:** First run downloads OCR models (~100MB)

## Hotkeys
- **Shift+K**: Activate/Deactivate
- **8**: Capture item at cursor
- **Mouse Side Button**: Instant capture

See README for full documentation.
```
6. Upload the executable: Click "Attach binaries" and upload `dist/WabbajackTarkovPriceChecker.exe`
7. Click "Publish release"

## Step 7: Update README

After creating the repository, update the README.md file:
- Replace `YOUR_USERNAME` with your actual GitHub username in the clone URL
- Update the releases link

## Troubleshooting

### Build Failed
If the build fails:
```bash
# Try building with fewer optimizations
pyinstaller --onefile --windowed --name=WabbajackTarkovPriceChecker tarkov_price_checker_ui.py
```

### Exe Too Large
The exe will be large (200-300MB) due to:
- EasyOCR libraries
- OpenCV
- NumPy
This is normal for OCR applications.

### Git Push Issues
If push is rejected:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Optional: Add GitHub Actions

Create `.github/workflows/build.yml` for automatic builds on new releases.

## Optional: Add Screenshots

1. Take screenshots of the application
2. Create `screenshots/` folder in repository
3. Add to README.md for better presentation

## Done!

Your Wabbajack Tarkov Price Checker is now on GitHub and available for download!
