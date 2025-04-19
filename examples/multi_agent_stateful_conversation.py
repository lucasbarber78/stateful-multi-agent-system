#!/usr/bin/env python
# Example of stateful multi-agent conversation with memory persistence

import sys
import os
import time
import uuid
from rich.console import Console
from rich.panel import Panel

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stateful_agents import Agent, MemoryManager, Tool
from stateful_agents.server import Server, AgentClient

# Initialize Rich console for prettier output
console = Console()


def setup_agents(client):
    """Create and configure the agents for the demo."""
    # Create a product manager agent
    pm_info = client.create_agent(
        name="ProductManager",
        model="gpt-4-turbo",
        persona="I am a product manager focused on user experience and business requirements. I'm detail-oriented and concentrate on delivering value to customers.",
        context_window_limit=8192
    )
    pm_id = pm_info["id"]
    
    # Create a developer agent
    dev_info = client.create_agent(
        name="Developer",
        model="gpt-4-turbo",
        persona="I am a senior software engineer with expertise in Python, JavaScript, and system design. I focus on writing clean, maintainable code and implementing scalable solutions.",
        context_window_limit=8192
    )
    dev_id = dev_info["id"]
    
    # Create a UX designer agent
    ux_info = client.create_agent(
        name="UXDesigner",
        model="gpt-4-turbo",
        persona="I am a UX designer with a background in user research and interface design. I create intuitive and accessible experiences that delight users.",
        context_window_limit=8192
    )
    ux_id = ux_info["id"]
    
    # Set up initial memory for each agent
    
    # Project context for all agents
    project_context = """
    Project: E-commerce Inventory Management System
    Client: GrowthRetail Inc.
    Timeline: 4 months
    Budget: $250,000
    
    Key requirements:
    - Real-time inventory tracking across multiple warehouses
    - Integration with existing POS systems
    - Mobile access for warehouse staff
    - Advanced reporting and analytics
    - User role management with different permissions
    """
    
    # Add shared project context to all agents
    for agent_id in [pm_id, dev_id, ux_id]:
        client.update_core_memory(agent_id, "project_context", project_context)
    
    # Add specific knowledge to each agent
    client.update_core_memory(pm_id, "stakeholders", 
                            "CEO: John Miller - Focused on ROI and growth\n"
                            "COO: Sarah Peters - Concerned with operational efficiency\n"
                            "Warehouse Manager: Miguel Rodriguez - Needs user-friendly mobile interface")
    
    client.update_core_memory(dev_id, "technical_stack", 
                             "Backend: Django with REST API\n"
                             "Frontend: React with Material UI\n"
                             "Database: PostgreSQL\n"
                             "Mobile: React Native\n"
                             "Deployment: AWS with Docker containers")
    
    client.update_core_memory(ux_id, "user_research", 
                             "User testing revealed warehouse staff prefer large buttons and simple navigation.\n"
                             "Color blind accessibility is important for warehouse staff.\n"
                             "Management needs comprehensive but easy-to-read dashboards.")
    
    console.print(Panel.fit(
        f"[bold]Agents Created:[/bold]\n\n"
        f"1. Product Manager (ID: {pm_id})\n"
        f"2. Developer (ID: {dev_id})\n"
        f"3. UX Designer (ID: {ux_id})",
        title="Multi-Agent Setup",
        border_style="green"
    ))
    
    return pm_id, dev_id, ux_id


