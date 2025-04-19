from typing import Dict, List, Optional, Any, Callable
from pydantic import BaseModel, Field


class Tool(BaseModel):
    """A tool that can be used by an agent."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Parameters for the tool")
    function: Optional[Callable] = Field(None, description="Function to execute when the tool is called")
    required_params: List[str] = Field(default_factory=list, description="List of required parameters")
    
    class Config:
        arbitrary_types_allowed = True
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        if self.function is None:
            raise ValueError(f"Tool {self.name} does not have an implementation")
        
        # Check for required parameters
        for param in self.required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Execute the function
        return self.function(**kwargs)
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "required": self.required_params
        }
