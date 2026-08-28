"""
Data Retrieval Agent
---------------------
Processes, cleans, language-filters, and normalizes raw search responses
into structured, de-duplicated source records categorized across:
  - Competitors
  - Industry News
  - Customer Demand
  - Market Size & Trends
"""

from urllib.parse import urlparse
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Fix seed for deterministic language detection
DetectorFactory.seed = 0

VALID_CATEGORIES = [
    "Competitors",
    "Industry News",
    "Customer Demand",
    "Market Size & Trends",
]

# Domains that provide generic dictionary entries, aggregators, or encyclopedic definitions
BLOCKED_DOMAINS = [
    "dictionary.cambridge.org",
    "merriam-webster.com",
    "dictionary.com",
    "thesaurus.com",
    "englishan.com",
    "wiktionary.org",
    "wikipedia.org",
    "whereorg.com",
    "yelp.com",
    "yellowpages.com",
    "tripadvisor.com",
    "vocabulary.com",
    "collinsdictionary.com",
    "oxfordlearnersdictionaries.com",
    "macmillandictionary.com",
    "lexico.com",
    "thefreedictionary.com",
    "myaccount.microsoft.com",
    "support.microsoft.com",
    "support.google.com",
    "forums.digitalspy.com",
    "math.stackexchange.com",
    "stackexchange.com",
    "answers.yahoo.com",
    "quora.com",
    "medicinesfaq.com",   # pharma drug-reference site; collides with product names
]


class DataRetrievalAgent:
    """Agent responsible for language filtering, deduplicating, domain filtering, and categorizing search records."""

    def _is_english(self, text: str) -> bool:
        """
        Determines whether the text is in English.
        Discards non-English search results.
        """
        clean_text = text.strip()
        if len(clean_text) < 15:
            return True  # Retain very short titles to avoid false positives

        try:
            lang = detect(clean_text)
            return lang == "en"
        except LangDetectException:
            return True
        except Exception:
            return True

    def _is_blocked_domain(self, url: str) -> bool:
        """Checks if a URL belongs to a blocked dictionary, aggregator, or non-commercial domain."""
        if not url:
            return True
        try:
            netloc = urlparse(url).netloc.lower()
            if ":" in netloc:
                netloc = netloc.split(":")[0]
            for blocked in BLOCKED_DOMAINS:
                if netloc == blocked or netloc.endswith("." + blocked):
                    return True
            return False
        except Exception:
            return False

    def structure(self, raw_batches: list[dict]) -> list[dict]:
        """
        Takes raw batch outputs from the WebSearchAgent, filters blocked domains,
        filters non-English content, removes duplicate URLs, and returns structured
        source records.

        Note: core_keywords / keyword-overlap filtering removed — the LLM judge
        in WebSearchAgent now handles relevance.
        """
        seen_urls = set()
        structured = []

        for batch in raw_batches:
            category = batch.get("category", "Industry News")
            query = batch.get("query", "")
            results = batch.get("response", {}).get("results", [])

            for item in results:
                title = item.get("title", "Untitled source").strip()
                url = item.get("url", "").strip()
                snippet = item.get("content", "").strip() or item.get("snippet", "").strip()
                score = float(item.get("score", 0.0) or 0.0)
                # Respect LLM-assigned category if present on item
                item_category = item.get("category", category)
                if item_category not in VALID_CATEGORIES:
                    item_category = category
                item_query = item.get("_query", query)

                if not url or url in seen_urls:
                    continue

                # Filter out blocked domains (belt-and-suspenders — also done pre-LLM)
                if self._is_blocked_domain(url):
                    continue

                # Filter out obvious junk, lyric search sites, or media player pages
                url_lower = url.lower()
                title_lower = title.lower()
                if any(junk in url_lower or junk in title_lower for junk in [
                    "lyrics", "azlyrics", "lyricfinder", "songlyrics", "youtube.com/watch",
                    "mp3", "ringtone", "chord", "guitar", "tablature"
                ]):
                    continue

                # English language filter
                combined_content = f"{title}. {snippet}"
                if not self._is_english(combined_content):
                    continue

                seen_urls.add(url)
                structured.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "query": item_query,
                    "category": item_category,
                    "score": score,
                })

        # Sort descending by relevance score
        structured.sort(key=lambda r: r["score"], reverse=True)
        return structured

    def summarize_counts(self, structured: list[dict]) -> dict:
        """Computes total source count, category breakdown, and grouped sources."""
        by_category: dict[str, int] = {cat: 0 for cat in VALID_CATEGORIES}
        sources_by_category: dict[str, list[dict]] = {cat: [] for cat in VALID_CATEGORIES}

        for record in structured:
            cat = record.get("category", "Industry News")
            if cat not in by_category:
                by_category[cat] = 0
                sources_by_category[cat] = []
            by_category[cat] += 1
            sources_by_category[cat].append(record)

        return {
            "total_sources": len(structured),
            "sources_per_category": by_category,
            "sources_by_category": sources_by_category,
        }
