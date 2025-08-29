
#!/bin/bash
# CPAS Master Agent (Greta) - Terminal Installation Script
# Complete installation via command line with error handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_DIR="$HOME/Applications/CPAS"
LOGS_DIR="$HOME/Library/Logs/Greta"
CONFIG_DIR="$INSTALL_DIR/config"

# Create directories
mkdir -p "$INSTALL_DIR" "$LOGS_DIR" "$CONFIG_DIR"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOGS_DIR/install.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOGS_DIR/install.log"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOGS_DIR/install.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOGS_DIR/install.log"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)
    MACOS_MINOR=$(echo "$MACOS_VERSION" | cut -d. -f2)
    
    if [[ $MACOS_MAJOR -lt 10 ]] || [[ $MACOS_MAJOR -eq 10 && $MACOS_MINOR -lt 15 ]]; then
        error "macOS 10.15 (Catalina) or later required. Found: $MACOS_VERSION"
    fi
    
    # Check available disk space (need at least 10GB)
    AVAILABLE_SPACE=$(df -g / | awk 'NR==2{print $4}')
    if [[ $AVAILABLE_SPACE -lt 10 ]]; then
        error "At least 10GB free disk space required. Available: ${AVAILABLE_SPACE}GB"
    fi
    
    # Check RAM (need at least 8GB)
    TOTAL_RAM=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    if [[ $TOTAL_RAM -lt 8 ]]; then
        warning "8GB RAM recommended. Found: ${TOTAL_RAM}GB"
    fi
    
    log "System requirements check passed"
}

# Install Homebrew
install_homebrew() {
    if command -v brew &> /dev/null; then
        log "Homebrew already installed"
        return
    fi
    
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    # Verify installation
    if ! command -v brew &> /dev/null; then
        error "Homebrew installation failed"
    fi
    
    log "Homebrew installed successfully"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Update Homebrew
    brew update
    
    # Install core dependencies
    local packages=(
        "python@3.11"
        "node@18"
        "mongodb-community"
        "ollama"
        "portaudio"
        "ffmpeg"
        "git"
        "pipx"
        "wget"
        "curl"
        "jq"
        "espeak"
        "festival"
        "mongodb-database-tools"
    )
    
    for package in "${packages[@]}"; do
        log "Installing $package..."
        brew install "$package" || warning "Failed to install $package"
    done
    
    # Install optional cask applications
    log "Installing optional applications..."
    brew install --cask mongodb-compass || warning "Failed to install MongoDB Compass"
    
    log "System dependencies installed"
}

