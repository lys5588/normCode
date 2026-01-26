# NormCode Canvas - Build Guide

This guide explains how to build NormCode Canvas into a standalone desktop application for Windows and macOS.

## Overview

The build scripts automate the entire process:
- Install required Python dependencies
- Install backend dependencies
- Build the frontend (npm run build)
- Package everything with PyInstaller
- Optionally create installers (Inno Setup for Windows, DMG for macOS)

## Prerequisites

### Common Requirements (All Platforms)
1. **Python 3.8+** with pip
2. **Node.js 18+** with npm
3. Git (for version control)

### Windows-Specific Requirements

**Required for build:**
- Python 3.8+ (64-bit recommended)
- PyInstaller (auto-installed by script)
- pywebview with CEF support
- Node.js 18+ with npm

**Optional:**
- **Inno Setup 6** - Download from https://jrsoftware.org/isdl.php (for installer creation)
- **WebView2 Runtime** - Auto-detects, fallback to CEF if not available

### macOS-Specific Requirements

**Required:**
- macOS 10.15+ (Catalina or later recommended)
- Python 3.10+
- Node.js 18+ with npm

**Optional:**
- **Xcode Command Line Tools** - `xcode-select --install` (for code signing and iconutil)
- **Apple Developer Account** - Required for distribution outside App Store

---

## Quick Start

### Windows

```powershell
# Navigate to build directory
cd build

# Run the build script (auto-installs dependencies)
python build_windows.py

# The executable will be at: build/dist/NormCodeCanvas/NormCodeCanvas.exe
```

### macOS

```bash
# Navigate to build directory
cd build

# Run the build script (auto-installs dependencies)
python build_macos.py

# The application will be at: build/dist/NormCodeCanvas.app
```

---

## Build Options

### Windows Build Options

```powershell
# Full build (default, windowed mode, no console)
python build_windows.py

# Build with console for debugging
python build_windows.py --debug

# Skip frontend build (use existing dist - faster for repeated builds)
python build_windows.py --skip-frontend

# Skip dependency installation (for faster rebuilds)
python build_windows.py --skip-deps

# Clean build artifacts before building
python build_windows.py --clean

# Create portable ZIP distribution
python build_windows.py --portable

# Create installer (requires Inno Setup)
python build_windows.py --installer

# Combine multiple options
python build_windows.py --clean --installer --portable
```

### macOS Build Options

```bash
# Full build (default)
python build_macos.py

# Skip frontend build (use existing dist)
python build_macos.py --skip-frontend

# Skip dependency installation
python build_macos.py --skip-deps

# Clean build artifacts before building
python build_macos.py --clean

# Create portable ZIP
python build_macos.py --portable

# Create DMG installer
python build_macos.py --dmg

# Code sign with specific identity
python build_macos.py --sign "Developer ID Application: Your Name"

# Combine multiple options
python build_macos.py --clean --dmg --portable
```

---

## Build Process

The build scripts perform these steps automatically:

### 1. Dependency Installation

**Windows:**
- PyInstaller
- Pillow (for icon conversion)
- pywebview[cef] (native desktop window with CEF fallback)
- bottle
- pythonnet (for EdgeChromium integration)
- clr-loader (.NET runtime loader)

**macOS:**
- PyInstaller
- Pillow (for icon conversion)

Then both install backend Python dependencies from `canvas_app/backend/requirements.txt`

### 2. Frontend Build

```bash
cd canvas_app/frontend
npm install      # Install dependencies if not present
npm run build    # Build React/TypeScript to static files
```

Output: `canvas_app/frontend/dist/`

### 3. Icon Processing

**Windows:**
- Reads `build/resources/Psylensai_log_raw.png`
- Creates `icon.ico` with multiple sizes (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256)
- Uses LANCZOS resampling for high-quality icons

**macOS:**
- Reads `build/resources/Psylensai_log_raw.png`
- Creates `icon.icns` with standard and retina sizes (16, 32, 64, 128, 256, 512, 1024)
- Uses iconutil for native macOS icon format
- Creates 2x retina versions for sizes up to 512

### 4. PyInstaller Packaging

**Windows:**
- Creates executable at `build/dist/NormCodeCanvas/`
- Bundles Python runtime and dependencies
- Includes frontend dist files
- Includes backend code
- Uses Tkinter/pywebview for desktop window

**macOS:**
- Creates .app bundle at `build/dist/NormCodeCanvas.app`
- Bundles Python runtime and dependencies
- Includes frontend dist files in Resources/
- Includes backend code
- Applies ad-hoc code signing by default

### 5. Installer Creation (Optional)

