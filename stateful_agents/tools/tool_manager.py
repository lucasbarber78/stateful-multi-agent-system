from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .tool import Tool
from ..memory.core_memory import CoreMemory


class ToolManager(BaseModel):
    """Manages tools for an agent."""
    
    agent_id: str
    tools: List[Tool] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        # Check if a tool with the same name already exists
        for existing_tool in self.tools:
            if existing_tool.name == tool.name:
                # Replace the existing tool
                self.tools.remove(existing_tool)
                break
        
        self.tools.append(tool)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with the given parameters."""
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool {name} not found")
        
        return tool.execute(**kwargs)
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self.tools]
    
    def add_memory_tools(self, core_memory: CoreMemory) -> None:
        """Add default memory management tools."""
        # Core memory tools
        self.register_tool(Tool(
            name="core_memory_add",
            description="Add or update a core memory block",
            parameters={
                "key": {"type": "string", "description": "Key for the memory block"},
                "value": {"type": "string", "description": "Content to store in the memory block"}
            },
            required_params=["key", "value"],
            function=lambda key, value: core_memory.add_or_update(key, value)
        ))
        
        self.register_tool(Tool(
            name="core_memory_get",
            description="Get a core memory block by key",
            parameters={
                "key": {"type": "string", "description": "Key for the memory block to retrieve"}
            },
            required_params=["key"],
            function=lambda key: core_memory.get(key)
        ))
        
        self.register_tool(Tool(
            name="core_memory_delete",
            description="Delete a core memory block",
            parameters={
                "key": {"type": "string", "description": "Key for the memory block to delete"}
            },
            required_params=["key"],
            function=lambda key: core_memory.delete(key)
        ))
        
        # TODO: Add archival memory and recall memory tools
