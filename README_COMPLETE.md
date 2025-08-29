
# CPAS Master Agent - Complete System Package

## 🎯 Overview

The **CPAS Master Agent** is a comprehensive AI-powered system that combines intelligent task orchestration, OSINT capabilities, German voice interface, and advanced memory management. This package contains everything needed to run the complete system.

## 📦 Package Contents

### Core Components

#### 🧠 Master Agent System
- **Location:** `backend/services/master_agent.py`
- **Features:** Intelligent task orchestration, multi-agent collaboration, advanced reasoning
- **Dependencies:** FastAPI, SQLAlchemy, Celery

#### 🔍 OSINT Tools
- **Location:** `backend/osint/`
- **Modules:**
  - Social Media Intelligence (`social.py`)
  - Technical Reconnaissance (`technical.py`)
  - Breach Data Analysis (`breach.py`)
  - Media Intelligence (`media.py`)
- **Coordinator:** `osint_coordinator.py`

#### 🎤 German Voice Interface
- **Location:** `backend/services/german_voice.py`
- **Features:** Natural language processing, voice commands, German language support
- **Native App:** `Greta.app` (macOS)

#### 💾 MemOS Integration
- **Location:** `MemOS/`
- **Features:** Persistent memory, context awareness, learning capabilities
- **Configuration:** `MemOS/examples/data/config/`

#### 🖥️ Frontend Interface
- **Location:** `frontend/`
- **Technology:** Next.js, TypeScript, Electron
- **Components:** Master desk, agent cards, voice interface, system status

#### 🤖 HRM (Hierarchical Reasoning Module)
- **Location:** `hrm/`
- **Features:** Advanced reasoning, puzzle solving, pattern recognition
- **Models:** Neural architectures for complex reasoning tasks

### Installation Scripts

#### macOS
- `mac_install.sh` - Complete macOS installation
- `Greta.app` - Native macOS voice interface
- `Brewfile` - Homebrew dependencies

#### Linux
- `install.sh` - Linux installation script
- `deploy_master_agent.sh` - Deployment script

#### Universal
- `scripts/run_all.sh` - Start all services
- `scripts/stop_all.sh` - Stop all services
- `docker-compose.yml` - Container orchestration

### Documentation

#### Quick Start
- `QUICK_START.md` - 5-minute setup guide
- `README.md` - System overview
- `INSTALLATION_GUIDE.md` - Detailed installation

#### Comprehensive Guides
- `docs/CPAS_Mac_Install.md` - macOS-specific installation
- `docs/Quick_Start_Guide.md` - Getting started
- `docs/Troubleshooting_Guide.md` - Common issues
- `docs/Voice_Activation_Guide.md` - Voice interface setup
- `docs/Uninstall_Guide.md` - Clean removal

#### Technical Documentation
- `MASTER_AGENT_COMPLETE.md` - System architecture
- `PHASE1_STATUS.md` - Development phase 1
- `PHASE2_STATUS.md` - Development phase 2
- `PLAN.md` - Project roadmap

## 🚀 Installation

### Quick Install (Recommended)

#### macOS
```bash
chmod +x mac_install.sh
./mac_install.sh
```

#### Linux
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. **Clone and setup:**
   ```bash
   cd cpas_enhanced
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Install system dependencies:**
   ```bash
   # macOS
   brew bundle --file=Brewfile
   
   # Linux
   sudo apt-get update
   sudo apt-get install -y python3-dev nodejs npm docker.io postgresql redis-server
   ```

3. **Setup frontend:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Initialize MemOS:**
   ```bash
   python scripts/mem_init.py
   ```

5. **Start services:**
   ```bash
   ./scripts/run_all.sh
   ```

## 🎯 Usage

### Web Interface
- **URL:** http://localhost:3000
- **Features:** Master desk, agent management, system monitoring
- **Login:** No authentication required for local use

### Voice Interface
- **macOS:** Launch `Greta.app` from Applications
- **Linux:** Voice commands through web interface
- **Language:** German with English fallback

### API Access
- **Base URL:** http://localhost:8000
- **Documentation:** http://localhost:8000/docs
- **Authentication:** API key based (see config)

### Command Line
```bash
# Start system
./scripts/run_all.sh

# Stop system
./scripts/stop_all.sh

# Run demo
python demo_phase2.py

