"""
Data Retrieval Agent
---------------------
Takes the raw, per-query search responses from the Web Search Agent and
turns them into one clean, de-duplicated list of source records that the
rest of the pipeline (Milestone 2+ analysis agents) can consume without
caring where the data came from.

Downstream agents (Market Opportunity, Competitor Discovery, SWOT/Risk,
etc.) should only ever depend on this shape:

    {
        "title": str,
        "url": str,
        "snippet": str,
        "query": str,     # which search angle surfaced this source
        "score": float,   # relevance score, 0-1 (rank-based; see web_search_agent.py)
    }
"""


class DataRetrievalAgent:
    def structure(self, raw_batches: list[dict]) -> list[dict]:
        seen_urls = set()
        structured = []

        for batch in raw_batches:
            query = batch["query"]
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

        structured.sort(key=lambda r: r["score"], reverse=True)
        return structured

    def summarize_counts(self, structured: list[dict]) -> dict:
        """Small helper the frontend uses to show a quick coverage summary."""
        by_query: dict[str, int] = {}
        for record in structured:
            by_query[record["query"]] = by_query.get(record["query"], 0) + 1
        return {
            "total_sources": len(structured),
            "sources_per_query": by_query,
        }
