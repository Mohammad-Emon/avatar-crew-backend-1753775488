"""Enhanced browser automation agent using Playwright with better error handling and waiting."""

from typing import Optional, Dict, Any, List, Union
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import base64
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserAgent:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def start(self):
        """Initialize the browser instance."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            return {"status": "Browser started"}
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return {"error": f"Failed to start browser: {str(e)}"}

    async def navigate(self, url: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to a URL with improved error handling and timeout management.
        
        Args:
            url: The URL to navigate to
            timeout: Maximum navigation time in milliseconds
            
        Returns:
            Dict containing navigation results or error information
        """
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            # Ensure URL has a protocol
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
                
            logger.info(f"Navigating to: {url}")
            
            # Set default navigation timeout
            self.page.set_default_navigation_timeout(timeout)
            
            # Try to navigate with networkidle as the primary wait condition
            try:
                response = await self.page.goto(url, wait_until="domcontentloaded")
                
                # Wait for the page to be fully loaded
                await self.page.wait_for_load_state("networkidle", timeout=timeout/2)
                
                # Get the final URL after redirects
                final_url = self.page.url
                title = await self.page.title()
                
                return {
                    "url": final_url,
                    "title": title,
                    "status": response.status if response else 200,
                    "message": f"Successfully navigated to {final_url}"
                }
                
            except PlaywrightTimeoutError as e:
                # If navigation times out, try to get whatever content is available
                logger.warning(f"Navigation to {url} timed out, but continuing with partial load")
                final_url = self.page.url
                title = await self.page.title()
                
                return {
                    "url": final_url,
                    "title": title,
                    "status": 200,  # Assume success if we have content
                    "warning": f"Navigation timed out but continuing with available content: {str(e)}",
                    "message": f"Navigation to {url} timed out, but continuing with available content"
                }
                
        except Exception as e:
            error_msg = f"Navigation to {url} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Try to recover by reloading the page
            try:
                if self.page:
                    await self.page.reload(wait_until="domcontentloaded")
                    return {
                        "url": self.page.url,
                        "title": await self.page.title(),
                        "status": 200,
                        "warning": f"Recovered from navigation error: {str(e)}",
                        "message": "Page recovered after navigation error"
                    }
            except Exception as reload_error:
                logger.error(f"Failed to recover page after navigation error: {str(reload_error)}")
            
            return {
                "error": error_msg,
                "suggestion": "The page may have loaded partially. Try getting content or taking a screenshot."
            }

    async def click(self, selector: str) -> Dict[str, Any]:
        """Click an element matching the selector."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            await self.page.click(selector, timeout=30000)
            return {"status": f"Clicked element: {selector}"}
        except PlaywrightTimeoutError:
            logger.error(f"Click timed out: {selector}")
            return {"error": f"Click timed out: {selector}"}
        except Exception as e:
            logger.error(f"Click failed: {str(e)}")
            return {"error": f"Click failed: {str(e)}"}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text into an input field."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            await self.page.fill(selector, text, timeout=30000)
            return {"status": f"Typed text into: {selector}"}
        except PlaywrightTimeoutError:
            logger.error(f"Type text timed out: {selector}")
            return {"error": f"Type text timed out: {selector}"}
        except Exception as e:
            logger.error(f"Type text failed: {str(e)}")
            return {"error": f"Type text failed: {str(e)}"}

    async def get_content(self) -> Dict[str, str]:
        """Get the current page content with title and main content extraction."""
        if not self.page:
            return {"error": "No active page. Call /browser/start first."}
        
        try:
            # Get the page title
            title = await self.page.title()
            
            # Execute JavaScript to extract the main content
            content = await self.page.evaluate("""() => {
                // Try to get the main content
                let content = '';
                
                // Try common content selectors
                const selectors = [
                    'main',
                    'article',
                    '.main-content',
                    '#content',
                    '.content',
                    'body'
                ];
                
                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        content = element.innerText || '';
                        if (content.trim().length > 0) break;
                    }
                }
                
                // If no content found, fall back to body
                if (!content || content.trim().length === 0) {
                    content = document.body.innerText || '';
                }
                
                // Clean up the content
                content = content
                    .replace(/\\s+/g, ' ')
                    .trim()
                    .substring(0, 10000);  // Limit content length
                    
                return content;
            }""")
            
            return {
                "title": title,
                "content": content,
                "url": self.page.url
            }
            
        except Exception as e:
            logger.error(f"Failed to get page content: {str(e)}")
            return {
                "error": f"Failed to get page content: {str(e)}",
                "title": "",
                "content": "",
                "url": self.page.url if self.page else ""
            }

    async def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            screenshot = await self.page.screenshot(type="png")
            return {
                "screenshot": base64.b64encode(screenshot).decode("utf-8"),
                "type": "image/png"
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return {"error": f"Screenshot failed: {str(e)}"}

    async def close(self) -> Dict[str, Any]:
        """Close the browser instance."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        return {"status": "Browser closed"}

    async def get_cookies(self) -> Dict[str, Any]:
        """Get the current cookies."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            cookies = await self.context.cookies()
            return {"cookies": cookies}
        except Exception as e:
            logger.error(f"Failed to get cookies: {str(e)}")
            return {"error": f"Failed to get cookies: {str(e)}"}

    async def add_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add cookies to the current context."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            await self.context.add_cookies(cookies)
            return {"status": "Cookies added"}
        except Exception as e:
            logger.error(f"Failed to add cookies: {str(e)}")
            return {"error": f"Failed to add cookies: {str(e)}"}

    async def delete_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Delete cookies from the current context."""
        if not self.page:
            return {"error": "Browser not initialized. Call /browser/start first."}
        
        try:
            await self.context.delete_cookies(cookies)
            return {"status": "Cookies deleted"}
        except Exception as e:
            logger.error(f"Failed to delete cookies: {str(e)}")
            return {"error": f"Failed to delete cookies: {str(e)}"}

# Global browser agent instance
browser_agent = BrowserAgent()
