"""
Data Retrieval Agent
---------------------
Processes and normalizes raw search responses into structured,
de-duplicated source records with relevance scoring.
"""


class DataRetrievalAgent:
    """Agent responsible for deduplicating, scoring, and formatting search records."""

    def structure(self, raw_batches: list[dict]) -> list[dict]:
        """
        Takes raw batch outputs from the WebSearchAgent and returns a de-duplicated,
        relevance-ranked list of source records.
        """
        seen_urls = set()
        structured = []

        for batch in raw_batches:
            query = batch.get("query", "")
            results = batch.get("response", {}).get("results", [])

            for item in results:
                url = item.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                structured.append({
                    "title": item.get("title", "Untitled source"),
                    "url": url,
                    "snippet": item.get("content", "").strip(),
                    "query": query,
                    "score": item.get("score", 0.0),
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
