"""
Test Suite for WebSearchAgent and DataRetrievalAgent
----------------------------------------------------
Tests stop-word stripping, domain blocklists, keyword overlap filtering,
and graceful fallbacks on empty search results.
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent


def test_stop_word_stripping():
    """
    Stop-Word Stripping Test:
    Inputting "I want to create an app that suggests music to me based on my mood"
    extracts keywords related to music and mood, without including "want" or "create".
    """
    agent = WebSearchAgent()
    input_idea = "I want to create an app that suggests music to me based on my mood"
    keywords = agent.extract_core_keywords(idea=input_idea)

    # Convert keywords to set of lowercase tokens for checking
    tokens = set(keywords.lower().split())

    # Assert high-signal terms are retained
    assert "music" in tokens or "mood" in tokens

    # Assert conversational stop words and starter phrases are excluded
    assert "want" not in tokens
    assert "create" not in tokens
    assert "i" not in tokens
    assert "app" not in tokens
    assert "based" not in tokens


def test_dictionary_blocklist():
    """
    Dictionary Blocklist Test:
    Mock search outputs containing dictionary.cambridge.org and merriam-webster.com
    and verify that DataRetrievalAgent completely strips them.
    """
    retrieval_agent = DataRetrievalAgent()

    mock_batches = [
        {
            "category": "Competitors",
            "query": "music mood software competitors alternatives startup",
            "response": {
                "results": [
                    {
                        "title": "WANT | English meaning - Cambridge Dictionary",
                        "url": "https://dictionary.cambridge.org/dictionary/english/want",
                        "content": "To wish for a particular thing or plan of action. Want definition.",
                        "score": 0.95,
                    },
                    {
                        "title": "Mood Definition & Meaning - Merriam-Webster",
                        "url": "https://www.merriam-webster.com/dictionary/mood",
                        "content": "The meaning of MOOD is a conscious state of mind or emotion.",
                        "score": 0.90,
                    },
                    {
                        "title": "MoodMusic AI - Smart Playlist & Music Recommendation App",
                        "url": "https://moodmusic.ai/product",
                        "content": "MoodMusic is an AI-powered music recommendation app based on user vibe and mood.",
                        "score": 0.88,
                    },
                ]
            },
        }
    ]

    core_keywords = {"music", "mood", "recommendation"}
    structured = retrieval_agent.structure(mock_batches, core_keywords=core_keywords)

    # Verify dictionary results were filtered out
    result_urls = [item["url"] for item in structured]
    assert "https://dictionary.cambridge.org/dictionary/english/want" not in result_urls
    assert "https://www.merriam-webster.com/dictionary/mood" not in result_urls

    # Verify the legitimate product passed
    assert len(structured) == 1
    assert structured[0]["url"] == "https://moodmusic.ai/product"


def test_keyword_overlap_filtering():
    """
    Keyword Overlap Filtering Test:
    Mock an unrelated automotive news article and verify it gets discarded
    when validating a music software idea.
    """
    retrieval_agent = DataRetrievalAgent()

    mock_batches = [
        {
            "category": "Industry News",
            "query": "music mood startup news venture funding",
            "response": {
                "results": [
                    {
                        "title": "BYD Launches New Luxury Electric Vehicle SUV",
                        "url": "https://autonews.com/articles/byd-ev-suv-launch",
                        "content": "Automaker BYD has announced its latest battery electric vehicle targeting the global EV automotive market.",
                        "score": 0.95,
                    },
                    {
                        "title": "Music AI Startup MoodWave Secures $5M Seed Funding",
                        "url": "https://techcrunch.com/2026/01/moodwave-seed-funding",
                        "content": "MoodWave, an AI music generation and mood-based playlist platform, has closed a seed round.",
                        "score": 0.90,
                    },
                ]
            },
        }
    ]

    core_keywords = {"music", "mood", "recommendation", "vibe"}
    structured = retrieval_agent.structure(mock_batches, core_keywords=core_keywords)

    # Automotive news should be discarded
    result_urls = [item["url"] for item in structured]
    assert "https://autonews.com/articles/byd-ev-suv-launch" not in result_urls

    # Relevant music startup article should pass
    assert len(structured) == 1
    assert structured[0]["url"] == "https://techcrunch.com/2026/01/moodwave-seed-funding"


def test_graceful_fallback():
    """
    Graceful Fallback Test:
    Ensure an empty search result returns total_sources: 0 without crashing.
    """
    retrieval_agent = DataRetrievalAgent()

    # Empty raw batches
    structured_empty = retrieval_agent.structure([], core_keywords={"music", "mood"})
    summary = retrieval_agent.summarize_counts(structured_empty)

    assert structured_empty == []
    assert summary["total_sources"] == 0
    assert summary["sources_per_category"]["Competitors"] == 0
    assert summary["sources_per_category"]["Industry News"] == 0
    assert summary["sources_per_category"]["Customer Demand"] == 0
    assert summary["sources_per_category"]["Market Size & Trends"] == 0


if __name__ == "__main__":
    test_stop_word_stripping()
    print("✓ test_stop_word_stripping passed")
    test_dictionary_blocklist()
    print("✓ test_dictionary_blocklist passed")
    test_keyword_overlap_filtering()
    print("✓ test_keyword_overlap_filtering passed")
    test_graceful_fallback()
    print("✓ test_graceful_fallback passed")
    print("\nAll agent test assertions passed successfully!")

