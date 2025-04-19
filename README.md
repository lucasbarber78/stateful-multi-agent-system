# Stateful Multi-Agent System

A framework for building effective multi-agent systems with sophisticated memory management capabilities, inspired by research from Anthropic and the MGPT project.

## Overview

This framework enables the creation of stateful agents that can:
- Maintain persistent memory across interactions
- Effectively manage context windows in LLMs
- Communicate with other agents asynchronously
- Use tools to modify their own memory and interact with external systems

Unlike traditional stateless agents, this system implements a hierarchical memory architecture that allows agents to learn from experience and maintain state over extended periods.

## Memory Architecture

The framework implements a three-tier memory system:

1. **Core Memory**: High-priority information kept directly in the context window
   - Personal information about the agent and user
   - Critical facts that affect agent behavior
   - Frequently accessed information

2. **Recall Memory**: Conversation history that can be searched
   - Previous messages in chronological order
   - Automatically stored and retrievable through search

3. **Archival Memory**: Long-term storage outside the context window
   - Extended knowledge base with vector search capabilities
   - Information explicitly saved for long-term retention
   - Can be augmented with external data sources

## Key Features

- **Context Management**: Intelligently manages context window limits through summarization, eviction, and retrieval
- **Tool Framework**: Enables agents to use tools to modify their memory and interact with external systems
- **Multi-Agent Communication**: Supports both synchronous and asynchronous communication between agents
- **Stateful Persistence**: Maintains agent state in a database, allowing for persistent identity across sessions
- **Observable Reasoning**: Provides visibility into agent reasoning process and memory management

## Architecture

The system is built on a server-client architecture:

- **Server**: Manages agent state, tool execution, and memory persistence
- **Client**: Provides API for interacting with agents and creating multi-agent systems

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/lucasbarber78/stateful-multi-agent-system.git
cd stateful-multi-agent-system

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

```python
from stateful_agents import Agent, MemoryManager

# Create a new agent with core memory
agent = Agent(
    name="Assistant",
    model="gpt-4-turbo",
    memory_manager=MemoryManager(),
    persona="I am a helpful assistant with expertise in programming."
)

# Add core memory about the user
agent.memory.add_core_memory("human", "The human's name is Alice. She is a software engineer.")

# Send a message and get a response
response = agent.send_message("Hello, can you help me with a Python question?")
print(response)

# The agent's memory persists between sessions
agent.save()
```

## Examples

See the `/examples` directory for complete examples of:
- Basic stateful agent with memory management
- Multi-agent conversation
- Tool use for memory modification
- Context window management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is inspired by:
- Anthropic's research on building effective agents
- The MGPT (Memory-GPT) project's work on LLM memory management
- Concepts from cognitive architecture and human memory systems
