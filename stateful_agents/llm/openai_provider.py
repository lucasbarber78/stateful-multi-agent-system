from typing import Dict, List, Optional, Any, Union
import json
import tiktoken
import openai

from .provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """LLM provider for OpenAI models (GPT-4, GPT-3.5, etc.)."""
    
    MODEL_CONTEXT_LIMITS = {
        "gpt-4-turbo": 128000,
        "gpt-4-0125-preview": 128000,
        "gpt-4-1106-preview": 128000,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-16k": 16385
    }
    
    def __init__(self, api_key: Optional[str] = None, organization: Optional[str] = None):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (uses environment variable if not provided)
            organization: OpenAI organization ID (optional)
        """
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if organization:
            client_kwargs["organization"] = organization
        
        self.client = openai.OpenAI(**client_kwargs)
        self.encoders = {}
    
    def _get_encoder(self, model: str):
        """Get the appropriate token encoder for a model."""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base for new models not yet in tiktoken
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        
        return self.encoders[model]
    
    def count_tokens(self, text: str, model: str = "gpt-4-turbo") -> int:
        """Count the number of tokens in a text string."""
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))
    
    def count_message_tokens(self, messages: List[Dict[str, str]], system_prompt: str, model: str = "gpt-4-turbo") -> int:
        """Count the number of tokens in a message list plus system prompt."""
        # Create a copy of messages with system prompt prepended
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages
        
        # Count tokens according to OpenAI's method
        encoder = self._get_encoder(model)
        num_tokens = 0
        
        # Add tokens for message formatting (varies by model)
        num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>
        
        for message in full_messages:
            num_tokens += 4  # Every message follows <|start|>{role}<|message|>{content}<|end|>
            for key, value in message.items():
                num_tokens += len(encoder.encode(value))
        
        return num_tokens
    
    def get_max_context_size(self, model: str) -> int:
        """Get the maximum context size for a given model."""
        if model in self.MODEL_CONTEXT_LIMITS:
            return self.MODEL_CONTEXT_LIMITS[model]
        
        # Default context size for unknown models
        return 4096
    
    def generate(self, 
                messages: List[Dict[str, str]], 
                system_prompt: str, 
                tools: Optional[List[Dict[str, Any]]] = None, 
                max_tokens: Optional[int] = None,
                temperature: float = 0.7,
                model: str = "gpt-4-turbo") -> Dict[str, Any]:
        """Generate a response from the OpenAI API."""
        # Prepare the complete messages list with system prompt
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages
        
        # Check if messages fit in context window
        if not self.fits_in_context(messages, system_prompt, model):
            overflow = self.get_context_overflow(messages, system_prompt, model)
            raise ValueError(f"Messages exceed context window by {overflow} tokens. Reduce context or summarize.")
        
        # Prepare API call parameters
        params = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if tools:
            params["tools"] = tools
        
        # Make the API call
        try:
            response = self.client.chat.completions.create(**params)
            
            # Process the response
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
            # Handle tool calls if present
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                tool_calls = []
                for tool_call in response.choices[0].message.tool_calls:
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {"raw_arguments": tool_call.function.arguments}
                        
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": args
                        }
                    })
                
                result["tool_calls"] = tool_calls
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"Error calling OpenAI API: {error_msg}")