# Check status
curl http://localhost:8000/health
```

## 🔧 Configuration

### Core Settings
- `config/logging_conf.yaml` - Logging configuration
- `backend/config.py` - Backend settings
- `frontend/next.config.js` - Frontend configuration

### MemOS Configuration
- `MemOS/examples/data/config/` - Memory system settings
- Supports multiple backends: Qdrant, Neo4j, PostgreSQL

### Voice Settings
- `Greta.app/Contents/Resources/config/greta_config.yaml`
- Language models, voice synthesis, recognition settings

## 🏗️ Architecture

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Master Agent  │    │   MemOS         │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Memory)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice UI      │    │   OSINT Tools   │    │   HRM Module    │
│   (Greta.app)   │    │   (Multi-agent) │    │   (Reasoning)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow
1. **Input:** Voice, web interface, or API
2. **Processing:** Master agent coordinates specialized agents
3. **Memory:** MemOS stores and retrieves context
4. **Reasoning:** HRM handles complex logic
5. **Output:** Structured responses via multiple channels

## 🛠️ Development

### Adding Custom Agents
```python
# backend/specialized_agents/my_agent.py
from .base_specialized_agent import BaseSpecializedAgent

class MyAgent(BaseSpecializedAgent):
    def process_task(self, task):
        # Your logic here
        return result
```

### Extending OSINT
```python
# backend/osint/my_osint.py
from .base import BaseOSINTTool

class MyOSINTTool(BaseOSINTTool):
    def gather_intelligence(self, target):
        # Your OSINT logic
        return intelligence
```

### Frontend Components
```typescript
// frontend/components/MyComponent.tsx
import React from 'react';

export const MyComponent: React.FC = () => {
    return <div>My Custom Component</div>;
};
```

## 📊 Monitoring

### Logs
- `logs/` - All system logs
- `backend_service.log` - Backend operations
- `ollama_service.log` - AI model operations
- `installation.log` - Setup process

### Health Checks
```bash
# System health
curl http://localhost:8000/health

# Service status
curl http://localhost:8000/status

# Memory usage
curl http://localhost:8000/memory/stats
```

### Performance Metrics
- CPU usage monitoring
- Memory consumption tracking
- Response time analysis
- Agent performance metrics

## 🔒 Security

### Local Deployment
- No external network access required
- All data stays on your machine
- Optional API key authentication

### Production Deployment
- HTTPS enforcement
- API rate limiting
- Input validation
- Secure credential storage

## 🆘 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
lsof -i :3000 -i :8000

# Kill conflicting processes
sudo kill -9 $(lsof -t -i:3000)
```

#### Memory Issues
```bash
# Check system resources
htop

# Restart services
./scripts/stop_all.sh
./scripts/run_all.sh
```

#### Voice Interface Problems
- Check microphone permissions
- Verify audio drivers
- Restart Greta.app

### Getting Help
1. Check `docs/Troubleshooting_Guide.md`
2. Review logs in `logs/` directory
3. Run diagnostic: `python tests/test_phase2.py`
4. Submit issues with log files

## 🚀 Deployment Options

### Local Development
- Default configuration
- All services on localhost
- SQLite database

### Docker Deployment
```bash
docker-compose up -d
```

### Production Setup
- PostgreSQL database
- Redis for caching
- Nginx reverse proxy
- SSL certificates

## 📈 Roadmap

### Phase 3 (Planned)
- [ ] Multi-language support
- [ ] Advanced OSINT modules
- [ ] Mobile application
- [ ] Cloud deployment options

### Phase 4 (Future)
- [ ] Federated learning
- [ ] Advanced reasoning models
- [ ] Enterprise features
- [ ] API marketplace

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests: `pytest tests/`
5. Submit pull request

### Code Standards
- Python: PEP 8, type hints
- TypeScript: ESLint, Prettier
- Documentation: Markdown, docstrings

## 📄 License

This project is licensed under the MIT License. See individual component licenses:
- MemOS: See `MemOS/LICENSE`
- HRM: See `hrm/LICENSE`
- Other components: MIT License

## 🙏 Acknowledgments

- MemOS team for memory system
- HRM researchers for reasoning module
- Open source community
- Beta testers and contributors

---

**🎉 You now have the complete CPAS Master Agent system!**

Start with `QUICK_START.md` for immediate setup, or dive into the `docs/` folder for comprehensive guides.

For support, check the troubleshooting guides or submit an issue with your logs.

**Happy exploring! 🚀**
