"""Comprehensive test for browser agent features."""

import asyncio
import aiohttp
import json
import base64
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def save_screenshot(data: Dict[str, Any], filename: str) -> None:
    """Save a base64-encoded screenshot to a file."""
    if "screenshot" not in data:
        print(f"No screenshot data in response: {data}")
        return
    
    try:
        screenshot_data = base64.b64decode(data["screenshot"])
        with open(filename, "wb") as f:
            f.write(screenshot_data)
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Failed to save screenshot: {str(e)}")

async def test_feature(session: aiohttp.ClientSession, name: str, method: str, 
                      endpoint: str, **kwargs) -> Dict[str, Any]:
    """Test a single browser feature and return the result."""
    print(f"\n--- Testing {name} ---")
    try:
        async with session.request(method, f"{BASE_URL}{endpoint}", **kwargs) as resp:
            result = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")
            return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

async def run_browser_tests():
    """Run all browser automation tests."""
    async with aiohttp.ClientSession() as session:
        # 1. Start the browser
        await test_feature(session, "Start Browser", "POST", "/browser/start")
        
        # 2. Navigate to a test page
        test_url = "https://httpbin.org/forms/post"
        await test_feature(session, "Navigate to URL", "POST", 
                         "/browser/navigate", 
                         json={"url": test_url})
        
        # 3. Take a screenshot
        screenshot = await test_feature(session, "Take Screenshot", "GET", "/browser/screenshot")
        save_screenshot(screenshot, "test_navigation.png")
        
        # 4. Fill out a form
        form_data = [
            ("input[name='custname']", "Test User"),
            ("input[name='custtel']", "123-456-7890"),
            ("input[value='small']", ""),  # Click radio button
            ("select[name='topping']", "cheese"),
            ("textarea[name='comments']", "This is a test comment")
        ]
        
        for selector, value in form_data:
            if value:
                await test_feature(session, f"Type in {selector}", "POST",
                                 "/browser/type",
                                 json={"selector": selector, "text": value})
            else:
                await test_feature(session, f"Click {selector}", "POST",
                                 "/browser/click",
                                 json={"selector": selector})
        
        # 5. Take another screenshot after form fill
        screenshot = await test_feature(session, "Take Form Screenshot", "GET", "/browser/screenshot")
        save_screenshot(screenshot, "test_form_filled.png")
        
        # 6. Get cookies
        await test_feature(session, "Get Cookies", "GET", "/browser/cookies")
        
        # 7. Navigate to a different page
        await test_feature(session, "Navigate to Google", "POST",
                         "/browser/navigate",
                         json={"url": "https://www.google.com"})
        
        # 8. Final screenshot
        screenshot = await test_feature(session, "Final Screenshot", "GET", "/browser/screenshot")
        save_screenshot(screenshot, "test_final.png")
        
        # 9. Close the browser
        await test_feature(session, "Close Browser", "POST", "/browser/close")

if __name__ == "__main__":
    print("=== Starting Browser Agent Tests ===")
    asyncio.run(run_browser_tests())
    print("\n=== Tests Completed ===")