def facilitate_agent_conversation(client, pm_id, dev_id, ux_id):
    """Facilitate a conversation between the agents, demonstrating memory persistence."""
    
    # Initial message to PM from user
    console.print("\n[bold blue]Initial Request:[/bold blue]")
    console.print("[bold]User to Product Manager:[/bold] We need to start designing the inventory management dashboard. Can you coordinate with the developer and UX designer?")
    
    response = client.send_message(pm_id, 
                                  "We need to start designing the inventory management dashboard. Can you coordinate with the developer and UX designer?")
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # PM message to Developer
    console.print("[bold blue]Agent-to-Agent Communication:[/bold blue]")
    console.print("[bold]User to Product Manager:[/bold] Please reach out to the developer to discuss technical requirements for the dashboard.")
    
    response = client.send_message(pm_id, 
                                  "Please reach out to the developer to discuss technical requirements for the dashboard.",
                                  metadata={"recipient_id": dev_id})  # Metadata to indicate intended recipient
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # Simulate PM sending message to Developer
    pm_message = "Hi Developer, I'm working on requirements for the inventory management dashboard. What are the key technical considerations we should keep in mind?"
    console.print(f"[bold]Product Manager to Developer:[/bold] {pm_message}")
    
    # Developer receives and responds to PM's message
    response = client.send_message(dev_id, 
                                  f"Message from Product Manager: {pm_message}",
                                  sender_id=pm_id)
    console.print(f"[bold]Developer:[/bold] {response['response']}\n")
    
    # Simulate Developer's response to PM
    dev_message = response['response']
    console.print(f"[bold]Developer to Product Manager:[/bold] {dev_message}")
    
    # PM receives Developer's response
    response = client.send_message(pm_id, 
                                  f"Message from Developer: {dev_message}",
                                  sender_id=dev_id)
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # PM message to UX Designer
    console.print("[bold]User to Product Manager:[/bold] Now please consult with the UX designer about the user interface.")
    
    response = client.send_message(pm_id, 
                                  "Now please consult with the UX designer about the user interface.",
                                  metadata={"recipient_id": ux_id})
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # Simulate PM sending message to UX Designer
    pm_to_ux_message = "Hi UX Designer, we're working on the inventory dashboard. Based on your user research, what design principles should we prioritize?"
    console.print(f"[bold]Product Manager to UX Designer:[/bold] {pm_to_ux_message}")
    
    # UX Designer receives and responds
    response = client.send_message(ux_id, 
                                  f"Message from Product Manager: {pm_to_ux_message}",
                                  sender_id=pm_id)
    console.print(f"[bold]UX Designer:[/bold] {response['response']}\n")
    
    # Simulate UX Designer's response to PM
    ux_message = response['response']
    console.print(f"[bold]UX Designer to Product Manager:[/bold] {ux_message}")
    
    # PM receives UX Designer's response
    response = client.send_message(pm_id, 
                                  f"Message from UX Designer: {ux_message}",
                                  sender_id=ux_id)
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # Let's update the memory with new project information
    console.print("[bold blue]Memory Update:[/bold blue]")
    console.print("[bold]User:[/bold] Adding new project information to all agents' memory...")
    
    updated_info = """
    UPDATE: The client has revised their requirements. They now need:
    - Barcode scanning functionality via mobile devices
    - Integration with their QuickBooks accounting system
    - Support for multiple currencies and international warehouses
    - Enhanced security features for remote access
    """
    
    for agent_id in [pm_id, dev_id, ux_id]:
        client.update_core_memory(agent_id, "project_updates", updated_info)
    
    console.print("Memory updated for all agents.\n")
    
    # Test if agents remember the updates
    console.print("[bold blue]Memory Persistence Test:[/bold blue]")
    
    # Ask PM about the updated requirements
    console.print("[bold]User to Product Manager:[/bold] Can you summarize the latest updates to our project requirements?")
    
    response = client.send_message(pm_id, "Can you summarize the latest updates to our project requirements?")
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")
    
    # Ask Developer how these changes affect the technical implementation
    console.print("[bold]User to Developer:[/bold] How do these requirement changes affect our technical implementation?")
    
    response = client.send_message(dev_id, "How do these requirement changes affect our technical implementation?")
    console.print(f"[bold]Developer:[/bold] {response['response']}\n")
    
    # Ask UX Designer about design implications
    console.print("[bold]User to UX Designer:[/bold] What design considerations arise from these new requirements?")
    
    response = client.send_message(ux_id, "What design considerations arise from these new requirements?")
    console.print(f"[bold]UX Designer:[/bold] {response['response']}\n")
    
    # Final check on conversation memory
    console.print("[bold blue]Conversation Memory Test:[/bold blue]")
    
    # Ask PM to recall previous conversation 
    console.print("[bold]User to Product Manager:[/bold] Can you summarize what you discussed with the developer and UX designer?")
    
    response = client.send_message(pm_id, "Can you summarize what you discussed with the developer and UX designer?")
    console.print(f"[bold]Product Manager:[/bold] {response['response']}\n")


def main():
    # Start the server in a background thread
    server = Server(db_path="multi_agent_example.db")
    server_thread = server.run_in_thread(port=8080)
    
    # Wait for server to start
    time.sleep(2)
    
    console.print(Panel.fit(
        "This example demonstrates a stateful multi-agent system where agents maintain memory across interactions.\n\n"
        "We'll create three agents - a Product Manager, a Developer, and a UX Designer - working on an inventory management system.\n"
        "The agents will communicate with each other and maintain state about the project requirements and their conversations.",
        title="Stateful Multi-Agent Conversation Demo",
        border_style="blue"
    ))
    
    # Create a client
    client = AgentClient(base_url="http://localhost:8080")
    
    try:
        # Set up the agents
        pm_id, dev_id, ux_id = setup_agents(client)
        
        # Run through the conversation scenario
        facilitate_agent_conversation(client, pm_id, dev_id, ux_id)
        
        console.print(Panel.fit(
            "The demonstration is complete. You've seen how stateful agents can:\n\n"
            "1. Maintain memory about their identity and knowledge\n"
            "2. Communicate with other agents while maintaining conversation history\n"
            "3. Recall previous interactions and project details\n"
            "4. Update their memory with new information\n\n"
            "This capability enables more realistic and effective multi-agent systems.",
            title="Demonstration Complete",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Demonstration interrupted by user.[/bold red]")
    finally:
        # Clean up
        console.print("\nShutting down server...")
        server.close()
        console.print("Done!")


if __name__ == "__main__":
    main()
