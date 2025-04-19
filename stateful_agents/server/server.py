from typing import Dict, List, Optional, Any, Union
import time
import uuid
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .database import Database
from ..agent import Agent
from ..memory import MemoryManager
from ..tools import ToolManager


class CreateAgentRequest(BaseModel):
    """Request model for creating an agent."""
    
    name: str
    model: str
    persona: Optional[str] = ""
    system_prompt: Optional[str] = ""
    context_window_limit: Optional[int] = 4096


class MessageRequest(BaseModel):
    """Request model for sending a message to an agent."""
    
    content: str
    sender_id: Optional[str] = "user"
    metadata: Optional[Dict[str, Any]] = None


class Server:
    """Server for managing stateful agents."""
    
    def __init__(self, db_path: str = "agents.db"):
        """Initialize the server.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.database = Database(db_path)
        self.agents: Dict[str, Agent] = {}
        self.app = FastAPI(title="Stateful Agent Server")
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up API routes."""
        @self.app.post("/agents")
        async def create_agent(request: CreateAgentRequest):
            """Create a new agent."""
            agent_id = f"agent-{uuid.uuid4().hex[:8]}"
            
            # Save agent to database
            self.database.save_agent({
                "id": agent_id,
                "name": request.name,
                "model": request.model,
                "persona": request.persona,
                "system_prompt": request.system_prompt,
                "context_window_limit": request.context_window_limit
            })
            
            # Initialize agent instance
            agent = self._load_agent(agent_id)
            
            return {
                "id": agent_id,
                "name": agent.name,
                "model": agent.model
            }
        
        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent details."""
            agent = self._get_agent(agent_id)
            
            return {
                "id": agent.id,
                "name": agent.name,
                "model": agent.model,
                "persona": agent.persona,
                "context_window_limit": agent.context_window_limit,
                "active": agent.active
            }
        
        @self.app.post("/agents/{agent_id}/messages")
        async def send_message(agent_id: str, request: MessageRequest):
            """Send a message to an agent."""
            agent = self._get_agent(agent_id)
            
            # Process message
            response = agent.send_message(
                message=request.content,
                user_id=request.sender_id,
                metadata=request.metadata
            )
            
            return {
                "response": response,
                "agent_id": agent_id,
                "timestamp": int(time.time())
            }
        
        @self.app.get("/agents/{agent_id}/memory/core")
        async def get_core_memory(agent_id: str):
            """Get all core memory for an agent."""
            agent = self._get_agent(agent_id)
            
            return agent.memory_manager.get_all_core_memory()
        
        @self.app.post("/agents/{agent_id}/memory/core/{key}")
        async def update_core_memory(agent_id: str, key: str, value: str):
            """Update a core memory block."""
            agent = self._get_agent(agent_id)
            
            agent.memory_manager.add_core_memory(key, value)
            
            return {"status": "success"}
        
        @self.app.get("/agents/{agent_id}/memory/recall")
        async def get_recent_messages(agent_id: str, limit: int = 10):
            """Get recent messages for an agent."""
            self._get_agent(agent_id)  # Just to verify agent exists
            
            messages = self.database.get_recent_messages(agent_id, limit)
            
            return messages
        
        @self.app.post("/agents/{agent_id}/memory/archival")
        async def add_to_archival(agent_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
            """Add content to archival memory."""
            agent = self._get_agent(agent_id)
            
            memory_id = agent.memory_manager.add_to_archival(content, metadata)
            
            return {"memory_id": memory_id}
        
        @self.app.get("/agents/{agent_id}/memory/archival/search")
        async def search_archival(agent_id: str, query: str, limit: int = 5):
            """Search archival memory."""
            agent = self._get_agent(agent_id)
            
            results = agent.memory_manager.search_archival(query, limit)
            
            return results
    
    def _get_agent(self, agent_id: str) -> Agent:
        """Get an agent instance, loading it if necessary.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The agent instance
            
        Raises:
            HTTPException: If the agent does not exist
        """
        if agent_id not in self.agents:
            # Try to load from database
            agent_data = self.database.get_agent(agent_id)
            if not agent_data:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            self._load_agent(agent_id)
        
        return self.agents[agent_id]
    
    def _load_agent(self, agent_id: str) -> Agent:
        """Load an agent from the database.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The loaded agent instance
        """
        # Get agent data from database
        agent_data = self.database.get_agent(agent_id)
        if not agent_data:
            raise ValueError(f"Agent {agent_id} not found in database")
        
        # Create memory manager
        memory_manager = MemoryManager()
        
        # Load core memory blocks
        memory_blocks = self.database.get_memory_blocks(agent_id)
        for key, value in memory_blocks.items():
            memory_manager.add_core_memory(key, value)
        
        # Create agent instance
        agent = Agent(
            id=agent_id,
            name=agent_data["name"],
            model=agent_data["model"],
            persona=agent_data["persona"],
            system_prompt=agent_data["system_prompt"],
            memory_manager=memory_manager,
            context_window_limit=agent_data["context_window_limit"],
            active=bool(agent_data["active"])
        )
        
        # Cache agent
        self.agents[agent_id] = agent
        
        return agent
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
    
    def run_in_thread(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server in a background thread.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            
        Returns:
            The server thread
        """
        server_thread = threading.Thread(target=self.run, args=(host, port))
        server_thread.daemon = True
        server_thread.start()
        
        return server_thread
    
    def close(self):
        """Close the server and database connection."""
        self.database.close()