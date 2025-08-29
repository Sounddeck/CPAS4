
# CPAS Master Agent (Greta) - Uninstallation Guide

## Complete Removal

### Automated Uninstall Script

The easiest way to remove Greta completely:

```bash
# Download and run the uninstall script
curl -L -o uninstall_greta.sh "https://github.com/cpas-project/greta/raw/main/uninstall_greta.sh"
chmod +x uninstall_greta.sh
./uninstall_greta.sh
```

### Manual Uninstallation

If you prefer to remove components manually:

#### Step 1: Stop All Services

```bash
# Stop Greta services
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "next.*start" 2>/dev/null || true

# Stop system services
brew services stop mongodb-community
brew services stop ollama
```

#### Step 2: Remove Launch Agents

```bash
# Unload and remove launch agents
launchctl unload ~/Library/LaunchAgents/com.cpas.mongodb.plist 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.cpas.ollama.plist 2>/dev/null || true

rm -f ~/Library/LaunchAgents/com.cpas.mongodb.plist
rm -f ~/Library/LaunchAgents/com.cpas.ollama.plist
```

#### Step 3: Remove Application Files

```bash
# Remove main application directory
rm -rf ~/Applications/CPAS

# Remove app bundle (if using drag-and-drop installer)
rm -rf /Applications/Greta.app

# Remove desktop shortcuts
rm -rf ~/Desktop/"Start Greta.app"
```

#### Step 4: Remove Data and Logs

```bash
# Remove logs
rm -rf ~/Library/Logs/Greta

# Remove application support files
rm -rf ~/Library/Application\ Support/Greta

# Remove preferences
rm -f ~/Library/Preferences/com.cpas.greta.plist
```

#### Step 5: Remove Homebrew Packages (Optional)

⚠️ **Warning**: Only remove these if you're not using them for other applications.

```bash
# Remove Greta-specific packages
brew uninstall mongodb-community ollama

# Remove development tools (optional)
brew uninstall python@3.11 node@18 portaudio ffmpeg

# Remove optional tools
brew uninstall pipx wget curl jq espeak festival mongodb-database-tools

# Remove cask applications
brew uninstall --cask mongodb-compass
```

#### Step 6: Clean Up Homebrew (Optional)

```bash
# Clean up unused dependencies
brew autoremove

# Clean up cache
brew cleanup
```

## Partial Removal Options

### Keep Dependencies, Remove Only Greta

If you want to keep the development tools for other projects:

```bash
# Stop Greta services only
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "next.*start" 2>/dev/null || true

# Remove application files
rm -rf ~/Applications/CPAS
rm -rf /Applications/Greta.app
rm -rf ~/Library/Logs/Greta

# Keep MongoDB and Ollama running for other uses
```

### Remove Only AI Models

To free up disk space but keep the application:

```bash
# List installed models
ollama list

# Remove specific models
ollama rm deepseek-r1:7b
ollama rm llama3.2:3b

# Keep Ollama service for other models
```

### Reset to Default Configuration

To reset Greta without removing it:

```bash
# Backup current configuration
cp ~/Applications/CPAS/config/greta_config.yaml ~/greta_config_backup.yaml

# Remove configuration and logs
rm -rf ~/Applications/CPAS/config/
rm -rf ~/Library/Logs/Greta/

# Restart Greta to regenerate default config
~/Applications/CPAS/start_greta.sh
```

## Verification

### Check Removal Completeness

Run this script to verify complete removal:

