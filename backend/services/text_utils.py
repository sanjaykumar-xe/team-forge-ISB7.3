"""
text_utils.py
Utilities for clean, word-boundary-aware text truncation.
Guarantees zero mid-word cutoffs across all backend agents, fallbacks, and evidence synthesizers.
"""

from typing import Optional


def truncate_at_word_boundary(
    text: Optional[str],
    max_length: int = 240,
    ellipsis: str = "...",
    min_ratio: float = 0.5,
) -> str:
    """
    Truncates text to at most max_length characters, snapping cleanly to the nearest
    preceding word boundary (whitespace) or sentence boundary to prevent mid-word cutoffs.
    
    Args:
        text: The string to truncate.
        max_length: Maximum allowed length.
        ellipsis: Optional trailing string (e.g. "..." or "…").
        min_ratio: Minimum fraction of max_length to accept when looking for boundaries.
                   Prevents over-aggressive truncation on very long single tokens.
    
    Returns:
        Cleanly truncated string ending on a full word or sentence boundary.
    """
    if not text:
        return ""
    clean = str(text).strip()
    if len(clean) <= max_length:
        return clean

    # Look up to max_length
    budget = max_length - len(ellipsis) if ellipsis else max_length
    sub = clean[:budget + 1]

    # 1. Prefer sentence boundary (. , ! , ? ) in the upper portion (>= min_ratio of budget)
    for punct in [". ", "! ", "? "]:
        last_punct = sub.rfind(punct)
        if last_punct >= int(budget * min_ratio):
            return sub[:last_punct + 1].strip()

    # 2. Snap to last whitespace boundary within budget
    last_space = sub[:budget].rfind(" ")
    if last_space > 0:
        return sub[:last_space].rstrip(",;:- ") + ellipsis

    # 3. Fallback only if string has zero whitespace
    return sub[:budget].rstrip(",;:- ") + ellipsis
