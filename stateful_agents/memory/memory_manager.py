from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from .core_memory import CoreMemory
from .archival_memory import ArchivalMemory
from .recall_memory import RecallMemory


class MemoryManager(BaseModel):
    """Manages different types of memory for an agent."""
    
    core_memory: CoreMemory = Field(default_factory=CoreMemory)
    archival_memory: ArchivalMemory = Field(default_factory=ArchivalMemory)
    recall_memory: RecallMemory = Field(default_factory=RecallMemory)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_core_memory(self, key: str, value: str) -> None:
        """Add or update a core memory block."""
        self.core_memory.add_or_update(key, value)
    
    def get_core_memory(self, key: str) -> Optional[str]:
        """Get a core memory block by key."""
        return self.core_memory.get(key)
    
    def has_core_memory(self, key: str) -> bool:
        """Check if a core memory block exists."""
        return self.core_memory.has(key)
    
    def get_all_core_memory(self) -> Dict[str, str]:
        """Get all core memory blocks."""
        return self.core_memory.get_all()
    
    def add_to_archival(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add content to archival memory."""
        return self.archival_memory.add(content, metadata)
    
    def search_archival(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search archival memory."""
        return self.archival_memory.search(query, limit)
    
    def add_to_recall(self, message: Any) -> None:
        """Add a message to recall memory."""
        self.recall_memory.add(message)
    
    def get_relevant_recall(self, query: str, limit: int = 5) -> List[Any]:
        """Get relevant messages from recall memory."""
        return self.recall_memory.search(query, limit)
    
    def get_recent_recall(self, limit: int = 10) -> List[Any]:
        """Get the most recent messages from recall memory."""
        return self.recall_memory.get_recent(limit)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent's memory."""
        return {
            "core_memory": {
                "count": self.core_memory.count(),
                "total_size": self.core_memory.total_size()
            },
            "archival_memory": {
                "count": self.archival_memory.count(),
                "total_size": self.archival_memory.total_size()
            },
            "recall_memory": {
                "count": self.recall_memory.count(),
                "total_size": self.recall_memory.total_size()
            }
        }
    
    def clear_all(self) -> None:
        """Clear all memory."""
        self.core_memory.clear()
        self.archival_memory.clear()
        self.recall_memory.clear()
