from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from .memory import MemoryManager
from .tools import ToolManager
from .communication import CommunicationManager, Message


class Agent(BaseModel):
    """A stateful agent with memory management capabilities."""
    
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Name of the agent")
    model: str = Field(..., description="LLM model to use")
    persona: str = Field("", description="Agent persona/role description")
    system_prompt: str = Field("", description="Base system prompt for the agent")
    memory_manager: MemoryManager = Field(..., description="Memory manager for the agent")
    tool_manager: Optional[ToolManager] = Field(None, description="Tool manager for the agent")
    communication_manager: Optional[CommunicationManager] = Field(None, description="Communication manager for agent")
    context_window_limit: int = Field(4096, description="Maximum context window size in tokens")
    active: bool = Field(True, description="Whether the agent is active")
    reasoning_enabled: bool = Field(True, description="Whether to use explicit reasoning steps")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize the agent with the given parameters."""
        super().__init__(**data)
        
        # Initialize managers if not provided
        if self.tool_manager is None:
            self.tool_manager = ToolManager(agent_id=self.id)
            
        if self.communication_manager is None:
            self.communication_manager = CommunicationManager(agent_id=self.id)
            
        # Set up default memory blocks if not already present
        if not self.memory_manager.has_core_memory("persona"):
            self.memory_manager.add_core_memory("persona", self.persona)
            
        # Build the complete system prompt including memory management instructions
        self._build_system_prompt()
    
    def _build_system_prompt(self) -> None:
        """Build the complete system prompt including memory instructions."""
        base_prompt = self.system_prompt or self._get_default_system_prompt()
        
        # Add memory management instructions
        memory_instructions = self._get_memory_instructions()
        
        # Add tool usage instructions if tools are available
        tool_instructions = ""
        if self.tool_manager and self.tool_manager.tools:
            tool_instructions = self._get_tool_instructions()
        
        # Combine all parts
        self.system_prompt = f"{base_prompt}\n\n{memory_instructions}\n\n{tool_instructions}"
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent."""
        return f"""You are {self.name}, an intelligent assistant. 
        
        {self.persona if self.persona else 'Your goal is to be helpful, harmless, and honest in all interactions.'}
        
        Always think carefully about each request before responding."""
    
    def _get_memory_instructions(self) -> str:
        """Get instructions for memory management."""
        return """# Memory Management
        
        You have access to different types of memory:
        
        1. CORE MEMORY: Critical information that must be remembered throughout all interactions.
        2. RECALL MEMORY: Past conversations that can be searched when needed.
        3. ARCHIVAL MEMORY: Extended knowledge storage that can be queried.
        
        You have tools to manage these memories. Use them when appropriate to store important information or retrieve relevant context.
        """
    
    def _get_tool_instructions(self) -> str:
        """Get instructions for tool usage."""
        tool_descriptions = "\n".join(
            [f"- {tool.name}: {tool.description}" for tool in self.tool_manager.tools]
        )
        
        return f"""# Available Tools
        
        You have access to the following tools:
        
        {tool_descriptions}
        
        To use a tool, you must specify the tool name and parameters in your reasoning.
        """
    
    def send_message(self, message: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a message to the agent and get a response."""
        # Create a message object
        user_message = Message(
            content=message,
            sender_id=user_id or "user",
            receiver_id=self.id,
            metadata=metadata or {}
        )
        
        # Store in recall memory
        self.memory_manager.add_to_recall(user_message)
        
        # Generate context for LLM
        context = self._prepare_context(user_message)
        
        # Call LLM with context
        response = self._call_llm(context)
        
        # Parse response and handle any tool calls
        response = self._process_response(response)
        
        # Store agent response in recall memory
        agent_message = Message(
            content=response,
            sender_id=self.id,
            receiver_id=user_id or "user"
        )
        self.memory_manager.add_to_recall(agent_message)
        
        return response
    
    def _prepare_context(self, message: Message) -> Dict[str, Any]:
        """Prepare the context for the LLM."""
        # This would include:
        # 1. System prompt
        # 2. Core memory blocks
        # 3. Relevant recall memory
        # 4. Tool definitions
        # 5. The current message
        
        # For now, return a placeholder
        return {
            "system_prompt": self.system_prompt,
            "core_memory": self.memory_manager.get_all_core_memory(),
            "recall_memory": self.memory_manager.get_relevant_recall(message.content),
            "tools": self.tool_manager.get_tool_schemas() if self.tool_manager else [],
            "current_message": message.dict()
        }
    
    def _call_llm(self, context: Dict[str, Any]) -> str:
        """Call the LLM with the given context."""
        # This would make the actual API call to the LLM provider
        # For now, return a placeholder response
        return "This is a placeholder response. Actual LLM integration will be implemented later."
    
    def _process_response(self, response: str) -> str:
        """Process the LLM response, handling any tool calls."""
        # This would parse the response, execute any tool calls, and potentially continue the LLM conversation
        # For now, return the response as-is
        return response
    
    def save(self) -> None:
        """Save the agent's state to persistence."""
        # This would save the agent's state to the database
        pass
    
    def load(self, agent_id: str) -> None:
        """Load the agent's state from persistence."""
        # This would load the agent's state from the database
        pass
