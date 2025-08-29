
# Enhanced CPAS - Phase 1: Foundation + Memory System

## Overview

Enhanced Comprehensive Personal AI System (CPAS) with advanced memory management, local LLM support, and extensible architecture for future AI capabilities.

### Phase 1 Components

✅ **MongoDB Database**
- Document-based storage for memories, conversations, and system data
- Optimized indexes for fast retrieval
- Scalable architecture for future growth

✅ **MemOS Memory System**
- Semantic memory storage and retrieval
- Vector embeddings for similarity search
- Importance scoring and access tracking
- Memory consolidation and cleanup

✅ **Local LLM Support (Ollama)**
- DeepSeek-R1 7B for reasoning tasks
- Llama 3.2 3B for general conversations
- Mixtral 8x7B for complex problem solving
- Model switching and management

✅ **FastAPI Backend**
- Async/await architecture for high performance
- RESTful API for all system interactions
- Comprehensive error handling and logging
- Health monitoring and system status

✅ **Integration Foundation**
- Prepared structure for HRM reasoning system
- Voice capability infrastructure ready
- Agent building system foundation
- API-based LLM support framework

## Quick Start

### 1. Installation

```bash
cd /home/ubuntu/cpas_enhanced
chmod +x install.sh
./install.sh
```

### 2. Activate Environment

```bash
source venv/bin/activate
```

### 3. Start Backend

```bash
cd backend
python main.py
```

### 4. Access API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/api/v1/system/status

## API Endpoints

### Memory Management
- `POST /api/v1/memory/` - Create new memory
- `GET /api/v1/memory/{id}` - Get specific memory
- `GET /api/v1/memory/` - List memories with filtering
- `POST /api/v1/memory/search` - Semantic memory search
- `PUT /api/v1/memory/{id}` - Update memory
- `DELETE /api/v1/memory/{id}` - Delete memory
- `GET /api/v1/memory/stats/summary` - Memory statistics

### LLM Interactions
- `POST /api/v1/llm/generate` - Generate text
- `POST /api/v1/llm/chat` - Chat with context
- `GET /api/v1/llm/models` - List available models
- `GET /api/v1/llm/models/{name}` - Get model info
- `POST /api/v1/llm/models/{name}/pull` - Download model
- `DELETE /api/v1/llm/models/{name}` - Remove model

### System Management
- `GET /api/v1/system/status` - System status and metrics
- `GET /api/v1/system/config` - System configuration
- `GET /api/v1/system/info` - System information
- `POST /api/v1/system/restart` - Restart system (debug mode)

## Configuration

Environment variables in `.env`:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/cpas_enhanced
MONGODB_DB_NAME=cpas_enhanced

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# MemOS Configuration
MEMOS_BACKEND=mongodb
MEMOS_COLLECTION=memories
MEMOS_INDEX_COLLECTION=memory_index
```

## Memory System Features

### Semantic Search
```python
# Search for relevant memories
search_request = {
    "query": "How to optimize database performance?",
    "limit": 5,
    "similarity_threshold": 0.7
}
```

### Memory Types
- `general` - General knowledge and facts
- `conversation` - Chat interactions
- `llm_interaction` - LLM Q&A pairs
- `system` - System events and logs
- `feature` - Feature descriptions
- `capability` - System capabilities

### Importance Scoring
- `0.9-1.0` - Critical system information
- `0.7-0.8` - Important features and capabilities
- `0.5-0.6` - Regular interactions and content
- `0.3-0.4` - Low priority information
- `0.0-0.2` - Temporary or disposable content

## LLM Model Management

### Available Models
- **DeepSeek-R1 7B** - Reasoning and problem solving
- **Llama 3.2 3B** - General conversation and tasks
- **Mixtral 8x7B** - Complex analysis and coding

### Model Operations
```bash
# Check model status
curl http://localhost:8000/api/v1/llm/models

# Pull new model
curl -X POST http://localhost:8000/api/v1/llm/models/llama3.1:8b/pull

# Generate text
curl -X POST http://localhost:8000/api/v1/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing", "model": "llama3.2:3b"}'
```

## Development

### Project Structure
```
cpas_enhanced/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   └── services/            # Business logic services
├── scripts/
│   └── mem_init.py          # MemOS initialization
├── MemOS/                   # Cloned MemOS repository
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── install.sh              # Installation script
```

### Adding New Features

1. **Models**: Add Pydantic models in `backend/models/`
2. **Routes**: Create API routes in `backend/routers/`
3. **Services**: Implement business logic in `backend/services/`
4. **Database**: Update indexes in `database.py`

## Monitoring and Logs

### Health Checks
```bash
# Overall system health
curl http://localhost:8000/health

# LLM service health
curl http://localhost:8000/api/v1/llm/health

# System metrics
curl http://localhost:8000/api/v1/system/status
```

### Log Files
- `ollama_deepseek.log` - DeepSeek model download
- `ollama_llama.log` - Llama model download
- `ollama_mixtral.log` - Mixtral model download

## Future Phases

### Phase 2: HRM Integration + Voice
- [ ] HRM reasoning system integration
- [ ] Voice input/output capabilities
- [ ] Speech recognition and synthesis
- [ ] Voice command processing

### Phase 3: Dynamic Agents
- [ ] Agent creation and management
- [ ] Specialized agent types
- [ ] Agent communication protocols
- [ ] Task delegation and coordination

### Phase 4: Advanced Learning
- [ ] Continuous learning from interactions
- [ ] Knowledge graph construction
- [ ] Adaptive behavior patterns
- [ ] Personalization engine

### Phase 5: API Integration
- [ ] OpenAI API integration
- [ ] Anthropic Claude integration
- [ ] Google Gemini integration
- [ ] Model routing and fallbacks

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   sudo systemctl status mongod
   sudo systemctl start mongod
   ```

2. **Ollama Models Not Loading**
   ```bash
   ollama list
   ollama pull llama3.2:3b
   ```

3. **Python Dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Port Conflicts**
   - MongoDB: 27017
   - Ollama: 11434
   - FastAPI: 8000

### Performance Optimization

1. **Memory Usage**: Monitor with `/api/v1/system/status`
2. **Database Indexes**: Ensure proper indexing for queries
3. **Model Selection**: Use appropriate model size for task
4. **Batch Operations**: Use bulk operations for large datasets

## Support and Documentation

- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **System Status**: http://localhost:8000/api/v1/system/info
- **Memory Stats**: http://localhost:8000/api/v1/memory/stats/summary

## Credits

- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database
- **Ollama**: Local LLM runtime
- **MemOS**: Memory management system
- **Motor**: Async MongoDB driver
- **Sentence Transformers**: Text embeddings

---

**Enhanced CPAS v1.0.0** - Phase 1: Foundation + Memory System
Built with ❤️ for advanced AI capabilities
