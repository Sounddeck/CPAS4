
# CPAS Master Agent - Troubleshooting Guide

## Quick Diagnostics

### System Health Check

Run this command to check overall system status:

```bash
# Create and run system health check script
cat > ~/check_greta_health.sh << 'EOF'
#!/bin/bash
echo "=== CPAS Master Agent Health Check ==="
echo "Date: $(date)"
echo

echo "1. System Information:"
echo "   macOS Version: $(sw_vers -productVersion)"
echo "   Architecture: $(uname -m)"
echo "   Available RAM: $(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')"
echo "   Free Disk Space: $(df -h / | awk 'NR==2{print $4}')"
echo

echo "2. Required Commands:"
for cmd in brew python3 node npm mongod ollama; do
    if command -v $cmd &> /dev/null; then
        echo "   ✓ $cmd: $(command -v $cmd)"
    else
        echo "   ✗ $cmd: NOT FOUND"
    fi
done
echo

echo "3. Service Status:"
echo "   MongoDB: $(brew services list | grep mongodb-community | awk '{print $2}')"
echo "   Ollama: $(brew services list | grep ollama | awk '{print $2}')"
echo

echo "4. Process Status:"
echo "   Backend (uvicorn): $(pgrep -f 'uvicorn.*main:app' > /dev/null && echo 'RUNNING' || echo 'STOPPED')"
echo "   Frontend (next): $(pgrep -f 'next.*start' > /dev/null && echo 'RUNNING' || echo 'STOPPED')"
echo

echo "5. Port Status:"
echo "   Port 8000 (Backend): $(lsof -ti:8000 > /dev/null && echo 'IN USE' || echo 'FREE')"
echo "   Port 3000 (Frontend): $(lsof -ti:3000 > /dev/null && echo 'IN USE' || echo 'FREE')"
echo "   Port 27017 (MongoDB): $(lsof -ti:27017 > /dev/null && echo 'IN USE' || echo 'FREE')"
echo "   Port 11434 (Ollama): $(lsof -ti:11434 > /dev/null && echo 'IN USE' || echo 'FREE')"
echo

echo "6. Log Files:"
LOGS_DIR="$HOME/Library/Logs/Greta"
if [ -d "$LOGS_DIR" ]; then
    echo "   Log directory: $LOGS_DIR"
    for log in greta.log backend.log frontend.log mongodb.log ollama.log; do
        if [ -f "$LOGS_DIR/$log" ]; then
            echo "   ✓ $log ($(wc -l < "$LOGS_DIR/$log") lines)"
        else
            echo "   ✗ $log: NOT FOUND"
        fi
    done
else
    echo "   ✗ Log directory not found: $LOGS_DIR"
fi
echo

echo "=== Health Check Complete ==="
EOF

chmod +x ~/check_greta_health.sh
~/check_greta_health.sh
```

## Common Issues and Solutions

### Installation Issues

#### Issue: "Command not found: brew"

**Symptoms**: 
- Terminal shows "brew: command not found"
- Installation scripts fail immediately

**Causes**:
- Homebrew not installed
- Homebrew not in PATH (especially on Apple Silicon Macs)

**Solutions**:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# For Apple Silicon Macs, add to PATH
if [[ $(uname -m) == "arm64" ]]; then
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Verify installation
brew --version
```

#### Issue: Python Virtual Environment Fails

**Symptoms**:
- "python3.11: command not found"
- Virtual environment creation fails
- Package installation errors

**Solutions**:

```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Create virtual environment with full path
/usr/local/bin/python3.11 -m venv venv
# OR for Apple Silicon:
/opt/homebrew/bin/python3.11 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

#### Issue: Node.js Dependencies Fail

**Symptoms**:
- "npm: command not found"
- "node: command not found"
- Package installation timeouts

**Solutions**:

```bash
# Install Node.js 18 via Homebrew
brew install node@18

# Add to PATH if needed
echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Service Issues

#### Issue: MongoDB Won't Start

**Symptoms**:
- "Connection refused" errors
- Backend fails to connect to database
- MongoDB service shows as "stopped"

**Solutions**:

```bash
# Check MongoDB status
brew services list | grep mongodb

# Stop and restart MongoDB
brew services stop mongodb-community
brew services start mongodb-community