**Windows (Inno Setup):**
- Reads configuration from `build/installer.iss`
- Creates standard Windows installer
- Output: `build/output/NormCodeCanvasSetup-x.x.x.exe`

**macOS (DMG):**
- Creates disk image with optimized compression
- Includes Applications symlink for drag-and-drop install
- Supports custom background image
- Output: `build/dist/NormCodeCanvas-x.x.x.dmg`

---

## Output Structure

### Windows Output

```
build/
├── dist/
│   ├── NormCodeCanvas/
│   │   ├── NormCodeCanvas.exe          # Main executable
│   │   ├── _internal/                  # Python runtime and dependencies
│   │   │   ├── frontend/dist/          # Built frontend
│   │   │   ├── backend/                # Backend code
│   │   │   └── infra/                  # NormCode infrastructure
│   │   ├── settings.yaml.example       # Configuration template
│   │   └── resources/                  # Icons and assets
│   └── NormCodeCanvas-Portable.zip     # Portable distribution
└── release/
    └── NormCodeCanvas.exe              # Single executable copy

build/output/ (if installer created)
└── NormCodeCanvasSetup-x.x.x.exe       # Windows installer
```

### macOS Output

```
build/
└── dist/
    ├── NormCodeCanvas.app/             # Application bundle
    │   └── Contents/
    │       ├── Info.plist              # App metadata
    │       ├── MacOS/
    │       │   └── NormCodeCanvas      # Main executable
    │       ├── Resources/
    │       │   ├── icon.icns           # App icon
    │       │   ├── frontend/dist/      # Built frontend
    │       │   ├── backend/            # Backend code
    │       │   ├── infra/              # NormCode infrastructure
    │       │   └── settings.yaml.example
    │       └── Frameworks/             # Python runtime and dependencies
    ├── NormCodeCanvas-x.x.x-macos.zip  # Portable distribution
    └── NormCodeCanvas-x.x.x.dmg        # DMG installer
```

---

## Running the Built Application

### Windows

**Standalone Executable:**
```powershell
# Run directly
.\build\dist\NormCodeCanvas\NormCodeCanvas.exe

# Or use release folder
.\build\release\NormCodeCanvas.exe
```

**Portable ZIP:**
- Extract `NormCodeCanvas-Portable.zip`
- Run `NormCodeCanvas.exe` from extracted folder

**Installer:**
- Run `NormCodeCanvasSetup-x.x.x.exe`
- Follow the installation wizard
- Launch from Start Menu or desktop shortcut

### macOS

**Application Bundle:**
```bash
# Open the .app directly
open build/dist/NormCodeCanvas.app

# Or drag to Applications folder and run from there
cp -R build/dist/NormCodeCanvas.app /Applications/
open -a NormCodeCanvas
```

**Portable ZIP:**
- Extract `NormCodeCanvas-x.x.x-macos.zip`
- Open the .app bundle
- May need to right-click → Open on first run (security warning)

**DMG Installer:**
- Open `NormCodeCanvas-x.x.x.dmg`
- Drag NormCodeCanvas.app to Applications folder
- Launch from Applications
- May need to allow on first launch (System Preferences → Security & Privacy)

---

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Install backend dependencies manually
pip install -r canvas_app/backend/requirements.txt

