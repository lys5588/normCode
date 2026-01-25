# Frontend Updates for Canvas Integration Tool

This document describes the integration between the backend `CanvasIntegrationTool` (First Person perspective) and the frontend event handling.

## ✅ IMPLEMENTATION STATUS: COMPLETE

All phases have been implemented as of 2026-01-25.

## Architecture

### Backend (hands.py)
The `Hands` faculty emits commands in the `canvas:command` format expected by the frontend:
```python
self._emit_canvas_command("select_node", {"node_id": node_id})
# Emits: {"type": "canvas:command", "data": {"type": "select_node", "params": {"node_id": ...}}}
```

Supported canvas commands:
- **Selection**: `select_node`, `select_nodes`, `deselect_all`
- **Structure**: `collapse_node`, `expand_node`, `toggle_collapse`, `collapse_all`, `expand_all`, `collapse_to_level`
- **Highlight**: `highlight_branch`, `clear_highlight`
- **View**: `zoom_in`, `zoom_out`, `zoom_to`, `fit_view`, `pan`, `center_on_node`
- **Interaction**: `double_click_node`, `right_click_node`, `hover_node`, `drag_node`

Other events use direct event types:
- `panel:open`, `panel:close`, `panel:toggle`, `panel:focus`
- `chat:type`, `chat:clear_input`, `chat:send`, `chat:message`, `chat:respond`, `chat:select_option`
- `execution:toggle_breakpoint`, `execution:add_breakpoint`, etc.

### Frontend (updated)
The frontend handles all event types:
- **useWebSocket.ts**: Handles `canvas:command`, `panel:*`, `chat:*` events
- **GraphCanvas.tsx**: Processes canvas commands via `canvasCommandStore`
- **panelStore.ts**: NEW - Manages panel visibility state for WebSocket access
- **agentStore.ts**: Updated `CanvasIntegrationConfig` with perspectives format

---

## ✅ Resolved: Event Alignment

### Backend-Frontend Event Alignment (IMPLEMENTED)

| Command Type | Backend Method | Frontend Handler | Status |
|-------------|----------------|------------------|--------|
| `select_node` | `hands.click_node()` | `GraphCanvas.tsx` | ✅ Complete |
| `select_nodes` | `hands.select_nodes()` | `GraphCanvas.tsx` | ✅ Complete |
| `deselect_all` | `hands.deselect_all()` | `GraphCanvas.tsx` | ✅ Complete |
| `collapse_node` | `hands.collapse_node()` | `GraphCanvas.tsx` | ✅ Complete |
| `expand_node` | `hands.expand_node()` | `GraphCanvas.tsx` | ✅ Complete |
| `collapse_all` | `hands.collapse_all()` | `GraphCanvas.tsx` | ✅ Complete |
| `expand_all` | `hands.expand_all()` | `GraphCanvas.tsx` | ✅ Complete |
| `highlight_branch` | `hands.highlight_branch()` | `GraphCanvas.tsx` | ✅ Complete |
| `zoom_in/out` | `hands.zoom_in/out()` | `GraphCanvas.tsx` | ✅ Complete |
| `zoom_to` | `hands.zoom_to()` | `GraphCanvas.tsx` | ✅ Complete |
| `pan` | `hands.pan()` | `GraphCanvas.tsx` | ✅ Complete |
| `fit_view` | `hands.fit_view()` | `GraphCanvas.tsx` | ✅ Complete |
| `center_on_node` | `hands.center_on_node()` | `GraphCanvas.tsx` | ✅ Complete |

### Panel Events (IMPLEMENTED)

| Event | Backend Method | Frontend Handler | Status |
|-------|----------------|------------------|--------|
| `panel:open` | `hands.open_panel()` | `useWebSocket.ts` → `panelStore` | ✅ Complete |
| `panel:close` | `hands.close_panel()` | `useWebSocket.ts` → `panelStore` | ✅ Complete |
| `panel:toggle` | `hands.toggle_panel()` | `useWebSocket.ts` → `panelStore` | ✅ Complete |
| `panel:focus` | `hands.focus_panel()` | `useWebSocket.ts` → `panelStore` | ✅ Complete |

### Chat Action Events (IMPLEMENTED)

