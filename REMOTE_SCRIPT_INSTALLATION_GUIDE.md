# 🎛️ ABLETON MCP REMOTE SCRIPT INSTALLATION GUIDE

## 🚨 **CRITICAL: The Remote Script is NOT currently installed!**

This is why you're seeing "all wavetable pads only" - the instruments aren't actually loading.

## 📁 **STEP 1: Find Ableton Live's Remote Scripts Directory**

### **Mac:**
```bash
# Navigate to Ableton's MIDI Remote Scripts folder
cd "/Applications/Ableton Live 12 Standard.app/Contents/App-Resources/MIDI Remote Scripts/"

# OR for other versions:
cd "/Applications/Ableton Live 11 Standard.app/Contents/App-Resources/MIDI Remote Scripts/"
```

### **Windows:**
```cmd
# Navigate to Ableton's MIDI Remote Scripts folder
cd "C:\Program Files\Ableton\Live\Resources\MIDI Remote Scripts\"
```

## 📋 **STEP 2: Create AbletonMCP Directory**

```bash
# Create the AbletonMCP folder
mkdir AbletonMCP

# List existing scripts to confirm location
ls -la
```

You should see folders like:
- `Push2/`
- `Launchkey_MK3/`
- `APC40_MkII/`
- etc.

## 📝 **STEP 3: Copy Remote Script Files**

Copy your `AbletonMCP_Remote_Script/__init__.py` to the new directory:

```bash
# Copy the Remote Script file
cp "/path/to/your/project/AbletonMCP_Remote_Script/__init__.py" "AbletonMCP/__init__.py"

# Verify the file was copied
ls -la AbletonMCP/
```

## ⚙️ **STEP 4: Activate in Ableton Live**

1. **Open Ableton Live**
2. **Go to Preferences** (Cmd+, on Mac, Ctrl+, on Windows)
3. **Click "Link, Tempo & MIDI" tab**
4. **In the "Control Surface" section:**
   - Set **Control Surface** dropdown to **"AbletonMCP"**
   - Set **Input** to **"None"** 
   - Set **Output** to **"None"**

## 🔍 **STEP 5: Verify Installation**

1. **Restart Ableton Live completely**
2. **Check the log file** for AbletonMCP messages:
   ```bash
   # Mac - check for our Remote Script in logs
   tail -f ~/Library/Preferences/Ableton/Live*/Log.txt | grep -i "ableton"
   ```

3. **You should see:**
   ```
   MidiRemoteScript X [Control Surface="AbletonMCP" Input="None" Output="None"]
   ```

## 🧪 **STEP 6: Test Connection**

Run our test script:
```bash
python test_instrument_loading_fix.py
```

**Expected successful output:**
```
✅ Loaded drum_rack on drums
✅ Loaded wavetable_bass on bass  
✅ Loaded wavetable_synth on pads
✅ Loaded wavetable_synth on lead
```

## 🚨 **TROUBLESHOOTING:**

### **If AbletonMCP doesn't appear in dropdown:**
1. **Check file permissions:**
   ```bash
   chmod 644 AbletonMCP/__init__.py
   ```

2. **Check file syntax:**
   ```bash
   python -m py_compile AbletonMCP/__init__.py
   ```

3. **Restart Ableton Live completely**

### **If still not working:**
1. **Delete .pyc files:**
   ```bash
   rm AbletonMCP/*.pyc
   ```

2. **Check Ableton Live version compatibility**
3. **Verify directory structure matches exactly**

## 📊 **CURRENT STATUS:**

- ❌ **Remote Script**: NOT INSTALLED
- ❌ **Instrument Loading**: FAILING (uses default behavior)  
- ❌ **Scale Constraints**: NOT WORKING
- ❌ **Clip Length Control**: NOT WORKING

## 🎯 **AFTER PROPER INSTALLATION:**

- ✅ **Remote Script**: ACTIVE
- ✅ **Instrument Loading**: WORKING (diverse instruments)
- ✅ **Scale Constraints**: WORKING (A-minor, etc.)
- ✅ **Clip Length Control**: WORKING (full-length clips)
- ✅ **AI Music Generation**: WORKING (coherent output)

---

## 🚀 **QUICK INSTALL SCRIPT (Mac):**

```bash
#!/bin/bash
echo "🎛️ Installing AbletonMCP Remote Script..."

# Find Ableton Live installation
ABLETON_DIR="/Applications/Ableton Live 12 Standard.app/Contents/App-Resources/MIDI Remote Scripts"
if [ ! -d "$ABLETON_DIR" ]; then
    ABLETON_DIR="/Applications/Ableton Live 11 Standard.app/Contents/App-Resources/MIDI Remote Scripts"
fi

# Create AbletonMCP directory
mkdir -p "$ABLETON_DIR/AbletonMCP"

# Copy Remote Script
cp "AbletonMCP_Remote_Script/__init__.py" "$ABLETON_DIR/AbletonMCP/__init__.py"

echo "✅ Remote Script installed at: $ABLETON_DIR/AbletonMCP/"
echo "🔧 Now activate it in Ableton Live Preferences → Link, Tempo & MIDI"
echo "🔄 Restart Ableton Live to load the script"
```

**Run this script in your project directory to auto-install!** 