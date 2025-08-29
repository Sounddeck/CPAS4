
"""
System management API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger
import psutil
import asyncio
from datetime import datetime

from config import settings

router = APIRouter()

@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            },
            "process": {
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            },
            "phase": "Phase 1: Foundation + Memory System"
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_system_config():
    """Get system configuration"""
    try:
        # Return non-sensitive configuration
        config = {
            "mongodb_db_name": settings.mongodb_db_name,
            "ollama_base_url": settings.ollama_base_url,
            "default_model": settings.default_model,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "debug": settings.debug,
            "memos_backend": settings.memos_backend,
            "memos_collection": settings.memos_collection,
            "voice_enabled": settings.voice_enabled,
            "max_agents": settings.max_agents,
            "agent_timeout": settings.agent_timeout
        }
        
        return {
            "success": True,
            "message": "System configuration retrieved",
            "config": config
        }
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_system_info():
    """Get system information"""
    try:
        import platform
        import sys
        
        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": sys.version,
                "executable": sys.executable
            },
            "cpas": {
                "version": "1.0.0",
                "phase": "Phase 1: Foundation + Memory System",
                "components": [
                    "MongoDB Database",
                    "MemOS Memory System",
                    "Ollama Local LLMs",
                    "FastAPI Backend",
                    "Memory Management",
                    "LLM Integration"
                ],
                "future_components": [
                    "HRM Reasoning System",
                    "Voice Input/Output",
                    "Dynamic Agent Building",
                    "API-based LLMs",
                    "Advanced Learning"
                ]
            }
        }
        
        return {
            "success": True,
            "message": "System information retrieved",
            "info": info
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_system():
    """Restart the system (development only)"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Restart only available in debug mode")
    
    try:
        logger.info("System restart requested")
        
        # Schedule restart after response
        async def delayed_restart():
            await asyncio.sleep(1)
            import os
            os._exit(0)
        
        asyncio.create_task(delayed_restart())
        
        return {
            "success": True,
            "message": "System restart initiated"
        }
    except Exception as e:
        logger.error(f"Failed to restart system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_recent_logs():
    """Get recent system logs"""
    try:
        # This is a placeholder - implement actual log retrieval
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "System running normally",
                "component": "system"
            }
        ]
        
        return {
            "success": True,
            "message": "Recent logs retrieved",
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
