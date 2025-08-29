
#!/bin/bash

# Enhanced CPAS Phase 2 Stop Script
# Stops all CPAS services

set -e

echo "🛑 Stopping Enhanced CPAS Phase 2 System..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Function to stop a service by port
stop_service_by_port() {
    local service_name=$1
    local port=$2
    
    echo "🔍 Stopping $service_name on port $port..."
    
    # Find and kill processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "🛑 Killing $service_name processes: $pids"
        kill -TERM $pids 2>/dev/null || true
        sleep 3
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo "🔨 Force killing remaining processes: $remaining_pids"
            kill -KILL $remaining_pids 2>/dev/null || true
        fi
        
        echo "✅ $service_name stopped"
    else
        echo "ℹ️  $service_name was not running on port $port"
    fi
}

# Function to stop MongoDB
stop_mongodb() {
    echo "🔍 Stopping MongoDB..."
    
    if pgrep mongod > /dev/null; then
        sudo systemctl stop mongod 2>/dev/null || {
            echo "⚠️  systemctl failed, killing mongod processes..."
            sudo pkill mongod 2>/dev/null || true
        }
        echo "✅ MongoDB stopped"
    else
        echo "ℹ️  MongoDB was not running"
    fi
}

# Function to stop Ollama
stop_ollama() {
    echo "🔍 Stopping Ollama..."
    
    # Stop by port
    stop_service_by_port "Ollama" 11434
    
    # Also kill any ollama processes
    pkill -f "ollama serve" 2>/dev/null || true
    pkill ollama 2>/dev/null || true
    
    echo "✅ Ollama stopped"
}

# Function to stop FastAPI backend
stop_backend() {
    echo "🔍 Stopping FastAPI Backend..."
    
    # Stop by port
    stop_service_by_port "FastAPI Backend" 8000
    
    # Also kill any uvicorn processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    
    echo "✅ FastAPI Backend stopped"
}

# Function to clean up log files
cleanup_logs() {
    echo "🧹 Cleaning up log files..."
    
    # Truncate log files instead of deleting them
    > "$PROJECT_DIR/backend_service.log" 2>/dev/null || true
    > "$PROJECT_DIR/ollama_service.log" 2>/dev/null || true
    
    echo "✅ Log files cleaned"
}

# Main execution
main() {
    echo "📁 Project directory: $PROJECT_DIR"
    
    # Stop all services
    stop_backend
    stop_ollama
    stop_mongodb
    
    # Clean up
    cleanup_logs
    
    echo ""
    echo "🎉 Enhanced CPAS Phase 2 System Stopped Successfully!"
    echo ""
    echo "ℹ️  All services have been stopped and log files cleaned."
    echo "   To restart, run: $SCRIPT_DIR/run_all.sh"
    echo ""
}

# Run main function
main
