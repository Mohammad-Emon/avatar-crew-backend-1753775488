"""Simplified browser test script to debug the browser automation."""

import asyncio
import aiohttp
import base64
import json

BASE_URL = "http://localhost:8000"

async def test_simple_navigation():
    """Test basic browser navigation and screenshot."""
    async with aiohttp.ClientSession() as session:
        # 1. Start the browser
        print("1. Starting browser...")
        async with session.post(f"{BASE_URL}/browser/start") as resp:
            result = await resp.json()
            print("   Result:", result)
        
        # 2. Navigate to example.com
        print("\n2. Navigating to example.com...")
        async with session.post(
            f"{BASE_URL}/browser/navigate",
            json={"url": "https://example.com"}
        ) as resp:
            result = await resp.json()
            print("   Result:", json.dumps(result, indent=2))
        
        # 3. Take a screenshot
        print("\n3. Taking screenshot...")
        async with session.get(f"{BASE_URL}/browser/screenshot") as resp:
            result = await resp.json()
            if "screenshot" in result:
                with open("simple_test_screenshot.png", "wb") as f:
                    f.write(base64.b64decode(result["screenshot"]))
                print("   Screenshot saved to simple_test_screenshot.png")
            else:
                print("   Error:", result.get("error", "Unknown error"))
        
        # 4. Close the browser
        print("\n4. Closing browser...")
        async with session.post(f"{BASE_URL}/browser/close") as resp:
            result = await resp.json()
            print("   Result:", result)

if __name__ == "__main__":
    print("=== Simple Browser Test ===")
    asyncio.run(test_simple_navigation())
