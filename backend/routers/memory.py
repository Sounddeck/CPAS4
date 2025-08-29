
"""
Memory management API routes
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from loguru import logger

from models.memory import Memory, MemoryCreate, MemoryUpdate, MemoryResponse, MemorySearchRequest
from services.memory_service import MemoryService

router = APIRouter()

async def get_memory_service() -> MemoryService:
    """Dependency to get memory service instance"""
    return MemoryService()

@router.post("/", response_model=MemoryResponse)
async def create_memory(
    memory_data: MemoryCreate,
    service: MemoryService = Depends(get_memory_service)
):
    """Create a new memory"""
    try:
        memory = await service.create_memory(memory_data)
        return MemoryResponse(
            success=True,
            message="Memory created successfully",
            memory=memory
        )
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    service: MemoryService = Depends(get_memory_service)
):
    """Get a specific memory by ID"""
    try:
        memory = await service.get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return MemoryResponse(
            success=True,
            message="Memory retrieved successfully",
            memory=memory
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=MemoryResponse)
async def list_memories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    memory_type: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    service: MemoryService = Depends(get_memory_service)
):
    """List memories with optional filtering"""
    try:
        memories, total_count = await service.list_memories(
            skip=skip,
            limit=limit,
            memory_type=memory_type,
            tags=tags
        )
        
        return MemoryResponse(
            success=True,
            message=f"Retrieved {len(memories)} memories",
            memories=memories,
            total_count=total_count
        )
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=MemoryResponse)
async def search_memories(
    search_request: MemorySearchRequest,
    service: MemoryService = Depends(get_memory_service)
):
    """Search memories using semantic similarity"""
    try:
        memories = await service.search_memories(search_request)
        
        return MemoryResponse(
            success=True,
            message=f"Found {len(memories)} similar memories",
            memories=memories
        )
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    service: MemoryService = Depends(get_memory_service)
):
    """Update a specific memory"""
    try:
        memory = await service.update_memory(memory_id, memory_update)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return MemoryResponse(
            success=True,
            message="Memory updated successfully",
            memory=memory
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{memory_id}", response_model=MemoryResponse)
async def delete_memory(
    memory_id: str,
    service: MemoryService = Depends(get_memory_service)
):
    """Delete a specific memory"""
    try:
        success = await service.delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return MemoryResponse(
            success=True,
            message="Memory deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_memory_stats(
    service: MemoryService = Depends(get_memory_service)
):
    """Get memory system statistics"""
    try:
        stats = await service.get_memory_stats()
        return {
            "success": True,
            "message": "Memory statistics retrieved",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
