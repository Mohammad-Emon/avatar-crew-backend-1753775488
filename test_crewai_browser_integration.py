"""Integration test for CrewAI and browser agent."""

import asyncio
import json
from crew_workflow import run_avatar_workflow

async def test_crewai_browser_integration():
    """Test the integration between CrewAI and the browser agent."""
    print("=== Testing CrewAI + Browser Agent Integration ===\n")
    
    # Test 1: Simple web search and information extraction
    print("\n--- Test 1: Web Search and Information Extraction ---")
    prompt = """
    Search for the latest news about artificial intelligence on TechCrunch.
    Find the title and summary of the most recent article.
    """
    
    print(f"Prompt: {prompt}")
    result = await run_avatar_workflow(prompt)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    # Test 2: Form interaction
    print("\n--- Test 2: Form Interaction ---")
    prompt = """
    Go to httpbin.org/forms/post and fill out the form with the following information:
    - Customer name: Test User
    - Telephone: 123-456-7890
    - Email: test@example.com
    - Select the small pizza option
    - Add extra cheese
    - Add a delivery instruction: "Please ring the doorbell"
    """
    
    print(f"Prompt: {prompt}")
    result = await run_avatar_workflow(prompt)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_crewai_browser_integration())
