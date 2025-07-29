#!/usr/bin/env python3
"""
Test script for OpenAI integration.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def test_openai_integration():
    """Test OpenAI integration with a simple prompt."""
    print("=== Testing OpenAI Integration ===\n")
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: Please set your OPENAI_API_KEY in the .env file")
        print("Get an API key from: https://platform.openai.com/api-keys")
        return False
    
    try:
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple prompt
        prompt = "Tell me a short, interesting fact about artificial intelligence."
        print(f"Sending test prompt to OpenAI:")
        print(f"Prompt: {prompt}")
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Print the response
        print("\nResponse from OpenAI:")
        print("-" * 50)
        print(response.choices[0].message.content)
        print("-" * 50)
        
        print("\n✅ OpenAI integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing OpenAI integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_openai_integration()
