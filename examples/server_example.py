#!/usr/bin/env python
# Example of running the stateful agent server

import sys
import os
import time

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stateful_agents.server import Server, AgentClient


def main():
    # Start the server in a background thread
    server = Server(db_path="example_agents.db")
    server_thread = server.run_in_thread(port=8080)
    
    # Wait for server to start
    time.sleep(2)
    
    print("\nStateful Agent Server running on http://localhost:8080")
    print("Creating and testing agents...\n")
    
    # Create a client
    client = AgentClient(base_url="http://localhost:8080")
    
    # Create an agent
    agent_info = client.create_agent(
        name="Memory Assistant",
        model="gpt-4-turbo",
        persona="I am a helpful AI assistant with excellent memory capabilities.",
        context_window_limit=4096
    )
    
    agent_id = agent_info["id"]
    print(f"Created agent: {agent_info['name']} (ID: {agent_id})")
    
    # Update core memory
    client.update_core_memory(agent_id, "user_profile", "The user's name is Alice, she is a software engineer.")
    print("Added user profile to core memory")
    
    # Send some messages
    messages = [
        "Hello there, can you help me with a Python question?",
        "I need to parse a large JSON file efficiently. What's the best approach?",
        "Thanks for the advice! By the way, do you remember my name?"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        response = client.send_message(agent_id, message)
        print(f"Agent: {response['response']}")
    
    # Add to archival memory
    client.add_to_archival(
        agent_id, 
        "Alice enjoys hiking and photography. She has two dogs named Max and Luna."
    )
    print("\nAdded personal interests to archival memory")
    
    # Test recall
    response = client.send_message(agent_id, "What do you know about my interests?")
    print(f"\nUser: What do you know about my interests?")
    print(f"Agent: {response['response']}")
    
    # Get recent messages
    messages = client.get_recent_messages(agent_id)
    print(f"\nRetrieved {len(messages)} recent messages")
    
    # Clean up
    print("\nExperiment complete. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.close()
        print("Done!")


if __name__ == "__main__":
    main()