# Install PyInstaller
pip install pyinstaller
```

**Frontend build fails**
```bash
cd canvas_app/frontend
npm install
npm run build
```

**Icon not showing or invalid**
- Ensure `build/resources/Psylensai_log_raw.png` exists
- Check Pillow is installed: `pip install pillow`
- On macOS, install Xcode Command Line Tools: `xcode-select --install`

**Large executable size**
- The executable includes the full Python runtime (~100MB+)
- To reduce size: use UPX compression (enabled by default)
- Exclude unnecessary packages in the spec file
- This is normal for Python applications

### Windows-Specific Issues

**Inno Setup not found**
- Download from: https://jrsoftware.org/isdl.php
- Install to default location: `C:\Program Files (x86)\Inno Setup 6\`
- Or skip installer creation: just use portable ZIP

**WebView2 Runtime not found**
- App will automatically fallback to CEF
- Users can install WebView2 if needed: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- Not required for basic functionality

**Console window appearing**
- Use `--debug` flag to keep console for debugging
- Default mode hides console (windowed application)

**Process locked during clean**
- Close any running instances of NormCodeCanvas
- Use `python build_windows.py --clean` to kill processes automatically

### macOS-Specific Issues

**"Unidentified developer" warning**
- Right-click → Open to bypass on first run
- Or go to System Preferences → Security & Privacy → click "Open Anyway"
- For distribution, code sign with Apple Developer certificate: `--sign "Developer ID Application: Name"`

**iconutil not found**
- Install Xcode Command Line Tools: `xcode-select --install`
- Required for creating .icns icons from PNG

**codesign not found**
- Install Xcode Command Line Tools: `xcode-select --install`
- Ad-hoc signing is automatic (no identity required)

**DMG creation fails**
- Ensure hdiutil is available (built-in on macOS)
- Check disk space

**App won't run on other Macs**
- Use code signing with Apple Developer certificate
- Consider notarization for distribution outside App Store

---

## Customization

### Application Icon

**Windows:**
- Place `Psylensai_log_raw.png` in `build/resources/`
- Script auto-generates `icon.ico` with all required sizes
- Recommended: 1024x1024 PNG with transparency

**macOS:**
- Place `Psylensai_log_raw.png` in `build/resources/`
- Script auto-generates `icon.icns` using iconutil
- Recommended: 1024x1024 PNG with transparency

### Version Information

Edit `build/installer.iss`:
```ini
#define MyAppVersion "1.0.0"
#define MyAppName "NormCode Canvas"
```

The macOS build script reads these values to keep versions in sync.

### Installer Branding (Windows)

Place these files in `build/resources/`:
- `banner.bmp` (164×314 pixels) - Top banner in installer
- `wizard.bmp` (55×58 pixels) - Small wizard icon

### DMG Background (macOS)

Place `dmg-background.png` in `build/resources/`
- Will be used as DMG window background

---

## Distribution

### Distribution Formats

**Windows:**

| Format | File | Description | Use Case |
|--------|------|-------------|----------|
| Portable | `build/dist/NormCodeCanvas-Portable.zip` | Extract and run | Testing, quick distribution |
| Installer | `build/output/NormCodeCanvasSetup-x.x.x.exe` | Standard installer | End-user distribution |

**macOS:**

| Format | File | Description | Use Case |
|--------|------|-------------|----------|
| Portable | `build/dist/NormCodeCanvas-x.x.x-macos.zip` | Extract and run | Testing, internal distribution |
| DMG | `build/dist/NormCodeCanvas-x.x.x.dmg` | Drag-and-drop installer | End-user distribution |

### Code Signing and Notarization (macOS)

**Levels of Signing:**

1. **Ad-hoc signed** (default)
   - App runs but shows "unidentified developer" warning
   - Suitable for personal use and testing

2. **Developer signed**
   - Requires Apple Developer account ($99/year)
   - Users still see warning on first run
   - Use: `--sign "Developer ID Application: Your Name"`

3. **Notarized** (recommended for distribution)
   - Required for distribution outside App Store
   - Additional steps after code signing:
   ```bash
   xcrun notarytool submit NormCodeCanvas-x.x.x.dmg --apple-id "your@email.com" --password "app-specific-password" --team-id "TEAMID"
   xcrun stapler staple NormCodeCanvas-x.x.x.dmg
   ```

---

## Development vs Production

| Aspect | Development | Production (Packaged) |
|--------|-------------|----------------------|
| Frontend | Vite dev server (port 5173) | Static files served by backend |
| Backend | Separate uvicorn process | Embedded in executable/app bundle |
| Hot Reload | Yes | No |
| Console | Terminal output | GUI window (Windows) / None (macOS) |
| Dependencies | Virtual environment | Bundled with PyInstaller |
| Updates | Git pull | Rebuild and reinstall |
| Debugging | Full stack traces | Limited (use --debug flag on Windows) |

---

## Platform-Specific Notes

### Windows

- Uses pywebview for native desktop window
- Supports EdgeChromium (WebView2) and CEF as fallback
- Console can be enabled for debugging with `--debug` flag
- Inno Setup creates a standard Windows installer
- Executable size is larger due to embedded Python runtime
- Single-file distribution possible with modifications

### macOS

- Uses pywebview for native desktop window (Tkinter-based)
- Creates a native `.app` bundle with proper structure
- DMG includes an Applications folder symlink for drag-and-drop install
- Ad-hoc signing is applied by default
- Supports dark mode and high-resolution displays
- For distribution, consider full code signing and notarization
- Requires macOS 10.15+ for proper functionality

---

## Application Data Storage

When running the packaged application, all runtime data is stored in platform-specific directories to ensure write access and prevent issues with read-only installations (e.g., DMG images).

### macOS

**Location:** `~/Library/Application Support/NormCode Canvas/`

**Contents:**
- `webview_data/` - pywebview storage (cookies, local storage, cache)
- Other application data (project registries, settings, etc.)

**Example:**
```bash
# For user "lys"
/Users/lys/Library/Application Support/NormCode Canvas/
```This directory is:
- Automatically created on first launch
- Fully writable from the application
- Preserved across application updates
- Not affected by read-only DMG or app bundle permissions

### Windows

**Location:** `C:\Users\<username>\.normcode-canvas\`

**Contents:**
- `webview_data/` - pywebview storage
- `deployment-servers.json` - Deployment server configurations
- `project-registry.json` - Project metadata
- `uploads/` - Uploaded files
- `llm-settings.json` - LLM configuration

**Example:**
```
C:\Users\lys\.normcode-canvas\
```

**Note:** This directory is compatible with development mode, where data is stored in the same location.

### Linux

**Location:** `~/.normcode-canvas/`

**Contents:** Similar to Windows

**Example:**
```bash
/home/lys/.normcode-canvas/
```

### Why These Locations?

The application uses platform-specific standard locations for data storage:

1. **macOS:** Uses `~/Library/Application Support/` - the standard location for application data
2. **Windows & Linux:** Uses `~/.normcode-canvas/` - following the XDG Base Directory Specification for Linux and common Windows practice

**Benefits:**
- ✅ Always writable, even when app is installed in read-only locations (DMG, Program Files)
- ✅ Isolated from application files, so updates don't delete user data
- ✅ Follows platform conventions
- ✅ Easy to backup or migrate
- ✅ Same location in development and production modes

### Managing Application Data

**To view application data on macOS:**
```bash
# Open in Finder
open ~/Library/Application\ Support/NormCode\ Canvas/

