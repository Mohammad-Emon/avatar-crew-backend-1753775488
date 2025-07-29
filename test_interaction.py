"""Test script for browser interaction functionality."""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_interaction():
    """Test browser interaction with a simple page."""
    async with aiohttp.ClientSession() as session:
        print("1. Starting browser...")
        async with session.post(f"{BASE_URL}/browser/start") as resp:
            result = await resp.json()
            print("   Result:", result)
        
        # Use a simple test page
        test_url = "https://httpbin.org/forms/post"
        print(f"\n2. Navigating to {test_url}...")
        async with session.post(
            f"{BASE_URL}/browser/navigate",
            json={"url": test_url}
        ) as resp:
            result = await resp.json()
            print("   Result:", json.dumps(result, indent=2))
        
        # Try to type in a form field
        print("\n3. Typing in form field...")
        async with session.post(
            f"{BASE_URL}/browser/type",
            json={"selector": "input[name='custname']", "text": "Test User"}
        ) as resp:
            result = await resp.json()
            print("   Result:", result)
        
        # Take a screenshot
        print("\n4. Taking screenshot...")
        async with session.get(f"{BASE_URL}/browser/screenshot") as resp:
            result = await resp.json()
            if "screenshot" in result:
                with open("interaction_test.png", "wb") as f:
                    f.write(result["screenshot"].encode('latin1'))
                print("   Screenshot saved to interaction_test.png")
            else:
                print("   Error:", result.get("error", "Unknown error"))
        
        print("\n5. Closing browser...")
        async with session.post(f"{BASE_URL}/browser/close") as resp:
            result = await resp.json()
            print("   Result:", result)

if __name__ == "__main__":
    print("=== Browser Interaction Test ===")
    asyncio.run(test_interaction())
