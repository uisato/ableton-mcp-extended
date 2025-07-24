#!/bin/bash

echo "🎛️ AbletonMCP Remote Script Installer"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "AbletonMCP_Remote_Script/__init__.py" ]; then
    echo "❌ Error: AbletonMCP_Remote_Script/__init__.py not found!"
    echo "Please run this script from your project root directory."
    exit 1
fi

# Find Ableton Live installation
ABLETON_DIR=""
LIVE_VERSIONS=("12 Standard" "12 Suite" "11 Standard" "11 Suite" "11 Intro")

for version in "${LIVE_VERSIONS[@]}"; do
    potential_dir="/Applications/Ableton Live ${version}.app/Contents/App-Resources/MIDI Remote Scripts"
    if [ -d "$potential_dir" ]; then
        ABLETON_DIR="$potential_dir"
        echo "✅ Found Ableton Live ${version}"
        break
    fi
done

if [ -z "$ABLETON_DIR" ]; then
    echo "❌ Error: Could not find Ableton Live installation!"
    echo "Please check that Ableton Live is installed in /Applications/"
    echo "Supported versions: Live 11, Live 12 (Standard, Suite, Intro)"
    exit 1
fi

echo "📁 Installation directory: $ABLETON_DIR"

# Create AbletonMCP directory
TARGET_DIR="$ABLETON_DIR/AbletonMCP"
echo "📂 Creating Remote Script directory..."
mkdir -p "$TARGET_DIR"

# Copy Remote Script
echo "📋 Copying Remote Script files..."
cp "AbletonMCP_Remote_Script/__init__.py" "$TARGET_DIR/__init__.py"

# Set proper permissions
chmod 644 "$TARGET_DIR/__init__.py"

# Verify installation
if [ -f "$TARGET_DIR/__init__.py" ]; then
    echo "✅ Remote Script installed successfully!"
    echo ""
    echo "🔧 NEXT STEPS:"
    echo "1. Open Ableton Live"
    echo "2. Go to Preferences → Link, Tempo & MIDI"
    echo "3. Set Control Surface to 'AbletonMCP'"
    echo "4. Set Input and Output to 'None'"
    echo "5. Restart Ableton Live"
    echo ""
    echo "🧪 TEST:"
    echo "python test_instrument_loading_fix.py"
    echo ""
    echo "📊 Installation Details:"
    echo "   Target: $TARGET_DIR"
    echo "   Size: $(ls -lh "$TARGET_DIR/__init__.py" | awk '{print $5}')"
    echo "   Permissions: $(ls -l "$TARGET_DIR/__init__.py" | awk '{print $1}')"
else
    echo "❌ Installation failed!"
    echo "Could not copy Remote Script to $TARGET_DIR"
    exit 1
fi 