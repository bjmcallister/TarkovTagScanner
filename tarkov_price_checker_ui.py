"""
Tarkov Item Price Checker with UI, Hotkey, and OCR Support
Press Ctrl+Shift+P to capture screen and automatically detect item names
"""

import pyautogui
import requests
import json
from datetime import datetime
import os
from PIL import Image
import time
import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, scrolledtext, messagebox
import keyboard
import threading
import easyocr
import cv2
import numpy as np
from pynput import mouse


class TarkovPriceCheckerUI:
    """Tarkov Price Checker with GUI, Hotkey, and OCR Support"""
    
    def __init__(self, api_key=None):
        """Initialize the price checker with UI"""
        self.base_url = "https://api.tarkov.dev/graphql"
        self.api_key = api_key  # Not needed for tarkov.dev but kept for compatibility
        self.headers = {'Content-Type': 'application/json'}
        
        # Create screenshots directory in user's temp folder to avoid permission issues
        import tempfile
        user_temp = tempfile.gettempdir()
        self.screenshots_dir = os.path.join(user_temp, "WabbajackTarkov", "screenshots")
        try:
            if not os.path.exists(self.screenshots_dir):
                os.makedirs(self.screenshots_dir, exist_ok=True)
        except Exception as e:
            # Fallback to current directory if temp fails
            self.screenshots_dir = "screenshots"
            if not os.path.exists(self.screenshots_dir):
                try:
                    os.makedirs(self.screenshots_dir, exist_ok=True)
                except:
                    pass  # Continue without screenshots directory
        
        # Hotkey configuration
        self.hotkey_enabled = False
        self.hotkey_registered = False
        self.toggle_hotkey_registered = False
        self.mouse_listener = None
        self.mouse_controller = mouse.Controller()
        self.auto_capture_timer = None
        
        # OCR configuration
        self.ocr_reader = None
        self.ocr_enabled = True
        
        # Overlay window for price display
        self.overlay_window = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Wabbajack Tarkov Price Checker")
        self.root.geometry("900x800")
        self.root.configure(bg='#000000')
        
        self.create_ui()
        self.register_toggle_hotkey()
        
    def create_ui(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#000000')
        title_frame.pack(pady=15, padx=10, fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="⚡ WABBAJACK ⚡",
            font=("Courier New", 24, "bold"),
            bg='#000000',
            fg='#00ff41'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="TARKOV PRICE CHECKER",
            font=("Courier New", 14, "bold"),
            bg='#000000',
            fg='#00ff41'
        )
        subtitle_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#000000', bd=2, relief='solid')
        status_frame.pack(pady=10, padx=10, fill='x')
        
        self.status_label = tk.Label(
            status_frame,
            text=">>> SYSTEM READY",
            font=("Courier New", 11, "bold"),
            bg='#000000',
            fg='#00ff41',
            pady=8
        )
        self.status_label.pack()
        
        # Hotkey control frame
        hotkey_frame = tk.LabelFrame(
            self.root,
            text="< SYSTEM CONTROLS >",
            font=("Courier New", 12, "bold"),
            bg='#001100',
            fg='#00ff41',
            padx=15,
            pady=15,
            bd=2,
            relief='ridge'
        )
        hotkey_frame.pack(pady=10, padx=10, fill='x')
        
        # Hotkey buttons
        button_frame = tk.Frame(hotkey_frame, bg='#001100')
        button_frame.pack(fill='x')
        
        self.hotkey_button = tk.Button(
            button_frame,
            text="[ ACTIVATE ]",
            command=self.toggle_hotkey,
            font=("Courier New", 12, "bold"),
            bg='#003300',
            fg='#00ff41',
            activebackground='#00ff41',
            activeforeground='#000000',
            padx=25,
            pady=12,
            bd=3,
            relief='raised',
            cursor='hand2'
        )
        self.hotkey_button.pack(side='left', padx=5)
        
        # OCR toggle
        self.ocr_var = tk.BooleanVar(value=True)
        self.ocr_checkbox = tk.Checkbutton(
            button_frame,
            text="[X] OCR DETECTION",
            variable=self.ocr_var,
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41',
            selectcolor='#000000',
            activebackground='#001100',
            activeforeground='#00ff41'
        )
        self.ocr_checkbox.pack(side='left', padx=15)
        
        # Manual search frame
        search_frame = tk.LabelFrame(
            self.root,
            text="< MANUAL QUERY >",
            font=("Courier New", 12, "bold"),
            bg='#001100',
            fg='#00ff41',
            padx=15,
            pady=15,
            bd=2,
            relief='ridge'
        )
        search_frame.pack(pady=10, padx=10, fill='x')
        
        search_input_frame = tk.Frame(search_frame, bg='#001100')
        search_input_frame.pack(fill='x')
        
        tk.Label(
            search_input_frame,
            text=">> ITEM:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41'
        ).pack(side='left', padx=5)
        
        self.search_entry = tk.Entry(
            search_input_frame,
            font=("Courier New", 11),
            width=35,
            bg='#000000',
            fg='#00ff41',
            insertbackground='#00ff41',
            bd=2,
            relief='sunken'
        )
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.manual_search())
        
        self.search_button = tk.Button(
            search_input_frame,
            text="[ QUERY ]",
            command=self.manual_search,
            font=("Courier New", 10, "bold"),
            bg='#003300',
            fg='#00ff41',
            activebackground='#00ff41',
            activeforeground='#000000',
            padx=15,
            pady=5,
            bd=2,
            relief='raised',
            cursor='hand2'
        )
        self.search_button.pack(side='left', padx=5)
        
        # Results display
        results_frame = tk.LabelFrame(
            self.root,
            text="< SYSTEM OUTPUT >",
            font=("Courier New", 12, "bold"),
            bg='#001100',
            fg='#00ff41',
            padx=15,
            pady=15,
            bd=2,
            relief='ridge'
        )
        results_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=("Courier New", 10),
            bg='#000000',
            fg='#00ff41',
            wrap=tk.WORD,
            height=22,
            insertbackground='#00ff41',
            selectbackground='#003300',
            selectforeground='#00ff41'
        )
        self.results_text.pack(fill='both', expand=True)
        
        # Instructions
        instructions = """
╔════════════════════════════════════════════════════════════════╗
║              WABBAJACK TARKOV PRICE CHECKER v1.0              ║
╚════════════════════════════════════════════════════════════════╝

>>> INITIALIZATION PROTOCOL:
  [1] Click [ACTIVATE] or press Shift+K to enable system
  [2] In Tarkov, hover cursor over target item
  [3] Press '8' key or Mouse Side Button to scan
  [4] Price matrix overlay will appear near cursor
  [5] Or use manual query interface below

>>> CONTROL COMMANDS:
  ┌─ Shift+K ────────── Activate/Deactivate System
  ┌─ 8 ─────────────── Capture Item at Cursor
  └─ Mouse Side Btn ──── Instant Capture

>>> SYSTEM REQUIREMENTS:
  • First run downloads OCR models (~100MB)
  • No administrator privileges required
  • No API key required - Uses tarkov.dev free API

>>> STATUS: AWAITING INPUT...
        """
        self.results_text.insert('1.0', instructions)
        
    def log(self, message, color='#00ff00'):
        """Log a message to the results text area"""
        self.results_text.insert('end', f"\n{message}", ('msg',))
        self.results_text.tag_config('msg', foreground=color)
        self.results_text.see('end')
        self.root.update()
        
    def update_status(self, status, color='#00ff41'):
        """Update the status label"""
        self.status_label.config(text=f">>> {status.upper()}", fg=color)
        self.root.update()
        
    def toggle_hotkey(self):
        """Toggle the hotkey listener on/off"""
        if not self.hotkey_enabled:
            self.start_hotkey_listener()
        else:
            self.stop_hotkey_listener()
    
    def start_hotkey_listener(self):
        """Start auto-capture mode"""
        try:
            self.hotkey_enabled = True
            self.hotkey_button.config(
                text="[ DEACTIVATE ]",
                bg='#330000',
                fg='#ff0000'
            )
            self.update_status("System Active", '#00ff41')
            self.log(">>> SYSTEM ACTIVATED", '#00ff41')
            self.log(">>> Hover cursor over target items", '#00ffff')
            self.log(">>> Press [8] or [Mouse Side Button] to scan", '#00ffff')
            self.log(">>> Press [Shift+K] to deactivate", '#ffff00')
            
            # Register keyboard hotkeys
            try:
                keyboard.add_hotkey('8', self.on_hotkey_triggered, suppress=False)
                self.hotkey_registered = True
                self.log(">>> Keyboard interface: [ONLINE]", '#00ff41')
            except:
                self.log(">>> WARNING: Keyboard requires admin privileges", '#ff9800')
                self.log(">>> Mouse interface remains operational", '#ffff00')
            
            # Start mouse listener (works without admin!)
            def on_click(x, y, button, pressed):
                if pressed:
                    # Trigger on mouse side buttons (Button.x1 or Button.x2)
                    # These are typically the back/forward buttons on gaming mice
                    if hasattr(button, 'name') and button.name in ['x1', 'x2']:
                        self.on_hotkey_triggered()
                    # Alternative: middle mouse button
                    elif button == mouse.Button.middle:
                        self.on_hotkey_triggered()
            
            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.mouse_listener.start()
            self.hotkey_registered = True
            
            self.log(">>> Mouse interface: [ONLINE]", '#00ff41')
            
        except Exception as e:
            self.log(f"✗ Failed to register hotkey: {e}", '#ff0000')
            self.hotkey_enabled = False
            self.hotkey_button.config(
                text="Start Hotkey (Mouse Side Button)",
                bg='#4CAF50'
            )
    
    def stop_hotkey_listener(self):
        """Stop auto-capture mode"""
        try:
            if self.hotkey_registered:
                try:
                    keyboard.remove_hotkey('8')
                except:
                    pass
                self.hotkey_registered = False
            
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            self.hotkey_enabled = False
            self.hotkey_button.config(
                text="[ ACTIVATE ]",
                bg='#003300',
                fg='#00ff41'
            )
            self.update_status("System Standby", '#ffff00')
            self.log(">>> SYSTEM DEACTIVATED", '#ffff00')
            
        except Exception as e:
            self.log(f"Error stopping hotkey: {e}", '#ff0000')
    
    def on_hotkey_triggered(self):
        """Called when the hotkey is pressed"""
        self.log("\n" + "="*60, '#ffff00')
        self.log("⚡ Hotkey triggered! Taking screenshot...", '#ffff00')
        self.update_status("Capturing screenshot...", '#ffff00')
        
        # Run in a separate thread to avoid blocking
        threading.Thread(target=self.capture_and_search, daemon=True).start()
    
    def capture_and_search(self):
        """Capture screenshot and search for item"""
        try:
            # Small delay to let keys be released
            time.sleep(0.3)
            
            # Take screenshot
            filepath = self.take_screenshot()
            self.log(f"✓ Screenshot saved: {filepath}", '#00ff00')
            
            # Try OCR if enabled
            if self.ocr_var.get():
                self.log("🔍 Detecting item name from screenshot...", '#ffff00')
                self.update_status("Reading item name with OCR...", '#ffff00')
                
                item_name = self.extract_item_name_from_image(filepath)
                
                if item_name:
                    self.log(f"✓ Detected item name: '{item_name}'", '#00ff00')
                    self.search_item(item_name)
                else:
                    self.log("⚠ Could not detect item name, please enter manually", '#ff9800')
                    self.root.after(0, self.prompt_for_item_name)
            else:
                # Get item name from user
                self.root.after(0, self.prompt_for_item_name)
            
        except Exception as e:
            self.log(f"✗ Error: {e}", '#ff0000')
            self.update_status("Error occurred", '#ff0000')
    
    def initialize_ocr(self):
        """Initialize the OCR reader (lazy loading)"""
        if self.ocr_reader is None:
            try:
                self.log("⏳ Initializing OCR engine (first time only, downloading models ~100MB)...", '#ffff00')
                self.update_status("Downloading OCR models...", '#ffff00')
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
                self.log("✓ OCR engine ready!", '#00ff00')
                self.update_status("OCR ready", '#00ff00')
                return True
            except Exception as e:
                self.log(f"✗ OCR initialization failed: {e}", '#ff0000')
                return False
        return True
    
    def fix_ocr_errors(self, text):
        """
        Fix common OCR misreads in Tarkov item names
        
        Args:
            text (str): OCR detected text
            
        Returns:
            str: Corrected text
        """
        if not text:
            return text
        
        # Common OCR corrections for Tarkov items
        corrections = {
            # Numbers misread as letters
            'I': '1',  # I → 1 (e.g., M4AI → M4A1)
            'l': '1',  # lowercase L → 1
            'O': '0',  # O → 0
            'o': '0',  # lowercase o → 0
            'S': '5',  # S → 5 (in some contexts)
            'B': '8',  # B → 8 (e.g., B13 → 813 but context matters)
            'Z': '2',  # Z → 2
        }
        
        # Apply corrections with context awareness
        corrected = text
        
        # Fix M4A1 variants (M4AI → M4A1)
        import re
        corrected = re.sub(r'M4A[Il]', 'M4A1', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'M4[Il]', 'M4A1', corrected, flags=re.IGNORECASE)
        
        # Fix AK variants (AKI4 → AK74, AKI02 → AK102)
        corrected = re.sub(r'AK[Il](\d)', r'AK\1', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'AK([Il])', r'AK7\1', corrected, flags=re.IGNORECASE)
        
        # Fix common item patterns
        corrected = re.sub(r'6[B8]I3', '6B13', corrected, flags=re.IGNORECASE)  # 6BI3 → 6B13
        corrected = re.sub(r'6813', '6B13', corrected, flags=re.IGNORECASE)  # 6813 → 6B13
        corrected = re.sub(r'68I3', '6B13', corrected, flags=re.IGNORECASE)  # 68I3 → 6B13
        
        # Fix ADAR (ADAR might be misread as AOAR)
        corrected = re.sub(r'A[O0]AR', 'ADAR', corrected, flags=re.IGNORECASE)
        
        # Fix REAP-IR (might be misread with numbers)
        corrected = re.sub(r'REAP[- ]?[Il]R', 'REAP-IR', corrected, flags=re.IGNORECASE)
        
        # Fix MPX variants
        corrected = re.sub(r'MPX[- ]?[Il]', 'MPX-1', corrected, flags=re.IGNORECASE)
        
        # Fix common number patterns in item names (e.g., Gen4, 5.45, 7.62)
        corrected = re.sub(r'Gen[Il]', 'Gen4', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'(\d)[Il](\d)', r'\1.\2', corrected)  # 5I45 → 5.45
        corrected = re.sub(r'[Il]\.(\d)', r'1.\1', corrected)  # I.56 → 1.56
        
        return corrected
    
    def extract_item_name_from_image(self, image_path):
        """
        Extract item name from screenshot using OCR
        Focuses on the top-center area where Tarkov displays item names
        """
        try:
            # Initialize OCR if needed
            if not self.initialize_ocr():
                return None
            
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                self.log("✗ Could not load screenshot", '#ff0000')
                return None
            
            height, width = img.shape[:2]
            
            # Get mouse position at time of capture
            mouse_x, mouse_y = self.mouse_controller.position
            
            # Define region of interest based on Tarkov tooltip position
            # Looking at the screenshot: red dot (mouse) on item icon,
            # text appears to the right and slightly up from cursor
            # Need wider capture to get full item names like "Gen4 body armor (High Mobility Kit, Tan)"
            roi_x = max(0, mouse_x + 80)  # Start 80px right of cursor (where text begins)
            roi_y = max(0, mouse_y - 60)  # Start 60px above cursor
            roi_width = 500  # Capture 500px width (wider for full item names)
            roi_height = 80  # Capture 80px height (taller for complete text)
            
            # Make sure we don't go out of bounds
            if roi_x + roi_width > width:
                roi_x = max(0, width - roi_width)
            if roi_y + roi_height > height:
                roi_y = max(0, height - roi_height)
            roi_width = min(roi_width, width - roi_x)
            roi_height = min(roi_height, height - roi_y)
            
            # Crop to region of interest
            roi = img[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
            
            # Save ROI for debugging (optional)
            debug_path = os.path.join(self.screenshots_dir, "last_ocr_region.png")
            cv2.imwrite(debug_path, roi)
            
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to make text more readable
            # Tarkov uses light text on dark background
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Also try inverted threshold
            _, thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Perform OCR on both versions
            results1 = self.ocr_reader.readtext(thresh, detail=0)
            results2 = self.ocr_reader.readtext(thresh_inv, detail=0)
            results3 = self.ocr_reader.readtext(roi, detail=0)
            
            # Combine all results
            all_results = results1 + results2 + results3
            
            if all_results:
                # Find the longest coherent text (likely the item name)
                longest_text = max(all_results, key=len)
                
                # Clean up the text
                item_name = longest_text.strip()
                
                # Fix common OCR misreads
                item_name = self.fix_ocr_errors(item_name)
                
                # Remove common UI elements that might be detected
                unwanted_phrases = [
                    'inspect', 'examine', 'filter', 'search', 'modding', 
                    'edit build', 'discard', 'use', 'equip', 'move',
                    'context menu', 'fold', 'unfold'
                ]
                
                item_name_lower = item_name.lower()
                for phrase in unwanted_phrases:
                    if phrase in item_name_lower:
                        # Try to find item name before the unwanted phrase
                        parts = item_name.split()
                        filtered_parts = [p for p in parts if phrase not in p.lower()]
                        if filtered_parts:
                            item_name = ' '.join(filtered_parts)
                
                item_name = item_name.strip()
                
                if len(item_name) > 2:  # Must be at least 3 characters
                    return item_name
            
            self.log("⚠ No text detected in screenshot", '#ff9800')
            return None
            
        except Exception as e:
            self.log(f"✗ OCR error: {e}", '#ff0000')
            import traceback
            self.log(traceback.format_exc(), '#ff0000')
            return None
    
    def prompt_for_item_name(self):
        """Prompt user to enter item name after screenshot"""
        item_name = tkinter.simpledialog.askstring(
            "Item Name",
            "Enter the item name to search:",
            parent=self.root
        )
        
        if item_name:
            self.search_item(item_name)
        else:
            self.log("Search cancelled.", '#ff9800')
            self.update_status("Ready", '#ffffff')
    
    def manual_search(self):
        """Search for an item manually"""
        item_name = self.search_entry.get().strip()
        
        if not item_name:
            messagebox.showwarning("No Item", "Please enter an item name!")
            return
        
        self.log("\n" + "="*60, '#00bfff')
        self.log(f"🔍 Manual search for: {item_name}", '#00bfff')
        self.search_item(item_name)
    
    def search_item(self, item_name):
        """Search for an item and display results using GraphQL"""
        self.update_status(f"Searching for {item_name}...", '#ffff00')
        
        try:
            # GraphQL query for Tarkov.dev API
            query = """
            query ItemsByName($name: String!) {
              itemsByName(name: $name) {
                name
                shortName
                width
                height
                avg24hPrice
                basePrice
                lastLowPrice
                changeLast48hPercent
                low24hPrice
                high24hPrice
                iconLink
                wikiLink
                link
                updated
                sellFor {
                  vendor {
                    name
                  }
                  price
                  currency
                }
              }
            }
            """
            
            variables = {"name": item_name}
            payload = {"query": query, "variables": variables}
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and 'data' in data and data['data']['itemsByName'] and len(data['data']['itemsByName']) > 0:
                item = data['data']['itemsByName'][0]
                self.display_item_price(item)
                self.update_status("Search complete", '#00ff41')
            else:
                self.log(f">>> ERROR: No item found - {item_name}", '#ff0000')
                self.log(">>> TIP: Try full item name or check spelling", '#ffff00')
                self.update_status("Item not found", '#ff0000')
                
        except Exception as e:
            self.log(f">>> ERROR: API request failed - {e}", '#ff0000')
            self.update_status("Error occurred", '#ff0000')
    
    def display_item_price(self, item_data):
        """Display item price information from GraphQL response"""
        self.log("\n" + "="*60, '#00ffff')
        self.log(f">>> ITEM: {item_data.get('name', 'Unknown').upper()}", '#00ff41')
        self.log("="*60, '#00ffff')
        self.log(f"SHORT NAME: {item_data.get('shortName', 'N/A')}", '#ffffff')
        
        # Use avg24hPrice as primary price (flea market average)
        price = item_data.get('avg24hPrice') or item_data.get('lastLowPrice') or item_data.get('basePrice', 'N/A')
        if isinstance(price, (int, float)) and price > 0:
            self.log(f"FLEA PRICE: {price:,} ₽", '#00ff41')
        else:
            self.log(f"FLEA PRICE: N/A", '#00ff41')
        
        base_price = item_data.get('basePrice', 'N/A')
        if isinstance(base_price, (int, float)):
            self.log(f"BASE PRICE: {base_price:,} ₽", '#ffffff')
        
        diff48h = item_data.get('changeLast48hPercent', 0)
        if diff48h is not None:
            color = '#00ff41' if diff48h >= 0 else '#ff0000'
            self.log(f"48H CHANGE: {diff48h:.2f}%", color)
        
        low24h = item_data.get('low24hPrice', None)
        high24h = item_data.get('high24hPrice', None)
        if low24h and high24h:
            self.log(f"24H RANGE: {low24h:,} - {high24h:,} ₽", '#00ffff')
        
        # Calculate price per slot from width and height
        width = item_data.get('width', None)
        height = item_data.get('height', None)
        if width and height and isinstance(price, (int, float)) and price > 0:
            slots = width * height
            price_per_slot = price / slots
            self.log(f"EFFICIENCY: {price_per_slot:,.0f} ₽/slot ({width}x{height} = {slots} slots)", '#00ffff')
        
        # Get best trader sell price
        sell_for = item_data.get('sellFor', [])
        if sell_for and len(sell_for) > 0:
            # Find highest price vendor
            best_vendor = max(sell_for, key=lambda x: x.get('price', 0))
            trader = best_vendor.get('vendor', {}).get('name', 'N/A')
            trader_price = best_vendor.get('price', 'N/A')
            if isinstance(trader_price, (int, float)):
                self.log(f"BEST TRADER: {trader} - {trader_price:,} ₽", '#ffff00')
        
        self.log("="*60, '#00ffff')
        
        # Show overlay near mouse cursor
        self.show_overlay(item_data)
    
    def take_screenshot(self, region=None, filename=None):
        """Take a screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"tarkov_screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.screenshots_dir, filename)
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(filepath)
        return filepath
    
    def run(self):
        """Start the GUI application"""
        # Test API connection on startup
        self.test_connection()
        
        # Start the main loop
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def test_connection(self):
        """Test API connection to Tarkov.dev GraphQL"""
        try:
            self.log(">>> Testing API connection...", '#ffff00')
            
            query = """
            query {
              itemsByName(name: "bitcoin") {
                name
              }
            }
            """
            
            payload = {"query": query}
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data and 'data' in data:
                self.log(">>> API connection: [ONLINE]", '#00ff41')
                self.update_status("Connected", '#00ff41')
                return True
            else:
                self.log(">>> API error: Empty response", '#ff0000')
                self.update_status("API Error", '#ff0000')
                return False
                
        except Exception as e:
            self.log(f">>> API connection: [OFFLINE] - {e}", '#ff0000')
            self.update_status("Connection Failed", '#ff0000')
            return False
    
    def show_overlay(self, item_data):
        """Show a floating overlay window with price info near mouse cursor"""
        # Close previous overlay if it exists
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
        
        # Get mouse position
        mouse_x, mouse_y = self.mouse_controller.position
        
        # Create overlay window
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("")
        self.overlay_window.overrideredirect(True)  # Remove window decorations
        self.overlay_window.attributes('-topmost', True)  # Always on top
        self.overlay_window.configure(bg='#000000')
        
        # Position near mouse (offset to avoid covering item)
        overlay_x = mouse_x + 20
        overlay_y = mouse_y + 20
        self.overlay_window.geometry(f"+{overlay_x}+{overlay_y}")
        
        # Create frame with border
        frame = tk.Frame(self.overlay_window, bg='#00ff41', padx=3, pady=3)
        frame.pack(fill='both', expand=True)
        
        inner_frame = tk.Frame(frame, bg='#000000', padx=12, pady=12)
        inner_frame.pack(fill='both', expand=True)
        
        # Item name
        name_label = tk.Label(
            inner_frame,
            text=f">>> {item_data.get('name', 'Unknown').upper()}",
            font=("Courier New", 11, "bold"),
            bg='#000000',
            fg='#00ff41',
            justify='left'
        )
        name_label.pack(anchor='w')
        
        # Price (use avg24hPrice from GraphQL)
        price = item_data.get('avg24hPrice') or item_data.get('lastLowPrice') or item_data.get('basePrice', 'N/A')
        price_text = f"{price:,} ₽" if isinstance(price, (int, float)) and price > 0 else "N/A"
        price_label = tk.Label(
            inner_frame,
            text=f"PRICE: {price_text}",
            font=("Courier New", 13, "bold"),
            bg='#000000',
            fg='#00ff41',
            justify='left'
        )
        price_label.pack(anchor='w', pady=(5, 0))
        
        # 48h change (GraphQL provides changeLast48hPercent)
        diff48h = item_data.get('changeLast48hPercent', 0)
        if diff48h is not None:
            change_color = '#00ff41' if diff48h >= 0 else '#ff0000'
            change_symbol = '▲' if diff48h >= 0 else '▼'
            change_label = tk.Label(
                inner_frame,
                text=f"{change_symbol} 48H: {diff48h:.2f}%",
                font=("Courier New", 10),
                bg='#000000',
                fg=change_color,
                justify='left'
            )
            change_label.pack(anchor='w')
        
        # Price per slot (calculate from width x height)
        width = item_data.get('width', None)
        height = item_data.get('height', None)
        if width and height and isinstance(price, (int, float)) and price > 0:
            slots = width * height
            price_per_slot = price / slots
            slot_label = tk.Label(
                inner_frame,
                text=f"EFFICIENCY: {price_per_slot:,.0f} ₽/slot ({width}x{height}={slots})",
                font=("Courier New", 9),
                bg='#000000',
                fg='#00ffff',
                justify='left'
            )
            slot_label.pack(anchor='w')
        
        # Trader price (get best from sellFor array)
        sell_for = item_data.get('sellFor', [])
        if sell_for and len(sell_for) > 0:
            best_vendor = max(sell_for, key=lambda x: x.get('price', 0))
            trader = best_vendor.get('vendor', {}).get('name', 'N/A')
            trader_price = best_vendor.get('price', 'N/A')
            if isinstance(trader_price, (int, float)):
                trader_label = tk.Label(
                    inner_frame,
                    text=f"TRADER: {trader} - {trader_price:,} ₽",
                    font=("Courier New", 9),
                    bg='#000000',
                    fg='#ffff00',
                    justify='left'
                )
                trader_label.pack(anchor='w')
        
        # Close button / Auto-close timer
        close_info = tk.Label(
            inner_frame,
            text="[CLICK TO CLOSE]",
            font=("Courier New", 7),
            bg='#000000',
            fg='#888888',
            justify='center'
        )
        close_info.pack(pady=(5, 0))
        
        # Click anywhere on overlay to close
        def close_overlay(event=None):
            if self.overlay_window:
                self.overlay_window.destroy()
                self.overlay_window = None
        
        self.overlay_window.bind('<Button-1>', close_overlay)
        for widget in [frame, inner_frame, name_label, price_label, change_label, close_info]:
            widget.bind('<Button-1>', close_overlay)
        
        # Auto-close after 5 seconds
        self.overlay_window.after(5000, close_overlay)
    
    def register_toggle_hotkey(self):
        """Register the Shift+K toggle hotkey on launch"""
        try:
            keyboard.add_hotkey('shift+k', self.toggle_hotkey, suppress=False)
            self.toggle_hotkey_registered = True
            self.log("✓ Shift+K hotkey registered (press to start/stop)", '#00ff00')
        except Exception as e:
            self.log(f"⚠ Could not register Shift+K hotkey: {e}", '#ff9800')
            self.log("💡 You can still use the Start button", '#ffff00')
    
    def on_closing(self):
        """Handle window closing"""
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
        if self.hotkey_enabled:
            self.stop_hotkey_listener()
        if self.toggle_hotkey_registered:
            try:
                keyboard.remove_hotkey('shift+k')
            except:
                pass
        self.root.destroy()


def main():
    """Main function to run the UI"""
    # Initialize (no API key needed for tarkov.dev GraphQL API)
    app = TarkovPriceCheckerUI()
    app.run()


if __name__ == "__main__":
    main()