```bash
cat > ~/verify_removal.sh << 'EOF'
#!/bin/bash
echo "=== Greta Removal Verification ==="

echo "1. Application Files:"
if [ -d ~/Applications/CPAS ]; then
    echo "   ❌ ~/Applications/CPAS still exists"
else
    echo "   ✅ ~/Applications/CPAS removed"
fi

if [ -d /Applications/Greta.app ]; then
    echo "   ❌ /Applications/Greta.app still exists"
else
    echo "   ✅ /Applications/Greta.app removed"
fi

echo "2. Launch Agents:"
if [ -f ~/Library/LaunchAgents/com.cpas.mongodb.plist ]; then
    echo "   ❌ MongoDB launch agent still exists"
else
    echo "   ✅ MongoDB launch agent removed"
fi

if [ -f ~/Library/LaunchAgents/com.cpas.ollama.plist ]; then
    echo "   ❌ Ollama launch agent still exists"
else
    echo "   ✅ Ollama launch agent removed"
fi

echo "3. Data and Logs:"
if [ -d ~/Library/Logs/Greta ]; then
    echo "   ❌ Log directory still exists"
else
    echo "   ✅ Log directory removed"
fi

echo "4. Running Processes:"
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "   ❌ Backend process still running"
else
    echo "   ✅ Backend process stopped"
fi

if pgrep -f "next.*start" > /dev/null; then
    echo "   ❌ Frontend process still running"
else
    echo "   ✅ Frontend process stopped"
fi

echo "5. System Services:"
MONGODB_STATUS=$(brew services list | grep mongodb-community | awk '{print $2}')
OLLAMA_STATUS=$(brew services list | grep ollama | awk '{print $2}')

echo "   MongoDB: $MONGODB_STATUS"
echo "   Ollama: $OLLAMA_STATUS"

echo "=== Verification Complete ==="
EOF

chmod +x ~/verify_removal.sh
~/verify_removal.sh
rm ~/verify_removal.sh
```

## Troubleshooting Removal Issues

### Processes Won't Stop

If Greta processes won't stop normally:

```bash
# Force kill processes
sudo pkill -9 -f "uvicorn"
sudo pkill -9 -f "next"
sudo pkill -9 -f "mongod"
sudo pkill -9 -f "ollama"
```

### Files Won't Delete

If you get permission errors:

```bash
# Fix permissions and try again
sudo chown -R $(whoami) ~/Applications/CPAS
sudo chown -R $(whoami) ~/Library/Logs/Greta
rm -rf ~/Applications/CPAS ~/Library/Logs/Greta
```

### Launch Agents Won't Unload

If launch agents are stuck:

```bash
# Force unload
sudo launchctl unload ~/Library/LaunchAgents/com.cpas.mongodb.plist
sudo launchctl unload ~/Library/LaunchAgents/com.cpas.ollama.plist

# Remove files
sudo rm -f ~/Library/LaunchAgents/com.cpas.mongodb.plist
sudo rm -f ~/Library/LaunchAgents/com.cpas.ollama.plist
```

### Database Won't Stop

If MongoDB won't stop:

```bash
# Find MongoDB process
ps aux | grep mongod

# Kill specific process (replace PID)
sudo kill -9 PID

# Or force stop via brew
sudo brew services stop mongodb-community
```

## Reinstallation

### Clean Reinstall

After complete removal, to reinstall:

```bash
# Clear any cached data
brew cleanup
npm cache clean --force
pip cache purge

# Download fresh installer
curl -L -o terminal_install.sh "https://github.com/cpas-project/greta/raw/main/terminal_install.sh"
chmod +x terminal_install.sh
./terminal_install.sh
```

### Restore Configuration

If you backed up your configuration:

```bash
# After reinstalling, restore your settings
cp ~/greta_config_backup.yaml ~/Applications/CPAS/config/greta_config.yaml

# Restart Greta
~/Applications/CPAS/stop_greta.sh
~/Applications/CPAS/start_greta.sh
```

## Data Recovery

### Backup Before Removal

Before uninstalling, backup important data:

```bash
# Create backup directory
mkdir -p ~/Greta_Backup

# Backup configuration
cp ~/Applications/CPAS/config/greta_config.yaml ~/Greta_Backup/

# Backup conversation history (if exists)
cp -r ~/Applications/CPAS/data/ ~/Greta_Backup/ 2>/dev/null || true

# Backup custom plugins (if any)
cp -r ~/Applications/CPAS/plugins/ ~/Greta_Backup/ 2>/dev/null || true

echo "Backup created in ~/Greta_Backup/"
```

### Export MongoDB Data

To backup conversation and memory data:

```bash
# Export all databases
mongodump --out ~/Greta_Backup/mongodb/

# Export specific collections
mongoexport --db cpas_db --collection conversations --out ~/Greta_Backup/conversations.json
mongoexport --db cpas_db --collection memory --out ~/Greta_Backup/memory.json
```

## Support

If you encounter issues during uninstallation:

1. **Check the troubleshooting section** in this guide
2. **Run the verification script** to identify remaining components
3. **Visit our GitHub issues**: https://github.com/cpas-project/greta/issues
4. **Contact support**: support@cpas-project.com

Include the output of the verification script when requesting help.

---

*Thank you for trying CPAS Master Agent (Greta)! We hope you'll consider reinstalling in the future.*