# Or navigate manually
cd ~/Library/Application Support/NormCode Canvas
```

**To view application data on Windows:**
```powershell
# Open in File Explorer
explorer %USERPROFILE%\.normcode-canvas
```

**To backup application data:**
```bash
# macOS/Linux
cp -r ~/Library/Application\ Support/NormCode\ Canvas ~/backup/normcode-canvas-backup

# Windows
xcopy "%USERPROFILE%\.normcode-canvas" "%USERPROFILE%\backup\normcode-canvas-backup" /E /I
```

**To reset application data (clear cache and settings):**
```bash
# macOS/Linux
rm -rf ~/Library/Application\ Support/NormCode\ Canvas/*# Windows
rd /s /q "%USERPROFILE%\.normcode-canvas"
```

**Warning:** Resetting will delete all your project registry, deployment server configurations, and other user data.

---

## Advanced Usage

### Skipping Steps for Faster Development

```powershell
# Windows - rebuild only Python packaging (no frontend, no deps)
python build_windows.py --skip-frontend --skip-deps

# macOS - rebuild only app bundle (no frontend, no deps)
python build_macos.py --skip-frontend --skip-deps
```

Use this when you've only changed Python backend code.

### Clean Builds

```powershell
# Windows
python build_windows.py --clean

# macOS
python build_macos.py --clean
```

Removes all build artifacts and rebuilds from scratch.

### Debug Mode (Windows only)

```powershell
python build_windows.py --debug
```

Shows console window with detailed logs for troubleshooting.

---

## File Locations Reference

| File/Directory | Purpose |
|----------------|---------|
| `build/build_windows.py` | Windows build script |
| `build/build_macos.py` | macOS build script |
| `build/installer.iss` | Inno Setup installer configuration (Windows) |
| `build/normcode.spec` | PyInstaller spec (Windows) |
| `build/normcode_macos.spec` | PyInstaller spec (macOS, auto-generated) |
| `build/resources/Psylensai_log_raw.png` | Source icon image |
| `canvas_app/frontend/` | Frontend source (React/TypeScript) |
| `canvas_app/backend/` | Backend source (FastAPI/Python) |
| `canvas_app/settings.yaml.example` | Configuration template |

---

## Additional Resources

- **PyInstaller Documentation:** https://pyinstaller.org/en/stable/
- **pywebview Documentation:** https://pywebview.flowrl.com/
- **Inno Setup Documentation:** https://jrsoftware.org/ishelp/
- **macOS Code Signing:** https://developer.apple.com/support/code-signing/
- **macOS Notarization:** https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution

---

## Getting Help

If you encounter issues:

1. Check the Troubleshooting section above
2. Run build with `--clean` flag to start fresh
3. On Windows, use `--debug` flag for detailed logs
4. Verify all prerequisites are installed
5. Check that all required files exist (especially icons)
6. Ensure you're using the correct Python version (3.8+)

For build script bugs or feature requests, please file an issue in the project repository.