| Event | Backend Method | Frontend Handler | Status |
|-------|----------------|------------------|--------|
| `chat:type` | `hands.type_in_chat()` | `useWebSocket.ts` → `chatStore` | ✅ Complete |
| `chat:clear_input` | `hands.clear_chat_input()` | `useWebSocket.ts` → `chatStore` | ✅ Complete |
| `chat:send` | `hands.send_chat_message()` | `useWebSocket.ts` → `chatStore` | ✅ Complete |
| `chat:respond` | `hands.respond_to_prompt()` | `useWebSocket.ts` → `chatStore` | ✅ Complete |
| `chat:select_option` | `hands.select_prompt_option()` | `useWebSocket.ts` → `chatStore` | ✅ Complete |

---

## Implementation Details

### Solution: Backend Adapts to Frontend (Option A - IMPLEMENTED)

The `Hands` faculty now uses `_emit_canvas_command()` for canvas operations:

```python
def _emit_canvas_command(self, command_type: str, params: Dict[str, Any]) -> None:
    # Emit in frontend-expected format
    self._emit("canvas:command", {"type": command_type, "params": params})
    # Record with semantic name for event store (Third Person observation)
    self._event_store.record(f"canvas:{command_type}", params)
```

This provides:
- ✅ Frontend compatibility with existing `canvas:command` dispatch
- ✅ Semantic event names in event store for observation
- ✅ Backward compatible

---

## ✅ Completed File Changes

### Backend Files Modified
1. ✅ `canvas_integration/faculties/hands.py` - Uses `_emit_canvas_command()` for canvas operations
2. ✅ `services/agent/config.py` - Added `CanvasIntegrationToolConfig` dataclass

### Frontend Files Modified
1. ✅ `src/hooks/useWebSocket.ts` - Added panel and chat action handlers
2. ✅ `src/components/graph/GraphCanvas.tsx` - Added all new command handlers
3. ✅ `src/stores/panelStore.ts` - NEW: Panel visibility state management
4. ✅ `src/stores/agentStore.ts` - Updated `CanvasIntegrationConfig` with perspectives

### New Files Created
1. ✅ `src/stores/panelStore.ts` - Panel visibility state for WebSocket access

### Additional UI Enhancements (IMPLEMENTED)
1. ✅ `src/components/panels/ToolConfigCards.tsx` - Updated `CanvasIntegrationSection` with perspectives UI
2. ✅ `src/App.tsx` - Migrated panel state to use `panelStore` for WebSocket control

---

## Testing

To test the integration:

1. **Canvas Commands**: Call `me.hands.click_node("node-1")` from an AI agent
2. **Panel Events**: Call `me.hands.open_panel("agent")` 
3. **Chat Actions**: Call `me.hands.type_in_chat("Hello")` then `me.hands.send_chat_message()`
4. **View Navigation**: Call `me.hands.fit_view()` or `me.hands.zoom_in()`

All commands should be processed by the frontend via WebSocket events.

---

## Agent Settings & Configuration

### ✅ Agent Config (IMPLEMENTED)

The agent configuration now supports the unified `CanvasIntegrationTool` with perspectives.

**Backend (`services/agent/config.py`):**
```python
@dataclass
class CanvasIntegrationToolConfig:
    """Configuration for the unified canvas integration tool."""
    enabled: bool = True
    
    # Perspective toggles
    first_person_enabled: bool = True   # me.* actions (Hands)
    second_person_enabled: bool = True  # you.* queries (Senses)
    third_person_enabled: bool = True   # it.* observation (Memory)
    
    # Optional overrides
    file_system_base_dir: Optional[str] = None
    python_timeout: int = 30
```

**Frontend (`stores/agentStore.ts`):**
```typescript
export interface CanvasIntegrationConfig {
  enabled: boolean;  // Master toggle
  perspectives?: {
    first_person?: boolean;   // me.* - Hands (actions)
    second_person?: boolean;  // you.* - Senses (queries)
    third_person?: boolean;   // it.* - Memory (observation)
  };
}
```

**Legacy Format Conversion:**
The frontend includes `normalizeCanvasIntegrationConfig()` to convert old format:
```typescript
// Old format: { chat: { enabled: true }, canvas: { enabled: true } }
// New format: { enabled: true, perspectives: { first_person: true, ... } }
```

### Future UI Enhancement (Optional)

**AgentPanel.tsx** could display:
```
┌─────────────────────────────────────────┐
│ Canvas Integration                    ☑ │
│ ─────────────────────────────────────── │
│ Perspectives:                           │
│   ☑ First Person (me.*)  - Act as user  │
│   ☑ Second Person (you.*) - Tool access │
│   ☑ Third Person (it.*) - Observation   │
└─────────────────────────────────────────┘
```

---

## Notes

- The `canvas:command` pattern provides a clean command queue
- Event store records all events for Third Person observation
- Keep backward compatibility with existing `execution:*` events

