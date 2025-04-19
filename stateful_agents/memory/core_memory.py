from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class CoreMemory(BaseModel):
    """Core memory keeps critical information within the context window."""
    
    blocks: Dict[str, str] = Field(default_factory=dict)
    max_block_size: int = Field(1024, description="Maximum size of a single memory block in characters")
    
    def add_or_update(self, key: str, value: str) -> None:
        """Add or update a memory block."""
        if len(value) > self.max_block_size:
            # Truncate if exceeds maximum size
            value = value[:self.max_block_size]
        
        self.blocks[key] = value
    
    def get(self, key: str) -> Optional[str]:
        """Get a memory block by key."""
        return self.blocks.get(key)
    
    def has(self, key: str) -> bool:
        """Check if a memory block exists."""
        return key in self.blocks
    
    def delete(self, key: str) -> None:
        """Delete a memory block."""
        if key in self.blocks:
            del self.blocks[key]
    
    def get_all(self) -> Dict[str, str]:
        """Get all memory blocks."""
        return self.blocks.copy()
    
    def count(self) -> int:
        """Get the number of memory blocks."""
        return len(self.blocks)
    
    def total_size(self) -> int:
        """Get the total size of all memory blocks in characters."""
        return sum(len(value) for value in self.blocks.values())
    
    def clear(self) -> None:
        """Clear all memory blocks."""
        self.blocks.clear()
