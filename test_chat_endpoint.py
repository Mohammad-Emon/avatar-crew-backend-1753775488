"""
Test script for the chat endpoint with OpenRouter integration.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chat_endpoint():
    """Test the /chat endpoint with OpenRouter integration."""
    url = "http://localhost:8000/chat"
    
    # Test payload with available free models
    payload = {
        "message": "Explain quantum computing in simple terms",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "fallback_models": [
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-2-9b-it:free"
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        print("Sending request to /chat endpoint...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result["success"]:
            print("✅ Chat successful!")
            print(f"Model used: {result['model_used']}")
            print("-" * 50)
            print(result["content"])
            print("-" * 50)
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    print("Testing OpenRouter chat endpoint...")
    test_chat_endpoint()
