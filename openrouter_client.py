"""OpenRouter API client with multi-model fallback support."""
import os
import sys
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

# Enable debug logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter API with model fallback support."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter client.
        
        Args:
            api_key: Optional OpenRouter API key. If not provided, will try to load from OPENROUTER_API_KEY env var.
        """
        logger.info("Initializing OpenRouter client...")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        logger.info(f"Using API key: {'*' * 8 + self.api_key[-4:] if self.api_key else 'None'}")
        
        if not self.api_key:
            error_msg = "OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("OpenRouter client initialized successfully")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Default free models to try in order
        self.free_models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-2-9b-it:free"
        ]
    
    def chat(self, message: str, model: str = None, fallbacks: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Chat with fallback support."""
        models = [model] if model else self.free_models
        if fallbacks:
            models.extend(fallbacks)
        
        last_error = None
        
        for model_name in models:
            try:
                logger.info(f"Trying model: {model_name}")
                
                # Prepare extra headers for OpenRouter
                extra_headers = {
                    "HTTP-Referer": kwargs.get("app_url", "https://github.com/yourusername/avatar-crew"),
                    "X-Title": kwargs.get("app_name", "Avatar-Crew")
                }
                
                # Create a new client with the extra headers
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                    default_headers=extra_headers
                )
                
                # Make the API request
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": message}],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 300)
                )
                
                logger.info(f"Successfully got response from {model_name}")
                
                return {
                    "success": True,
                    "content": response.choices[0].message.content,
                    "model_used": model_name,
                    "full_response": response
                }
                
            except RateLimitError as e:
                last_error = f"Rate limit exceeded for {model_name}: {str(e)}"
                logger.warning(last_error)
                continue
                
            except APIConnectionError as e:
                last_error = f"API connection error with {model_name}: {str(e)}"
                logger.error(last_error)
                continue
                
            except APIError as e:
                last_error = f"API error with {model_name}: {str(e)}"
                logger.error(last_error)
                continue
                
            except Exception as e:
                last_error = f"Unexpected error with {model_name}: {str(e)}"
                logger.error(last_error, exc_info=True)
                continue
        
        return {
            "success": False, 
            "error": last_error or "All models failed",
            "models_tried": models
        }
