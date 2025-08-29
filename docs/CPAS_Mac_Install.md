
# CPAS Master Agent (Greta) - Mac Installation Guide

## Overview

The CPAS Master Agent, codenamed "Greta," is a comprehensive AI assistant system featuring:
- German-accented voice personality with customizable name and behavior
- Complete OSINT intelligence suite
- Mac-native UI with Tufte-style graphics
- Voice activation with wake-word detection
- FastAPI backend, Next.js frontend, MongoDB database, and Ollama LLMs

## System Requirements

- **macOS**: 10.15 (Catalina) or later
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free disk space
- **Processor**: Intel x64 or Apple Silicon (M1/M2/M3)
- **Internet**: Required for initial setup and model downloads

## Installation Methods

Choose one of the following installation methods:

### Method 1: Drag-and-Drop Installer (Recommended)

This is the easiest method for most users.

#### Step 1: Download and Install

1. Download `Greta-CPAS-Master-Agent-v1.0.0.dmg`
2. Double-click the DMG file to mount it
3. Drag `Greta.app` to the `Applications` folder
4. Eject the DMG file

#### Step 2: First Launch

1. Open `Applications` folder
2. Right-click on `Greta.app` and select "Open"
3. Click "Open" when macOS asks about running an unsigned application
4. The dependency installer will launch automatically

#### Step 3: Complete Setup

The app will automatically:
- Install Homebrew (if not present)
- Install Python, Node.js, MongoDB, and Ollama
- Download required AI models
- Configure all services
- Launch the Greta interface

**Expected Installation Time**: 15-30 minutes (depending on internet speed)

### Method 2: Terminal Installation (Advanced Users)

Use this method if you prefer manual control or the drag-and-drop installer fails.

#### Prerequisites Check

First, verify your system meets the requirements:

```bash
# Check macOS version
sw_vers

# Check available disk space (should show >10GB free)
df -h

# Check if Xcode Command Line Tools are installed
xcode-select --version
```

If Command Line Tools are missing, install them:

```bash
xcode-select --install
```

#### Step 1: Install Homebrew

```bash
# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# For Apple Silicon Macs, add Homebrew to PATH
if [[ $(uname -m) == "arm64" ]]; then
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi
```

**Expected Output**: Homebrew installation messages, may take 5-10 minutes

#### Step 2: Install System Dependencies

```bash
# Update Homebrew
brew update

# Install core dependencies
brew install python@3.11 node@18 mongodb-community ollama portaudio ffmpeg git pipx

# Install optional tools
brew install wget curl jq espeak festival mongodb-database-tools

# Install MongoDB Compass (optional GUI)
brew install --cask mongodb-compass
```

**Expected Output**: Package installation messages, may take 10-15 minutes

#### Step 3: Download and Extract CPAS

```bash
# Create installation directory
mkdir -p ~/Applications/CPAS
cd ~/Applications/CPAS

# Download CPAS source (replace with actual download URL)
curl -L -o cpas-master-agent.zip "https://github.com/cpas-project/greta/archive/main.zip"
unzip cpas-master-agent.zip
cd cpas-master-agent-main
```

#### Step 4: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected Output**: Python package installation messages

#### Step 5: Set Up Node.js Environment

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Build production version
npm run build

# Return to main directory
cd ..
```

**Expected Output**: Node.js package installation and build messages

#### Step 6: Configure MongoDB

```bash
# Start MongoDB service
brew services start mongodb-community

# Wait for MongoDB to start
sleep 5

# Initialize database
mongosh --eval "
use cpas_db;
db.createCollection('agents');
db.createCollection('conversations');
db.createCollection('memory');
db.createCollection('osint_cache');
print('Database initialized successfully');
"
```

**Expected Output**: MongoDB connection and database creation messages

#### Step 7: Set Up Ollama and AI Models

```bash
# Start Ollama service
brew services start ollama

# Wait for Ollama to start
sleep 5

# Download required AI models (this may take 20-30 minutes)
ollama pull deepseek-r1:7b
ollama pull llama3.2:3b

# Verify models are installed
ollama list
```

**Expected Output**: Model download progress and final model list

#### Step 8: Configure Auto-Start Services

```bash
# Create launch agents directory
mkdir -p ~/Library/LaunchAgents

