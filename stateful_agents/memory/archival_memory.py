from typing import Dict, List, Optional, Any
import time
from pydantic import BaseModel, Field


class ArchivalMemoryItem(BaseModel):
    """A single item in archival memory."""
    
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class ArchivalMemory(BaseModel):
    """Archival memory stores information outside the context window."""
    
    items: List[ArchivalMemoryItem] = Field(default_factory=list)
    vector_store_initialized: bool = Field(False)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add content to archival memory."""
        # Generate a simple ID for now
        item_id = f"mem_{int(time.time())}_{len(self.items)}"
        
        # Create memory item
        item = ArchivalMemoryItem(
            id=item_id,
            content=content,
            metadata=metadata or {}
        )
        
        # Store the item
        self.items.append(item)
        
        # TODO: Add to vector store once implemented
        
        return item_id
    
    def get(self, item_id: str) -> Optional[ArchivalMemoryItem]:
        """Get a memory item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search archival memory."""
        # TODO: Implement vector search
        # For now, return simple keyword matching
        results = []
        query = query.lower()
        
        for item in self.items:
            if query in item.content.lower():
                results.append({
                    "id": item.id,
                    "content": item.content,
                    "metadata": item.metadata,
                    "timestamp": item.timestamp
                })
                if len(results) >= limit:
                    break
        
        return results
    
    def delete(self, item_id: str) -> bool:
        """Delete a memory item."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                # TODO: Remove from vector store once implemented
                return True
        return False
    
    def count(self) -> int:
        """Get the number of memory items."""
        return len(self.items)
    
    def total_size(self) -> int:
        """Get the total size of all memory items in characters."""
        return sum(len(item.content) for item in self.items)
    
    def clear(self) -> None:
        """Clear all memory items."""
        self.items.clear()
        # TODO: Clear vector store once implemented
