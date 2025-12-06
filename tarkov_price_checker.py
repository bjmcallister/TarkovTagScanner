"""
Tarkov Item Price Checker
Automatically takes screenshots and retrieves item prices from Tarkov Market API
"""

import pyautogui
import requests
import json
from datetime import datetime
import os
from PIL import Image
import time


class TarkovPriceChecker:
    """Main class for checking Tarkov item prices"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Tarkov Price Checker
        
        Args:
            api_key (str, optional): Tarkov Market API key for higher rate limits
        """
        self.base_url = "https://api.tarkov-market.app/api/v1"
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers['x-api-key'] = api_key
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = "screenshots"
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def test_connection(self):
        """
        Test the API connection
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            print("Testing API connection...")
            
            # First test basic internet connectivity
            try:
                test_response = requests.get("https://www.google.com", timeout=5)
                print("✓ Internet connection working")
            except:
                print("✗ No internet connection detected")
                print("  Please check your network connection")
                return False
            
            # Test Tarkov Market website
            try:
                site_response = requests.get("https://tarkov-market.com", timeout=5)
                print("✓ Tarkov Market website is reachable")
            except:
                print("✗ Cannot reach Tarkov Market website")
                print("  The site may be down or blocked by your firewall")
              # Test API endpoint with a simple item search
            url = f"{self.base_url}/item"
            params = {'q': 'bitcoin'}
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            response.raise_for_status()
            
            if response.json():
                print("✓ API connection successful!")
                return True
            else:
                print("✗ API returned empty response")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"✗ API connection failed: {e}")
            print("\nPossible solutions:")
            print("1. Check if firewall/antivirus is blocking Python")
            print("2. Try disabling VPN if you're using one")
            print("3. Verify the API is not down: https://tarkov-market.com")
            print("4. Wait a few minutes and try again")
            return False
    
    def take_screenshot(self, region=None, filename=None):
        """
        Take a screenshot of the entire screen or a specific region
        
        Args:
            region (tuple, optional): Region to capture (x, y, width, height)
            filename (str, optional): Custom filename for the screenshot
            
        Returns:
            str: Path to the saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"tarkov_screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.screenshots_dir, filename)
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(filepath)
        print(f"Screenshot saved: {filepath}")
        
        return filepath
    
    def get_item_by_name(self, item_name):
        """
        Search for an item by name in the Tarkov Market API
        
        Args:
            item_name (str): Name of the item to search for
            
        Returns:
            dict: Item data including prices
        """
        try:
            url = f"{self.base_url}/item"
            params = {'q': item_name}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]  # Return the first match
            else:
                print(f"No item found with name: {item_name}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching item data: {e}")
            return None
    
    def get_all_items(self):
        """
        Get all items from the Tarkov Market API
        
        Returns:
            list: List of all items with their data
        """
        try:
            url = f"{self.base_url}/items/all"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching all items: {e}")
            return None
    
    def display_item_price(self, item_data):
        """
        Display formatted item price information
        
        Args:
            item_data (dict): Item data from API
        """
        if not item_data:
            print("No item data to display")
            return
        
        print("\n" + "="*60)
        print(f"Item: {item_data.get('name', 'Unknown')}")
        print("="*60)
        print(f"Short Name: {item_data.get('shortName', 'N/A')}")
        print(f"Price: {item_data.get('price', 'N/A'):,} ₽")
        print(f"Base Price: {item_data.get('basePrice', 'N/A'):,} ₽")
        print(f"24h Price Change: {item_data.get('diff24h', 0):.2f}%")
        print(f"7d Price Change: {item_data.get('diff7days', 0):.2f}%")
        print(f"Average 24h Price: {item_data.get('avg24hPrice', 'N/A'):,} ₽")
        print(f"Average 7d Price: {item_data.get('avg7daysPrice', 'N/A'):,} ₽")
        print(f"Trader: {item_data.get('traderName', 'N/A')}")
        print(f"Trader Price: {item_data.get('traderPrice', 'N/A'):,} ₽")
        print(f"Trader Price Currency: {item_data.get('traderPriceCur', 'N/A')}")
        print(f"Wiki Link: {item_data.get('wikiLink', 'N/A')}")
        print(f"Image Link: {item_data.get('img', 'N/A')}")
        print("="*60 + "\n")
    
    def search_and_display(self, item_name, take_screenshot_first=False, screenshot_region=None):
        """
        Search for an item and display its price information
        
        Args:
            item_name (str): Name of the item to search
            take_screenshot_first (bool): Whether to take a screenshot before searching
            screenshot_region (tuple, optional): Region for screenshot (x, y, width, height)
        """
        if take_screenshot_first:
            print(f"Taking screenshot in 3 seconds...")
            time.sleep(3)
            self.take_screenshot(region=screenshot_region)
        
        print(f"Searching for: {item_name}...")
        item_data = self.get_item_by_name(item_name)
        
        if item_data:
            self.display_item_price(item_data)
            return item_data
        else:
            print(f"Could not find item: {item_name}")
            return None
    
    def batch_search(self, item_names, take_screenshots=False, delay=2):
        """
        Search for multiple items
        
        Args:
            item_names (list): List of item names to search
            take_screenshots (bool): Whether to take screenshots for each item
            delay (int): Delay in seconds between searches
            
        Returns:
            dict: Dictionary of item names and their data
        """
        results = {}
        
        for item_name in item_names:
            print(f"\nProcessing: {item_name}")
            result = self.search_and_display(item_name, take_screenshot_first=take_screenshots)
            results[item_name] = result
            
            if len(item_names) > 1:
                time.sleep(delay)
        
        return results
    
    def save_results_to_file(self, results, filename="price_results.json"):
        """
        Save search results to a JSON file
        
        Args:
            results (dict): Dictionary of search results
            filename (str): Output filename
        """
        filepath = os.path.join(self.screenshots_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"Results saved to: {filepath}")


def main():
    """Main function to demonstrate usage"""
    
    # Initialize the price checker
    # You can add your API key here for higher rate limits
    # Get your API key from: https://tarkov-market.com/dev/api
    checker = TarkovPriceChecker(api_key="VavlKtSd7y3wu6DG")
    
    # Test API connection
    if not checker.test_connection():
        return
      # Example usage
    print("\nTarkov Item Price Checker")
    print("="*60)
    
    # Example 1: Search for a single item
    print("\nExample 1: Single item search")
    checker.search_and_display("Physical bitcoin")
    
    # Example 2: Search with screenshot
    print("\nExample 2: Search with screenshot")
    # Uncomment the line below to enable screenshot capture
    # checker.search_and_display("TerraGroup Labs keycard (Red)", take_screenshot_first=True)
    
    # Example 3: Batch search multiple items
    print("\nExample 3: Batch search")
    items_to_search = [
        "Paracord",
        "LEDX Skin Transilluminator",
        "Graphics card"
    ]
    
    results = checker.batch_search(items_to_search, take_screenshots=False)
    
    # Save results to file
    checker.save_results_to_file(results)


if __name__ == "__main__":
    main()
