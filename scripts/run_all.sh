
#!/bin/bash

# Enhanced CPAS Phase 2 Startup Script
# Starts all required services for the complete system

set -e

echo "🚀 Starting Enhanced CPAS Phase 2 System..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1; then
            echo "✅ $service_name is running on port $port"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start on port $port"
    return 1
}

# Function to start MongoDB if not running
start_mongodb() {
    echo "🔍 Checking MongoDB..."
    
    if pgrep mongod > /dev/null; then
        echo "✅ MongoDB is already running"
    else
        echo "🚀 Starting MongoDB..."
        sudo systemctl start mongod || {
            echo "⚠️  systemctl failed, trying direct mongod..."
            mongod --dbpath /var/lib/mongodb --logpath /var/log/mongodb/mongod.log --fork
        }
        
        # Wait for MongoDB to be ready
        sleep 5
        
        if pgrep mongod > /dev/null; then
            echo "✅ MongoDB started successfully"
        else
            echo "❌ Failed to start MongoDB"
            exit 1
        fi
    fi
}

# Function to start Ollama if not running
start_ollama() {
    echo "🔍 Checking Ollama..."
    
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo "✅ Ollama is already running"
    else
        echo "🚀 Starting Ollama..."
        nohup ollama serve > "$PROJECT_DIR/ollama_service.log" 2>&1 &
        
        # Wait for Ollama to be ready
        if check_service "Ollama" 11434; then
            echo "✅ Ollama started successfully"
            
            # Ensure Llama 3.2 1B model is available
            echo "🔍 Checking Llama 3.2 1B model..."
            if ollama list | grep -q "llama3.2:1b"; then
                echo "✅ Llama 3.2 1B model is available"
            else
                echo "📥 Pulling Llama 3.2 1B model..."
                ollama pull llama3.2:1b
                echo "✅ Llama 3.2 1B model downloaded"
            fi
        else
            echo "❌ Failed to start Ollama"
            exit 1
        fi
    fi
}

# Function to start FastAPI backend
start_backend() {
    echo "🚀 Starting FastAPI Backend..."
    
    cd "$PROJECT_DIR/backend"
    
    # Start the backend server
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$PROJECT_DIR/backend_service.log" 2>&1 &
    
    # Wait for backend to be ready
    if check_service "FastAPI Backend" 8000; then
        echo "✅ FastAPI Backend started successfully"
    else
        echo "❌ Failed to start FastAPI Backend"
        exit 1
    fi
}

# Function to initialize MemOS if needed
initialize_memos() {
    echo "🔍 Initializing MemOS..."
    
    cd "$PROJECT_DIR"
    python scripts/mem_init.py
    
    echo "✅ MemOS initialized"
}

# Main execution
main() {
    echo "📁 Project directory: $PROJECT_DIR"
    
    # Start core services
    start_mongodb
    start_ollama
    
    # Initialize MemOS
    initialize_memos
    
    # Start backend
    start_backend
    
    echo ""
    echo "🎉 Enhanced CPAS Phase 2 System Started Successfully!"
    echo ""
    echo "📊 Service Status:"
    echo "   • MongoDB:     http://localhost:27017"
    echo "   • Ollama:      http://localhost:11434"
    echo "   • FastAPI:     http://localhost:8000"
    echo "   • API Docs:    http://localhost:8000/docs"
    echo ""
    echo "🔧 Available APIs:"
    echo "   • Agent:       /api/v1/agent/*"
    echo "   • Voice:       /api/v1/voice/*"
    echo "   • Reasoning:   /api/v1/reasoning/*"
    echo "   • Memory:      /api/v1/memory/*"
    echo "   • LLM:         /api/v1/llm/*"
    echo ""
    echo "📝 Logs:"
    echo "   • Backend:     $PROJECT_DIR/backend_service.log"
    echo "   • Ollama:      $PROJECT_DIR/ollama_service.log"
    echo ""
    echo "🛑 To stop all services, run: $SCRIPT_DIR/stop_all.sh"
    echo ""
}

# Handle script termination
cleanup() {
    echo ""
    echo "🛑 Received termination signal. Services will continue running in background."
    echo "   Use $SCRIPT_DIR/stop_all.sh to stop all services."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run main function
main

# Keep script running to show it's active
echo "✅ All services are running. Press Ctrl+C to exit this script (services will continue)."
while true; do
    sleep 60
    echo "⏰ $(date): All services running..."
done
