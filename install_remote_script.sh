#!/bin/bash

# AbletonMCP Remote Script Installer
# This script copies the enhanced remote script to Ableton Live's MIDI Remote Scripts directory

set -e  # Exit on any error

echo "🎵 AbletonMCP Remote Script Installer"
echo "======================================"

# Define paths
SOURCE_SCRIPT="./AbletonMCP_Remote_Script/__init__.py"
ABLETON_SUITE_PATH="/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/"
ABLETON_BETA_PATH="/Applications/Ableton Live 12 Beta.app/Contents/App-Resources/MIDI Remote Scripts/AbletonMCP/"

# Check if source script exists
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "❌ Error: Source script not found at $SOURCE_SCRIPT"
    echo "   Make sure you're running this from the ableton-mcp-extended directory"
    exit 1
fi

echo "📁 Source script found: $SOURCE_SCRIPT"

# Function to install to a specific Ableton version
install_to_ableton() {
    local ableton_path="$1"
    local version_name="$2"
    
    if [ -d "$(dirname "$ableton_path")" ]; then
        echo "📦 Installing to $version_name..."
        
        # Create directory if it doesn't exist
        sudo mkdir -p "$ableton_path"
        
        # Copy the script
        sudo cp "$SOURCE_SCRIPT" "$ableton_path"
        
        # Set proper permissions
        sudo chmod 644 "$ableton_path/__init__.py"
        
        echo "✅ Successfully installed to $version_name"
        return 0
    else
        echo "⚠️  $version_name not found, skipping..."
        return 1
    fi
}

# Install to both versions if they exist
installed_count=0

if install_to_ableton "$ABLETON_SUITE_PATH" "Ableton Live 12 Suite"; then
    ((installed_count++))
fi

if install_to_ableton "$ABLETON_BETA_PATH" "Ableton Live 12 Beta"; then
    ((installed_count++))
fi

# Summary
echo ""
echo "📊 Installation Summary:"
echo "======================="
if [ $installed_count -eq 0 ]; then
    echo "❌ No Ableton Live installations found!"
    echo "   Make sure Ableton Live 12 is installed in /Applications/"
    exit 1
else
    echo "✅ Remote script installed to $installed_count Ableton version(s)"
    echo ""
    echo "🔄 Next Steps:"
    echo "1. Restart Ableton Live completely"
    echo "2. Go to Live → Preferences → MIDI"
    echo "3. Set 'Control Surface' to 'AbletonMCP' (if not already set)"
    echo "4. Try loading the Analog Lab V plugin using the MCP server"
    echo ""
    echo "🎉 Enhanced plugin loading functionality is now available!"
fi