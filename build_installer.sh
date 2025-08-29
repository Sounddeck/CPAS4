
#!/bin/bash
# CPAS Master Agent - Mac Installer Builder
# This script creates the complete Mac application bundle

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="/home/ubuntu/cpas_enhanced"
BUILD_DIR="$SCRIPT_DIR"
APP_BUNDLE="$BUILD_DIR/Greta.app"
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Copy source code to app bundle
copy_source_code() {
    log "Copying source code to app bundle..."
    
    # Copy backend
    cp -r "$SOURCE_DIR/backend" "$RESOURCES_DIR/"
    cp "$SOURCE_DIR/requirements.txt" "$RESOURCES_DIR/backend/"
    
    # Copy frontend
    cp -r "$SOURCE_DIR/frontend" "$RESOURCES_DIR/"
    
    # Copy configuration files
    cp -r "$SOURCE_DIR/config" "$RESOURCES_DIR/" 2>/dev/null || true
    
    # Copy any additional scripts
    cp -r "$SOURCE_DIR/scripts" "$RESOURCES_DIR/" 2>/dev/null || true
}

# Create Python virtual environment in the bundle
setup_bundle_python() {
    log "Setting up Python environment in bundle..."
    
    cd "$RESOURCES_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Build frontend for production
build_frontend() {
    log "Building frontend for production..."
    
    cd "$RESOURCES_DIR/frontend"
    npm install
    npm run build
}

# Make launcher executable
make_executable() {
    log "Making launcher executable..."
    chmod +x "$APP_BUNDLE/Contents/MacOS/greta_launcher"
    chmod +x "$RESOURCES_DIR/scripts/install_dependencies.sh"
}

# Create DMG installer
create_dmg() {
    log "Creating DMG installer..."
    
    DMG_NAME="Greta-CPAS-Master-Agent-v1.0.0"
    DMG_PATH="$BUILD_DIR/$DMG_NAME.dmg"
    
    # Remove existing DMG
    rm -f "$DMG_PATH"
    
    # Create temporary directory for DMG contents
    DMG_TEMP="$BUILD_DIR/dmg_temp"
    rm -rf "$DMG_TEMP"
    mkdir -p "$DMG_TEMP"
    
    # Copy app bundle to temp directory
    cp -r "$APP_BUNDLE" "$DMG_TEMP/"
    
    # Create Applications symlink
    ln -s /Applications "$DMG_TEMP/Applications"
    
    # Create README for DMG
    cat > "$DMG_TEMP/README.txt" << EOF
CPAS Master Agent (Greta) v1.0.0

INSTALLATION INSTRUCTIONS:
1. Drag Greta.app to the Applications folder
2. Open Greta from Applications folder
3. Follow the setup wizard to install dependencies
4. Enjoy your AI assistant!

For detailed instructions, see the documentation at:
https://github.com/cpas-project/greta

SYSTEM REQUIREMENTS:
- macOS 10.15 (Catalina) or later
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space
- Internet connection for initial setup

SUPPORT:
- Documentation: See included docs folder
- Issues: Report at GitHub repository
- Email: support@cpas-project.com
EOF
    
    # Create DMG
    hdiutil create -volname "$DMG_NAME" -srcfolder "$DMG_TEMP" -ov -format UDZO "$DMG_PATH"
    
    # Clean up temp directory
    rm -rf "$DMG_TEMP"
    
    log "DMG created: $DMG_PATH"
}

# Main build process
main() {
    log "Building CPAS Master Agent Mac installer..."
    
    copy_source_code
    setup_bundle_python
    build_frontend
    make_executable
    create_dmg
    
    log "Build completed successfully!"
    log "Installer location: $BUILD_DIR/Greta-CPAS-Master-Agent-v1.0.0.dmg"
}

main "$@"
