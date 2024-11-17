import requests
from typing import List, Dict, Any
import os

class OpenRouterAPI:
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:3000"),  # Required by OpenRouter
            "X-Title": os.getenv("X_TITLE", "Integuru Local")  # Required by OpenRouter
        }
        
        response = requests.get(
            f"{self.BASE_URL}/models",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def format_model_info(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format model information for display"""
        formatted_models = []
        for model in models:
            formatted_models.append({
                "id": model.get("id"),
                "name": model.get("name"),
                "context_length": model.get("context_length"),
                "pricing": {
                    "prompt": model.get("pricing", {}).get("prompt"),
                    "completion": model.get("pricing", {}).get("completion")
                }
            })
        return formatted_models
