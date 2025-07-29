"""Test script for the browser automation agent with improved error handling."""

import asyncio
import aiohttp
import json
import base64
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def save_screenshot(data: dict, filename: str):
    """Save a base64-encoded screenshot to a file."""
    if "screenshot" not in data:
        print("No screenshot data in response")
        return
    
    screenshot_data = base64.b64decode(data["screenshot"])
    with open(filename, "wb") as f:
        f.write(screenshot_data)
    print(f"Screenshot saved to {filename}")

async def browser_request(session, method, endpoint, **kwargs):
    """Make a request to the browser API with error handling."""
    url = f"{BASE_URL}{endpoint}"
    try:
        async with session.request(method, url, **kwargs) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"Error {response.status} from {endpoint}: {error_text}")
                return None
            return await response.json()
    except Exception as e:
        print(f"Request to {endpoint} failed: {str(e)}")
        return None

async def test_browser_automation():
    """Test the browser automation endpoints with improved reliability."""
    async with aiohttp.ClientSession() as session:
        # Start the browser
        print("Starting browser...")
        start_result = await browser_request(session, 'POST', '/browser/start')
        if not start_result:
            print("Failed to start browser. Aborting test.")
            return
        print("Start browser:", start_result)
        
        # Add a small delay to ensure browser is ready
        await asyncio.sleep(2)
        
        # Test 1: Navigate to example.com
        print("\n--- Test 1: Navigate to example.com ---")
        nav1_result = await browser_request(
            session, 'POST', '/browser/navigate',
            json={"url": "https://example.com"}
        )
        if nav1_result:
            print("Navigation successful:", json.dumps({
                "url": nav1_result.get("url"),
                "title": nav1_result.get("title")
            }, indent=2))
            
            # Take a screenshot
            print("Taking screenshot...")
            screenshot1 = await browser_request(session, 'GET', '/browser/screenshot')
            if screenshot1:
                save_screenshot(screenshot1, "example_screenshot.png")
        
        # Add delay between navigations
        await asyncio.sleep(2)
        
        # Test 2: Navigate to Google
        print("\n--- Test 2: Navigate to Google ---")
        nav2_result = await browser_request(
            session, 'POST', '/browser/navigate',
            json={"url": "https://www.google.com"}
        )
        
        if nav2_result:
            print("Navigation successful:", json.dumps({
                "url": nav2_result.get("url"),
                "title": nav2_result.get("title")
            }, indent=2))
            
            # Wait for Google to load
            await asyncio.sleep(3)
            
            # Try to accept cookies if the banner appears
            print("Attempting to accept cookies...")
            await browser_request(
                session, 'POST', '/browser/click',
                json={"selector": "button:has-text('Accept all')"}
            )
            
            # Wait a bit for any dialogs to be handled
            await asyncio.sleep(2)
            
            # Try to type in the search box
            print("Typing search query...")
            type_result = await browser_request(
                session, 'POST', '/browser/type',
                json={"selector": "textarea[name='q'], input[name='q']", "text": "Avatar Crew AI Demo"}
            )
            if type_result:
                print("Type result:", type_result)
            
            # Take a screenshot
            print("Taking screenshot of Google search...")
            screenshot2 = await browser_request(session, 'GET', '/browser/screenshot')
            if screenshot2:
                save_screenshot(screenshot2, "google_search.png")
        
        # Close the browser
        print("\n--- Cleaning up ---")
        close_result = await browser_request(session, 'POST', '/browser/close')
        if close_result:
            print("Browser closed successfully:", close_result)
        else:
            print("Failed to close browser properly")

if __name__ == "__main__":
    print("Testing browser automation endpoints...")
    asyncio.run(test_browser_automation())
