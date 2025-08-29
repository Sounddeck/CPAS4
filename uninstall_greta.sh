
#!/bin/bash
# CPAS Master Agent (Greta) - Complete Uninstall Script
# This script removes all Greta components and optionally removes dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Ask user for confirmation
confirm() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Stop all Greta services
stop_services() {
    log "Stopping CPAS Master Agent services..."
    
    # Stop application processes
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "next.*start" 2>/dev/null || true
    
    # Stop system services
    brew services stop mongodb-community 2>/dev/null || true
    brew services stop ollama 2>/dev/null || true
    
    log "Services stopped"
}

# Remove launch agents
remove_launch_agents() {
    log "Removing launch agents..."
    
    # Unload launch agents
    launchctl unload ~/Library/LaunchAgents/com.cpas.mongodb.plist 2>/dev/null || true
    launchctl unload ~/Library/LaunchAgents/com.cpas.ollama.plist 2>/dev/null || true
    
    # Remove launch agent files
    rm -f ~/Library/LaunchAgents/com.cpas.mongodb.plist
    rm -f ~/Library/LaunchAgents/com.cpas.ollama.plist
    
    log "Launch agents removed"
}

# Remove application files
remove_application() {
    log "Removing application files..."
    
    # Remove main application directory
    if [[ -d ~/Applications/CPAS ]]; then
        rm -rf ~/Applications/CPAS
        log "Removed ~/Applications/CPAS"
    fi
    
    # Remove app bundle (drag-and-drop installer)
    if [[ -d /Applications/Greta.app ]]; then
        rm -rf /Applications/Greta.app
        log "Removed /Applications/Greta.app"
    fi
    
    # Remove desktop shortcuts
    rm -rf ~/Desktop/"Start Greta.app" 2>/dev/null || true
    
    log "Application files removed"
}

# Remove data and logs
remove_data() {
    log "Removing data and logs..."
    
    # Remove logs
    rm -rf ~/Library/Logs/Greta
    
    # Remove application support files
    rm -rf ~/Library/Application\ Support/Greta
    
    # Remove preferences
    rm -f ~/Library/Preferences/com.cpas.greta.plist
    
    # Remove any cached data
    rm -rf ~/.cpas_cache 2>/dev/null || true
    
    log "Data and logs removed"
}

# Remove Homebrew packages
remove_homebrew_packages() {
    if confirm "Remove Homebrew packages (MongoDB, Ollama, etc.)? This may affect other applications"; then
        log "Removing Homebrew packages..."
        
        # Remove main packages
        brew uninstall mongodb-community 2>/dev/null || true
        brew uninstall ollama 2>/dev/null || true
        
        if confirm "Remove development tools (Python, Node.js, etc.)? Only do this if you don't use them elsewhere"; then
            brew uninstall python@3.11 2>/dev/null || true
            brew uninstall node@18 2>/dev/null || true
            brew uninstall portaudio 2>/dev/null || true
            brew uninstall ffmpeg 2>/dev/null || true
        fi
        
        # Remove optional tools
        brew uninstall pipx wget curl jq espeak festival mongodb-database-tools 2>/dev/null || true
        
        # Remove cask applications
        brew uninstall --cask mongodb-compass 2>/dev/null || true
        
        # Clean up
        brew autoremove
        brew cleanup
        
        log "Homebrew packages removed"
    else
        info "Keeping Homebrew packages"
    fi
}

# Remove AI models
remove_models() {
    if command -v ollama &> /dev/null; then
        if confirm "Remove AI models? This will free up several GB of disk space"; then
            log "Removing AI models..."
            
            # List and remove models
            ollama list | grep -v "NAME" | awk '{print $1}' | while read model; do
                if [[ -n "$model" ]]; then
                    ollama rm "$model" 2>/dev/null || true
                    log "Removed model: $model"
                fi
            done
            
            log "AI models removed"
        else
            info "Keeping AI models"
        fi
    fi
}

# Backup data before removal
backup_data() {
    if confirm "Create backup of configuration and data before removal?"; then
        log "Creating backup..."
        
        BACKUP_DIR="$HOME/Greta_Backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup configuration
        if [[ -f ~/Applications/CPAS/config/greta_config.yaml ]]; then
            cp ~/Applications/CPAS/config/greta_config.yaml "$BACKUP_DIR/"
        fi
        
        # Backup any custom data
        if [[ -d ~/Applications/CPAS/data ]]; then
            cp -r ~/Applications/CPAS/data "$BACKUP_DIR/"
        fi
        
        # Export MongoDB data if available
        if command -v mongodump &> /dev/null; then
            mongodump --db cpas_db --out "$BACKUP_DIR/mongodb/" 2>/dev/null || true
        fi
        
        log "Backup created at: $BACKUP_DIR"
    fi
}

# Verify removal
verify_removal() {
    log "Verifying removal..."
    
    local remaining=0
    
    # Check application files
    if [[ -d ~/Applications/CPAS ]]; then
        warning "~/Applications/CPAS still exists"
        ((remaining++))
    fi
    
    if [[ -d /Applications/Greta.app ]]; then
        warning "/Applications/Greta.app still exists"
        ((remaining++))
    fi
    
    # Check launch agents
    if [[ -f ~/Library/LaunchAgents/com.cpas.mongodb.plist ]]; then
        warning "MongoDB launch agent still exists"
        ((remaining++))
    fi
    
    if [[ -f ~/Library/LaunchAgents/com.cpas.ollama.plist ]]; then
        warning "Ollama launch agent still exists"
        ((remaining++))
    fi
    
    # Check running processes
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        warning "Backend process still running"
        ((remaining++))
    fi
    
    if pgrep -f "next.*start" > /dev/null; then
        warning "Frontend process still running"
        ((remaining++))
    fi
    
    if [[ $remaining -eq 0 ]]; then
        log "✅ Removal verification passed - Greta completely removed"
    else
        warning "⚠️  $remaining components may still remain"
    fi
}

# Main uninstall function
main() {
    echo -e "${BLUE}CPAS Master Agent (Greta) - Uninstaller${NC}"
    echo "This will remove Greta and optionally its dependencies."
    echo
    
    if ! confirm "Are you sure you want to uninstall CPAS Master Agent (Greta)?"; then
        info "Uninstallation cancelled"
        exit 0
    fi
    
    backup_data
    stop_services
    remove_launch_agents
    remove_application
    remove_data
    remove_models
    remove_homebrew_packages
    verify_removal
    
    echo
    log "🎉 CPAS Master Agent (Greta) has been successfully uninstalled!"
    echo
    echo "Thank you for trying Greta. If you decide to reinstall in the future,"
    echo "you can download the latest version from:"
    echo "https://github.com/cpas-project/greta"
    echo
    
    if [[ -d ~/Greta_Backup_* ]]; then
        echo "Your backup is available at:"
        ls -d ~/Greta_Backup_* 2>/dev/null | tail -1
        echo
    fi
}

# Handle script interruption
cleanup() {
    echo
    warning "Uninstallation interrupted by user"
    exit 1
}

trap cleanup INT

# Run main uninstall
main "$@"
