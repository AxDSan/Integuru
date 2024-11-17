from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Set
import json

class LLMSingleton:
    _instance = None
    _default_model = "gpt-4o"  
    _alternate_model = "o1-preview"
    _openrouter_base_url = "https://openrouter.ai/api/v1"
    _valid_urls: Set[str] = set()

    @classmethod
    def set_api_key(cls, api_key: str):
        """Set the OpenRouter API key"""
        os.environ["OPENROUTER_API_KEY"] = api_key
        # Also set OPENAI_API_KEY since langchain-openai still looks for it
        os.environ["OPENAI_API_KEY"] = api_key
        cls._instance = None

    @classmethod
    def set_valid_urls(cls, urls: Set[str]):
        """Set the valid URLs from the HAR file"""
        cls._valid_urls = urls
        print(f"Valid URLs set: {urls}")

    @classmethod
    def _validate_url(cls, url: str) -> str:
        """Validate URL against HAR file and return closest match if not exact"""
        if not cls._valid_urls:
            print("Warning: No valid URLs set. Call set_valid_urls() with HAR file URLs first.")
            return url

        if url in cls._valid_urls:
            return url

        # Try to find the closest matching URL
        for valid_url in cls._valid_urls:
            if url.lower() in valid_url.lower() or valid_url.lower() in url.lower():
                print(f"Found closest matching URL: {valid_url} for {url}")
                return valid_url

        # If no match found, return the first valid URL as fallback
        fallback_url = next(iter(cls._valid_urls)) if cls._valid_urls else url
        print(f"No matching URL found. Using fallback URL: {fallback_url}")
        return fallback_url

    @classmethod
    def _convert_functions_to_tools(cls, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Convert functions format to tools format"""
        if "functions" in kwargs:
            tools = []
            for function in kwargs["functions"]:
                tools.append({
                    "type": "function",
                    "function": function
                })
            kwargs["tools"] = tools
            
            # Convert function_call to tool_choice with proper format
            if "function_call" in kwargs:
                if kwargs["function_call"] == "auto":
                    kwargs["tool_choice"] = {
                        "type": "function"
                    }
                elif kwargs["function_call"] == "none":
                    kwargs["tool_choice"] = "none"
                elif isinstance(kwargs["function_call"], dict) and "name" in kwargs["function_call"]:
                    kwargs["tool_choice"] = {
                        "type": "function",
                        "function": {"name": kwargs["function_call"]["name"]}
                    }
                else:
                    kwargs["tool_choice"] = {
                        "type": "function"
                    }
                del kwargs["function_call"]
            else:
                kwargs["tool_choice"] = {
                    "type": "function"
                }
                
            del kwargs["functions"]
            
        return kwargs

    @classmethod
    def _convert_tool_call_to_function_call(cls, response):
        """Convert tool calls to function calls format in the response"""
        try:
            if hasattr(response, 'generations') and response.generations:
                generation = response.generations[0]
                if hasattr(generation, 'message') and hasattr(generation.message, 'additional_kwargs'):
                    additional_kwargs = generation.message.additional_kwargs
                    
                    if 'tool_calls' in additional_kwargs:
                        tool_calls = additional_kwargs['tool_calls']
                        if tool_calls and len(tool_calls) > 0:
                            tool_call = tool_calls[0]
                            if isinstance(tool_call, dict) and 'function' in tool_call:
                                # Parse arguments and validate URL
                                args = json.loads(tool_call['function'].get('arguments', '{}'))
                                if 'url' in args:
                                    args['url'] = cls._validate_url(args['url'])
                                
                                generation.message.additional_kwargs['function_call'] = {
                                    'name': tool_call['function'].get('name', ''),
                                    'arguments': json.dumps(args)
                                }
                                print(f"Converted tool call to function call: {generation.message.additional_kwargs['function_call']}")
                                return response
                    
                    # If no tool calls found, create a default function call
                    fallback_url = next(iter(cls._valid_urls)) if cls._valid_urls else ''
                    generation.message.additional_kwargs['function_call'] = {
                        'name': 'default_function',
                        'arguments': json.dumps({'url': fallback_url})
                    }
                    print("No tool calls found, created default function call")
            
            return response
        except Exception as e:
            print(f"Error converting tool call to function call: {e}")
            # Ensure we always have a function_call with a valid URL
            if hasattr(response, 'generations') and response.generations:
                generation = response.generations[0]
                if hasattr(generation, 'message'):
                    fallback_url = next(iter(cls._valid_urls)) if cls._valid_urls else ''
                    generation.message.additional_kwargs['function_call'] = {
                        'name': 'default_function',
                        'arguments': json.dumps({'url': fallback_url})
                    }
            return response

    @classmethod
    def get_instance(cls, model: str = None):
        if model is None:
            model = cls._default_model
            
        if cls._instance is None:
            if "OPENROUTER_API_KEY" not in os.environ:
                raise ValueError("OpenRouter API key not set. Call set_api_key() first.")
            
            headers = {
                "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "http://localhost:3000"),
                "X-Title": os.getenv("OPENROUTER_TITLE", "Integuru"),
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"
            }
            
            cls._instance = ChatOpenAI(
                model=model,
                temperature=1,
                base_url=cls._openrouter_base_url,
                default_headers=headers
            )

            original_generate = cls._instance._generate
            def wrapped_generate(*args, **kwargs):
                kwargs = cls._convert_functions_to_tools(kwargs)
                print(f"Converted kwargs: {kwargs}")  # Debug print
                
                response = original_generate(*args, **kwargs)
                if hasattr(response, 'generations') and response.generations:
                    print(f"Original response: {response.generations[0].message.additional_kwargs}")  # Debug print
                
                response = cls._convert_tool_call_to_function_call(response)
                if hasattr(response, 'generations') and response.generations:
                    print(f"Final response: {response.generations[0].message.additional_kwargs}")  # Debug print
                
                return response
                
            cls._instance._generate = wrapped_generate

        return cls._instance
    
    @classmethod
    def set_default_model(cls, model: str):
        """Set the default model to use when no specific model is requested"""
        cls._default_model = model
        cls._instance = None

    @classmethod
    def revert_to_default_model(cls):
        """Set the default model to use when no specific model is requested"""
        print("Reverting to default model: ", cls._default_model, "Performance will be degraded as Integuru is using non O1 model")
        cls._alternate_model = cls._default_model

    @classmethod
    def switch_to_alternate_model(cls):
        """Returns a ChatOpenAI instance configured for o1-miniss"""
        if "OPENROUTER_API_KEY" not in os.environ:
            raise ValueError("OpenRouter API key not set. Call set_api_key() first.")
            
        headers = {
            "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "http://localhost:3000"),
            "X-Title": os.getenv("OPENROUTER_TITLE", "Integuru"),
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"
        }
        
        cls._instance = ChatOpenAI(
            model=cls._alternate_model,
            temperature=1,
            base_url=cls._openrouter_base_url,
            default_headers=headers
        )

        original_generate = cls._instance._generate
        def wrapped_generate(*args, **kwargs):
            kwargs = cls._convert_functions_to_tools(kwargs)
            print(f"Converted kwargs: {kwargs}")  # Debug print
            
            response = original_generate(*args, **kwargs)
            if hasattr(response, 'generations') and response.generations:
                print(f"Original response: {response.generations[0].message.additional_kwargs}")  # Debug print
            
            response = cls._convert_tool_call_to_function_call(response)
            if hasattr(response, 'generations') and response.generations:
                print(f"Final response: {response.generations[0].message.additional_kwargs}")  # Debug print
            
            return response
            
        cls._instance._generate = wrapped_generate

        return cls._instance

llm = LLMSingleton()

