from typing import Dict, Optional, Any
import time
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message between agents or between an agent and a user."""
    
    content: str = Field(..., description="Content of the message")
    sender_id: str = Field(..., description="ID of the sender")
    receiver_id: str = Field(..., description="ID of the receiver")
    timestamp: float = Field(default_factory=time.time, description="Timestamp of the message")
    message_type: str = Field("text", description="Type of message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
