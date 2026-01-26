"""
First Person Perspective - "I am the user"

The AI acts AS the user. Everything is visible to the user.
"""

from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from ..types import UserViewSnapshot, ActionResult
from ..faculties import Vision, Hands, Mind
from ..event_store import EventStore

if TYPE_CHECKING:
    from services.execution.controller import ExecutionController
    from ..facades.system import ServiceContainer


class FirstPersonPerspective:
    """
    "I am the user" - shared stage.
    
    Everything here affects what the user sees.
    Use for UI interaction and state changes.
    
    Faculties:
    - vision: See UI state (read-only)
    - hands: Manipulate UI (actions)
    - mind: Control and understand (decisions)
    """
    
    def __init__(
        self,
        emit: Callable[[str, Dict], None],
        execution_getter: Optional[Callable[[], Optional["ExecutionController"]]],
        services: "ServiceContainer",
        event_store: EventStore
    ):
        """
        Initialize First Person perspective.
        
        Args:
            emit: WebSocket event emitter
            execution_getter: Callable that returns current ExecutionController
            services: Service container
            event_store: Event store for recording actions
        """
        self._emit = emit
        self._execution_getter = execution_getter
        self._services = services
        self._event_store = event_store
        
        # Create faculties
        self._vision = Vision(emit, execution_getter, services)
        self._hands = Hands(emit, execution_getter, services, event_store)
        self._mind = Mind(emit, execution_getter, services)
    
    @property
    def vision(self) -> Vision:
        """My eyes - what I can see."""
        return self._vision
    
    @property
    def hands(self) -> Hands:
        """My hands - what I can manipulate."""
        return self._hands
    
    @property
    def mind(self) -> Mind:
        """My mind - understanding and control."""
        return self._mind
    
    # =========================================================================
    # Shortcuts (convenience methods for common actions)
    # =========================================================================
    
    def look(self) -> UserViewSnapshot:
        """Look at everything. Shortcut for vision.get_full_snapshot()."""
        return self._vision.get_full_snapshot()
    
    def click(self, target: str) -> ActionResult:
        """Click a node. Shortcut for hands.click_node()."""
        return self._hands.click_node(target)
    
    def say(self, message: str) -> ActionResult:
        """Send a chat message. Shortcut for hands.say()."""
        return self._hands.say(message)

