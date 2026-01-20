"""
Path utilities for NormCode Canvas.

Provides correct path resolution for both development and frozen (PyInstaller) modes.

Key concepts:
- BUNDLE_DIR: Where read-only bundled data files are located (sys._MEIPASS in frozen mode)
- APP_DIR: The application install directory (where executable is)
- DATA_DIR: User-writable config directory (~/.normcode-canvas/)
"""
import sys
import os
from pathlib import Path

# Detect if running as frozen executable (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)


def get_bundle_dir() -> Path:
    """Get the directory where bundled data files are located.
    
    In frozen mode: sys._MEIPASS (temp extraction dir with bundled data)
    In dev mode: project root (normCode/)
    
    Use this for read-only bundled assets like:
    - frontend/dist/
    - built_in_projects/
    - bundled seed config files
    """
    if IS_FROZEN:
        return Path(sys._MEIPASS)
    # Dev mode: go up from core/path_utils.py to project root
    return Path(__file__).parent.parent.parent.parent


def get_app_dir() -> Path:
    """Get the application install directory.
    
    In frozen mode: directory containing the executable
    In dev mode: project root (normCode/)
    
    Use this for app-level writable data that stays with the install.
    """
    if IS_FROZEN:
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get the user data directory for writable config files.
    
    Always returns ~/.normcode-canvas/ for user-specific data like:
    - llm-settings.json
    - settings.yaml (if user-customized)
    - logs
    - cache
    
    Creates the directory if it doesn't exist.
    """
    data_dir = Path.home() / ".normcode-canvas"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_backend_dir() -> Path:
    """Get the backend directory.
    
    In frozen mode: BUNDLE_DIR/backend
    In dev mode: canvas_app/backend
    """
    if IS_FROZEN:
        return get_bundle_dir() / "backend"
    return Path(__file__).parent.parent


def get_tools_dir() -> Path:
    """Get the tools directory (backend/tools).
    
    Contains bundled tool configs and LLM settings seed files.
    """
    return get_backend_dir() / "tools"


def get_built_in_projects_dir() -> Path:
    """Get the built-in projects directory.
    
    Contains bundled NormCode projects that serve as chat controllers.
    """
    if IS_FROZEN:
        return get_bundle_dir() / "built_in_projects"
    return Path(__file__).parent.parent.parent / "built_in_projects"


def get_infra_dir() -> Path:
    """Get the infra module directory.
    
    Contains the NormCode infrastructure/orchestration code.
    """
    if IS_FROZEN:
        return get_bundle_dir() / "infra"
    return Path(__file__).parent.parent.parent.parent / "infra"


def get_frontend_dist_dir() -> Path:
    """Get the frontend dist directory for static files.
    
    Returns None if not found.
    """
    if IS_FROZEN:
        # Check both possible locations in frozen mode
        for subdir in ["frontend/dist", "frontend", "_internal/frontend/dist"]:
            path = get_bundle_dir() / subdir
            if path.exists() and (path / "index.html").exists():
                return path
        return None
    
    # Dev mode
    path = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if path.exists() and (path / "index.html").exists():
        return path
    return None


# Debug helper
if __name__ == "__main__":
    print(f"IS_FROZEN: {IS_FROZEN}")
    print(f"Bundle Dir: {get_bundle_dir()}")
    print(f"App Dir: {get_app_dir()}")
    print(f"Data Dir: {get_data_dir()}")
    print(f"Backend Dir: {get_backend_dir()}")
    print(f"Tools Dir: {get_tools_dir()}")
    print(f"Built-in Projects Dir: {get_built_in_projects_dir()}")
    print(f"Infra Dir: {get_infra_dir()}")
    print(f"Frontend Dist Dir: {get_frontend_dist_dir()}")
