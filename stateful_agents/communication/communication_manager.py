from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .message import Message


class CommunicationManager(BaseModel):
    """Manages communication between agents."""
    
    agent_id: str
    message_queue: List[Message] = Field(default_factory=list)
    max_queue_size: int = Field(100, description="Maximum number of messages to keep in queue")
    
    def send_message(self, receiver_id: str, content: str, message_type: str = "text", metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Send a message to another agent."""
        message = Message(
            content=content,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        # In a real implementation, this would send the message to the receiver
        # For now, just return the message
        return message
    
    def receive_message(self, message: Message) -> None:
        """Receive a message from another agent or user."""
        if message.receiver_id != self.agent_id:
            raise ValueError(f"Message not for this agent. Expected {self.agent_id}, got {message.receiver_id}")
        
        self.message_queue.append(message)
        
        # Trim queue if necessary
        if len(self.message_queue) > self.max_queue_size:
            self.message_queue = self.message_queue[-self.max_queue_size:]
    
    def get_pending_messages(self) -> List[Message]:
        """Get all pending messages."""
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages
    
    def has_pending_messages(self) -> bool:
        """Check if there are pending messages."""
        return len(self.message_queue) > 0
