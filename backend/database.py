
"""
Database connection and management for Enhanced CPAS Backend
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError
from loguru import logger
from config import settings

class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.database = self.client[settings.mongodb_db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            await self.client.admin.command('ping')
            return {"status": "healthy", "database": settings.mongodb_db_name}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Memory collection indexes
            await self.database[settings.memos_collection].create_index("timestamp")
            await self.database[settings.memos_collection].create_index("memory_type")
            await self.database[settings.memos_collection].create_index("tags")
            
            # Memory index collection
            await self.database[settings.memos_index_collection].create_index("embedding")
            await self.database[settings.memos_index_collection].create_index("memory_id")
            
            # Agent collection (future)
            await self.database["agents"].create_index("agent_id")
            await self.database["agents"].create_index("created_at")
            
            # Conversation collection
            await self.database["conversations"].create_index("session_id")
            await self.database["conversations"].create_index("timestamp")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.database[collection_name]

# Global database instance
database = Database()
