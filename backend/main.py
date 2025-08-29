
"""
Enhanced CPAS Backend - FastAPI Server
Phase 1: Foundation + Memory System
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger

from routers import memory, llm, system, agent, voice, reasoning, master_agent, osint
from config import Settings
from database import Database

# Load environment variables
load_dotenv()

# Global database instance
db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Enhanced CPAS Backend...")
    
    # Initialize database connection
    await db.connect()
    
    # Initialize MemOS
    from scripts.mem_init import initialize_memos
    await initialize_memos()
    
    # Initialize Master Agent and Orchestrator
    from services.llm_service import LLMService
    from services.memory_service import MemoryService
    from routers.master_agent import initialize_master_agent_router
    
    try:
        llm_service = LLMService()
        memory_service = MemoryService()
        await initialize_master_agent_router(llm_service, memory_service)
        logger.info("🎭 Master Agent and Orchestrator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Master Agent: {e}")
    
    logger.info("✅ Backend startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Enhanced CPAS Backend...")
    await db.disconnect()
    logger.info("✅ Backend shutdown complete!")

# Create FastAPI app
app = FastAPI(
    title="Enhanced CPAS Backend",
    description="Comprehensive Personal AI System with Memory, LLM, and Agent capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["LLM"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(agent.router, prefix="/api/v1", tags=["Agent"])
app.include_router(voice.router, prefix="/api/v1", tags=["Voice"])
app.include_router(reasoning.router, prefix="/api/v1", tags=["Reasoning"])
app.include_router(master_agent.router, prefix="/api/v1", tags=["Master Agent"])
app.include_router(osint.router, prefix="/api/v1", tags=["OSINT"])

# Include Phase 3 agent management router
from routers import agents
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agent Management"])

# Include new enhanced routers
from routers import workflows, integrations, proactive
app.include_router(workflows.router, prefix="/api/v1", tags=["Workflows"])
app.include_router(integrations.router, prefix="/api/v1", tags=["Integrations"])
app.include_router(proactive.router, prefix="/api/v1", tags=["Proactive AI"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced CPAS Backend API",
        "version": "1.0.0",
        "status": "running",
        "phase": "Phase 3: Dynamic Agent Building + Multi-Agent Coordination",
        "features": [
            "Dynamic Agent Templates",
            "Specialized Agent Types",
            "Multi-Agent Task Delegation",
            "Agent Collaboration",
            "Conflict Resolution",
            "Shared Knowledge Base",
            "Agent Lifecycle Management"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await db.health_check()
        
        # Check Ollama connection
        from services.llm_service import LLMService
        llm_service = LLMService()
        ollama_status = await llm_service.health_check()
        
        return {
            "status": "healthy",
            "database": db_status,
            "ollama": ollama_status,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    import uvicorn
    settings = Settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
