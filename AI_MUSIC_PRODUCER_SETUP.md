# AI Music Producer Extension - Setup Guide

## 🎵 Quick Setup

### 1. Get Your Google AI API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it in your environment:
```bash
export GOOGLE_AI_API_KEY="your-api-key-here"
```

### 2. Install Dependencies
```bash
pip install google-generativeai>=0.8.0 librosa pretty_midi scipy scikit-learn pydantic
```

### 3. Test Installation
```bash
python test_ai_producer.py
```

### 4. Try the Demo
```bash
python demo_ai_music_producer.py
```

## 🎛️ Available AI Tools

### High-Level Generation
- **`generate_complete_track`**: Complete track from description
- **`analyze_and_replicate_style`**: Analyze and recreate any style
- **`create_arrangement_from_elements`**: Professional arrangement

### Style-Specific Generators
- **`create_afro_house_track`**: Black Coffee style
- **`create_keinemusik_style_track`**: Sophisticated deep house
- **`create_progressive_house_anthem`**: Epic progressive house

### Utilities
- **`get_style_characteristics`**: Style database lookup
- **`get_plugin_recommendation`**: Ableton plugin advice
- **`chat_with_ai_producer`**: Interactive guidance

## 🎨 Example Usage

### In Claude Desktop
```
👤 "Generate a complete Afro House track inspired by Black Coffee at 122 BPM"

🤖 Creates complete production plan with:
   - Style analysis
   - Track elements
   - Chord progressions
   - Arrangement structure
   - Plugin recommendations
   - Next steps
```

### Interactive Chat
```
👤 "How do I create a warm Afro House bassline using stock plugins?"

🤖 Provides detailed guidance:
   - Use Bass plugin with analog character
   - Filter settings for warmth
   - Envelope shaping
   - Effect chain recommendations
```

## 🔧 Integration with MCP

Add to your `mcp_config.json`:
```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": ["/path/to/ableton-mcp-extended/enhanced_mcp_tools.py"],
      "env": {
        "GOOGLE_AI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🎹 Supported Styles

- **Afro House**: Black Coffee, organic percussion, warm basslines
- **Keinemusik**: Sophisticated deep house, vintage electric pianos
- **Progressive House**: Eric Prydz, epic builds, emotional breakdowns
- **Deep House**: Dixon, jazz influences, vintage warmth
- **Tech House**: Punchy, tribal elements, rolling basslines

## 🎵 What You Get

### Complete Track Generation
1. **Style Analysis** - Deep understanding of genre characteristics
2. **Track Elements** - All necessary components (kick, bass, leads, etc.)
3. **Harmonic Progression** - Style-appropriate chord sequences
4. **Arrangement Plan** - Professional song structure
5. **Plugin Settings** - Specific Ableton stock plugin configurations
6. **Mixing Guidelines** - Professional approach for the style

### Stock Plugin Mastery
- **Wavetable**: Advanced synthesis for any sound
- **Bass**: Analog-style bass sounds
- **Impulse**: Complete drum programming
- **Effect Chains**: Professional processing templates

## 🚀 Next Steps

1. Try the test script to verify installation
2. Run the demo to see all capabilities
3. Start with simple requests in your AI assistant
4. Explore interactive chat for learning
5. Create your first AI-generated track!

## 🎤 Share Your Creations

Tag [@uisato_](https://www.instagram.com/uisato_) with your AI-generated music! We love seeing what the community creates.

Happy music making! 🎵 