#!/usr/bin/env python
# Basic example of a stateful agent with memory management

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stateful_agents import Agent, MemoryManager


def main():
    # Create a memory manager
    memory_manager = MemoryManager()
    
    # Add some core memory
    memory_manager.add_core_memory("human", "The human's name is Alice. She is a software engineer.")
    
    # Create an agent
    agent = Agent(
        id="assistant-1",
        name="Assistant",
        model="gpt-4-turbo",  # This would be the model to use
        persona="I am a helpful AI assistant with expertise in programming and technology.",
        memory_manager=memory_manager
    )
    
    # Add default memory tools
    agent.tool_manager.add_memory_tools(memory_manager.core_memory)
    
    # Simulate a conversation
    print("\nSimulating a conversation with a stateful agent...\n")
    
    # Send messages and print responses
    messages = [
        "Hello there, can you help me with a Python question?",
        "I need to parse a JSON file in Python. What's the best way to do that?",
        "Thank you! By the way, do you remember my name?"
    ]
    
    for message in messages:
        print(f"User: {message}")
        response = agent.send_message(message)
        print(f"Agent: {response}\n")
    
    # Print memory statistics
    stats = memory_manager.get_memory_stats()
    print("Memory Statistics:")
    for memory_type, stats in stats.items():
        print(f"  {memory_type}: {stats['count']} items, {stats['total_size']} characters")


if __name__ == "__main__":
    main()
