"""
Canvas Model Runner Tool - Runtime environment for paradigm execution.

This tool provides the runtime environment for executing paradigms:
- ModelEnv: Binds tool affordances to executables
- ModelSequenceRunner: Executes step sequences

Canvas version adds WebSocket event emission for monitoring execution.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Callable
import logging

logger = logging.getLogger(__name__)

# Import spec dataclasses from infra
try:
    from infra._states import (
        AffordanceSpecLite,
        ToolSpecLite,
        ModelEnvSpecLite,
        ModelStepSpecLite,
        ModelSequenceSpecLite,
        MetaValue,
        AffordanceValue,
    )
    INFRA_AVAILABLE = True
except ImportError:
    logger.warning("Could not import infra._states - model runner will have limited functionality")
    INFRA_AVAILABLE = False
    # Define placeholder types
    AffordanceSpecLite = Any
    ToolSpecLite = Any
    ModelEnvSpecLite = Any
    ModelStepSpecLite = Any
    ModelSequenceSpecLite = Any
    MetaValue = Any
    AffordanceValue = Any


class CanvasModelEnv:
    """
    Canvas runtime environment materialized from a spec-like object.
    
    Canvas version adds WebSocket event emission for monitoring affordance execution.

    - Binds tool affordances (e.g., "prompt.substitute") to executable callables.
    - Provides `execute(qualified_affordance, params)` to invoke affordances.
    - Provides `get_affordance(qualified_affordance)` to obtain a callable handle.
    
    Expected `spec` shape at minimum (via ModelEnvSpecLite):
      model?: ToolSpecLite(tool_name, affordances)
      prompt?: ToolSpecLite
      tools:  list[ToolSpecLite]
    """

    def __init__(
        self, 
        states: Any, 
        spec: ModelEnvSpecLite,
        emit_callback: Optional[Callable[[str, Dict], None]] = None
    ):
        logger.debug(f"Initializing CanvasModelEnv with spec: {type(spec).__name__}")
        self._states = states
        self._spec = spec
        self._emit_callback = emit_callback
        self._registry: Dict[str, Tuple[str, str, Dict[str, Any], str]] = {}
        self._build_registry()
        logger.debug(f"CanvasModelEnv initialized with {len(self._registry)} affordances registered")
        
        self._emit("model_env:initialized", {
            "affordance_count": len(self._registry),
            "affordances": list(self._registry.keys())
        })

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

    def execute(self, qualified_affordance: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute an affordance by its qualified name, e.g. "prompt.substitute"."""
        logger.debug(f"Executing affordance: {qualified_affordance} with params: {params}")
        
        self._emit("affordance:execute_started", {
            "affordance": qualified_affordance,
            "params": self._safe_serialize(params)
        })
        
        try:
            handle = self.get_affordance(qualified_affordance)
            result = handle(params or {})
            
            self._emit("affordance:execute_completed", {
                "affordance": qualified_affordance,
                "result_type": type(result).__name__
            })
            
            logger.debug(f"Affordance {qualified_affordance} executed, result type: {type(result).__name__}")
            return result
        except Exception as e:
            self._emit("affordance:execute_failed", {
                "affordance": qualified_affordance,
                "error": str(e)
            })
            raise

    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize an object for event emission."""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {k: self._safe_serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._safe_serialize(v) for v in obj]
        return f"<{type(obj).__name__}>"

    def get_affordance(self, qualified_affordance: str) -> Callable[[Dict[str, Any]], Any]:
        """Return a callable that executes the bound affordance."""
        logger.debug(f"Getting affordance: {qualified_affordance}")
        try:
            tool_name, call_code, static_params, output_var = self._resolve(qualified_affordance)
            logger.debug(f"Resolved affordance {qualified_affordance} -> tool: {tool_name}, output_var: {output_var}")
        except KeyError as exc:
            logger.error(f"Affordance not found: {qualified_affordance}")
            raise KeyError(f"Affordance not found: {qualified_affordance}") from exc

        emit = self._emit
        
        def _runner(runtime_params: Dict[str, Any]) -> Any:
            logger.debug(f"Running affordance {qualified_affordance} with runtime_params: {runtime_params}")
            merged_params = {**static_params, **(runtime_params or {})}
            logger.debug(f"Merged params for {qualified_affordance}: {merged_params}")
            
            local_vars: Dict[str, Any] = {
                "states": self._states,
                "tool": self._get_tool_provider(tool_name),
                "params": merged_params,
                "result": None,
            }
            logger.debug(f"Executing call_code for {qualified_affordance}: {call_code[:100]}...")
            exec(call_code, {}, local_vars)
            result = local_vars.get(output_var, local_vars.get("result"))
            logger.debug(f"Affordance {qualified_affordance} completed, result: {type(result).__name__}")
            return result

        return _runner

    def list_affordances(self) -> Dict[str, Dict[str, Any]]:
        """List all registered affordances."""
        logger.debug("Listing all registered affordances")
        out: Dict[str, Dict[str, Any]] = {}
        for key, (tool_name, _, static_params, output_var) in self._registry.items():
            out[key] = {
                "tool": tool_name,
                "static_params": static_params,
                "output": output_var,
            }
        logger.debug(f"Found {len(out)} affordances: {list(out.keys())}")
        return out

    def _build_registry(self) -> None:
        """Build the affordance registry from the spec."""
        logger.debug("Building affordance registry")
        tools: Dict[str, Any] = {}
        model_spec = getattr(self._spec, "model", None)
        if model_spec is not None:
            logger.debug(f"Adding model spec: {model_spec.tool_name}")
            tools[model_spec.tool_name] = model_spec
        prompt_spec = getattr(self._spec, "prompt", None)
        if prompt_spec is not None:
            logger.debug(f"Adding prompt spec: {prompt_spec.tool_name}")
            tools[prompt_spec.tool_name] = prompt_spec
        for tool_spec in (getattr(self._spec, "tools", []) or []):
            if tool_spec is not None:
                logger.debug(f"Adding tool spec: {tool_spec.tool_name}")
                tools[tool_spec.tool_name] = tool_spec

        for tool_name, tool_spec in tools.items():
            logger.debug(f"Processing tool: {tool_name}")
            for aff in getattr(tool_spec, "affordances", []) or []:
                qualified = f"{tool_name}.{aff.affordance_name}"
                output_var = getattr(aff, "output", None) or "result"
                static_params = dict(getattr(aff, "params", None) or {})
                call_code = getattr(aff, "call_code")
                self._registry[qualified] = (tool_name, call_code, static_params, output_var)
                logger.debug(f"Registered affordance: {qualified} -> {tool_name}.{aff.affordance_name}")

    def _resolve(self, qualified_affordance: str) -> Tuple[str, str, Dict[str, Any], str]:
        """Resolve an affordance from the registry."""
        logger.debug(f"Resolving affordance: {qualified_affordance}")
        tool_name, call_code, static_params, output_var = self._registry[qualified_affordance]
        return tool_name, call_code, static_params, output_var

    def _get_tool_provider(self, tool_name: str) -> Any:
        """Get the tool provider for a given tool name."""
        logger.debug(f"Getting tool provider for: {tool_name}")
        body = getattr(self._states, "body", None)
        if body is not None and hasattr(body, tool_name):
            logger.debug(f"Found tool provider at states.body.{tool_name}")
            return getattr(body, tool_name)
        if hasattr(self._states, tool_name):
            logger.debug(f"Found tool provider at states.{tool_name}")
            return getattr(self._states, tool_name)
        logger.error(f"Tool provider not found for '{tool_name}'")
        raise AttributeError(f"Tool provider not found for '{tool_name}'. Expected at states.body.{tool_name} or states.{tool_name}.")


class CanvasModelSequenceRunner:
    """
    Canvas version of ModelSequenceRunner - executes paradigm step sequences.
    
    Adds WebSocket event emission for monitoring step execution.

    - Resolves MetaValue to meta keys or states dotted paths
    - Resolves AffordanceValue to a callable affordance handle
    - Merges params and executes in step order, storing results by result_key
    """

    def __init__(
        self, 
        states: Any, 
        sequence_spec: ModelSequenceSpecLite,
        emit_callback: Optional[Callable[[str, Dict], None]] = None
    ) -> None:
        logger.debug(f"Initializing CanvasModelSequenceRunner with {len(sequence_spec.steps)} steps")
        self.states = states
        self.sequence_spec = sequence_spec
        self._emit_callback = emit_callback
        self.env = CanvasModelEnv(states, sequence_spec.env, emit_callback)
        self.meta: Dict[str, Any] = {}
        
        self._emit("sequence:initialized", {
            "step_count": len(sequence_spec.steps)
        })
        logger.debug("CanvasModelSequenceRunner initialized")

    def set_emit_callback(self, callback: Callable[[str, Dict], None]):
        """Set the callback for emitting WebSocket events."""
        self._emit_callback = callback
        self.env.set_emit_callback(callback)

    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit a WebSocket event if callback is set."""
        if self._emit_callback:
            try:
                self._emit_callback(event_type, data)
            except Exception as e:
                logger.error(f"Failed to emit event {event_type}: {e}")

    def _resolve_value(self, value: Any) -> Any:
        """Resolve a value that may contain MetaValue or AffordanceValue."""
        logger.debug(f"Resolving value: {type(value).__name__} = {value}")
        
        if INFRA_AVAILABLE:
            if isinstance(value, MetaValue):
                key = value.key
                logger.debug(f"Resolving MetaValue with key: {key}")
                if key.startswith("states."):
                    path = key.split(".")[1:]
                    obj: Any = self.states
                    for part in path:
                        obj = getattr(obj, part)
                    logger.debug(f"Resolved MetaValue from states path: {key} -> {type(obj).__name__}")
                    return obj
                result = self.meta.get(key)
                logger.debug(f"Resolved MetaValue from meta: {key} -> {type(result).__name__}")
                return result
            if isinstance(value, AffordanceValue):
                logger.debug(f"Resolving AffordanceValue: {value.qualified_affordance}")
                return self.env.get_affordance(value.qualified_affordance)
        
        if isinstance(value, dict):
            logger.debug(f"Resolving dict with {len(value)} items")
            return {k: self._resolve_value(v) for k, v in value.items()}
        if isinstance(value, list):
            logger.debug(f"Resolving list with {len(value)} items")
            return [self._resolve_value(v) for v in value]
        logger.debug(f"Value is primitive type: {type(value).__name__}")
        return value

    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameters that may contain MetaValue or AffordanceValue."""
        logger.debug(f"Resolving params: {params}")
        resolved = self._resolve_value(params)
        logger.debug(f"Resolved params: {resolved}")
        return resolved

    def run(self) -> Dict[str, Any]:
        """Execute the sequence and return the meta dictionary with results."""
        logger.debug(f"Starting sequence execution with {len(self.sequence_spec.steps)} steps")
        
        self._emit("sequence:run_started", {
            "step_count": len(self.sequence_spec.steps)
        })
        
        try:
            for step in sorted(self.sequence_spec.steps, key=lambda s: s.step_index):
                self._emit("sequence:step_started", {
                    "step_index": step.step_index,
                    "affordance": step.affordance,
                    "result_key": step.result_key
                })
                
                logger.debug(f"Executing step {step.step_index}: {step.affordance}")
                resolved_params = self._resolve_params(step.params)
                logger.debug(f"Step {step.step_index} resolved params: {resolved_params}")
                
                result = self.env.execute(step.affordance, resolved_params)
                logger.debug(f"Step {step.step_index} result type: {type(result).__name__}")
                
                if step.result_key:
                    logger.debug(f"Storing step {step.step_index} result in meta with key: {step.result_key}")
                    self.meta[step.result_key] = result
                
                self._emit("sequence:step_completed", {
                    "step_index": step.step_index,
                    "affordance": step.affordance,
                    "result_key": step.result_key,
                    "result_type": type(result).__name__
                })
            
            self._emit("sequence:run_completed", {
                "step_count": len(self.sequence_spec.steps),
                "meta_keys": list(self.meta.keys())
            })
            
            logger.debug(f"Sequence execution completed. Meta contains {len(self.meta)} items: {list(self.meta.keys())}")
            return self.meta
            
        except Exception as e:
            self._emit("sequence:run_failed", {
                "error": str(e)
            })
            raise


class CanvasModelRunnerTool:
    """
    Canvas Model Runner Tool - provides model execution capabilities.
    
    This tool wraps CanvasModelEnv and CanvasModelSequenceRunner to provide
    a unified interface for paradigm execution with WebSocket monitoring.
    """
    
    def __init__(self, emit_callback: Optional[Callable[[str, Dict], None]] = None):
        self._emit_callback = emit_callback
    
    def set_emit_callback(self, callback: Callable[[str, Dict], None]):
        """Set the callback for emitting WebSocket events."""
        self._emit_callback = callback
    
    def create_env(self, states: Any, spec: ModelEnvSpecLite) -> CanvasModelEnv:
        """Create a new CanvasModelEnv for executing affordances."""
        return CanvasModelEnv(states, spec, self._emit_callback)
    
    def create_sequence_runner(
        self, 
        states: Any, 
        sequence_spec: ModelSequenceSpecLite
    ) -> CanvasModelSequenceRunner:
        """Create a new CanvasModelSequenceRunner for executing step sequences."""
        return CanvasModelSequenceRunner(states, sequence_spec, self._emit_callback)
    
    def run_sequence(
        self, 
        states: Any, 
        sequence_spec: ModelSequenceSpecLite
    ) -> Dict[str, Any]:
        """Execute a sequence and return the results."""
        runner = self.create_sequence_runner(states, sequence_spec)
        return runner.run()


# Backward compatibility aliases
ModelEnv = CanvasModelEnv
ModelSequenceRunner = CanvasModelSequenceRunner

__all__ = [
    "CanvasModelEnv", 
    "CanvasModelSequenceRunner", 
    "CanvasModelRunnerTool",
    "ModelEnv",
    "ModelSequenceRunner",
    "INFRA_AVAILABLE"
]

