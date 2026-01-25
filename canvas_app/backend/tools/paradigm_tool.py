"""
Canvas Paradigm Tool - Loads paradigms from project-local directories.

This tool allows projects to define their own paradigms locally instead of
using the default infra/_agent/_models/_paradigms location.

Canvas version adds WebSocket event emission for monitoring paradigm operations.
"""

import os
import json
import logging
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class CanvasParadigmTool:
    """
    Canvas paradigm tool that loads paradigms from a specified directory
    instead of the default infra/_agent/_models/_paradigms location.
    
    This allows projects to define their own paradigms locally.
    Canvas version adds WebSocket event emission for monitoring.
    """
    
    def __init__(
        self, 
        paradigm_dir: Path,
        emit_callback: Optional[Callable[[str, Dict], None]] = None
    ):
        self.paradigm_dir = Path(paradigm_dir)
        self._emit_callback = emit_callback
        self._Paradigm = None
        
        # Try to load the Paradigm class from the local paradigm directory
        local_paradigm_py = self.paradigm_dir / "_paradigm.py"
        if local_paradigm_py.exists():
            self._init_from_local_paradigm_py(local_paradigm_py)
        else:
            self._init_from_infra_paradigm()
    
    def set_emit_callback(self, callback: Callable[[str, Dict], None]):
        """Set the callback for emitting WebSocket events."""
        self._emit_callback = callback
    
    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit a WebSocket event if callback is set."""
        if self._emit_callback:
            try:
                self._emit_callback(event_type, data)
            except Exception as e:
                logger.error(f"Failed to emit event {event_type}: {e}")
    
    def _init_from_local_paradigm_py(self, local_paradigm_py: Path):
        """Initialize using a local _paradigm.py file."""
        self._emit("paradigm:init_started", {
            "source": "local",
            "path": str(local_paradigm_py)
        })
        
        # Load from local _paradigm.py (allows full customization)
        spec = importlib.util.spec_from_file_location("_paradigm", local_paradigm_py)
        paradigm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(paradigm_module)
        LocalParadigmClass = paradigm_module.Paradigm
        # Override PARADIGMS_DIR in the module to point to our custom dir
        paradigm_module.PARADIGMS_DIR = self.paradigm_dir
        logger.info(f"Loaded custom Paradigm class from {local_paradigm_py}")
        
        # Wrap with fallback to default paradigms
        try:
            from infra._agent._models._paradigms._paradigm import Paradigm as DefaultParadigm, PARADIGMS_DIR
            custom_dir = self.paradigm_dir
            emit = self._emit
            
            class WrappedLocalParadigm:
                """Wrapper that tries local paradigm first, then falls back to default."""
                @classmethod
                def load(cls, paradigm_name: str):
                    # Try local paradigm directory first
                    paradigm_file = custom_dir / f"{paradigm_name}.json"
                    if paradigm_file.exists():
                        logger.debug(f"Loading paradigm '{paradigm_name}' from custom directory")
                        emit("paradigm:load_started", {
                            "name": paradigm_name,
                            "source": "custom",
                            "path": str(paradigm_file)
                        })
                        result = LocalParadigmClass.load(paradigm_name)
                        emit("paradigm:load_completed", {
                            "name": paradigm_name,
                            "source": "custom"
                        })
                        return result
                    
                    # Fall back to default paradigms
                    default_paradigm_file = PARADIGMS_DIR / f"{paradigm_name}.json"
                    if default_paradigm_file.exists():
                        logger.info(f"Paradigm '{paradigm_name}' not in custom dir, loading from default")
                        emit("paradigm:load_started", {
                            "name": paradigm_name,
                            "source": "default",
                            "path": str(default_paradigm_file)
                        })
                        result = DefaultParadigm.load(paradigm_name)
                        emit("paradigm:load_completed", {
                            "name": paradigm_name,
                            "source": "default"
                        })
                        return result
                    
                    # Not found in either location
                    emit("paradigm:load_failed", {
                        "name": paradigm_name,
                        "error": f"Not found in custom ({custom_dir}) or default ({PARADIGMS_DIR})"
                    })
                    raise FileNotFoundError(
                        f"Paradigm '{paradigm_name}' not found in custom ({custom_dir}) or default ({PARADIGMS_DIR})"
                    )
            
            self._Paradigm = WrappedLocalParadigm
            logger.info(f"Wrapped local Paradigm with fallback to default paradigms")
            self._emit("paradigm:init_completed", {"source": "local_with_fallback"})
        except ImportError as e:
            # If infra not available, just use local paradigm without fallback
            logger.warning(f"Could not import default paradigms for fallback: {e}")
            self._Paradigm = LocalParadigmClass
            self._emit("paradigm:init_completed", {"source": "local_only"})
    
    def _init_from_infra_paradigm(self):
        """Initialize using infra's Paradigm class with custom directory fallback."""
        paradigm_dir = self.paradigm_dir
        emit = self._emit
        
        self._emit("paradigm:init_started", {
            "source": "infra",
            "custom_dir": str(paradigm_dir)
        })
        
        try:
            from infra._agent._models._paradigms._paradigm import (
                Paradigm, PARADIGMS_DIR, 
                _paradigm_object_hook, _build_env_spec, _build_sequence_spec
            )
            
            # Create a wrapper that loads from custom directory first, then falls back to default
            class LocalParadigm:
                """Wrapper to load paradigms from custom directory, falling back to default."""
                @classmethod
                def load(cls, paradigm_name: str):
                    # Try custom directory first
                    paradigm_file = paradigm_dir / f"{paradigm_name}.json"
                    if paradigm_file.exists():
                        emit("paradigm:load_started", {
                            "name": paradigm_name,
                            "source": "custom",
                            "path": str(paradigm_file)
                        })
                        with open(paradigm_file, 'r', encoding='utf-8') as f:
                            # Use the proper object hook to handle MetaValue etc
                            raw_spec = json.load(f, object_hook=_paradigm_object_hook)
                        
                        # Properly reconstruct spec objects (not raw dicts!)
                        env_spec_data = raw_spec.get('env_spec', {})
                        sequence_spec_data = raw_spec.get('sequence_spec', {})
                        metadata_data = raw_spec.get('metadata', {})
                        
                        env_spec = _build_env_spec(env_spec_data)
                        sequence_spec = _build_sequence_spec(sequence_spec_data, env_spec)
                        
                        # Create Paradigm instance properly
                        paradigm = Paradigm(env_spec, sequence_spec, metadata_data)
                        logger.debug(f"Loaded paradigm '{paradigm_name}' from custom directory")
                        emit("paradigm:load_completed", {
                            "name": paradigm_name,
                            "source": "custom"
                        })
                        return paradigm
                    
                    # Fall back to default paradigms directory
                    default_paradigm_file = PARADIGMS_DIR / f"{paradigm_name}.json"
                    if default_paradigm_file.exists():
                        logger.debug(f"Paradigm '{paradigm_name}' not in custom dir, loading from default")
                        emit("paradigm:load_started", {
                            "name": paradigm_name,
                            "source": "default",
                            "path": str(default_paradigm_file)
                        })
                        result = Paradigm.load(paradigm_name)
                        emit("paradigm:load_completed", {
                            "name": paradigm_name,
                            "source": "default"
                        })
                        return result
                    
                    # Not found in either location
                    emit("paradigm:load_failed", {
                        "name": paradigm_name,
                        "error": f"Not found in custom ({paradigm_dir}) or default ({PARADIGMS_DIR})"
                    })
                    raise FileNotFoundError(
                        f"Paradigm '{paradigm_name}' not found in custom ({paradigm_dir}) or default ({PARADIGMS_DIR})"
                    )
            
            self._Paradigm = LocalParadigm
            logger.info(f"Using infra Paradigm with custom directory fallback: {paradigm_dir}")
            self._emit("paradigm:init_completed", {"source": "infra_with_fallback"})
        except ImportError as e:
            logger.error(f"Failed to import Paradigm from infra: {e}")
            self._emit("paradigm:init_failed", {"error": str(e)})
            raise
    
    def load(self, paradigm_name: str) -> Any:
        """Load a paradigm by name."""
        return self._Paradigm.load(paradigm_name)
    
    def list_paradigms(self) -> list:
        """List all available paradigm names in the custom directory."""
        paradigms = []
        for filename in os.listdir(self.paradigm_dir):
            if filename.endswith(".json"):
                paradigms.append(filename[:-5])  # Remove .json extension
        return paradigms
    
    def list_manifest(self) -> str:
        """List all available paradigms in the custom directory with descriptions."""
        manifest = []
        for filename in os.listdir(self.paradigm_dir):
            if filename.endswith(".json"):
                name = filename[:-5]  # Remove .json extension
                try:
                    with open(self.paradigm_dir / filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        metadata = data.get('metadata', {})
                        desc = metadata.get('description', 'No description provided.')
                        manifest.append(
                            f"<paradigm name=\"{name}\">\n"
                            f"    <description>{desc}</description>\n"
                            f"</paradigm>"
                        )
                except Exception as e:
                    manifest.append(f"<error paradigm=\"{name}\">{str(e)}</error>")
        return "\n\n".join(manifest)


def create_canvas_paradigm_tool(
    paradigm_dir: Optional[str], 
    base_dir: str,
    emit_callback: Optional[Callable[[str, Dict], None]] = None
) -> Optional[CanvasParadigmTool]:
    """
    Create a CanvasParadigmTool if paradigm_dir is specified and exists.
    
    Args:
        paradigm_dir: Relative or absolute path to paradigm directory
        base_dir: Base directory for resolving relative paths
        emit_callback: Optional callback for emitting WebSocket events
        
    Returns:
        CanvasParadigmTool instance, or None if not applicable
    """
    if not paradigm_dir:
        return None
    
    paradigm_path = Path(paradigm_dir)
    # If relative path, resolve relative to base_dir
    if not paradigm_path.is_absolute():
        paradigm_path = Path(base_dir) / paradigm_dir
    
    if paradigm_path.exists() and paradigm_path.is_dir():
        logger.info(f"Using custom paradigm directory: {paradigm_path}")
        return CanvasParadigmTool(paradigm_path, emit_callback)
    else:
        logger.warning(f"Paradigm directory not found: {paradigm_path}")
        return None


# Backward compatibility aliases
CustomParadigmTool = CanvasParadigmTool
create_paradigm_tool = create_canvas_paradigm_tool

