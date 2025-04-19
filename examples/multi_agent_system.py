#!/usr/bin/env python
# Example of a multi-agent system with communication

import sys
import os
import uuid

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stateful_agents import Agent, MemoryManager, Tool
from stateful_agents.communication import Message


def create_agent(name, persona, model="gpt-4-turbo"):
    # Create a unique ID for the agent
    agent_id = f"{name.lower()}-{uuid.uuid4().hex[:8]}"
    
    # Create a memory manager
    memory_manager = MemoryManager()
    
    # Add persona to core memory
    memory_manager.add_core_memory("persona", persona)
    
    # Create the agent
    agent = Agent(
        id=agent_id,
        name=name,
        model=model,
        persona=persona,
        memory_manager=memory_manager
    )
    
    # Add default memory tools
    agent.tool_manager.add_memory_tools(memory_manager.core_memory)
    
    return agent


def register_communication_tools(agent1, agent2):
    """Register tools for agents to communicate with each other."""
    # Add tool for agent1 to message agent2
    agent1.tool_manager.register_tool(Tool(
        name=f"message_{agent2.name.lower()}",
        description=f"Send a message to {agent2.name}",
        parameters={
            "content": {"type": "string", "description": "Content of the message to send"}
        },
        required_params=["content"],
        function=lambda content: agent2.communication_manager.receive_message(Message(
            content=content,
            sender_id=agent1.id,
            receiver_id=agent2.id
        ))
    ))
    
    # Add tool for agent2 to message agent1
    agent2.tool_manager.register_tool(Tool(
        name=f"message_{agent1.name.lower()}",
        description=f"Send a message to {agent1.name}",
        parameters={
            "content": {"type": "string", "description": "Content of the message to send"}
        },
        required_params=["content"],
        function=lambda content: agent1.communication_manager.receive_message(Message(
            content=content,
            sender_id=agent2.id,
            receiver_id=agent1.id
        ))
    ))


def process_pending_messages(agent):
    """Process any pending messages for an agent."""
    if agent.communication_manager.has_pending_messages():
        messages = agent.communication_manager.get_pending_messages()
        for message in messages:
            print(f"{agent.name} received message from {message.sender_id}: {message.content}")
            # Process the message
            response = agent.send_message(message.content, user_id=message.sender_id)
            print(f"{agent.name} processed message and responded: {response}")


def main():
    # Create a programmer agent
    programmer = create_agent(
        name="Programmer",
        persona="I am an expert programmer with deep knowledge of Python, JavaScript, and system design."
    )
    
    # Create a product manager agent
    product_manager = create_agent(
        name="ProductManager",
        persona="I am a product manager focused on user experience and business requirements."
    )
    
    # Register communication tools
    register_communication_tools(programmer, product_manager)
    
    # Simulate a conversation between the user and both agents
    print("\nSimulating a multi-agent conversation...\n")
    
    # User asks the product manager to create a project plan
    user_request = "We need to build a web application for inventory management. Can you create a project plan?"
    print(f"User to ProductManager: {user_request}")
    
    # Product manager responds to the user
    pm_response = product_manager.send_message(user_request)
    print(f"ProductManager to User: {pm_response}\n")
    
    # Product manager sends a message to the programmer
    user_to_pm = "Can you coordinate with the programmer to determine technical requirements?"
    print(f"User to ProductManager: {user_to_pm}")
    
    # Product manager responds and may use the communication tool
    pm_response = product_manager.send_message(user_to_pm)
    print(f"ProductManager to User: {pm_response}\n")
    
    # Process any pending messages for the programmer
    process_pending_messages(programmer)
    
    # Process any pending messages for the product manager
    process_pending_messages(product_manager)
    
    # Check what the programmer remembers
    user_to_programmer = "What do you know about the inventory management project?"
    print(f"User to Programmer: {user_to_programmer}")
    
    programmer_response = programmer.send_message(user_to_programmer)
    print(f"Programmer to User: {programmer_response}\n")


if __name__ == "__main__":
    main()