# If that fails, try manual start
mongod --config /usr/local/etc/mongod.conf --fork --logpath ~/Library/Logs/Greta/mongodb.log

# Check MongoDB logs
tail -f ~/Library/Logs/Greta/mongodb.log

# Fix permissions if needed
sudo chown -R $(whoami) /usr/local/var/mongodb
sudo chown -R $(whoami) /usr/local/var/log/mongodb
```

#### Issue: Ollama Service Problems

**Symptoms**:
- "Failed to connect to Ollama" errors
- Models won't load
- Ollama API not responding

**Solutions**:

```bash
# Check Ollama status
brew services list | grep ollama

# Restart Ollama service
brew services stop ollama
brew services start ollama

# Manual start with debugging
ollama serve --debug

# Check if models are installed
ollama list

# Re-download models if missing
ollama pull deepseek-r1:7b
ollama pull llama3.2:3b

# Test Ollama API
curl http://localhost:11434/api/tags
```

#### Issue: Backend Service Fails

**Symptoms**:
- "uvicorn: command not found"
- Backend API not responding
- Import errors in Python

**Solutions**:

```bash
# Navigate to backend directory
cd ~/Applications/CPAS/cpas-master-agent-main

# Activate virtual environment
source venv/bin/activate

# Check if uvicorn is installed
pip list | grep uvicorn

# Reinstall if missing
pip install uvicorn[standard]

# Start backend manually with debugging
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug

# Check for import errors
python -c "from backend.main import app; print('Backend imports OK')"
```

#### Issue: Frontend Won't Start

**Symptoms**:
- "next: command not found"
- Frontend build fails
- Port 3000 not responding

**Solutions**:

```bash
# Navigate to frontend directory
cd ~/Applications/CPAS/cpas-master-agent-main/frontend

# Check Node.js and npm versions
node --version
npm --version

# Clear cache and reinstall
rm -rf node_modules .next package-lock.json
npm cache clean --force
npm install

# Build and start
npm run build
npm start

# If build fails, try development mode
npm run dev
```

### Voice Activation Issues

#### Issue: Microphone Not Working

**Symptoms**:
- Wake word not detected
- "Microphone permission denied" errors
- No audio input detected

**Solutions**:

1. **Check System Preferences**:
   - System Preferences → Security & Privacy → Privacy
   - Select "Microphone" from sidebar
   - Ensure "Greta" or Terminal is checked

2. **Test Microphone**:
   ```bash
   # Test microphone with system tool
   rec -t wav test.wav trim 0 5
   play test.wav
   rm test.wav
   ```

3. **Check Audio Devices**:
   ```bash
   # List audio devices
   system_profiler SPAudioDataType
   ```

#### Issue: Wake Word Not Recognized

**Symptoms**:
- Voice commands ignored
- Wake word detection inconsistent
- High false positive rate

**Solutions**:

1. **Adjust Sensitivity**:
   ```bash
   nano ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml
   ```
   
   ```yaml
   voice:
     silence_threshold: 0.3      # Lower = more sensitive
     phrase_timeout: 3           # Shorter timeout
     wake_word_sensitivity: 0.7  # Adjust recognition threshold
   ```

2. **Test Wake Word**:
   ```bash
   # Enable debug mode
   echo "voice_debug: true" >> config/greta_config.yaml
   
   # Check voice logs
   tail -f ~/Library/Logs/Greta/voice.log
   ```

#### Issue: Text-to-Speech Problems

**Symptoms**:
- No voice output
- Robotic or unclear speech
- TTS engine errors

**Solutions**:

1. **Test System TTS**:
   ```bash
   say "This is a test of text to speech"
   ```

2. **Switch TTS Engine**:
   ```yaml
   voice:
     tts_engine: "system"        # Try different engines
     voice_speed: 1.0
     voice_volume: 0.8
   ```

3. **Install Alternative TTS**:
   ```bash
   pip install pyttsx3 gTTS
   ```

### Network and API Issues

#### Issue: Port Conflicts

**Symptoms**:
- "Port already in use" errors
- Services fail to start
- Connection refused errors

**Solutions**:

```bash
# Find processes using ports
lsof -ti:8000  # Backend port
lsof -ti:3000  # Frontend port
lsof -ti:27017 # MongoDB port
lsof -ti:11434 # Ollama port

# Kill processes if needed
lsof -ti:8000 | xargs kill -9

