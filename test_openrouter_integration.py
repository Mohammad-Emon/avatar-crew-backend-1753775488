#!/usr/bin/env python3
"""
Test script for OpenRouter integration with Kimi K2 model.
"""
import os
import asyncio
from dotenv import load_dotenv
from llm_utils import LLMConfig, get_llm

# Load environment variables from .env file
load_dotenv()

async def test_openrouter_integration():
    """Test OpenRouter integration with Kimi K2 model."""
    print("=== Testing OpenRouter Integration with Kimi K2 ===\n")
    
    # Get configuration from environment
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL")
    model_name = os.getenv("KIMI_MODEL")
    
    if not api_key:
        print("Error: KIMI_API_KEY environment variable not set.")
        return False
    
    try:
        # Configure the LLM
        print("Configuring LLM with OpenRouter...")
        config = LLMConfig(
            provider="kimi",
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=0.7,
            max_tokens=500
        )
        
        # Get the LLM instance
        llm = get_llm(config)
        
        # Test with a simple prompt
        prompt = "Tell me a short, interesting fact about artificial intelligence."
        print(f"\nSending test prompt to {model_name}:")
        print(f"Prompt: {prompt}")
        
        # Make the API call
        response = llm.invoke(prompt)
        
        # Print the response
        print("\nResponse from Kimi K2 via OpenRouter:")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        
        print("\n✅ OpenRouter integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing OpenRouter integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_openrouter_integration())
