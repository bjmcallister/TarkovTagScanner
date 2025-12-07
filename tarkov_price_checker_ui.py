"""
Tarkov Item Price Checker with UI, Hotkey, and OCR Support
Press Ctrl+Shift+P to capture screen and automatically detect item names
"""

import pyautogui
import requests
import json
from datetime import datetime, timedelta
import os
from PIL import Image
import time
import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, scrolledtext, messagebox, colorchooser
import keyboard
import threading
import easyocr
import cv2
import numpy as np
from pynput import mouse
import pickle
from packaging import version
from difflib import SequenceMatcher
try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image as PILImage
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


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
        
        # Configurable hotkeys
        self.toggle_hotkey = 'shift+k'
        self.capture_hotkey = '8'
        
        # Game mode (PVP/PVE)
        self.game_mode = 'PVP'  # Default to PVP
        
        # OCR configuration
        self.ocr_reader = None
        self.ocr_enabled = True
        self.ocr_loading = False
        
        # Cache for OCR results (item_name: {data, timestamp})
        self.ocr_cache = {}
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
        # Cache for all items (for fuzzy matching)
        self.all_items_cache = None
        self.all_items_timestamp = None
        
        # Preview mode for capture
        self.preview_mode = False
        self.preview_window = None
        self.preview_update_timer = None
        
        # Settings
        self.settings_file = os.path.join(user_temp, "WabbajackTarkov", "settings.pkl")
        self.items_cache_file = os.path.join(user_temp, "WabbajackTarkov", "items_cache.pkl")
        self.current_version = "1.3.2"
        self.settings = {
            'theme_color': '#00ff41',
            'bg_color': '#000000',
            'font_size': 10,
            'overlay_font_size': 11
        }
        self.load_settings()
        
        # System tray
        self.tray_icon = None
        
        # Overlay window for price display
        self.overlay_window = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Tarkov Tag Scanner")
        self.root.geometry("900x800")
        self.root.configure(bg='#000000')
        
        # Show loading screen and initialize OCR in background
        self.show_loading_screen()
        
        self.create_ui()
        self.register_toggle_hotkey()
        
    def show_loading_screen(self):
        """Display loading screen while OCR models initialize"""
        # Create loading window
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Loading")
        self.loading_window.geometry("400x200")
        self.loading_window.configure(bg='#000000')
        self.loading_window.transient(self.root)
        
        # Center the loading window
        self.loading_window.update_idletasks()
        x = (self.loading_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (200 // 2)
        self.loading_window.geometry(f"400x200+{x}+{y}")
        
        # Loading content
        tk.Label(
            self.loading_window,
            text="TARKOV TAG SCANNER INITIALIZING...",
            font=("Courier New", 14, "bold"),
            bg='#000000',
            fg='#00ff41'
        ).pack(pady=20)
        
        self.loading_label = tk.Label(
            self.loading_window,
            text="Loading OCR models...\nThis may take up to 60 seconds on first run",
            font=("Courier New", 10),
            bg='#000000',
            fg='#00ffff',
            justify='center'
        )
        self.loading_label.pack(pady=20)
        
        # Progress animation
        self.loading_dots = 0
        self.animate_loading()
        
        # Start OCR initialization in background thread
        threading.Thread(target=self.initialize_ocr_background, daemon=True).start()
    
    def animate_loading(self):
        """Animate loading dots"""
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            dots = '.' * (self.loading_dots % 4)
            self.loading_label.config(text=f"Loading OCR models{dots}\nThis may take up to 60 seconds on first run")
            self.loading_dots += 1
            self.root.after(500, self.animate_loading)
    
    def initialize_ocr_background(self):
        """Initialize OCR in background thread"""
        try:
            self.ocr_loading = True
            # Initialize EasyOCR (downloads models on first run)
            self.ocr_reader = easyocr.Reader(['en'], gpu=False)
            self.ocr_loading = False
            
            # Pre-fetch all items for fuzzy matching
            try:
                if hasattr(self, 'loading_label') and self.loading_window.winfo_exists():
                    self.loading_label.config(text="Loading item database...")
                self.load_or_fetch_all_items()
            except Exception as e:
                print(f"Warning: Could not pre-fetch items: {e}")
            
            # Close loading window
            if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
                self.loading_window.destroy()
        except Exception as e:
            self.ocr_loading = False
            if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
                self.loading_window.destroy()
            messagebox.showerror("OCR Error", f"Failed to initialize OCR: {e}")
    
    def create_ui(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#000000')
        title_frame.pack(pady=15, padx=10, fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="🏷️ TARKOV TAG SCANNER 🏷️",
            font=("Courier New", 22, "bold"),
            bg='#000000',
            fg='#00ff41'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="INSTANT PRICE TAG SCANNING",
            font=("Courier New", 11, "bold"),
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
            command=self.toggle_hotkey_method,
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
        
        # Configure hotkey button
        self.configure_button = tk.Button(
            button_frame,
            text="[ CONFIGURE HOTKEY ]",
            command=self.configure_hotkeys,
            font=("Courier New", 10, "bold"),
            bg='#003300',
            fg='#00ff41',
            activebackground='#00ff41',
            activeforeground='#000000',
            padx=15,
            pady=10,
            bd=3,
            relief='raised',
            cursor='hand2'
        )
        self.configure_button.pack(side='left', padx=5)
        
        # PVP/PVE mode toggle
        self.mode_var = tk.StringVar(value='PVP')
        mode_label = tk.Label(
            button_frame,
            text="MODE:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41'
        )
        mode_label.pack(side='left', padx=(15, 5))
        
        pvp_radio = tk.Radiobutton(
            button_frame,
            text="PVP",
            variable=self.mode_var,
            value='PVP',
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41',
            selectcolor='#000000',
            activebackground='#001100',
            activeforeground='#00ff41',
            command=self.update_game_mode
        )
        pvp_radio.pack(side='left')
        
        pve_radio = tk.Radiobutton(
            button_frame,
            text="PVE",
            variable=self.mode_var,
            value='PVE',
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41',
            selectcolor='#000000',
            activebackground='#001100',
            activeforeground='#00ff41',
            command=self.update_game_mode
        )
        pve_radio.pack(side='left', padx=(0, 15))
        
        # Settings button
        settings_btn = tk.Button(
            button_frame,
            text="[ SETTINGS ]",
            command=self.open_settings,
            font=("Courier New", 9, "bold"),
            bg='#003300',
            fg='#00ff41',
            padx=10,
            pady=10,
            bd=2,
            cursor='hand2'
        )
        settings_btn.pack(side='left', padx=5)
        
        # Minimize to tray button
        if TRAY_AVAILABLE:
            tray_btn = tk.Button(
                button_frame,
                text="[ MINIMIZE ]",
                command=self.minimize_to_tray,
                font=("Courier New", 9, "bold"),
                bg='#003300',
                fg='#00ff41',
                padx=10,
                pady=10,
                bd=2,
                cursor='hand2'
            )
            tray_btn.pack(side='left', padx=5)
        
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
║                 TARKOV TAG SCANNER v1.0                       ║
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

>>> SUPPORT THE PROJECT:
  ☕ Buy Me a Coffee: buymeacoffee.com/allisteras

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
        
    def toggle_hotkey_method(self):
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
            self.log(f">>> Press [{self.capture_hotkey.upper()}] or [Mouse Side Button] to scan", '#00ffff')
            self.log(f">>> Press [{self.toggle_hotkey.upper()}] to deactivate", '#ffff00')
            
            # Register keyboard hotkeys
            try:
                keyboard.add_hotkey(self.capture_hotkey, self.on_hotkey_triggered, suppress=False)
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
                    keyboard.remove_hotkey(self.capture_hotkey)
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
        if not self.preview_mode:
            # First press: Show preview rectangle
            self.log("\n" + "="*60, '#00ff00')
            self.log("⚡ Preview mode activated - Press hotkey again to capture", '#00ff00')
            self.show_preview_rectangle()
        else:
            # Second press: Capture the area
            self.log("⚡ Capturing...", '#ffff00')
            self.hide_preview_rectangle()
            self.update_status("Capturing screenshot...", '#ffff00')
            # Run in a separate thread to avoid blocking
            threading.Thread(target=self.capture_and_search, daemon=True).start()
    
    def show_preview_rectangle(self):
        """Show a green rectangle overlay to preview capture area"""
        try:
            # Create transparent overlay window
            self.preview_window = tk.Toplevel(self.root)
            self.preview_window.attributes('-topmost', True)
            self.preview_window.attributes('-alpha', 0.3)  # Semi-transparent
            self.preview_window.overrideredirect(True)  # No window decorations
            
            # Tooltip-sized dimensions (same as actual capture)
            capture_width = 350
            capture_height = 80
            
            # Initial position
            mouse_x, mouse_y = self.mouse_controller.position
            capture_x = mouse_x + 15
            capture_y = mouse_y - 60
            
            self.preview_window.geometry(f"{capture_width}x{capture_height}+{capture_x}+{capture_y}")
            
            # Green border frame
            border_frame = tk.Frame(self.preview_window, bg='#00ff00', bd=0)
            border_frame.pack(fill='both', expand=True, padx=3, pady=3)
            
            # Transparent inner area
            inner_frame = tk.Frame(border_frame, bg='black')
            inner_frame.pack(fill='both', expand=True)
            
            self.preview_mode = True
            
            # Start updating position to follow mouse
            self.update_preview_position()
            
        except Exception as e:
            self.log(f"✗ Preview error: {e}", '#ff0000')
    
    def update_preview_position(self):
        """Update preview rectangle position to follow mouse"""
        if self.preview_mode and self.preview_window:
            try:
                # Get current mouse position
                mouse_x, mouse_y = self.mouse_controller.position
                
                # Calculate new position (same offset as capture)
                capture_x = mouse_x + 15
                capture_y = mouse_y - 60
                
                # Update window position
                self.preview_window.geometry(f"+{capture_x}+{capture_y}")
                
                # Schedule next update (60 FPS)
                self.preview_update_timer = self.root.after(16, self.update_preview_position)
            except:
                pass
    
    def hide_preview_rectangle(self):
        """Hide the preview rectangle"""
        # Cancel update timer
        if self.preview_update_timer:
            try:
                self.root.after_cancel(self.preview_update_timer)
            except:
                pass
            self.preview_update_timer = None
        
        # Destroy window
        if self.preview_window:
            try:
                self.preview_window.destroy()
            except:
                pass
            self.preview_window = None
        
        self.preview_mode = False
    
    def capture_and_search(self):
        """Capture screenshot and search for item"""
        try:
            # Small delay to let keys be released
            time.sleep(0.3)
            
            # Get mouse position
            mouse_x, mouse_y = self.mouse_controller.position
            
            # Capture tooltip-sized area near cursor
            capture_width = 350
            capture_height = 80
            capture_x = mouse_x + 15   # Slightly to the right
            capture_y = mouse_y - 60   # Above cursor
            
            region = (capture_x, capture_y, capture_width, capture_height)
            filepath = self.take_screenshot(region=region, filename="tooltip_capture.png")
            self.log(f"✓ Captured {capture_width}x{capture_height}px around cursor", '#00ff00')
            
            # Use OCR to detect item name (always enabled)
            self.log("🔍 Detecting item name from screenshot...", '#ffff00')
            self.update_status("Reading item name with OCR...", '#ffff00')
            
            item_name = self.extract_item_name_from_image(filepath)
            
            if item_name:
                self.log(f"✓ Detected item name: '{item_name}'", '#00ff00')
                self.search_item(item_name)
            else:
                self.log("⚠ Could not detect item name from screenshot", '#ff9800')
                self.update_status("No text detected", '#ff0000')
            
        except Exception as e:
            self.log(f"✗ Error: {e}", '#ff0000')
            self.update_status("Error occurred", '#ff0000')
    
    def initialize_ocr(self):
        """Check if OCR is ready (already initialized in background)"""
        if self.ocr_loading:
            self.log(">>> Waiting for OCR initialization...", '#ffff00')
            self.update_status("Waiting for OCR...", '#ffff00')
            while self.ocr_loading:
                time.sleep(0.1)
                self.root.update()
        
        if self.ocr_reader is None:
            self.log(">>> ERROR: OCR not initialized", '#ff0000')
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
        Detects the black tooltip box with white border and extracts text from it
        """
        try:
            # Initialize OCR if needed
            if not self.initialize_ocr():
                return None
            
            # Load the screenshot - this should already be just the tooltip
            img = cv2.imread(image_path)
            if img is None:
                self.log("✗ Could not load screenshot", '#ff0000')
                return None
            
            # Since we captured exactly where the tooltip is, just use the whole image
            roi = img
            
            self.log(f"✓ Using captured tooltip region", '#00ffff')
            
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to make text more readable
            # Tarkov uses light text on dark background
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Perform OCR with position data (detail=1 returns bbox, text, confidence)
            results = self.ocr_reader.readtext(thresh, detail=1)
            
            if results:
                # Filter out UI elements
                unwanted_phrases = [
                    'inspect', 'examine', 'filter', 'search', 'modding', 
                    'edit build', 'discard', 'use', 'equip', 'move',
                    'context menu', 'fold', 'unfold', 'sort', 'filter by'
                ]
                
                # Mouse position in the captured image (we captured 350x80 with mouse at x+15, y-60)
                # So mouse is at approximately x=-15, y=60 relative to capture origin
                mouse_in_capture_x = -15  # 15 pixels to the left of capture area
                mouse_in_capture_y = 60   # 60 pixels below capture area top
                
                # Filter and find text closest to mouse position
                text_candidates = []
                seen = set()
                
                for (bbox, text, confidence) in results:
                    text_clean = text.strip()
                    text_lower = text_clean.lower()
                    
                    # Skip duplicates, unwanted phrases, and very short text
                    if text_lower in seen:
                        continue
                    if any(phrase in text_lower for phrase in unwanted_phrases):
                        continue
                    if len(text_clean) < 3:
                        continue
                    
                    # Calculate center position of this text
                    center_x = sum([point[0] for point in bbox]) / 4
                    center_y = sum([point[1] for point in bbox]) / 4
                    
                    # Calculate distance from mouse position
                    distance = ((center_x - mouse_in_capture_x)**2 + (center_y - mouse_in_capture_y)**2)**0.5
                    
                    seen.add(text_lower)
                    text_candidates.append({
                        'text': text_clean,
                        'distance': distance,
                        'confidence': confidence
                    })
                
                if not text_candidates:
                    self.log("⚠ No valid text detected in screenshot", '#ff9800')
                    return None
                
                # Sort by distance (closest first)
                text_candidates.sort(key=lambda x: x['distance'])
                
                # Take the closest text as the item name
                item_name = text_candidates[0]['text']
                self.log(f"✓ Selected closest text (distance: {text_candidates[0]['distance']:.1f}px)", '#00ffff')
                
                # Fix common OCR misreads
                item_name = self.fix_ocr_errors(item_name)
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
    
    def manual_search(self):
        """Search for an item manually"""
        item_name = self.search_entry.get().strip()
        
        if not item_name:
            messagebox.showwarning("No Item", "Please enter an item name!")
            return
        
        self.log("\n" + "="*60, '#00bfff')
        self.log(f"🔍 Manual search for: {item_name}", '#00bfff')
        self.search_item(item_name)
    
    def load_or_fetch_all_items(self):
        """Load items from disk cache or fetch from API if version changed"""
        try:
            # Try to load from disk cache
            if os.path.exists(self.items_cache_file):
                try:
                    with open(self.items_cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                        
                    # Check if cache version matches current app version
                    if cache_data.get('version') == self.current_version:
                        self.all_items_cache = cache_data.get('items', [])
                        if self.all_items_cache:
                            self.log(f">>> Loaded {len(self.all_items_cache)} items from cache", '#00ff41')
                            return self.all_items_cache
                    else:
                        self.log(f">>> Cache version mismatch, fetching fresh data...", '#ffff00')
                except Exception as e:
                    self.log(f">>> Could not load cache: {e}", '#ff9800')
            
            # Fetch from API
            self.log(">>> Fetching all items from API...", '#ffff00')
            
            # Determine game mode for API query
            game_mode = 'regular' if self.game_mode == 'PVP' else 'pve'
            
            # GraphQL query to fetch all items (just names)
            query = """
            query AllItems($gameMode: GameMode) {
              items(gameMode: $gameMode) {
                name
                shortName
              }
            }
            """
            
            variables = {"gameMode": game_mode}
            payload = {"query": query, "variables": variables}
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data and 'data' in data and data['data']['items']:
                items = data['data']['items']
                # Store both full names and short names
                all_names = set()
                for item in items:
                    if item.get('name'):
                        all_names.add(item['name'])
                    if item.get('shortName'):
                        all_names.add(item['shortName'])
                
                self.all_items_cache = list(all_names)
                
                # Save to disk with version
                try:
                    os.makedirs(os.path.dirname(self.items_cache_file), exist_ok=True)
                    cache_data = {
                        'version': self.current_version,
                        'items': self.all_items_cache
                    }
                    with open(self.items_cache_file, 'wb') as f:
                        pickle.dump(cache_data, f)
                    self.log(f">>> Cached {len(self.all_items_cache)} items to disk", '#00ff41')
                except Exception as e:
                    self.log(f">>> Could not save cache: {e}", '#ff9800')
                
                return self.all_items_cache
            
            return []
            
        except Exception as e:
            self.log(f">>> WARNING: Could not fetch all items - {e}", '#ff9800')
            return self.all_items_cache if self.all_items_cache else []
    
    def find_best_match(self, search_name, threshold=0.6):
        """Find the best matching item name using fuzzy matching"""
        # Use cached items (already loaded on startup)
        all_items = self.all_items_cache if self.all_items_cache else []
        
        if not all_items:
            return search_name  # Return original if can't fetch items
        
        # Calculate similarity scores
        best_match = None
        best_score = 0
        
        search_lower = search_name.lower().strip()
        
        for item_name in all_items:
            item_lower = item_name.lower()
            
            # Exact match
            if search_lower == item_lower:
                return item_name
            
            # Check if search is contained in item name
            if search_lower in item_lower:
                score = len(search_lower) / len(item_lower)
                if score > best_score:
                    best_score = score
                    best_match = item_name
                continue
            
            # Fuzzy matching using SequenceMatcher
            similarity = SequenceMatcher(None, search_lower, item_lower).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = item_name
        
        # Only return match if similarity is above threshold
        if best_score >= threshold:
            if best_match.lower() != search_lower:
                self.log(f">>> Fuzzy match: '{search_name}' → '{best_match}' (score: {best_score:.2f})", '#00ffff')
            return best_match
        
        return search_name  # Return original if no good match
    
    def search_item(self, item_name):
        """Search for an item and display results using GraphQL"""
        # Try fuzzy matching to find correct item name
        corrected_name = self.find_best_match(item_name)
        
        self.update_status(f"Searching for {corrected_name}...", '#ffff00')
        
        # Check cache first
        cache_key = f"{corrected_name}_{self.game_mode}"
        cached_data = self.get_cached_item(cache_key)
        if cached_data:
            self.log(">>> Using cached data", '#00ffff')
            self.display_item_price(cached_data)
            self.update_status("Search complete (cached)", '#00ff41')
            return
        
        try:
            # Determine game mode for API query
            game_mode = 'regular' if self.game_mode == 'PVP' else 'pve'
            
            # GraphQL query for Tarkov.dev API
            # Using 'items' query instead of deprecated 'itemsByName'
            query = """
            query Items($name: String!, $gameMode: GameMode) {
              items(name: $name, gameMode: $gameMode) {
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
            
            variables = {
                "name": corrected_name,
                "gameMode": game_mode
            }
            payload = {"query": query, "variables": variables}
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_msg = data['errors'][0].get('message', 'Unknown error')
                self.log(f">>> ERROR: GraphQL error - {error_msg}", '#ff0000')
                self.update_status("Query error", '#ff0000')
                return
            
            if data and 'data' in data and data['data']['items'] and len(data['data']['items']) > 0:
                item = data['data']['items'][0]
                # Cache the result
                self.cache_item(cache_key, item)
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
        
        # Check for updates in background
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
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
        
        # Get screen dimensions
        screen_width = self.overlay_window.winfo_screenwidth()
        screen_height = self.overlay_window.winfo_screenheight()
        
        # Estimate overlay size (width ~400px, height ~250px)
        overlay_width = 400
        overlay_height = 250
        
        # Position near mouse (offset to avoid covering item)
        overlay_x = mouse_x + 20
        overlay_y = mouse_y + 20
        
        # Keep overlay on screen - adjust if too close to edges
        if overlay_x + overlay_width > screen_width:
            overlay_x = mouse_x - overlay_width - 20  # Position to left of cursor
        if overlay_y + overlay_height > screen_height:
            overlay_y = screen_height - overlay_height - 20  # Position above cursor
        
        # Ensure minimum position
        overlay_x = max(10, overlay_x)
        overlay_y = max(10, overlay_y)
        
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
            font=("Courier New", 10, "bold"),
            bg='#000000',
            fg='#00ff41',
            justify='left'
        )
        name_label.pack(anchor='w')
        
        # Price (use avg24hPrice from GraphQL) - MOST PROMINENT
        price = item_data.get('avg24hPrice') or item_data.get('lastLowPrice') or item_data.get('basePrice', 'N/A')
        price_text = f"{price:,} ₽" if isinstance(price, (int, float)) and price > 0 else "N/A"
        price_label = tk.Label(
            inner_frame,
            text=price_text,
            font=("Courier New", 18, "bold"),
            bg='#000000',
            fg='#00ff41',
            justify='left'
        )
        price_label.pack(anchor='w', pady=(3, 0))
        
        # Price per slot (calculate from width x height) - SECOND MOST PROMINENT
        width = item_data.get('width', None)
        height = item_data.get('height', None)
        if width and height and isinstance(price, (int, float)) and price > 0:
            slots = width * height
            price_per_slot = price / slots
            slot_label = tk.Label(
                inner_frame,
                text=f"{price_per_slot:,.0f} ₽/slot",
                font=("Courier New", 15, "bold"),
                bg='#000000',
                fg='#00ffff',
                justify='left'
            )
            slot_label.pack(anchor='w', pady=(2, 0))
            
            # Small dimension info
            size_label = tk.Label(
                inner_frame,
                text=f"({width}x{height} = {slots} slots)",
                font=("Courier New", 8),
                bg='#000000',
                fg='#00aaaa',
                justify='left'
            )
            size_label.pack(anchor='w')
        
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
                    font=("Courier New", 8),
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
        for widget in [frame, inner_frame, name_label, price_label, close_info]:
            widget.bind('<Button-1>', close_overlay)
        
        # Auto-close after 5 seconds
        self.overlay_window.after(5000, close_overlay)
    
    def update_game_mode(self):
        """Update the game mode for API queries"""
        self.game_mode = self.mode_var.get()
        self.log(f">>> Game mode set to: {self.game_mode}", '#00ff41')
    
    def configure_hotkeys(self):
        """Open dialog to configure custom hotkeys"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configure Hotkeys")
        config_window.geometry("500x300")
        config_window.configure(bg='#000000')
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Title
        title_label = tk.Label(
            config_window,
            text="HOTKEY CONFIGURATION",
            font=("Courier New", 14, "bold"),
            bg='#000000',
            fg='#00ff41'
        )
        title_label.pack(pady=15)
        
        # Toggle hotkey
        toggle_frame = tk.Frame(config_window, bg='#001100', padx=15, pady=10)
        toggle_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            toggle_frame,
            text="Toggle System (Activate/Deactivate):",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41'
        ).pack(anchor='w')
        
        toggle_entry = tk.Entry(
            toggle_frame,
            font=("Courier New", 11),
            bg='#000000',
            fg='#00ff41',
            insertbackground='#00ff41',
            width=30
        )
        toggle_entry.insert(0, self.toggle_hotkey)
        toggle_entry.pack(pady=5)
        
        # Capture hotkey
        capture_frame = tk.Frame(config_window, bg='#001100', padx=15, pady=10)
        capture_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            capture_frame,
            text="Capture Item:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg='#00ff41'
        ).pack(anchor='w')
        
        capture_entry = tk.Entry(
            capture_frame,
            font=("Courier New", 11),
            bg='#000000',
            fg='#00ff41',
            insertbackground='#00ff41',
            width=30
        )
        capture_entry.insert(0, self.capture_hotkey)
        capture_entry.pack(pady=5)
        
        # Help text
        help_label = tk.Label(
            config_window,
            text="Examples: 'shift+k', 'ctrl+p', 'f1', '8'\nSeparate keys with '+' for combinations",
            font=("Courier New", 8),
            bg='#000000',
            fg='#00aaaa'
        )
        help_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(config_window, bg='#000000')
        button_frame.pack(pady=15)
        
        def save_hotkeys():
            new_toggle = toggle_entry.get().strip().lower()
            new_capture = capture_entry.get().strip().lower()
            
            if new_toggle and new_capture:
                # Unregister old hotkeys
                if self.hotkey_registered:
                    try:
                        keyboard.remove_hotkey(self.capture_hotkey)
                    except:
                        pass
                if self.toggle_hotkey_registered:
                    try:
                        keyboard.remove_hotkey(self.toggle_hotkey)
                    except:
                        pass
                
                # Update hotkeys
                self.toggle_hotkey = new_toggle
                self.capture_hotkey = new_capture
                
                # Re-register if active
                if self.hotkey_enabled:
                    try:
                        keyboard.add_hotkey(self.capture_hotkey, self.on_hotkey_triggered)
                        self.hotkey_registered = True
                    except:
                        self.log(">>> ERROR: Failed to register capture hotkey", '#ff0000')
                
                try:
                    keyboard.add_hotkey(self.toggle_hotkey, lambda: self.root.after(0, self.toggle_hotkey_handler))
                    self.toggle_hotkey_registered = True
                except:
                    self.log(">>> ERROR: Failed to register toggle hotkey", '#ff0000')
                
                self.log(f">>> Hotkeys updated: Toggle={new_toggle}, Capture={new_capture}", '#00ff41')
                config_window.destroy()
            else:
                messagebox.showerror("Error", "Both hotkeys must be specified")
        
        save_btn = tk.Button(
            button_frame,
            text="[ SAVE ]",
            command=save_hotkeys,
            font=("Courier New", 10, "bold"),
            bg='#003300',
            fg='#00ff41',
            padx=20,
            pady=8
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="[ CANCEL ]",
            command=config_window.destroy,
            font=("Courier New", 10, "bold"),
            bg='#330000',
            fg='#ff4444',
            padx=20,
            pady=8
        )
        cancel_btn.pack(side='left', padx=5)
    
    def register_toggle_hotkey(self):
        """Register the toggle hotkey on launch"""
        try:
            keyboard.add_hotkey(self.toggle_hotkey, lambda: self.root.after(0, self.toggle_hotkey_handler), suppress=False)
            self.toggle_hotkey_registered = True
            self.log(f">>> Toggle hotkey registered: {self.toggle_hotkey.upper()}", '#00ff00')
        except Exception as e:
            self.log(f">>> Could not register toggle hotkey: {e}", '#ff9800')
            self.log(">>> You can still use the [ACTIVATE] button", '#ffff00')
    
    def toggle_hotkey_handler(self):
        """Handle toggle hotkey press"""
        self.toggle_hotkey_method()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'rb') as f:
                    saved_settings = pickle.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            self.log(f">>> Could not load settings: {e}", '#ff9800')
    
    def save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'wb') as f:
                pickle.dump(self.settings, f)
        except Exception as e:
            self.log(f">>> Could not save settings: {e}", '#ff0000')
    
    def get_cached_item(self, item_name):
        """Get item from cache if not expired"""
        if item_name in self.ocr_cache:
            cached = self.ocr_cache[item_name]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                return cached['data']
            else:
                del self.ocr_cache[item_name]
        return None
    
    def cache_item(self, item_name, data):
        """Cache item data"""
        self.ocr_cache[item_name] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def check_for_updates(self):
        """Check GitHub for new releases"""
        try:
            response = requests.get(
                'https://api.github.com/repos/bjmcallister/TarkovTagScanner/releases/latest',
                timeout=5
            )
            if response.status_code == 200:
                latest = response.json()
                latest_version = latest['tag_name'].lstrip('v')
                
                if version.parse(latest_version) > version.parse(self.current_version):
                    self.log(f"\n>>> UPDATE AVAILABLE: v{latest_version}", '#ffff00')
                    self.log(f">>> Current version: v{self.current_version}", '#ffffff')
                    self.log(f">>> Download: {latest['html_url']}", '#00ffff')
                    
                    if messagebox.askyesno("Update Available", 
                        f"New version v{latest_version} is available!\n\nWould you like to download it?"):
                        import webbrowser
                        webbrowser.open(latest['html_url'])
        except Exception as e:
            pass  # Silently fail for update check
    
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        if not TRAY_AVAILABLE:
            self.root.iconify()
            return
        
        try:
            self.root.withdraw()
            
            if self.tray_icon is None:
                # Create tray icon
                icon_image = PILImage.new('RGB', (64, 64), color='black')
                from PIL import ImageDraw
                draw = ImageDraw.Draw(icon_image)
                draw.text((10, 20), "TTS", fill='#00ff41')
                
                menu = Menu(
                    MenuItem('Show', self.show_from_tray),
                    MenuItem('Exit', self.exit_from_tray)
                )
                
                self.tray_icon = Icon("TarkovTagScanner", icon_image, "Tarkov Tag Scanner", menu)
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            self.log(f">>> Tray icon error: {e}", '#ff0000')
            self.root.iconify()
    
    def show_from_tray(self):
        """Restore window from tray"""
        self.root.after(0, self.root.deiconify)
    
    def exit_from_tray(self):
        """Exit from tray icon"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.on_closing)
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#000000')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        tk.Label(
            settings_window,
            text="SETTINGS",
            font=("Courier New", 14, "bold"),
            bg='#000000',
            fg=self.settings['theme_color']
        ).pack(pady=15)
        
        # Theme color
        theme_frame = tk.Frame(settings_window, bg='#001100', padx=15, pady=10)
        theme_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            theme_frame,
            text="Theme Color:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg=self.settings['theme_color']
        ).pack(side='left')
        
        tk.Button(
            theme_frame,
            text="Choose Color",
            command=lambda: self.choose_theme_color(settings_window),
            font=("Courier New", 9),
            bg='#003300',
            fg=self.settings['theme_color']
        ).pack(side='right', padx=5)
        
        # Font size
        font_frame = tk.Frame(settings_window, bg='#001100', padx=15, pady=10)
        font_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            font_frame,
            text="UI Font Size:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg=self.settings['theme_color']
        ).pack(side='left')
        
        font_var = tk.IntVar(value=self.settings['font_size'])
        font_spin = tk.Spinbox(
            font_frame,
            from_=8,
            to=16,
            textvariable=font_var,
            width=5,
            font=("Courier New", 10),
            bg='#000000',
            fg=self.settings['theme_color']
        )
        font_spin.pack(side='right', padx=5)
        
        # Overlay font size
        overlay_frame = tk.Frame(settings_window, bg='#001100', padx=15, pady=10)
        overlay_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            overlay_frame,
            text="Overlay Font Size:",
            font=("Courier New", 10, "bold"),
            bg='#001100',
            fg=self.settings['theme_color']
        ).pack(side='left')
        
        overlay_var = tk.IntVar(value=self.settings['overlay_font_size'])
        overlay_spin = tk.Spinbox(
            overlay_frame,
            from_=8,
            to=20,
            textvariable=overlay_var,
            width=5,
            font=("Courier New", 10),
            bg='#000000',
            fg=self.settings['theme_color']
        )
        overlay_spin.pack(side='right', padx=5)
        
        # Buttons
        button_frame = tk.Frame(settings_window, bg='#000000')
        button_frame.pack(pady=15)
        
        def apply_settings():
            self.settings['font_size'] = font_var.get()
            self.settings['overlay_font_size'] = overlay_var.get()
            self.save_settings()
            messagebox.showinfo("Settings", "Settings saved! Restart the app to apply all changes.")
            settings_window.destroy()
        
        tk.Button(
            button_frame,
            text="[ SAVE ]",
            command=apply_settings,
            font=("Courier New", 10, "bold"),
            bg='#003300',
            fg=self.settings['theme_color'],
            padx=20,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="[ CANCEL ]",
            command=settings_window.destroy,
            font=("Courier New", 10, "bold"),
            bg='#330000',
            fg='#ff4444',
            padx=20,
            pady=8
        ).pack(side='left', padx=5)
    
    def choose_theme_color(self, parent):
        """Open color chooser for theme"""
        color = colorchooser.askcolor(
            initialcolor=self.settings['theme_color'],
            parent=parent,
            title="Choose Theme Color"
        )
        if color[1]:
            self.settings['theme_color'] = color[1]
            parent.destroy()
            self.open_settings()  # Reopen with new color
    
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
                keyboard.remove_hotkey(self.toggle_hotkey)
            except:
                pass
        if self.tray_icon:
            self.tray_icon.stop()
        self.save_settings()
        self.root.destroy()


def main():
    """Main function to run the UI"""
    # Initialize (no API key needed for tarkov.dev GraphQL API)
    app = TarkovPriceCheckerUI()
    app.run()


if __name__ == "__main__":
    main()
