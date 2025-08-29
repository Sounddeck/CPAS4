
# CPAS Master Agent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- macOS 10.15+ or Linux Ubuntu 20.04+
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Installation

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

### First Run

1. **Start the system:**
   ```bash
   ./scripts/run_all.sh
   ```

2. **Access interfaces:**
   - Web Interface: http://localhost:3000
   - API: http://localhost:8000
   - Voice Interface: Launch Greta.app (macOS)

3. **Test the system:**
   ```bash
   python demo_phase2.py
   ```

### Key Features

#### 🧠 Master Agent
- Intelligent task orchestration
- Multi-agent collaboration
- Advanced reasoning capabilities

#### 🔍 OSINT Tools
- Social media monitoring
- Technical reconnaissance
- Breach data analysis
- Media intelligence

#### 🎤 German Voice Interface
- Natural language processing
- Voice commands and responses
- Integrated with all system functions

#### 💾 MemOS Integration
- Persistent memory system
- Context-aware responses
- Learning from interactions

#### 🖥️ Mac Native UI
- Native macOS application (Greta.app)
- System tray integration
- Keyboard shortcuts

### Common Commands

```bash
# Start all services
./scripts/run_all.sh

# Stop all services
./scripts/stop_all.sh

# View logs
tail -f logs/*.log

# Update system
git pull && pip install -r requirements.txt
```

### Troubleshooting

#### Services won't start
```bash
# Check if ports are available
lsof -i :3000 -i :8000

# Restart services
./scripts/stop_all.sh
./scripts/run_all.sh
```

#### Voice interface issues
- Ensure microphone permissions are granted
- Check audio input/output settings
- Restart Greta.app

#### Memory issues
- Increase Docker memory allocation
- Close unnecessary applications
- Check system resources: `htop`

### Next Steps

1. **Explore the documentation:**
   - `docs/` folder contains detailed guides
   - `INSTALLATION_GUIDE.md` for advanced setup
   - `MASTER_AGENT_COMPLETE.md` for system architecture

2. **Customize your setup:**
   - Edit `config/` files for your preferences
   - Add custom agents in `backend/specialized_agents/`
   - Modify UI in `frontend/components/`

3. **Join the community:**
   - Report issues on GitHub
   - Contribute improvements
   - Share your use cases

### Support

- 📖 Full documentation in `docs/` folder
- 🐛 Issues: Check logs in `logs/` directory
- 💬 Community: GitHub Discussions
- 📧 Support: See README.md for contact info

---

**Ready to explore? Start with the web interface at http://localhost:3000**
