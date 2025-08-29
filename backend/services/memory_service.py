
"""
Memory management service using MemOS
"""

import asyncio
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId
from loguru import logger

from models.memory import Memory, MemoryCreate, MemoryUpdate, MemorySearchRequest
from database import database
from config import settings

class MemoryService:
    """Service for managing memories with MemOS integration"""
    
    def __init__(self):
        self.collection_name = settings.memos_collection
        self.index_collection_name = settings.memos_index_collection
    
    async def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        try:
            # Create memory document
            memory_dict = memory_data.dict()
            memory_dict["timestamp"] = datetime.utcnow()
            memory_dict["last_accessed"] = None
            memory_dict["access_count"] = 0
            
            # Generate embedding if content provided
            if memory_data.content:
                embedding = await self._generate_embedding(memory_data.content)
                memory_dict["embedding"] = embedding
            
            # Insert into database
            collection = database.get_collection(self.collection_name)
            result = await collection.insert_one(memory_dict)
            
            # Retrieve created memory
            created_memory = await collection.find_one({"_id": result.inserted_id})
            created_memory["_id"] = str(created_memory["_id"])
            
            logger.info(f"Created memory: {result.inserted_id}")
            return Memory(**created_memory)
            
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID"""
        try:
            collection = database.get_collection(self.collection_name)
            memory_doc = await collection.find_one({"_id": ObjectId(memory_id)})
            
            if memory_doc:
                # Update access tracking
                await collection.update_one(
                    {"_id": ObjectId(memory_id)},
                    {
                        "$set": {"last_accessed": datetime.utcnow()},
                        "$inc": {"access_count": 1}
                    }
                )
                
                memory_doc["_id"] = str(memory_doc["_id"])
                return Memory(**memory_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise
    
    async def list_memories(
        self,
        skip: int = 0,
        limit: int = 10,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[List[Memory], int]:
        """List memories with optional filtering"""
        try:
            collection = database.get_collection(self.collection_name)
            
            # Build query filter
            query_filter = {}
            if memory_type:
                query_filter["memory_type"] = memory_type
            if tags:
                query_filter["tags"] = {"$in": tags}
            
            # Get total count
            total_count = await collection.count_documents(query_filter)
            
            # Get memories
            cursor = collection.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)
            memory_docs = await cursor.to_list(length=limit)
            
            # Convert to Memory objects
            memories = []
            for doc in memory_docs:
                doc["_id"] = str(doc["_id"])
                memories.append(Memory(**doc))
            
            return memories, total_count
            
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            raise
    
    async def search_memories(self, search_request: MemorySearchRequest) -> List[Memory]:
        """Search memories using semantic similarity"""
        try:
            # Generate embedding for search query
            query_embedding = await self._generate_embedding(search_request.query)
            
            collection = database.get_collection(self.collection_name)
            
            # Build aggregation pipeline for vector search
            pipeline = [
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dot_product": {
                                        "$reduce": {
                                            "input": {"$range": [0, {"$size": "$embedding"}]},
                                            "initialValue": 0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {
                                                        "$multiply": [
                                                            {"$arrayElemAt": ["$embedding", "$$this"]},
                                                            {"$arrayElemAt": [query_embedding, "$$this"]}
                                                        ]
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": "$$dot_product"
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": search_request.similarity_threshold}}},
                {"$sort": {"similarity": -1}},
                {"$limit": search_request.limit}
            ]
            
            # Add additional filters
            if search_request.memory_type:
                pipeline.insert(-3, {"$match": {"memory_type": search_request.memory_type}})
            if search_request.tags:
                pipeline.insert(-3, {"$match": {"tags": {"$in": search_request.tags}}})
            
            # Execute search
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=search_request.limit)
            
            # Convert to Memory objects
            memories = []
            for doc in results:
                doc["_id"] = str(doc["_id"])
                memories.append(Memory(**doc))
            
            logger.info(f"Found {len(memories)} similar memories for query: {search_request.query}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    async def update_memory(self, memory_id: str, memory_update: MemoryUpdate) -> Optional[Memory]:
        """Update a specific memory"""
        try:
            collection = database.get_collection(self.collection_name)
            
            # Build update document
            update_doc = {}
            update_data = memory_update.dict(exclude_unset=True)
            
            if update_data:
                update_doc["$set"] = update_data
                
                # Regenerate embedding if content changed
                if "content" in update_data:
                    embedding = await self._generate_embedding(update_data["content"])
                    update_doc["$set"]["embedding"] = embedding
            
            if not update_doc:
                # No updates to apply
                return await self.get_memory(memory_id)
            
            # Update memory
            result = await collection.update_one(
                {"_id": ObjectId(memory_id)},
                update_doc
            )
            
            if result.modified_count > 0:
                return await self.get_memory(memory_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory"""
        try:
            collection = database.get_collection(self.collection_name)
            result = await collection.delete_one({"_id": ObjectId(memory_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted memory: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            collection = database.get_collection(self.collection_name)
            
            # Basic counts
            total_memories = await collection.count_documents({})
            
            # Memory types distribution
            type_pipeline = [
                {"$group": {"_id": "$memory_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            type_stats = await collection.aggregate(type_pipeline).to_list(length=None)
            
            # Recent activity
            recent_pipeline = [
                {"$match": {"timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}}},
                {"$count": "today_count"}
            ]
            recent_result = await collection.aggregate(recent_pipeline).to_list(length=1)
            today_count = recent_result[0]["today_count"] if recent_result else 0
            
            # Most accessed memories
            popular_pipeline = [
                {"$match": {"access_count": {"$gt": 0}}},
                {"$sort": {"access_count": -1}},
                {"$limit": 5},
                {"$project": {"content": {"$substr": ["$content", 0, 100]}, "access_count": 1}}
            ]
            popular_memories = await collection.aggregate(popular_pipeline).to_list(length=5)
            
            return {
                "total_memories": total_memories,
                "memories_today": today_count,
                "memory_types": {item["_id"]: item["count"] for item in type_stats},
                "popular_memories": popular_memories,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            raise
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence transformers"""
        try:
            # Import here to avoid startup dependency issues
            from sentence_transformers import SentenceTransformer
            
            # Use a lightweight model for embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text).tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 384  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
