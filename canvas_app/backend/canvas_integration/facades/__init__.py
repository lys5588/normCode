"""
Facades for Second Person perspective.

These provide a cleaner API while delegating to existing tools.
"""

from .files import FilesFacade
from .code import CodeFacade
from .parser import ParserFacade
from .blackboard import BlackboardFacade
from .graph import GraphFacade
from .database import DatabaseFacade
from .llm import LLMFacade
from .prompt import PromptFacade
from .paradigm import ParadigmFacade
from .model import ModelFacade
from .compose import ComposeFacade
from .perceive import PerceiveFacade
from .format import FormatFacade
from .input import InputFacade
from .system import SystemFacade
from .history import HistoryFacade

__all__ = [
    "FilesFacade",
    "CodeFacade",
    "ParserFacade",
    "BlackboardFacade",
    "GraphFacade",
    "DatabaseFacade",
    "LLMFacade",
    "PromptFacade",
    "ParadigmFacade",
    "ModelFacade",
    "ComposeFacade",
    "PerceiveFacade",
    "FormatFacade",
    "InputFacade",
    "SystemFacade",
    "HistoryFacade",
]

