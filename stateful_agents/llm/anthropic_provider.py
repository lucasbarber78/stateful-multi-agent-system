from typing import Dict, List, Optional, Any, Union
import json
import anthropic

from .provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """LLM provider for Anthropic Claude models."""
    
    MODEL_CONTEXT_LIMITS = {
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-2.1": 200000,
        "claude-2.0": 100000,
        "claude-instant-1.2": 100000
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key (uses environment variable if not provided)
        """
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        
        self.client = anthropic.Anthropic(**client_kwargs)
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return self.client.count_tokens(text)
    
    def count_message_tokens(self, messages: List[Dict[str, str]], system_prompt: str) -> int:
        """Count the number of tokens in a message list plus system prompt."""
        # Convert to Anthropic message format
        anthropic_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            anthropic_messages.append({"role": role, "content": msg["content"]})
        
        # Calculate tokens using Anthropic's helper
        return self.client.count_tokens(anthropic_messages)
    
    def get_max_context_size(self, model: str) -> int:
        """Get the maximum context size for a given model."""
        if model in self.MODEL_CONTEXT_LIMITS:
            return self.MODEL_CONTEXT_LIMITS[model]
        
        # Default context size for unknown models (Claude models have large context)
        return 100000
    
    def generate(self, 
                messages: List[Dict[str, str]], 
                system_prompt: str, 
                tools: Optional[List[Dict[str, Any]]] = None, 
                max_tokens: Optional[int] = None,
                temperature: float = 0.7,
                model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
        """Generate a response from the Anthropic API."""
        # Convert to Anthropic message format
        anthropic_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            anthropic_messages.append({"role": role, "content": msg["content"]})
        
        # Check if messages fit in context window
        if not self.fits_in_context(messages, system_prompt, model):
            overflow = self.get_context_overflow(messages, system_prompt, model)
            raise ValueError(f"Messages exceed context window by {overflow} tokens. Reduce context or summarize.")
        
        # Prepare API call parameters
        params = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if tools:
            params["tools"] = tools
        
        # Make the API call
        try:
            response = self.client.messages.create(**params)
            
            # Process the response
            result = {
                "content": response.content[0].text,
                "model": response.model,
                "stop_reason": response.stop_reason,
            }
            
            # Handle tool calls if present
            if hasattr(response, "tool_use") and response.tool_use:
                tool_calls = []
                for tool_use in response.tool_use:
                    tool_calls.append({
                        "id": tool_use.id if hasattr(tool_use, "id") else "tool-call",
                        "type": "function",
                        "function": {
                            "name": tool_use.name,
                            "arguments": tool_use.input
                        }
                    })
                
                result["tool_calls"] = tool_calls
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"Error calling Anthropic API: {error_msg}")
    
    def generate_with_structured_response(self,
                                         messages: List[Dict[str, str]],
                                         system_prompt: str,
                                         response_schema: Dict[str, Any],
                                         model: str = "claude-3-sonnet-20240229",
                                         temperature: float = 0.7) -> Dict[str, Any]:
        """Generate a response that conforms to a specific JSON schema."""
        # Convert to Anthropic message format
        anthropic_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            anthropic_messages.append({"role": role, "content": msg["content"]})
        
        # Prepare API call parameters
        params = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object", "schema": response_schema}
        }
        
        try:
            response = self.client.messages.create(**params)
            
            # Parse JSON response
            content = response.content[0].text
            parsed_response = json.loads(content)
            
            result = {
                "content": parsed_response,
                "model": response.model,
                "stop_reason": response.stop_reason,
                "raw_content": content
            }
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"Error calling Anthropic API with structured response: {error_msg}")
