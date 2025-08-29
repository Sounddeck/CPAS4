
#!/bin/bash

# CPAS Master Agent - Mac Installation Script
# This script installs the complete CPAS Master Agent system on macOS

set -e

echo "🚀 CPAS Master Agent - Mac Installation"
echo "======================================"

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

# Install dependencies using Brewfile
echo "📦 Installing system dependencies..."
if [ -f "Brewfile" ]; then
    brew bundle --file=Brewfile
else
    echo "⚠️  Brewfile not found, installing essential packages..."
    brew install python@3.11 node npm ollama docker postgresql redis
fi

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies for frontend
echo "🌐 Setting up frontend..."
cd frontend
npm install
cd ..

# Initialize MemOS
echo "🧠 Initializing MemOS..."
python scripts/mem_init.py

# Set up Ollama models
echo "🤖 Setting up AI models..."
ollama pull deepseek-r1:1.5b
ollama pull llama3.2:3b

# Start services
echo "🚀 Starting services..."
chmod +x scripts/run_all.sh
./scripts/run_all.sh

# Install Greta.app if available
if [ -d "Greta.app" ]; then
    echo "🎤 Installing Greta Voice Interface..."
    cp -r Greta.app /Applications/
    echo "✅ Greta.app installed to Applications folder"
fi

echo ""
echo "✅ CPAS Master Agent installation complete!"
echo ""
echo "🎯 Quick Start:"
echo "   1. Open http://localhost:3000 for the web interface"
echo "   2. Launch Greta.app for voice interface"
echo "   3. Check docs/ folder for detailed guides"
echo ""
echo "📚 Documentation:"
echo "   - README.md - System overview"
echo "   - QUICK_START.md - Get started quickly"
echo "   - docs/ - Detailed guides and troubleshooting"
echo ""
