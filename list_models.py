"""List available models from OpenRouter API."""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_available_models():
    """List available models from OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json().get('data', [])
            print("\nAvailable Models:")
            print("-" * 50)
            for model in models:
                if model.get('pricing', {}).get('prompt') == "0" and model.get('pricing', {}).get('completion') == "0":
                    print(f"ID: {model['id']}")
                    print(f"Name: {model.get('name', 'N/A')}")
                    print(f"Description: {model.get('description', 'N/A')}")
                    print(f"Context Length: {model.get('context_length', 'N/A')}")
                    print("-" * 50)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Fetching available models from OpenRouter...")
    list_available_models()
