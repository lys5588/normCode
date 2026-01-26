"""
Perspectives for Canvas Integration.

The three perspectives represent different modes of interaction:
- First Person ("I"): Act as user on shared stage
- Second Person ("You"): Private backend/tool access
- Third Person ("It"): Observe system activity
"""

from .first_person import FirstPersonPerspective
from .second_person import SecondPersonPerspective
from .third_person import ThirdPersonPerspective

__all__ = [
    "FirstPersonPerspective",
    "SecondPersonPerspective", 
    "ThirdPersonPerspective",
]

