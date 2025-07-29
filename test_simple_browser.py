"""Simple test script for browser agent integration."""

import asyncio
from browser_agent import BrowserAgent

async def test_browser_agent():
    """Test the browser agent directly."""
    print("=== Testing Browser Agent ===\n")
    
    browser = BrowserAgent()
    
    try:
        # Start the browser
        print("Starting browser...")
        await browser.start()
        
        # Navigate to a page
        print("\nNavigating to example.com...")
        await browser.navigate("https://example.com")
        
        # Get page content
        print("\nGetting page content...")
        content = await browser.get_content()
        print(f"\nPage title: {content.get('title', 'No title')}")
        print(f"Page content preview: {content.get('content', 'No content')[:200]}...")
        
        # Take a screenshot
        print("\nTaking screenshot...")
        screenshot = await browser.take_screenshot()
        with open("test_simple_screenshot.png", "wb") as f:
            f.write(screenshot['screenshot'].encode('latin1'))
        print("Screenshot saved to test_simple_screenshot.png")
        
        return {"status": "success", "title": content.get('title', 'No title')}
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return {"status": "error", "error": str(e)}
        
    finally:
        print("\nClosing browser...")
        await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_browser_agent())
    print("\nTest result:", result)
