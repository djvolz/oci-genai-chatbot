"""
OCI GenAI Chatbot - Sample application demonstrating LiteLLM integration with Oracle Cloud Infrastructure GenAI.
"""

__version__ = "0.1.0"

from .litellm_client import OCIGenAIChatBot
from .cli import main as cli_main
from .codex_cli import codex as codex_main

__all__ = ["OCIGenAIChatBot", "cli_main", "codex_main"]