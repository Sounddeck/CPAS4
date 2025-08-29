
#!/bin/bash
set -e

echo "🚀 Starting Enhanced CPAS Phase 1 Installation..."

# Update system
echo "📦 Updating system packages..."
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y curl gnupg python3 python3-pip python3-venv git build-essential

# Install MongoDB
echo "🍃 Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt update -y
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
cd /home/ubuntu/cpas_enhanced
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clone MemOS
echo "🧠 Cloning MemOS..."
git clone https://github.com/MemTensor/MemOS.git
cd MemOS
pip install -e .
cd ..

# Initialize MongoDB for MemOS
echo "🗄️ Initializing MongoDB for MemOS..."
python scripts/mem_init.py

# Pull Ollama models in background
echo "📥 Pulling Ollama models (this will take time)..."
nohup ollama pull deepseek-r1:7b > ollama_deepseek.log 2>&1 &
nohup ollama pull llama3.2:3b > ollama_llama.log 2>&1 &
nohup ollama pull mixtral:8x7b > ollama_mixtral.log 2>&1 &

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
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

# Future API Keys (placeholder)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
EOF

echo "✅ Installation complete! Check logs for Ollama model downloads."
echo "🔧 To activate environment: source venv/bin/activate"
echo "🚀 To start backend: python backend/main.py"