# Use alternative ports
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

#### Issue: API Key Problems

**Symptoms**:
- "Invalid API key" errors
- OpenAI/Anthropic integration fails
- Rate limiting errors

**Solutions**:

1. **Check API Keys**:
   ```bash
   nano ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml
   ```
   
   ```yaml
   integrations:
     openai_api_key: "sk-..."     # Ensure key is valid
     anthropic_api_key: "..."     # Check key format
   ```

2. **Test API Keys**:
   ```bash
   # Test OpenAI API
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.openai.com/v1/models
   
   # Test Anthropic API
   curl -H "x-api-key: YOUR_API_KEY" \
        https://api.anthropic.com/v1/messages
   ```

### Performance Issues

#### Issue: High CPU Usage

**Symptoms**:
- System becomes slow
- Fan noise increases
- High CPU usage in Activity Monitor

**Solutions**:

1. **Optimize Configuration**:
   ```yaml
   voice:
     continuous_listening: false  # Use wake words instead
     processing_threads: 1        # Reduce CPU threads
   
   advanced:
     max_memory_mb: 1024         # Limit memory usage
   ```

2. **Monitor Resource Usage**:
   ```bash
   # Check CPU usage
   top -pid $(pgrep -f "uvicorn\|ollama\|mongod")
   
   # Check memory usage
   ps aux | grep -E "(uvicorn|ollama|mongod)" | awk '{print $4, $11}'
   ```

#### Issue: High Memory Usage

**Symptoms**:
- System runs out of memory
- Swap usage increases
- Applications become unresponsive

**Solutions**:

1. **Reduce Model Size**:
   ```bash
   # Use smaller models
   ollama pull llama3.2:1b      # Instead of 3b
   ollama pull deepseek-r1:1.5b # Instead of 7b
   ```

2. **Optimize Settings**:
   ```yaml
   ai:
     max_context_length: 4096    # Reduce from 8192
     enable_memory: false        # Disable if not needed
   
   advanced:
     max_memory_mb: 1024        # Set memory limit
   ```

### Data and Storage Issues

#### Issue: Database Connection Errors

**Symptoms**:
- "Failed to connect to MongoDB" errors
- Data not persisting
- Database timeout errors

**Solutions**:

```bash
# Check MongoDB connection
mongosh --eval "db.adminCommand('ismaster')"

# Reset database if corrupted
brew services stop mongodb-community
rm -rf /usr/local/var/mongodb/*
brew services start mongodb-community

# Recreate database
mongosh --eval "
use cpas_db;
db.createCollection('agents');
db.createCollection('conversations');
db.createCollection('memory');
db.createCollection('osint_cache');
"
```

#### Issue: Disk Space Problems

**Symptoms**:
- "No space left on device" errors
- Models fail to download
- Logs grow too large

**Solutions**:

```bash
# Check disk usage
df -h

# Clean up logs
rm -rf ~/Library/Logs/Greta/*.log

# Clean up Ollama models (keep only needed ones)
ollama list
ollama rm MODEL_NAME

# Clean up npm cache
npm cache clean --force

# Clean up pip cache
pip cache purge
```

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```yaml
advanced:
  log_level: "DEBUG"
  developer_mode: true
  voice_debug: true
  api_debug: true
```

### Log Analysis

Analyze logs for patterns:

```bash
# Create log analysis script
cat > ~/analyze_logs.sh << 'EOF'
#!/bin/bash
LOGS_DIR="$HOME/Library/Logs/Greta"

echo "=== Log Analysis ==="
echo "Recent errors:"
grep -i error "$LOGS_DIR"/*.log | tail -10

echo -e "\nWarnings:"
grep -i warning "$LOGS_DIR"/*.log | tail -5

echo -e "\nConnection issues:"
grep -i "connection\|timeout\|refused" "$LOGS_DIR"/*.log | tail -5

echo -e "\nMemory issues:"
grep -i "memory\|oom" "$LOGS_DIR"/*.log | tail -5
EOF

chmod +x ~/analyze_logs.sh
~/analyze_logs.sh
```

### Network Diagnostics

Test network connectivity:

```bash
# Test local services
curl -I http://localhost:8000/health
curl -I http://localhost:3000
curl -I http://localhost:11434/api/tags

# Test external APIs
curl -I https://api.openai.com/v1/models
curl -I https://api.anthropic.com/v1/messages

# Check DNS resolution
nslookup api.openai.com
nslookup api.anthropic.com
```

