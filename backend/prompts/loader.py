"""
Prompt Loader Utility
--------------------
Loads externalized prompt templates from backend/prompts/*.md files at runtime.
Supports variable substitution via Python's str.format(**kwargs).
"""

import os
from functools import lru_cache

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


@lru_cache(maxsize=32)
def _read_prompt_file(name: str) -> str:
    """Reads and caches a prompt file from the prompts directory."""
    filepath = os.path.join(_PROMPTS_DIR, f"{name}.md")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_prompt(name: str, **kwargs) -> str:
    """
    Loads a prompt template by name and substitutes variables.
    
    Args:
        name: The prompt file name (without .md extension).
              E.g., 'market_analysis_system' loads prompts/market_analysis_system.md
        **kwargs: Variables to substitute using str.format().
                  Use {{double_braces}} in the .md file for literal braces (e.g., JSON examples).
    
    Returns:
        The formatted prompt string.
    """
    template = _read_prompt_file(name)
    if kwargs:
        return template.format(**kwargs)
    return template
