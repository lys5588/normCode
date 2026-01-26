# -*- mode: python ; coding: utf-8 -*-
"""
NormCode Canvas - macOS PyInstaller Spec File
==============================================

Auto-generated spec file for macOS build.
Version: 0.1.0-alpha
Display Name: NormCode Canvas
"""

import sys
import datetime
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Paths
SPEC_DIR = Path(SPECPATH)
PROJECT_ROOT = SPEC_DIR.parent
CANVAS_APP = PROJECT_ROOT / "canvas_app"
LAUNCHER_DIR = SPEC_DIR / "launcher"
RESOURCES_DIR = SPEC_DIR / "resources"

block_cipher = None

# Hidden imports (same as Windows)
hidden_imports = [
    # FastAPI and web framework
    'uvicorn', 'uvicorn.config', 'uvicorn.main', 'uvicorn.logging',
    'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.loops.asyncio',
    'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off',
    'uvicorn.server', 'uvicorn.supervisors',
    
    # FastAPI
    'fastapi', 'fastapi.applications', 'fastapi.routing',
    'fastapi.responses', 'fastapi.staticfiles', 'fastapi.middleware',
    'fastapi.middleware.cors',
    
    # Starlette
    'starlette', 'starlette.responses', 'starlette.staticfiles',
    'starlette.routing', 'starlette.middleware', 'starlette.middleware.cors',
    'starlette.websockets',
    
    # Pydantic
    'pydantic', 'pydantic.main', 'pydantic_settings', 'pydantic_core',
    
    # WebSocket
    'websockets', 'websockets.legacy', 'websockets.legacy.server', 'websockets.server',
    
    # HTTP
    'httptools', 'h11',
    
    # Multipart
    'multipart', 'python_multipart',
    
    # Async
    'anyio', 'anyio._core', 'anyio._backends', 'anyio._backends._asyncio', 'sniffio',
    
    # Other
    'click', 'email_validator', 'encodings', 'encodings.idna', 'yaml',
    'openai', 'httpx', 'requests', 'requests.exceptions',
]

# Collect submodules
try:
    hidden_imports += collect_submodules('uvicorn')
    hidden_imports += collect_submodules('fastapi')
    hidden_imports += collect_submodules('starlette')
except Exception:
    pass

try:
    sys.path.insert(0, str(CANVAS_APP / "backend"))
    hidden_imports += collect_submodules('routers')
    hidden_imports += collect_submodules('services')
    hidden_imports += collect_submodules('schemas')
    hidden_imports += collect_submodules('core')
except Exception:
    pass

try:
    sys.path.insert(0, str(PROJECT_ROOT))
    hidden_imports += collect_submodules('infra')
except Exception:
    pass

# Data files
datas = [
    (str(CANVAS_APP / "frontend" / "dist"), "frontend/dist"),
    (str(CANVAS_APP / "backend"), "backend"),
    (str(PROJECT_ROOT / "infra"), "infra"),
    (str(CANVAS_APP / "settings.yaml.example"), "."),
]

# Add icon resources
if RESOURCES_DIR.exists():
    datas.append((str(RESOURCES_DIR), "resources"))

a = Analysis(
    [str(LAUNCHER_DIR / "desktop_launcher.py")],
    pathex=[
        str(PROJECT_ROOT),
        str(CANVAS_APP / "backend"),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
        'torch', 'tensorflow', 'keras', 'sklearn',
        'jupyter', 'notebook', 'IPython', 'pytest', 'sphinx', '_pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NormCodeCanvas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window on macOS
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NormCodeCanvas',
)

# Create macOS .app bundle
app = BUNDLE(
    coll,
    name='NormCodeCanvas.app',
    icon='/Users/lys/Code/project/normCode/build/resources/icon.icns',
    bundle_identifier='com.normcode.canvas',
    info_plist={
        'CFBundleName': 'NormCode Canvas',
        'CFBundleDisplayName': 'NormCode Canvas',
        'CFBundleVersion': '0.1.0-alpha',
        'CFBundleShortVersionString': '0.1.0-alpha',
        'CFBundleIdentifier': 'com.normcode.canvas',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'LSMinimumSystemVersion': '10.15.0',
        'NSPrincipalClass': 'NSApplication',
        'NSHumanReadableCopyright': '© 2026 NormCode. All rights reserved.',
    },
)
