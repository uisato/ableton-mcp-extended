# Roadmap

Future plans and improvements for Ableton MCP Extended.

---

## Current Status

### ✅ Implemented Features

- Session and transport control
- Track management (create, rename, control properties)
- MIDI clip and note manipulation
- Device and parameter control
- Browser integration
- ElevenLabs voice integration
- High-performance UDP server

### ⚠️ Experimental Features

- **Clip Automation**: Works but may have issues with point placement

### ❌ Not Yet Implemented

- Scene management (create, delete, rename, fire)
- Arrangement view control
- Full VST plugin support
- Hardware MIDI controller integration

---

## Planned Features

### High Priority

#### 🎬 Scene Management
**Status:** Planned for v1.1.0

Complete implementation of scene control:

- Create and delete scenes
- Rename scenes
- Fire scenes
- Get scene information
- Scene colors

**Timeline:** Next release

---

#### 🎼 Arrangement View Support
**Status:** Planned for v1.2.0

Control Ableton's arrangement view:

- Navigate timeline
- Create and edit arrangement clips
- Automation in arrangement
- Markers and loop regions

**Timeline:** Q1 2025

---

### Medium Priority

#### 🎛️ VST Plugin Support
**Status:** Research phase

Direct control of third-party VST plugins:

- Plugin parameter mapping
- Preset management
- Plugin-specific controls

**Note:** Currently achievable through generic "Configure" parameter function

**Timeline:** Q2 2025

---

#### 🎹 Hardware MIDI Controller Integration
**Status:** Planned

Bridge physical MIDI controllers through AI:

- Map hardware controls to parameters
- Create custom controller scripts
- Bidirectional communication

**Timeline:** Q2 2025

---

#### 🔄 Undo/Redo Support
**Status:** Research phase

Implement undo/redo for MCP actions:

- Track undo stack
- Revert changes
- Redo actions

**Timeline:** TBD

---

### Low Priority / Future Ideas

#### 🎨 Max for Live Integration

- Control Max for Live devices
- Create custom Max devices
- M4L parameter mapping

---

#### 🤖 AI-Powered Music Understanding

- Analyze existing tracks
- Suggest improvements
- Generate complementary parts
- Music theory assistance

---

#### 📊 Advanced Visualization

- Real-time waveform display
- Spectral analysis
- Parameter automation visualization

---

#### 🌐 Multi-Instance Support

- Control multiple Ableton instances
- Session synchronization
- Cross-project communication

---

## Bug Fixes & Improvements

### In Progress

- [ ] Fix clip automation point placement issues
- [ ] Improve error messages for browser operations
- [ ] Add validation for parameter ranges
- [ ] Optimize connection retry logic

### Planned

- [ ] Add comprehensive test suite
- [ ] Improve documentation with more examples
- [ ] Add video tutorials
- [ ] Create community examples repository

---

## Community Requests

Have a feature request? We'd love to hear from you!

- **GitHub Issues**: [Submit a feature request](https://github.com/MarvinHauke/ableton-mcp-extended/issues/new?template=feature_request.md)
- **GitHub Discussions**: [Discuss ideas](https://github.com/MarvinHauke/ableton-mcp-extended/discussions)

Popular community requests:

1. **Scene Management** (many requests) - ✅ Planned for v1.1.0
2. **Arrangement View** (many requests) - ✅ Planned for v1.2.0
3. **Undo/Redo** - Under consideration
4. **VST Control** - Under research

---

## Contributing

Want to help implement these features?

Check out our [Contributing Guide](contributing.md) to get started!

---

## Release History

### v1.0.0 (Current)

- ✅ Core MCP server implementation
- ✅ Session and transport control
- ✅ Track management
- ✅ MIDI clip and note manipulation
- ✅ Device and parameter control
- ✅ Browser integration
- ✅ ElevenLabs integration
- ✅ UDP high-performance server
- ✅ XY Mouse Controller example

---

## Stay Updated

- **Watch the repo** on GitHub for release notifications
- **Star the project** to show support
- **Follow development** through GitHub Issues and Pull Requests

---

*This roadmap is subject to change based on community feedback and development priorities.*
