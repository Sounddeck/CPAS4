from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="CPAS Master Agent - Greta", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "🇩🇪 Guten Tag! I am Greta, your CPAS Master Agent",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "personality": "German AI Research Assistant",
        "capabilities": [
            "OSINT Intelligence Gathering",
            "Hierarchical Reasoning (HRM)",
            "Voice Interface (German-accented)",
            "Multi-Agent Coordination",
            "Technical Analysis",
            "Research & Investigation"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "agent": "Greta", "version": "1.0.0"}

@app.get("/api/v1/agent/status")
def agent_status():
    return {
        "agent_name": "Greta",
        "personality": "German AI Researcher",
        "accent": "German-English",
        "status": "ready",
        "capabilities": {
            "osint": "Social, Technical, Breach, Media Intelligence",
            "reasoning": "4-level Hierarchical Reasoning Machine",
            "voice": "German-accented speech synthesis",
            "coordination": "Multi-agent task delegation"
        }
    }

@app.get("/api/v1/chat")
def chat_endpoint():
    return {
        "message": "Chat endpoint ready",
        "instructions": "Send POST requests here to chat with Greta"
    }

if __name__ == "__main__":
    print("🚀 Starting CPAS Master Agent - Greta")
    print("🇩🇪 German AI Research Assistant initializing...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
