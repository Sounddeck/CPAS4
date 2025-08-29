
# CPAS Master Agent (Greta) - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Drag-and-Drop Installation (Easiest)

1. **Download** `Greta-CPAS-Master-Agent-v1.0.0.dmg`
2. **Double-click** the DMG file
3. **Drag** `Greta.app` to `Applications` folder
4. **Open** Greta from Applications
5. **Follow** the automatic setup wizard

**That's it!** Greta will install all dependencies and launch automatically.

### Option 2: Terminal Installation (Advanced)

```bash
# Download and run the installer
curl -L -o terminal_install.sh "https://github.com/cpas-project/greta/raw/main/terminal_install.sh"
chmod +x terminal_install.sh
./terminal_install.sh
```

## 🎯 First Steps with Greta

### 1. Launch Greta

**Drag-and-Drop Users:**
- Open Applications folder
- Double-click `Greta.app`

**Terminal Users:**
- Double-click "Start Greta" on Desktop, OR
- Run: `~/Applications/CPAS/start_greta.sh`

### 2. Access the Interface

Greta will automatically open in your browser at: `http://localhost:3000`

If it doesn't open automatically, click the link or type the URL manually.

### 3. Complete Initial Setup

1. **Welcome Screen**: Click "Get Started"
2. **Microphone Permission**: Click "Allow" when prompted
3. **Voice Test**: Say "Hello Greta" to test voice activation
4. **Personality Setup**: Choose your preferred settings
5. **API Keys** (Optional): Add OpenAI/Anthropic keys for enhanced features

## 🗣️ Voice Activation Quick Setup

### Enable Voice Commands

1. **Say the Wake Word**: "Greta" (or your custom name)
2. **Wait for Response**: Greta will acknowledge with a sound
3. **Give Your Command**: Speak naturally
4. **Listen to Response**: Greta will respond with voice and text

### Common Voice Commands

- **"Greta, what time is it?"**
- **"Search for information about Tesla"**
- **"What's the weather like?"**
- **"Check system status"**
- **"Go to sleep"** (stops listening)

### Customize Wake Word

1. Open Settings in the web interface
2. Go to "Voice Configuration"
3. Change "Wake Word" to your preference
4. Click "Save Changes"

## 🔧 Basic Customization

### Change Greta's Name

**Method 1: Web Interface**
1. Open `http://localhost:3000`
2. Click "Settings" → "Agent Configuration"
3. Change "Agent Name" field
4. Click "Save"

**Method 2: Configuration File**
```bash
nano ~/Applications/CPAS/config/greta_config.yaml
```
Change the `name` field:
```yaml
agent:
  name: "Your_Custom_Name"
```

### Personality Options

Choose from these personality types:
- **Professional**: Formal, business-like responses
- **Friendly**: Warm, conversational tone
- **Casual**: Relaxed, informal communication
- **Formal**: Very polite, structured responses

### Voice Accents

Available accent options:
- **German**: Default Greta accent
- **American**: Standard US English
- **British**: UK English accent
- **Australian**: Australian English

## 🛠️ Essential Features

### OSINT Intelligence

Ask Greta to research topics:
- **"Research [company name]"**
- **"Analyze domain example.com"**
- **"Find information about [person]"**
- **"Check IP address [IP]"**

### Memory System

Greta remembers conversations:
- **"Remember that I prefer morning meetings"**
- **"What do you remember about my project?"**
- **"Forget about [topic]"**

### System Integration

Control your Mac:
- **"Open Applications folder"**
- **"Check system resources"**
- **"Show running processes"**
- **"What's my IP address?"**

## 📱 Interface Overview

### Main Dashboard
- **Chat Interface**: Central conversation area
- **Voice Status**: Shows listening/speaking state
- **Agent Info**: Current agent and personality
- **Quick Actions**: Common commands as buttons

### Settings Panel
- **Agent Configuration**: Name, personality, voice
- **Voice Settings**: Wake word, TTS options
- **Privacy Settings**: Data storage, encryption
- **Integration Settings**: API keys, external services

### OSINT Tools
- **Domain Analysis**: Website investigation
- **IP Lookup**: Network information
- **Social Media**: Public information gathering
- **Document Analysis**: File examination

## 🔍 Troubleshooting Quick Fixes

### Greta Won't Start
```bash
# Check if services are running
brew services list | grep -E "(mongodb|ollama)"

# Restart services if needed
brew services restart mongodb-community
brew services restart ollama
```

### Voice Not Working
1. Check microphone permissions in System Preferences
2. Test microphone: `say "test"` in Terminal
3. Restart Greta application

### Can't Access Web Interface
1. Check if port 3000 is free: `lsof -ti:3000`
2. Try alternative URL: `http://127.0.0.1:3000`
3. Restart frontend service

### High CPU Usage
1. Open Settings → Advanced
2. Set `continuous_listening: false`
3. Reduce `processing_threads` to 1
4. Use smaller AI models

## 📚 Next Steps

### Learn More
- **Full Installation Guide**: `docs/CPAS_Mac_Install.md`
- **Voice Activation Guide**: `docs/Voice_Activation_Guide.md`
- **Troubleshooting Guide**: `docs/Troubleshooting_Guide.md`

### Advanced Features
- **Custom OSINT Tools**: Add your own investigation modules
- **API Integrations**: Connect external services
- **Workflow Automation**: Create custom task sequences
- **Plugin Development**: Extend Greta's capabilities

### Community
- **GitHub**: https://github.com/cpas-project/greta
- **Documentation**: https://docs.cpas-project.com
- **Discord**: Join our community server
- **Support**: support@cpas-project.com

## 🎉 You're Ready!

Congratulations! You now have a fully functional AI assistant with:
- ✅ Voice activation and natural conversation
- ✅ OSINT intelligence capabilities
- ✅ Mac-native integration
- ✅ Customizable personality and behavior
- ✅ Privacy-focused local processing

**Enjoy exploring with Greta!**

---

*Need help? Check the troubleshooting guide or visit our support channels.*
