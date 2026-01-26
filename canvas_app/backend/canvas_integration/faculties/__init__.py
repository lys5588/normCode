"""
Faculties for First Person perspective.

These implement the "eyes, hands, and mind" of the AI user.
"""

from .vision import Vision, submit_vision_input, buffer_vision_message
from .hands import Hands
from .mind import Mind

__all__ = [
    "Vision", 
    "Hands", 
    "Mind",
    # Vision input handling (for API integration)
    "submit_vision_input",
    "buffer_vision_message",
]

