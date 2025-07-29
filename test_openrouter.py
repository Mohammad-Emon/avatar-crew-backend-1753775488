"""Test script for OpenRouter multi-model integration."""
import os
from dotenv import load_dotenv
from openrouter_client import OpenRouterClient

# Load environment variables
load_dotenv()

def test_openrouter():
    """Test the OpenRouter client with multiple models."""
    # Initialize client
    client = OpenRouterClient()
    
    # Test with multiple models and fallbacks
    response = client.chat(
        message="Explain quantum computing in simple terms",
        model="anthropic/claude-2:free",
        fallbacks=["google/gemini-pro:free", "mistral/mistral-7b:free"],
        temperature=0.7,
        max_tokens=300,
        app_url="https://github.com/yourusername/avatar-crew",
        app_name="Avatar-Crew Test"
    )
    
    # Print results
    if response["success"]:
        print(f"✅ Success! Used model: {response['model_used']}")
        print("-" * 50)
        print(response["content"])
        print("-" * 50)
    else:
        print("❌ All models failed:")
        print(response.get("error", "Unknown error"))
    
    # Show available free models
    print("\nAvailable free models:")
    for i, model in enumerate(client.free_models, 1):
        print(f"{i}. {model}")

if __name__ == "__main__":
    test_openrouter()