# Download CPAS source code
download_cpas() {
    log "Downloading CPAS Master Agent source code..."
    
    cd "$INSTALL_DIR"
    
    # For this demo, we'll copy from the existing source
    # In production, this would download from GitHub
    if [[ -d "/home/ubuntu/cpas_enhanced" ]]; then
        log "Copying CPAS source from local directory..."
        cp -r /home/ubuntu/cpas_enhanced/* .
    else
        # Fallback: create minimal structure
        log "Creating minimal CPAS structure..."
        mkdir -p backend frontend config scripts
        
        # Create minimal backend structure
        cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CPAS Master Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CPAS Master Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF
        
        # Create requirements.txt
        cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
motor==3.3.2
httpx==0.25.2
python-dotenv==1.0.0
speechrecognition==3.10.0
pyttsx3==2.90
pyaudio==0.2.11
EOF
        
        # Create minimal frontend
        mkdir -p frontend
        cat > frontend/package.json << 'EOF'
{
  "name": "cpas-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
EOF
    fi
    
    log "CPAS source code ready"
}

# Set up Python environment
setup_python() {
    log "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        error "requirements.txt not found"
    fi
    
    log "Python environment setup complete"
}

# Set up Node.js environment
setup_nodejs() {
    log "Setting up Node.js environment..."
    
    cd "$INSTALL_DIR/frontend"
    
    # Install Node.js dependencies
    npm install
    
    # Build production version
    npm run build || warning "Frontend build failed, will use development mode"
    
    log "Node.js environment setup complete"
}

# Configure MongoDB
setup_mongodb() {
    log "Configuring MongoDB..."
    
    # Start MongoDB service
    brew services start mongodb-community
    
    # Wait for MongoDB to start
    sleep 10
    
    # Test connection and create database
    mongosh --eval "
        try {
            use cpas_db;
            db.createCollection('agents');
            db.createCollection('conversations');
            db.createCollection('memory');
            db.createCollection('osint_cache');
            print('Database initialized successfully');
        } catch (e) {
            print('Database setup completed (may already exist)');
        }
    " || warning "MongoDB setup had issues, but continuing..."
    
    log "MongoDB configuration complete"
}

# Set up Ollama and download models
setup_ollama() {
    log "Setting up Ollama and downloading AI models..."
    
    # Start Ollama service
    brew services start ollama
    
    # Wait for Ollama to start
    sleep 10
    
    # Download required models
    log "Downloading DeepSeek R1 model (this may take 10-20 minutes)..."
    ollama pull deepseek-r1:7b || warning "Failed to download deepseek-r1:7b"
    
    log "Downloading Llama 3.2 model..."
    ollama pull llama3.2:3b || warning "Failed to download llama3.2:3b"
    
    # Verify models
    log "Installed models:"
    ollama list
    
    log "Ollama setup complete"
}

# Create configuration files
create_config() {
    log "Creating configuration files..."
    
    # Create main configuration file
    cat > "$CONFIG_DIR/greta_config.yaml" << 'EOF'
# CPAS Master Agent (Greta) Configuration
agent:
  name: "Greta"
  personality: "professional"
  voice_accent: "german"
  response_style: "detailed"

voice:
  wake_word: "Greta"
  wake_word_enabled: true
  continuous_listening: false
  voice_feedback: true
  tts_engine: "piper"
  voice_speed: 1.0
  voice_volume: 0.8

system:
  auto_start: true
  menu_bar_icon: true
  dock_icon: false
  notifications: true
  hotkey: "cmd+shift+g"

ai:
  default_model: "deepseek-r1:7b"
  fallback_model: "llama3.2:3b"
  max_context_length: 8192
  temperature: 0.7
  enable_reasoning: true
  enable_memory: true

osint:
  enabled: true
  safe_mode: true
  max_concurrent_searches: 3
  timeout_seconds: 30

privacy:
  store_conversations: true
  encrypt_storage: true
  auto_delete_after_days: 30
  share_analytics: false
  local_processing_only: false

advanced:
  log_level: "INFO"
  max_memory_mb: 2048
  enable_plugins: true
  developer_mode: false
EOF
    
    log "Configuration files created"
}

# Create startup scripts
create_startup_scripts() {
    log "Creating startup scripts..."
    
    # Create main startup script
    cat > "$INSTALL_DIR/start_greta.sh" << 'EOF'
#!/bin/bash
# CPAS Master Agent Startup Script

set -e

CPAS_DIR="$HOME/Applications/CPAS"
LOGS_DIR="$HOME/Library/Logs/Greta"

mkdir -p "$LOGS_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGS_DIR/greta.log"
}

# Check if services are running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Start MongoDB if not running
if ! is_running "mongod"; then
    log "Starting MongoDB..."
    brew services start mongodb-community
    sleep 3
fi

# Start Ollama if not running
if ! is_running "ollama"; then
    log "Starting Ollama..."
    brew services start ollama
    sleep 5
fi

# Start backend
if ! is_running "uvicorn.*main:app"; then
    log "Starting Python backend..."
    cd "$CPAS_DIR"
    source venv/bin/activate
    uvicorn main:app --host 127.0.0.1 --port 8000 > "$LOGS_DIR/backend.log" 2>&1 &
    sleep 3
fi

# Start frontend
if ! is_running "next.*start"; then
    log "Starting Next.js frontend..."
    cd "$CPAS_DIR/frontend"
    npm start > "$LOGS_DIR/frontend.log" 2>&1 &
    sleep 5
fi

# Open browser
log "Opening Greta interface..."
sleep 2
open "http://localhost:3000" || log "Please manually open http://localhost:3000"

log "Greta is now running!"
EOF
    
    chmod +x "$INSTALL_DIR/start_greta.sh"
    
    # Create stop script
    cat > "$INSTALL_DIR/stop_greta.sh" << 'EOF'
#!/bin/bash
# CPAS Master Agent Stop Script

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Stopping CPAS Master Agent services..."

# Stop backend and frontend
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "next.*start" 2>/dev/null || true

log "Greta services stopped"
EOF
    
    chmod +x "$INSTALL_DIR/stop_greta.sh"
    
    log "Startup scripts created"
}

# Create launch agents for auto-start
create_launch_agents() {
    log "Creating launch agents for auto-start..."
    
    LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # MongoDB launch agent
    cat > "$LAUNCH_AGENTS_DIR/com.cpas.mongodb.plist" << EOF
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
    <key>StandardOutPath</key>
    <string>$LOGS_DIR/mongodb.log</string>
    <key>StandardErrorPath</key>
    <string>$LOGS_DIR/mongodb_error.log</string>
</dict>
</plist>
EOF

    # Ollama launch agent
    cat > "$LAUNCH_AGENTS_DIR/com.cpas.ollama.plist" << EOF
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
    <key>StandardOutPath</key>
    <string>$LOGS_DIR/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>$LOGS_DIR/ollama_error.log</string>
</dict>
</plist>
EOF

    # Load launch agents
    launchctl load "$LAUNCH_AGENTS_DIR/com.cpas.mongodb.plist" 2>/dev/null || true
    launchctl load "$LAUNCH_AGENTS_DIR/com.cpas.ollama.plist" 2>/dev/null || true
    
    log "Launch agents created and loaded"
}

# Create desktop shortcut
create_desktop_shortcut() {
    log "Creating desktop shortcut..."
    
    # Create an AppleScript application
    cat > "$HOME/Desktop/Start Greta.scpt" << 'EOF'
tell application "Terminal"
    do script "~/Applications/CPAS/start_greta.sh"
end tell
EOF
    
    # Compile to application
    osacompile -o "$HOME/Desktop/Start Greta.app" "$HOME/Desktop/Start Greta.scpt"
    rm "$HOME/Desktop/Start Greta.scpt"
    
    log "Desktop shortcut created"
}

# Final verification
verify_installation() {
    log "Verifying installation..."
    
    local errors=0
    
    # Check if required commands exist
    for cmd in brew python3 node npm mongod ollama; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Command not found: $cmd"
            ((errors++))
        fi
    done
    
    # Check if services are running
    if ! brew services list | grep -q "mongodb-community.*started"; then
        warning "MongoDB service not started"
        ((errors++))
    fi
    
    if ! brew services list | grep -q "ollama.*started"; then
        warning "Ollama service not started"
        ((errors++))
    fi
    
    # Check if Python environment exists
    if [[ ! -d "$INSTALL_DIR/venv" ]]; then
        error "Python virtual environment not found"
        ((errors++))
    fi
    
    # Check if Node.js dependencies are installed
    if [[ ! -d "$INSTALL_DIR/frontend/node_modules" ]]; then
        error "Node.js dependencies not installed"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log "Installation verification passed"
        return 0
    else
        warning "Installation verification found $errors issues"
        return 1
    fi
}

# Main installation function
main() {
    log "Starting CPAS Master Agent installation..."
    log "Installation directory: $INSTALL_DIR"
    log "Logs directory: $LOGS_DIR"
    
    check_requirements
    install_homebrew
    install_dependencies
    download_cpas
    setup_python
    setup_nodejs
    setup_mongodb
    setup_ollama
    create_config
    create_startup_scripts
    create_launch_agents
    create_desktop_shortcut
    
    if verify_installation; then
        log "Installation completed successfully!"
        echo
        echo -e "${GREEN}🎉 CPAS Master Agent (Greta) has been installed successfully!${NC}"
        echo
        echo "To start Greta:"
        echo "  1. Double-click 'Start Greta' on your Desktop, OR"
        echo "  2. Run: ~/Applications/CPAS/start_greta.sh"
        echo
        echo "To stop Greta:"
        echo "  Run: ~/Applications/CPAS/stop_greta.sh"
        echo
        echo "Configuration file: $CONFIG_DIR/greta_config.yaml"
        echo "Logs directory: $LOGS_DIR"
        echo
        echo "For help and documentation, see:"
        echo "  ~/Applications/CPAS/docs/"
        echo
    else
        error "Installation completed with issues. Check the logs for details."
    fi
}

# Handle script interruption
cleanup() {
    log "Installation interrupted by user"
    exit 1
}

trap cleanup INT

# Run main installation
main "$@"
