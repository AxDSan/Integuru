from langchain_openai import ChatOpenAI
from .openrouter import OpenRouterAPI
import os

class LLMSingleton:
    _instance = None
    _default_model = "gpt-4"
    _alternate_model = "anthropic/claude-3-sonnet"  # Example OpenRouter model
    _provider = "openai"  # Default provider
    
    @classmethod
    def get_instance(cls, model: str = None):
        if model is None:
            model = cls._default_model
            
        if cls._instance is None:
            if cls._provider == "openai":
                cls._instance = ChatOpenAI(
                    model=model,
                    temperature=1
                )
            else:  # openrouter
                cls._instance = ChatOpenAI(
                    model=model,
                    temperature=1,
                    openai_api_base="https://openrouter.ai/api/v1",
                    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                    headers={
                        "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:3000"),
                        "X-Title": os.getenv("X_TITLE", "Integuru Local")
                    }
                )
        return cls._instance
    
    @classmethod
    def set_provider(cls, provider: str):
        """Set the provider to use (openai or openrouter)"""
        if provider not in ["openai", "openrouter"]:
            raise ValueError("Provider must be either 'openai' or 'openrouter'")
        cls._provider = provider
        cls._instance = None  # Reset instance to force recreation
    
    @classmethod
    def get_available_models(cls):
        """Get available models from current provider"""
        if cls._provider == "openrouter":
            api = OpenRouterAPI()
            return api.get_available_models()
        else:
            # Return default OpenAI models
            return [
                {"id": "gpt-4", "name": "GPT-4"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
            ]

llm = LLMSingleton()