### System Resource Monitoring

Monitor system resources in real-time:

```bash
# Create monitoring script
cat > ~/monitor_greta.sh << 'EOF'
#!/bin/bash
echo "Monitoring CPAS Master Agent resources..."
echo "Press Ctrl+C to stop"

while true; do
    clear
    echo "=== $(date) ==="
    echo
    
    echo "CPU Usage:"
    ps aux | grep -E "(uvicorn|ollama|mongod|next)" | grep -v grep | awk '{print $3"% "$11}'
    echo
    
    echo "Memory Usage:"
    ps aux | grep -E "(uvicorn|ollama|mongod|next)" | grep -v grep | awk '{print $4"% "$11}'
    echo
    
    echo "Disk Usage:"
    df -h / | tail -1
    echo
    
    echo "Network Connections:"
    netstat -an | grep -E "(8000|3000|27017|11434)" | grep LISTEN
    echo
    
    sleep 5
done
EOF

chmod +x ~/monitor_greta.sh
~/monitor_greta.sh
```

## Getting Help

### Collecting Debug Information

Before seeking help, collect this information:

```bash
# Create debug info script
cat > ~/collect_debug_info.sh << 'EOF'
#!/bin/bash
DEBUG_FILE="greta_debug_$(date +%Y%m%d_%H%M%S).txt"

echo "Collecting debug information..."
echo "=== CPAS Master Agent Debug Information ===" > "$DEBUG_FILE"
echo "Generated: $(date)" >> "$DEBUG_FILE"
echo >> "$DEBUG_FILE"

echo "System Information:" >> "$DEBUG_FILE"
sw_vers >> "$DEBUG_FILE"
uname -a >> "$DEBUG_FILE"
echo >> "$DEBUG_FILE"

echo "Installed Software:" >> "$DEBUG_FILE"
brew --version >> "$DEBUG_FILE" 2>&1
python3 --version >> "$DEBUG_FILE" 2>&1
node --version >> "$DEBUG_FILE" 2>&1
npm --version >> "$DEBUG_FILE" 2>&1
echo >> "$DEBUG_FILE"

echo "Service Status:" >> "$DEBUG_FILE"
brew services list >> "$DEBUG_FILE" 2>&1
echo >> "$DEBUG_FILE"

echo "Process Status:" >> "$DEBUG_FILE"
ps aux | grep -E "(uvicorn|ollama|mongod|next)" | grep -v grep >> "$DEBUG_FILE"
echo >> "$DEBUG_FILE"

echo "Port Status:" >> "$DEBUG_FILE"
netstat -an | grep -E "(8000|3000|27017|11434)" >> "$DEBUG_FILE"
echo >> "$DEBUG_FILE"

echo "Recent Logs:" >> "$DEBUG_FILE"
if [ -d "$HOME/Library/Logs/Greta" ]; then
    for log in greta.log backend.log frontend.log; do
        if [ -f "$HOME/Library/Logs/Greta/$log" ]; then
            echo "--- $log (last 20 lines) ---" >> "$DEBUG_FILE"
            tail -20 "$HOME/Library/Logs/Greta/$log" >> "$DEBUG_FILE"
            echo >> "$DEBUG_FILE"
        fi
    done
fi

echo "Debug information saved to: $DEBUG_FILE"
echo "Please attach this file when reporting issues."
EOF

chmod +x ~/collect_debug_info.sh
~/collect_debug_info.sh
```

### Support Channels

1. **GitHub Issues**: https://github.com/cpas-project/greta/issues
2. **Documentation**: https://docs.cpas-project.com
3. **Community Discord**: [Join our Discord server]
4. **Email Support**: support@cpas-project.com

### Reporting Bugs

When reporting issues, include:

1. **System Information**: macOS version, hardware specs
2. **Installation Method**: Drag-and-drop or Terminal
3. **Error Messages**: Exact error text
4. **Steps to Reproduce**: What you were doing when the error occurred
5. **Debug Information**: Output from the debug collection script
6. **Configuration**: Your `greta_config.yaml` (remove API keys)

---

*This troubleshooting guide covers the most common issues. For additional help, visit our support channels or check the latest documentation.*
