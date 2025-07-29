"""
Test script for the CrewAI workflow with browser automation.

This script tests the integration between CrewAI and the browser automation agent.
It includes a mock LLM for testing without requiring API keys.
"""

import asyncio
import json
import os
import sys
import logging
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import crew_workflow
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the workflow function
from backend.crew_workflow import run_avatar_workflow

class MockLLM:
    """Mock LLM for testing without requiring API keys."""
    
    def __init__(self, *args, **kwargs):
        self.model_name = "mock-llm"
        self.temperature = 0.7
        
    def __call__(self, prompt, **kwargs):
        """Return a mock response based on the prompt."""
        logger.info(f"Mock LLM received prompt: {prompt[:200]}...")
        
        # Return different responses based on the prompt
        if "TechCrunch" in prompt:
            return """
            Here's the latest AI news from TechCrunch:
            
            Title: "New Breakthrough in AI Research Shows Promise for Healthcare"
            
            Summary: Researchers have developed a new AI model that can analyze medical 
            images with unprecedented accuracy, potentially revolutionizing diagnostics. 
            The technology is still in early stages but shows great promise for 
            improving patient outcomes.
            """
        else:
            return "This is a mock response from the test LLM. The actual workflow would use a real LLM in production."

def setup_mock_llm():
    """Set up a mock LLM for testing."""
    # This function can be used to patch LLM imports in the crew_workflow module
    import sys
    import types
    
    # Create a mock module for langchain
    mock_langchain = types.ModuleType('langchain')
    mock_langchain.llms = types.ModuleType('langchain.llms')
    mock_langchain.chat_models = types.ModuleType('langchain.chat_models')
    
    # Add our mock LLM
    mock_langchain.llms.OpenAI = MockLLM
    mock_langchain.chat_models.ChatOpenAI = MockLLM
    
    # Add the mock module to sys.modules
    sys.modules['langchain'] = mock_langchain
    sys.modules['langchain.llms'] = mock_langchain.llms
    sys.modules['langchain.chat_models'] = mock_langchain.chat_models

def test_crewai_workflow():
    """Test the CrewAI workflow with browser automation."""
    print("=== Testing CrewAI Workflow with Browser Automation ===\n")
    
    # Set up mock LLM
    setup_mock_llm()
    
    # Test 1: Simple web search and information extraction
    print("\n--- Test 1: Web Search and Information Extraction ---")
    prompt = """
    Search for the latest news about artificial intelligence on TechCrunch.
    Find the title and summary of the most recent article.
    """
    
    print(f"Prompt: {prompt}")
    
    try:
        # Run the workflow (which is already synchronous)
        print("\nStarting workflow execution...")
        result = run_avatar_workflow(prompt)
        
        print("\nWorkflow completed successfully!")
        print("\nResult:")
        print(json.dumps(result, indent=2))
        
        # Save the result to a file for reference
        with open("test_workflow_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\nFull result saved to: test_workflow_result.json")
        
        return 0
        
    except Exception as e:
        print(f"\nError during workflow execution: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main entry point for the test script."""
    # Use asyncio's event loop policy to avoid event loop issues
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the test
    return test_crewai_workflow()

if __name__ == "__main__":
    sys.exit(main())
