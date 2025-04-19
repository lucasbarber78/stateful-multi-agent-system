#!/usr/bin/env python
# Demonstration of advanced memory management techniques in stateful agents

import sys
import os
import time
from rich.console import Console
from rich.panel import Panel

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stateful_agents import Agent, MemoryManager, Tool

# Initialize Rich console for prettier output
console = Console()


def create_memory_tool(agent, name, description, function):
    """Create a memory tool and register it with the agent."""
    tool = Tool(
        name=name,
        description=description,
        parameters={
            "content": {"type": "string", "description": "Content to process"}
        },
        required_params=["content"],
        function=function
    )
    agent.tool_manager.register_tool(tool)
    return tool


def show_memory_state(memory_manager, context_window_size):
    """Display the current state of memory and context window usage."""
    stats = memory_manager.get_memory_stats()
    
    total_core_size = stats["core_memory"]["total_size"]
    total_recall_size = stats["recall_memory"]["total_size"]
    
    # Estimate total context window usage (this would be more accurate in a real implementation)
    # We're assuming a rough approximation of characters to tokens
    estimated_tokens = (total_core_size + total_recall_size) // 4  # Rough estimate: 4 chars ≈ 1 token
    window_percent = min(100, (estimated_tokens / context_window_size) * 100)
    
    console.print(Panel.fit(
        f"[bold]Memory State[/bold]\n\n"
        f"Core Memory: {stats['core_memory']['count']} blocks, {total_core_size} chars\n"
        f"Recall Memory: {stats['recall_memory']['count']} messages, {total_recall_size} chars\n"
        f"Archival Memory: {stats['archival_memory']['count']} items\n\n"
        f"Estimated Context Window Usage: {estimated_tokens} tokens / {context_window_size} tokens "
        f"({window_percent:.1f}%)",
        title="Memory Dashboard",
        border_style="green"
    ))


def demonstrate_context_management():
    """Demonstrate how memory management works with context windows."""
    # Create a memory manager
    memory_manager = MemoryManager()
    
    # Define a small context window to better demonstrate management
    context_window_size = 4096  # tokens
    
    # Create an agent with limited context window
    agent = Agent(
        id="memory-demo-agent",
        name="MemoryManager",
        model="gpt-4-turbo",
        persona="I am an agent that demonstrates memory management techniques.",
        memory_manager=memory_manager,
        context_window_limit=context_window_size
    )
    
    # Add default memory tools
    agent.tool_manager.add_memory_tools(memory_manager.core_memory)
    
    # Add custom tools for memory management
    create_memory_tool(
        agent,
        "summarize_and_store",
        "Summarize content and store in archival memory",
        lambda content: memory_manager.add_to_archival(f"SUMMARY: {content[:100]}...")
    )
    
    create_memory_tool(
        agent,
        "prioritize_memory",
        "Move less important information from core to archival memory",
        lambda content: memory_manager.add_to_archival(f"ARCHIVED: {content}")
    )
    
    # Show initial state
    console.print("\n[bold blue]Initial Memory State[/bold blue]")
    show_memory_state(memory_manager, context_window_size)
    
    # Add core memories (important information)
    console.print("\n[bold blue]Adding Core Memories[/bold blue]")
    memory_manager.add_core_memory("user_profile", "The user is Alice, a software engineer with 5 years of experience in Python and JavaScript.")
    memory_manager.add_core_memory("preferences", "Alice prefers detailed technical explanations and code examples.")
    memory_manager.add_core_memory("current_project", "Alice is working on a web application for inventory management using React and Django.")
    
    # Show state after adding core memories
    show_memory_state(memory_manager, context_window_size)
    
    # Simulate a conversation with multiple messages
    conversation = [
        "Can you help me design the database schema for my inventory management system?",
        "I need tables for products, categories, suppliers, and inventory levels.",
        "For products, I need to store name, SKU, description, price, and category.",
        "Categories should have a name, description, and parent category for hierarchical organization.",
        "Suppliers need contact information, payment terms, and lead times.",
        "Inventory levels should track quantity on hand, reorder point, and warehouse location.",
        "I also want to track purchase orders, sales orders, and inventory adjustments.",
        "The system needs to generate reports on inventory valuation, stock movements, and reorder suggestions.",
        "It should support multiple warehouses and bin locations within warehouses.",
        "I want to implement barcode scanning for inventory operations.",
        "The application needs user roles like admin, manager, and warehouse staff with different permissions.",
        "We need to integrate with our accounting software for financial reporting.",
        "The system should support batch tracking for certain products.",
        "I want to implement FIFO (First In, First Out) inventory costing.",
        "We need to track inventory transactions with full audit trails."
    ]
    
    # Process each message and show memory status
    for i, message in enumerate(conversation):
        console.print(f"\n[bold green]Processing Message {i+1}/{len(conversation)}[/bold green]")
        console.print(f"[italic]User: {message}[/italic]")
        
        # Send message to agent
        response = agent.send_message(message)
        console.print(f"[italic]Agent: {response}[/italic]")
        
        # Show memory state after processing
        show_memory_state(memory_manager, context_window_size)
        
        # If context window is getting full (over 70%), prompt for management
        stats = memory_manager.get_memory_stats()
        total_size = stats["core_memory"]["total_size"] + stats["recall_memory"]["total_size"]
        estimated_tokens = total_size // 4
        
        if estimated_tokens > (context_window_size * 0.7):
            console.print("\n[bold yellow]Context window is filling up! Managing memory...[/bold yellow]")
            
            # Archive older conversation items
            if i > 5:
                oldest_messages = agent.memory_manager.recall_memory.get_by_range(0, 3)
                for old_msg in oldest_messages:
                    # Summarize and move to archival memory
                    summary = f"User asked about: {old_msg.content[:50]}..."
                    agent.memory_manager.add_to_archival(summary)
                
                # Remove from recall after archiving
                agent.memory_manager.recall_memory.messages = agent.memory_manager.recall_memory.messages[3:]
                
                console.print("[yellow]Archived oldest conversation items to free up context window[/yellow]")
                show_memory_state(memory_manager, context_window_size)
        
        # Pause briefly for demo purposes
        time.sleep(1)
    
    # Demonstrate retrieving information from archival memory
    console.print("\n[bold blue]Retrieving Information from Archival Memory[/bold blue]")
    query = "inventory tracking"
    results = memory_manager.search_archival(query)
    
    console.print(f"[bold]Search Results for '{query}':[/bold]")
    for i, result in enumerate(results):
        console.print(f"{i+1}. {result['content']}")
    
    # Final memory state
    console.print("\n[bold blue]Final Memory State[/bold blue]")
    show_memory_state(memory_manager, context_window_size)


if __name__ == "__main__":
    demonstrate_context_management()
