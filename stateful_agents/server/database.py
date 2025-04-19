from typing import Dict, List, Optional, Any, Union
import sqlite3
import json
import os
import time


class Database:
    """Database for storing agent state and memory."""
    
    def __init__(self, db_path: str = "agents.db"):
        """Initialize the database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize the database schema."""
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        
        # Connect to the database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.conn.cursor()
        
        # Agents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            persona TEXT,
            system_prompt TEXT,
            context_window_limit INTEGER DEFAULT 4096,
            active BOOLEAN DEFAULT 1,
            created_at INTEGER,
            updated_at INTEGER
        )
        """)
        
        # Memory blocks table (core memory)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_blocks (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            UNIQUE (agent_id, key)
        )
        """)
        
        # Archival memory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS archival_memory (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            embedding TEXT,
            created_at INTEGER,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Recall memory table (conversation history)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recall_memory (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            content TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            metadata TEXT,
            created_at INTEGER,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_blocks_agent_id ON memory_blocks(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_archival_memory_agent_id ON archival_memory(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recall_memory_agent_id ON recall_memory(agent_id)")
        
        self.conn.commit()
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def save_agent(self, agent_data: Dict[str, Any]) -> str:
        """Save or update an agent.
        
        Args:
            agent_data: Dictionary containing agent data
            
        Returns:
            The agent ID
        """
        cursor = self.conn.cursor()
        
        # Check if agent already exists
        agent_id = agent_data.get("id")
        cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        
        current_time = int(time.time())
        
        if cursor.fetchone():
            # Update existing agent
            cursor.execute("""
            UPDATE agents SET
                name = ?,
                model = ?,
                persona = ?,
                system_prompt = ?,
                context_window_limit = ?,
                active = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                agent_data.get("name"),
                agent_data.get("model"),
                agent_data.get("persona", ""),
                agent_data.get("system_prompt", ""),
                agent_data.get("context_window_limit", 4096),
                agent_data.get("active", True),
                current_time,
                agent_id
            ))
        else:
            # Insert new agent
            cursor.execute("""
            INSERT INTO agents (
                id, name, model, persona, system_prompt, context_window_limit, active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                agent_data.get("name"),
                agent_data.get("model"),
                agent_data.get("persona", ""),
                agent_data.get("system_prompt", ""),
                agent_data.get("context_window_limit", 4096),
                agent_data.get("active", True),
                current_time,
                current_time
            ))
        
        self.conn.commit()
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Dictionary containing agent data, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    def save_memory_block(self, agent_id: str, key: str, value: str) -> str:
        """Save or update a memory block.
        
        Args:
            agent_id: The agent ID
            key: Memory block key
            value: Memory block value
            
        Returns:
            The memory block ID
        """
        cursor = self.conn.cursor()
        
        # Check if memory block already exists
        block_id = f"{agent_id}-{key}"
        cursor.execute("SELECT id FROM memory_blocks WHERE agent_id = ? AND key = ?", (agent_id, key))
        
        current_time = int(time.time())
        
        if cursor.fetchone():
            # Update existing memory block
            cursor.execute("""
            UPDATE memory_blocks SET
                value = ?,
                updated_at = ?
            WHERE agent_id = ? AND key = ?
            """, (
                value,
                current_time,
                agent_id,
                key
            ))
        else:
            # Insert new memory block
            cursor.execute("""
            INSERT INTO memory_blocks (
                id, agent_id, key, value, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                block_id,
                agent_id,
                key,
                value,
                current_time,
                current_time
            ))
        
        self.conn.commit()
        return block_id
    
    def get_memory_blocks(self, agent_id: str) -> Dict[str, str]:
        """Get all memory blocks for an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Dictionary mapping keys to values
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM memory_blocks WHERE agent_id = ?", (agent_id,))
        
        return {row["key"]: row["value"] for row in cursor.fetchall()}
    
    def save_archival_memory(self, agent_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save an item to archival memory.
        
        Args:
            agent_id: The agent ID
            content: Memory content
            metadata: Optional metadata
            
        Returns:
            The memory item ID
        """
        cursor = self.conn.cursor()
        
        current_time = int(time.time())
        item_id = f"arch-{agent_id}-{current_time}"
        
        cursor.execute("""
        INSERT INTO archival_memory (
            id, agent_id, content, metadata, created_at
        ) VALUES (?, ?, ?, ?, ?)
        """, (
            item_id,
            agent_id,
            content,
            json.dumps(metadata or {}),
            current_time
        ))
        
        self.conn.commit()
        return item_id
    
    def search_archival_memory(self, agent_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search archival memory for an agent.
        
        Args:
            agent_id: The agent ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of memory items
        """
        cursor = self.conn.cursor()
        
        # Simple text search for now - would be replaced with vector search
        cursor.execute("""
        SELECT id, content, metadata, created_at 
        FROM archival_memory 
        WHERE agent_id = ? AND content LIKE ? 
        ORDER BY created_at DESC
        LIMIT ?
        """, (agent_id, f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]),
                "timestamp": row["created_at"]
            })
        
        return results
    
    def save_message(self, agent_id: str, sender_id: str, receiver_id: str, content: str, 
                    message_type: str = "text", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a message to recall memory.
        
        Args:
            agent_id: The agent ID
            sender_id: ID of the sender
            receiver_id: ID of the receiver
            content: Message content
            message_type: Type of message
            metadata: Optional metadata
            
        Returns:
            The message ID
        """
        cursor = self.conn.cursor()
        
        current_time = int(time.time())
        message_id = f"msg-{agent_id}-{current_time}"
        
        cursor.execute("""
        INSERT INTO recall_memory (
            id, agent_id, sender_id, receiver_id, content, message_type, metadata, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            agent_id,
            sender_id,
            receiver_id,
            content,
            message_type,
            json.dumps(metadata or {}),
            current_time
        ))
        
        self.conn.commit()
        return message_id
    
    def get_recent_messages(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for an agent.
        
        Args:
            agent_id: The agent ID
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, sender_id, receiver_id, content, message_type, metadata, created_at
        FROM recall_memory
        WHERE agent_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (agent_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row["id"],
                "sender_id": row["sender_id"],
                "receiver_id": row["receiver_id"],
                "content": row["content"],
                "message_type": row["message_type"],
                "metadata": json.loads(row["metadata"]),
                "timestamp": row["created_at"]
            })
        
        # Return in chronological order
        return list(reversed(messages))
    
    def search_messages(self, agent_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search messages for an agent.
        
        Args:
            agent_id: The agent ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of messages
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, sender_id, receiver_id, content, message_type, metadata, created_at
        FROM recall_memory
        WHERE agent_id = ? AND content LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (agent_id, f"%{query}%", limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row["id"],
                "sender_id": row["sender_id"],
                "receiver_id": row["receiver_id"],
                "content": row["content"],
                "message_type": row["message_type"],
                "metadata": json.loads(row["metadata"]),
                "timestamp": row["created_at"]
            })
        
        return messages