"""
Test script for Kimi K2 LLM integration.

This script tests the integration with Kimi K2 LLM using the llm_utils module.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from llm_utils import LLMConfig, get_llm, LLMProvider

# Load environment variables from .env file
load_dotenv()

async def test_kimi_integration():
    """Test Kimi K2 LLM integration with detailed error handling."""
    print("=== Testing Kimi K2 LLM Integration ===\n")
    
    # Check if API key is set
    kimi_api_key = os.getenv("KIMI_API_KEY")
    if not kimi_api_key:
        print("Error: KIMI_API_KEY environment variable not set.")
        print("Please set the KIMI_API_KEY environment variable to your Kimi K2 API key.")
        return False
    
    # Validate API key format
    if not kimi_api_key.startswith('sk-'):
        print("Warning: The API key format doesn't match the expected format (should start with 'sk-').")
        print("Please verify that you're using the correct API key for Kimi K2.")
    
    # Known Kimi K2 models to try
    kimi_models = [
        "moonshot-v1-8k"  # Primary model name for Kimi K2
    ]
    
    for model_name in kimi_models:
        try:
            print(f"\n{'='*80}")
            print(f"Attempting to use model: {model_name}")
            print("-" * 80)
            
            # Configure Kimi K2 LLM
            print("\nConfiguring Kimi K2 LLM...")
            config = LLMConfig(
                provider=LLMProvider.KIMI,
                api_key=kimi_api_key,
                model_name=model_name,
                temperature=0.7,
                max_tokens=100
            )
            
            # Get the LLM instance
            print("Initializing LLM...")
            llm = get_llm(config)
            
            # Test the LLM with a simple prompt
            print("\nSending test prompt to Kimi K2...")
            prompt = "Tell me a short, interesting fact about artificial intelligence."
            print(f"Prompt: {prompt}")
            
            # Try to make a direct API call first to validate the key and model
            try:
                import requests
                
                headers = {
                    "Authorization": f"Bearer {kimi_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Test the models endpoint
                print("\nTesting API access with direct call to /models...")
                models_response = requests.get(
                    "https://api.moonshot.cn/v1/models",
                    headers=headers
                )
                
                print(f"Status code: {models_response.status_code}")
                
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    print("\nAvailable models:")
                    print("-" * 50)
                    if 'data' in models_data and models_data['data']:
                        for model in models_data['data']:
                            print(f"- {model.get('id', 'N/A')} (owned_by: {model.get('owned_by', 'N/A')})")
                    else:
                        print("No models found in the response.")
                    print("-" * 50)
                else:
                    print(f"Error response: {models_response.text}")
                
                # Test the completions endpoint
                print("\nTesting completions endpoint...")
                completion_data = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100
                }
                
                completion_response = requests.post(
                    "https://api.moonshot.cn/v1/chat/completions",
                    headers=headers,
                    json=completion_data
                )
                
                print(f"Completion status code: {completion_response.status_code}")
                if completion_response.status_code != 200:
                    print(f"Error response: {completion_response.text}")
                else:
                    result = completion_response.json()
                    print("\nResponse from Kimi K2:")
                    print("-" * 50)
                    if 'choices' in result and result['choices']:
                        print(result['choices'][0]['message']['content'])
                    else:
                        print("No choices in response:", result)
                    print("-" * 50)
                    return True
                
            except Exception as e:
                print(f"\n❌ Error making direct API call: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # If we get here, the direct API call failed, try with LangChain
            print("\nDirect API call failed, trying with LangChain...")
            try:
                response = llm.invoke(prompt)
                print("\nResponse from Kimi K2 (via LangChain):")
                print("-" * 50)
                print(response.content)
                print("-" * 50)
                return True
            except Exception as e:
                print(f"\n❌ Error with LangChain integration: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # If we get a 404, the model name is likely incorrect
                if "404" in str(e) or "not found" in str(e).lower():
                    print(f"\n⚠️ Model '{model_name}' not found. Trying next model...")
                    continue
                else:
                    print(f"\n❌ Failed to use model: {model_name}")
                    break
                    
        except Exception as e:
            print(f"\n❌ Unexpected error with model {model_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n❌ All model attempts failed. Please check your API key and model names.")
    print("If you believe this is an error, please check:")
    print("1. Your API key is correct and has the necessary permissions")
    print("2. The model names are correct for your account")
    print("3. Your account has access to the Kimi K2 API")
    return False

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_kimi_integration())