# Create MongoDB launch agent
cat > ~/Library/LaunchAgents/com.cpas.mongodb.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cpas.mongodb</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/mongod</string>
        <string>--config</string>
        <string>/usr/local/etc/mongod.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Create Ollama launch agent
cat > ~/Library/LaunchAgents/com.cpas.ollama.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cpas.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load launch agents
launchctl load ~/Library/LaunchAgents/com.cpas.mongodb.plist
launchctl load ~/Library/LaunchAgents/com.cpas.ollama.plist
```

#### Step 9: Create Startup Script

```bash
# Create startup script
cat > ~/Applications/CPAS/start_greta.sh << 'EOF'
#!/bin/bash
# CPAS Master Agent Startup Script

set -e

CPAS_DIR="$HOME/Applications/CPAS/cpas-master-agent-main"
LOGS_DIR="$HOME/Library/Logs/Greta"

mkdir -p "$LOGS_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGS_DIR/greta.log"
}

# Start backend
log "Starting Python backend..."
cd "$CPAS_DIR"
source venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 > "$LOGS_DIR/backend.log" 2>&1 &

# Start frontend
log "Starting Next.js frontend..."
cd "$CPAS_DIR/frontend"
npm start > "$LOGS_DIR/frontend.log" 2>&1 &

# Wait for services to start
sleep 5

# Open browser
log "Opening Greta interface..."
open "http://localhost:3000"

log "Greta is now running! Access at http://localhost:3000"
EOF

# Make script executable
chmod +x ~/Applications/CPAS/start_greta.sh
```

#### Step 10: Test Installation

```bash
# Run the startup script
~/Applications/CPAS/start_greta.sh
```

**Expected Output**: Service startup messages and browser opening to Greta interface

## Voice Activation & Name Customization

### Changing Greta's Name

You can easily customize your AI assistant's name and personality:

#### Method 1: Configuration File (Recommended)

1. Open the configuration file in nano:

```bash
nano ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml
```

2. Modify the following settings:

```yaml
agent:
  name: "Your_Custom_Name"        # Change this to your preferred name
  personality: "friendly"         # Options: professional, friendly, casual, formal
  voice_accent: "american"        # Options: german, british, american, australian
```

3. Save and exit nano: `Ctrl+X`, then `Y`, then `Enter`

4. Restart Greta for changes to take effect

#### Method 2: Web Interface

1. Open Greta at `http://localhost:3000`
2. Click on "Settings" in the top menu
3. Navigate to "Agent Configuration"
4. Change the name and personality settings
5. Click "Save Changes"

### Voice Activation Setup

#### Enable Wake-Word Detection

1. Edit the configuration file:

```bash
nano ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml
```

2. Configure voice settings:

```yaml
voice:
  wake_word: "Your_Custom_Name"   # Use your chosen name or "Hey Assistant"
  wake_word_enabled: true         # Enable voice activation
  continuous_listening: false     # Set to true for always-on listening
  voice_feedback: true           # Enable spoken responses
```

3. Save and restart Greta

#### Custom Wake Words

You can set multiple wake words by adding them to the configuration:

```yaml
wake_words:
  - "Hey Greta"
  - "Computer"
  - "Assistant"
  - "AI Helper"
```

#### Voice Commands

Once voice activation is enabled, you can use these commands:

- **Wake up**: Say your wake word (e.g., "Greta")
- **Ask questions**: "What's the weather like?"
- **OSINT queries**: "Search for information about [topic]"
- **System control**: "Open applications" or "Check system status"
- **Sleep mode**: "Go to sleep" or "Stop listening"

### Microphone Permissions

macOS will request microphone permissions when you first use voice features:

1. Click "OK" when prompted for microphone access
2. If you missed the prompt, go to:
   - System Preferences → Security & Privacy → Privacy → Microphone
   - Check the box next to "Greta" or your Terminal application

## Troubleshooting

### Common Issues and Solutions

