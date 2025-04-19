from typing import Dict, List, Optional, Any
import time
from pydantic import BaseModel, Field


class RecallMemory(BaseModel):
    """Recall memory stores conversation history."""
    
    messages: List[Any] = Field(default_factory=list)
    max_messages: int = Field(1000, description="Maximum number of messages to store")
    
    def add(self, message: Any) -> None:
        """Add a message to recall memory."""
        self.messages.append(message)
        
        # Trim if exceeds maximum
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def search(self, query: str, limit: int = 5) -> List[Any]:
        """Search recall memory for relevant messages."""
        # For now, implement a simple keyword search
        # This would be replaced with a more sophisticated semantic search later
        results = []
        query = query.lower()
        
        for message in reversed(self.messages):  # Most recent first
            content = message.content if hasattr(message, "content") else str(message)
            if query in content.lower():
                results.append(message)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_recent(self, limit: int = 10) -> List[Any]:
        """Get the most recent messages."""
        return self.messages[-limit:] if self.messages else []
    
    def get_by_range(self, start: int, end: Optional[int] = None) -> List[Any]:
        """Get messages by range."""
        if end is None:
            return self.messages[start:]
        return self.messages[start:end]
    
    def count(self) -> int:
        """Get the number of messages."""
        return len(self.messages)
    
    def total_size(self) -> int:
        """Get an approximate total size of all messages."""
        return sum(len(msg.content) if hasattr(msg, "content") else len(str(msg)) for msg in self.messages)
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
