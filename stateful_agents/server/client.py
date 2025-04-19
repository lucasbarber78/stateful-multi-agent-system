from typing import Dict, List, Optional, Any, Union
import requests


class AgentClient:
    """Client for interacting with the agent server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the agent server
        """
        self.base_url = base_url.rstrip("/")
    
    def create_agent(self, name: str, model: str, persona: str = "", 
                   system_prompt: str = "", context_window_limit: int = 4096) -> Dict[str, Any]:
        """Create a new agent.
        
        Args:
            name: Name of the agent
            model: Model to use
            persona: Agent persona
            system_prompt: System prompt
            context_window_limit: Context window limit in tokens
            
        Returns:
            Dictionary with agent details
        """
        response = requests.post(
            f"{self.base_url}/agents",
            json={
                "name": name,
                "model": model,
                "persona": persona,
                "system_prompt": system_prompt,
                "context_window_limit": context_window_limit
            }
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Dictionary with agent details
        """
        response = requests.get(f"{self.base_url}/agents/{agent_id}")
        
        response.raise_for_status()
        return response.json()
    
    def send_message(self, agent_id: str, content: str, sender_id: str = "user", 
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a message to an agent.
        
        Args:
            agent_id: The agent ID
            content: Message content
            sender_id: ID of the sender
            metadata: Optional metadata
            
        Returns:
            Dictionary with the response
        """
        response = requests.post(
            f"{self.base_url}/agents/{agent_id}/messages",
            json={
                "content": content,
                "sender_id": sender_id,
                "metadata": metadata or {}
            }
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_core_memory(self, agent_id: str) -> Dict[str, str]:
        """Get all core memory for an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Dictionary mapping keys to values
        """
        response = requests.get(f"{self.base_url}/agents/{agent_id}/memory/core")
        
        response.raise_for_status()
        return response.json()
    
    def update_core_memory(self, agent_id: str, key: str, value: str) -> Dict[str, Any]:
        """Update a core memory block.
        
        Args:
            agent_id: The agent ID
            key: Memory block key
            value: Memory block value
            
        Returns:
            Dictionary with status
        """
        response = requests.post(
            f"{self.base_url}/agents/{agent_id}/memory/core/{key}",
            data=value
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_recent_messages(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for an agent.
        
        Args:
            agent_id: The agent ID
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        response = requests.get(
            f"{self.base_url}/agents/{agent_id}/memory/recall",
            params={"limit": limit}
        )
        
        response.raise_for_status()
        return response.json()
    
    def add_to_archival(self, agent_id: str, content: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add content to archival memory.
        
        Args:
            agent_id: The agent ID
            content: Memory content
            metadata: Optional metadata
            
        Returns:
            Dictionary with memory ID
        """
        response = requests.post(
            f"{self.base_url}/agents/{agent_id}/memory/archival",
            params={"content": content},
            json=metadata or {}
        )
        
        response.raise_for_status()
        return response.json()
    
    def search_archival(self, agent_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search archival memory.
        
        Args:
            agent_id: The agent ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of memory items
        """
        response = requests.get(
            f"{self.base_url}/agents/{agent_id}/memory/archival/search",
            params={
                "query": query,
                "limit": limit
            }
        )
        
        response.raise_for_status()
        return response.json()