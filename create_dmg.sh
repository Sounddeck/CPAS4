
#!/bin/bash
# Create DMG installer for CPAS Master Agent (Greta)
# This script creates a professional DMG installer with custom background and layout

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
APP_BUNDLE="$SCRIPT_DIR/Greta.app"
DMG_NAME="Greta-CPAS-Master-Agent-v1.0.0"
DMG_PATH="$BUILD_DIR/$DMG_NAME.dmg"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Create build directory
mkdir -p "$BUILD_DIR"

# Remove existing DMG
rm -f "$DMG_PATH"

log "Creating DMG installer for CPAS Master Agent..."

# Create temporary directory for DMG contents
DMG_TEMP="$BUILD_DIR/dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copy app bundle to temp directory
log "Copying application bundle..."
cp -r "$APP_BUNDLE" "$DMG_TEMP/"

# Create Applications symlink for easy installation
log "Creating Applications symlink..."
ln -s /Applications "$DMG_TEMP/Applications"

# Create documentation folder
log "Adding documentation..."
mkdir -p "$DMG_TEMP/Documentation"
cp -r docs/* "$DMG_TEMP/Documentation/"

# Create README for DMG
log "Creating installer README..."
cat > "$DMG_TEMP/README - Start Here.txt" << 'EOF'
CPAS Master Agent (Greta) v1.0.0
================================

Welcome to your new AI assistant!

QUICK INSTALLATION:
1. Drag "Greta.app" to the "Applications" folder
2. Open Greta from your Applications folder
3. Follow the setup wizard
4. Start talking to your AI assistant!

WHAT IS GRETA?
- German-accented AI assistant with customizable personality
- Voice activation with wake-word detection
- Complete OSINT intelligence suite
- Mac-native interface with beautiful design
- Privacy-focused with local processing options

VOICE ACTIVATION:
- Say "Greta" to wake up your assistant
- Try: "What time is it?" or "Search for Tesla"
- Customize the wake word and personality in Settings

SYSTEM REQUIREMENTS:
- macOS 10.15 (Catalina) or later
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space
- Internet connection for initial setup

DOCUMENTATION:
- See the "Documentation" folder for detailed guides
- Quick Start Guide for 5-minute setup
- Voice Activation Guide for customization
- Troubleshooting Guide for problem solving

SUPPORT:
- GitHub: https://github.com/cpas-project/greta
- Email: support@cpas-project.com
- Documentation: https://docs.cpas-project.com

Enjoy your new AI assistant!
EOF

# Create installation script for advanced users
log "Creating terminal installation option..."
cp terminal_install.sh "$DMG_TEMP/Terminal Installation (Advanced).sh"
chmod +x "$DMG_TEMP/Terminal Installation (Advanced).sh"

# Create uninstaller
cp uninstall_greta.sh "$DMG_TEMP/Uninstall Greta.sh"
chmod +x "$DMG_TEMP/Uninstall Greta.sh"

# Create custom DMG background (text-based for now)
cat > "$DMG_TEMP/.DS_Store_template" << 'EOF'
# Custom DMG layout instructions
# This would normally contain binary data for Finder window positioning
# For now, we'll rely on default layout
EOF

# Set custom volume name and create DMG
log "Creating DMG file..."
hdiutil create \
    -volname "CPAS Master Agent (Greta) v1.0.0" \
    -srcfolder "$DMG_TEMP" \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    "$DMG_PATH"

# Clean up temp directory
rm -rf "$DMG_TEMP"

# Get DMG size
DMG_SIZE=$(du -h "$DMG_PATH" | cut -f1)

log "✅ DMG installer created successfully!"
info "Location: $DMG_PATH"
info "Size: $DMG_SIZE"
info "Volume name: CPAS Master Agent (Greta) v1.0.0"

echo
echo "📦 DMG Contents:"
echo "   • Greta.app (drag to Applications)"
echo "   • Applications symlink"
echo "   • README - Start Here.txt"
echo "   • Documentation folder"
echo "   • Terminal Installation (Advanced).sh"
echo "   • Uninstall Greta.sh"
echo

echo "🚀 Ready for distribution!"
echo "Users can now:"
echo "   1. Download and mount the DMG"
echo "   2. Drag Greta.app to Applications"
echo "   3. Launch and enjoy their AI assistant"
echo

# Verify DMG
log "Verifying DMG integrity..."
if hdiutil verify "$DMG_PATH"; then
    log "✅ DMG verification passed"
else
    log "❌ DMG verification failed"
    exit 1
fi

echo "🎉 CPAS Master Agent installer is ready for distribution!"
