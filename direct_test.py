"""Direct test of OpenRouter integration."""
import os
import sys
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_openrouter_direct():
    """Test OpenRouter API directly."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error("Error: OPENROUTER_API_KEY not found in environment variables")
        return False
        
    logger.info("Initializing OpenAI client with OpenRouter...")
    
    try:
        logger.info("Sending test request to OpenRouter...")
        
        # Create client with headers
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/yourusername/avatar-crew",
                "X-Title": "Avatar-Crew Test"
            }
        )
        
        # Make the API request with an available model
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            temperature=0.7,
            max_tokens=100
        )
        
        logger.info("Success! Response received:")
        print(f"Model: {response.model}")
        print(f"Content: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("Testing OpenRouter API directly...")
    if test_openrouter_direct():
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed. Check the logs for details.")
        sys.exit(1)
