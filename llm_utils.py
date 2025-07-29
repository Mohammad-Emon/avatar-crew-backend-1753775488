"""
LLM Utilities for the Avatar-Crew project.

This module provides utilities for working with different LLM providers
like OpenAI and Kimi K2.
"""

import os
from typing import Optional, Dict, Any, Union
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    KIMI = "kimi"
    MOCK = "mock"

class LLMConfig:
    """Configuration for LLM providers."""
    
    def __init__(self, provider: Union[LLMProvider, str] = LLMProvider.OPENAI, **kwargs):
        """Initialize LLM configuration.
        
        Args:
            provider: The LLM provider to use (default: OPENAI)
            **kwargs: Provider-specific configuration
                For OpenAI: api_key, model_name, temperature, etc.
                For Kimi: api_key, model_name, temperature, etc.
        """
        if isinstance(provider, str):
            try:
                self.provider = LLMProvider(provider.lower())
            except ValueError:
                logger.warning(f"Unknown provider: {provider}. Defaulting to MOCK.")
                self.provider = LLMProvider.MOCK
        else:
            self.provider = provider
            
        self.config = kwargs
        
        # Set default config based on provider
        if self.provider == LLMProvider.OPENAI:
            self.config.setdefault("model_name", "gpt-3.5-turbo")
            self.config.setdefault("temperature", 0.7)
            if "api_key" not in self.config:
                self.config["api_key"] = os.getenv("OPENAI_API_KEY")
                
        elif self.provider == LLMProvider.KIMI:
            self.config.setdefault("model_name", "k2")
            self.config.setdefault("temperature", 0.7)
            if "api_key" not in self.config:
                self.config["api_key"] = os.getenv("KIMI_API_KEY")
        
        elif self.provider == LLMProvider.MOCK:
            self.config.setdefault("model_name", "mock-llm")
            self.config["temperature"] = 0.7


def get_llm(config: Optional[LLMConfig] = None, **kwargs):
    """Get an LLM instance based on the configuration.
    
    Args:
        config: Optional LLMConfig instance
        **kwargs: Configuration overrides
        
    Returns:
        An LLM instance from the specified provider
    """
    if config is None:
        # Try to create config from environment variables
        provider = os.getenv("LLM_PROVIDER", "openai")
        config = LLMConfig(provider=provider, **kwargs)
    
    # Update config with any provided overrides
    config.config.update(kwargs)
    
    try:
        if config.provider == LLMProvider.OPENAI:
            return _get_openai_llm(config)
        elif config.provider == LLMProvider.KIMI:
            return _get_kimi_llm(config)
        else:
            logger.warning(f"Unknown LLM provider: {config.provider}. Using mock LLM.")
            return _get_mock_llm(config)
            
    except ImportError as e:
        logger.error(f"Failed to initialize {config.provider} LLM: {e}")
        logger.warning("Falling back to mock LLM")
        return _get_mock_llm(config)
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise


def _get_openai_llm(config: LLMConfig):
    """Get an OpenAI LLM instance."""
    try:
        from langchain.chat_models import ChatOpenAI
        
        return ChatOpenAI(
            model_name=config.config["model_name"],
            temperature=config.config["temperature"],
            openai_api_key=config.config["api_key"],
            **{k: v for k, v in config.config.items() 
               if k not in ["model_name", "temperature", "api_key"]}
        )
    except ImportError as e:
        logger.error("OpenAI not installed. Please install it with: pip install openai")
        raise


def _get_kimi_llm(config: LLMConfig):
    """Get a Kimi K2 LLM instance using OpenRouter."""
    try:
        from openai import OpenAI
        from langchain.chat_models import ChatOpenAI
        
        # Get configuration with defaults
        api_key = config.config.get("api_key") or os.getenv("KIMI_API_KEY")
        base_url = config.config.get("base_url") or os.getenv("KIMI_BASE_URL", "https://openrouter.ai/api/v1")
        model_name = config.config.get("model_name") or os.getenv("KIMI_MODEL", "moonshotai/kimi-k2:free")
        
        if not api_key:
            raise ValueError("Kimi K2 API key not provided. Set KIMI_API_KEY in environment or pass api_key in config.")
        
        print(f"Configuring Kimi K2 via OpenRouter:")
        print(f"  - Model: {model_name}")
        print(f"  - Base URL: {base_url}")
        print(f"  - API Key: {api_key[:8]}...{api_key[-4:]}")
        
        # Create a custom client for OpenRouter
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Use the custom client with LangChain's ChatOpenAI
        return ChatOpenAI(
            client=client,
            model=model_name,
            temperature=config.config.get("temperature", 0.7),
            **{k: v for k, v in config.config.items() 
               if k not in ["model_name", "temperature", "api_key", "base_url"]}
        )
    except ImportError as e:
        logger.error("OpenAI package required for Kimi K2 integration. Install with: pip install openai")
        raise


def _get_mock_llm(config: LLMConfig):
    """Get a mock LLM instance for testing."""
    class MockLLM:
        def __init__(self, *args, **kwargs):
            self.model_name = config.config.get("model_name", "mock-llm")
            self.temperature = config.config.get("temperature", 0.7)
            
        def __call__(self, prompt, **kwargs):
            logger.info(f"Mock LLM received prompt: {prompt[:200]}...")
            return "This is a mock response from the test LLM. The actual workflow would use a real LLM in production."
    
    return MockLLM()
