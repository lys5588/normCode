"""
Faculties for First Person perspective.

These implement the "eyes, hands, and mind" of the AI user.
"""

from .vision import Vision
from .hands import Hands
from .mind import Mind

__all__ = ["Vision", "Hands", "Mind"]