| Symptom | Probable Cause | Fix |
|---------|---------------|-----|
| "Command not found: brew" | Homebrew not in PATH | Run: `eval "$(/opt/homebrew/bin/brew shellenv)"` |
| MongoDB connection failed | MongoDB not running | Run: `brew services start mongodb-community` |
| Ollama models not loading | Ollama service stopped | Run: `brew services start ollama` |
| Voice activation not working | Microphone permissions | Check System Preferences → Privacy → Microphone |
| Frontend won't start | Node.js dependencies missing | Run: `cd frontend && npm install` |
| Python import errors | Virtual environment not activated | Run: `source venv/bin/activate` |
| Port 8000 already in use | Another service using port | Run: `lsof -ti:8000 \| xargs kill -9` |
| "App can't be opened" error | Gatekeeper blocking app | Right-click app → Open, then click Open |

### Checking Service Status

```bash
# Check if services are running
brew services list | grep -E "(mongodb|ollama)"

# Check process status
ps aux | grep -E "(mongod|ollama|uvicorn|next)"

# Check logs
tail -f ~/Library/Logs/Greta/greta.log
```

### Resetting Configuration

If you need to reset Greta to default settings:

```bash
# Backup current config
cp ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml ~/greta_config_backup.yaml

# Download fresh config
curl -o ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml \
  "https://raw.githubusercontent.com/cpas-project/greta/main/config/greta_config.yaml"
```

## Customization Options

### Personality Traits

Edit the configuration file to customize Greta's behavior:

```yaml
agent:
  personality: "professional"     # professional, friendly, casual, formal
  response_style: "detailed"     # brief, detailed, conversational
  voice_accent: "german"         # german, british, american, australian
  voice_speed: 1.0              # 0.5 - 2.0 (speech rate)
  voice_volume: 0.8             # 0.0 - 1.0 (volume level)
```

### UI Themes

Greta supports multiple UI themes:

1. Open `http://localhost:3000`
2. Go to Settings → Appearance
3. Choose from:
   - **Tufte Classic**: Minimal, data-focused design
   - **Dark Mode**: Easy on the eyes for night use
   - **High Contrast**: Better accessibility
   - **Compact**: More information density

### Adding Custom OSINT Tools

You can extend Greta's OSINT capabilities:

1. Create a new Python file in `backend/osint_tools/`
2. Follow the existing tool patterns
3. Register the tool in `backend/routers/osint.py`
4. Restart the backend service

### API Integrations

Add your API keys for enhanced capabilities:

```yaml
integrations:
  openai_api_key: "YOUR_OPENAI_KEY"
  anthropic_api_key: "YOUR_ANTHROPIC_KEY"
  enable_web_search: true
  enable_file_analysis: true
```

## Uninstallation

### Complete Removal

To completely remove Greta and all components:

```bash
# Stop all services
brew services stop mongodb-community
brew services stop ollama
pkill -f "uvicorn.*main:app"
pkill -f "next.*start"

# Remove launch agents
launchctl unload ~/Library/LaunchAgents/com.cpas.mongodb.plist
launchctl unload ~/Library/LaunchAgents/com.cpas.ollama.plist
rm ~/Library/LaunchAgents/com.cpas.mongodb.plist
rm ~/Library/LaunchAgents/com.cpas.ollama.plist

# Remove application files
rm -rf ~/Applications/CPAS
rm -rf /Applications/Greta.app  # If using drag-and-drop installer

# Remove logs and data (optional)
rm -rf ~/Library/Logs/Greta

# Remove Homebrew packages (optional - only if not used by other apps)
brew uninstall mongodb-community ollama python@3.11 node@18
```

### Partial Removal (Keep Dependencies)

To remove only Greta but keep the dependencies for other uses:

```bash
# Stop Greta services
pkill -f "uvicorn.*main:app"
pkill -f "next.*start"

# Remove application files
rm -rf ~/Applications/CPAS
rm -rf /Applications/Greta.app

# Remove logs
rm -rf ~/Library/Logs/Greta
```

## Support and Documentation

- **GitHub Repository**: https://github.com/cpas-project/greta
- **Documentation**: https://docs.cpas-project.com
- **Issues**: Report bugs at GitHub Issues
- **Community**: Join our Discord server
- **Email Support**: support@cpas-project.com

## Version Information

- **Version**: 1.0.0
- **Release Date**: August 27, 2025
- **Compatibility**: macOS 10.15+
- **License**: MIT License

---

*This installation guide was generated for CPAS Master Agent v1.0.0. For the latest version and updates, visit our GitHub repository.*
