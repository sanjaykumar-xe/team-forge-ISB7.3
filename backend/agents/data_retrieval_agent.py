"""
Data Retrieval Agent
---------------------
Processes, cleans, language-filters, and normalizes raw search responses
into structured, de-duplicated source records with relevance scoring.
"""

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Fix seed for deterministic language detection
DetectorFactory.seed = 0


class DataRetrievalAgent:
    """Agent responsible for language filtering, deduplicating, scoring, and formatting search records."""

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

    def structure(self, raw_batches: list[dict]) -> list[dict]:
        """
        Takes raw batch outputs from the WebSearchAgent, filters non-English content,
        removes duplicate URLs, and returns a relevance-ranked list of source records.
        """
        seen_urls = set()
        structured = []

        for batch in raw_batches:
            query = batch.get("query", "")
            results = batch.get("response", {}).get("results", [])

            for item in results:
                title = item.get("title", "Untitled source").strip()
                url = item.get("url", "").strip()
                snippet = item.get("content", "").strip()
                score = item.get("score", 0.0)

                if not url or url in seen_urls:
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
                    "query": query,
                    "score": score,
                })

        # Sort descending by relevance score
        structured.sort(key=lambda r: r["score"], reverse=True)
        return structured

    def summarize_counts(self, structured: list[dict]) -> dict:
        """Computes total source count and category breakdown for the summary panel."""
        by_query: dict[str, int] = {}
        for record in structured:
            by_query[record["query"]] = by_query.get(record["query"], 0) + 1

        return {
            "total_sources": len(structured),
            "sources_per_query": by_query,
        }
