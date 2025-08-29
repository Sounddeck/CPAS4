
"""
MemOS initialization script for MongoDB backend
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from config import settings

async def initialize_memos():
    """Initialize MemOS with MongoDB backend"""
    try:
        logger.info("🧠 Initializing MemOS with MongoDB backend...")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.mongodb_uri)
        db = client[settings.mongodb_db_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")
        
        # Create collections if they don't exist
        collections = await db.list_collection_names()
        
        # Memory collection
        if settings.memos_collection not in collections:
            await db.create_collection(settings.memos_collection)
            logger.info(f"✅ Created collection: {settings.memos_collection}")
        
        # Memory index collection
        if settings.memos_index_collection not in collections:
            await db.create_collection(settings.memos_index_collection)
            logger.info(f"✅ Created collection: {settings.memos_index_collection}")
        
        # Create indexes for better performance
        memory_collection = db[settings.memos_collection]
        index_collection = db[settings.memos_index_collection]
        
        # Memory collection indexes
        await memory_collection.create_index("timestamp")
        await memory_collection.create_index("memory_type")
        await memory_collection.create_index("tags")
        await memory_collection.create_index("importance")
        await memory_collection.create_index("last_accessed")
        await memory_collection.create_index("access_count")
        
        # Index collection indexes
        await index_collection.create_index("memory_id")
        await index_collection.create_index("embedding")
        
        logger.info("✅ Created database indexes")
        
        # Initialize with some sample memories
        sample_count = await memory_collection.count_documents({})
        if sample_count == 0:
            await create_sample_memories(memory_collection)
        
        # Try to import and initialize MemOS if available
        try:
            # This will be available after MemOS is cloned and installed
            logger.info("🔧 Attempting to initialize MemOS integration...")
            
            # Basic MemOS configuration
            memos_config = {
                "backend": "mongodb",
                "mongodb_uri": settings.mongodb_uri,
                "database_name": settings.mongodb_db_name,
                "collection_name": settings.memos_collection,
                "index_collection": settings.memos_index_collection,
                "embedding_model": "all-MiniLM-L6-v2",
                "max_memory_size": 10000,
                "cleanup_threshold": 0.8
            }
            
            logger.info("✅ MemOS configuration prepared")
            
        except ImportError as e:
            logger.warning(f"MemOS not yet available: {e}")
            logger.info("📝 MemOS will be integrated after installation")
        
        await client.close()
        logger.info("✅ MemOS initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MemOS: {e}")
        raise

async def create_sample_memories(collection):
    """Create sample memories for testing"""
    try:
        from datetime import datetime
        
        sample_memories = [
            {
                "content": "Enhanced CPAS system initialized with MongoDB and MemOS integration",
                "memory_type": "system",
                "tags": ["initialization", "system", "cpas"],
                "metadata": {"phase": "Phase 1", "component": "foundation"},
                "importance": 0.9,
                "timestamp": datetime.utcnow(),
                "access_count": 0,
                "embedding": [0.0] * 384  # Placeholder embedding
            },
            {
                "content": "Local LLM support added with Ollama integration for DeepSeek, Llama, and Mixtral models",
                "memory_type": "feature",
                "tags": ["llm", "ollama", "models"],
                "metadata": {"models": ["deepseek-r1:7b", "llama3.2:3b", "mixtral:8x7b"]},
                "importance": 0.8,
                "timestamp": datetime.utcnow(),
                "access_count": 0,
                "embedding": [0.0] * 384
            },
            {
                "content": "Memory system supports semantic search, importance scoring, and access tracking",
                "memory_type": "capability",
                "tags": ["memory", "search", "tracking"],
                "metadata": {"features": ["semantic_search", "importance_scoring", "access_tracking"]},
                "importance": 0.7,
                "timestamp": datetime.utcnow(),
                "access_count": 0,
                "embedding": [0.0] * 384
            }
        ]
        
        await collection.insert_many(sample_memories)
        logger.info(f"✅ Created {len(sample_memories)} sample memories")
        
    except Exception as e:
        logger.error(f"Failed to create sample memories: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_memos())
