
#!/bin/bash

# Enhanced CPAS Mac Installer
# Optimized for MacBook Pro M2 with 32GB RAM

set -e

echo "🚀 Installing Enhanced CPAS - Complete AI System"
echo "================================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only"
    exit 1
fi

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
brew install python@3.11 node mongodb-community ollama redis tesseract ffmpeg

# Start services
echo "🔧 Starting system services..."
brew services start mongodb-community
brew services start redis

# Create application directory
APP_DIR="/Applications/Enhanced-CPAS"
mkdir -p "$APP_DIR"

# Copy application files
echo "📁 Installing application files..."
cp -r . "$APP_DIR/"

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd "$APP_DIR"
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Node.js frontend
echo "⚛️ Setting up frontend..."
cd frontend
npm install
npm run build

# Install Ollama models
echo "🤖 Installing AI models..."
ollama pull llama3.2:3b
ollama pull deepseek-r1:7b

# Create launch scripts
echo "🚀 Creating launch scripts..."
cat > "$APP_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# Start backend
cd backend
python main.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Enhanced CPAS started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Access at: http://localhost:3000"

# Save PIDs for cleanup
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

wait
EOF

chmod +x "$APP_DIR/start.sh"

# Create desktop shortcut
echo "🖥️ Creating desktop shortcut..."
cat > ~/Desktop/Enhanced-CPAS.command << EOF
#!/bin/bash
cd "$APP_DIR"
./start.sh
EOF

chmod +x ~/Desktop/Enhanced-CPAS.command

echo "✅ Enhanced CPAS installed successfully!"
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo "• Application installed to: $APP_DIR"
echo "• Desktop shortcut created"
echo "• All services configured"
echo ""
echo "To start Enhanced CPAS:"
echo "1. Double-click 'Enhanced-CPAS' on your desktop"
echo "2. Or run: $APP_DIR/start.sh"
echo ""
echo "Access your AI system at: http://localhost:3000"
echo ""
echo "Features included:"
echo "✓ Dynamic AI Agents (Task Manager, Research, Creative, Technical, Personal Assistant)"
echo "✓ Workflow Automation & Multi-Agent Coordination"
echo "✓ Proactive AI Suggestions & Smart Notifications"
echo "✓ Google Workspace & Slack Integrations"
echo "✓ Voice Interface & Real-time Chat"
echo "✓ Advanced Memory & Learning System"
echo "✓ Mac-optimized Performance"
echo ""
echo "Enjoy your Enhanced Personal AI System! 🤖✨"
