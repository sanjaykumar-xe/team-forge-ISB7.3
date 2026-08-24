"""
Web Search Agent
-----------------
Responsible for turning a startup idea into a set of targeted search
queries and retrieving live market data for each one.

Search provider: DuckDuckGo via the `ddgs` package — no API key, no
signup, no card, no cost. This is a free community-run library that
scrapes DuckDuckGo's public search results, so it's meant for a project
like this, not high-volume production traffic. If the team later gets a
paid key (Tavily, Serper, Brave, etc.), only this file needs to change —
everything downstream depends on the `{query, response}` shape returned
by `search()`, not on which provider produced it.

This agent's only job is *fetching* raw results. Cleaning and structuring
those results into a consistent shape is the Data Retrieval Agent's job
(see agents/data_retrieval_agent.py).
"""

import urllib.request
import urllib.parse
from lxml import html as lxml_html

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class WebSearchAgent:
    def build_queries(self, idea: str) -> list[str]:
        """Expand one startup idea into a few angles worth searching."""
        # Trim idea if needed for cleaner search queries
        clean_idea = " ".join(idea.split()[:12])
        return [
            f"{clean_idea} market size and growth",
            f"{clean_idea} competitors and alternatives",
            f"{clean_idea} target customers and demand",
        ]

    def _search_ddg_lite(self, query: str, max_results: int = 5) -> list[dict]:
        """Fallback search using DuckDuckGo Lite when DDGS hits rate limits or bot blocks."""
        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": query}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Origin": "https://lite.duckduckgo.com",
                "Referer": "https://lite.duckduckgo.com/",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            tree = lxml_html.fromstring(content)
            links = tree.xpath("//a[contains(@class, 'result-link')]")
            snippets = tree.xpath("//td[contains(@class, 'result-snippet')]")

            results = []
            for i, (link, snippet) in enumerate(zip(links, snippets)):
                if len(results) >= max_results:
                    break
                raw_url = link.get("href", "")
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    clean_url = parsed.get("uddg", [raw_url])[0]
                else:
                    clean_url = raw_url

                title = link.text_content().strip()
                body = snippet.text_content().strip()
                if clean_url and title:
                    results.append({
                        "title": title,
                        "url": clean_url,
                        "content": body,
                        "score": round(1 - (i / max(len(links), 1)), 2),
                    })
            return results

    def search(self, idea: str, max_results_per_query: int = 5) -> list[dict]:
        """
        Run all queries for this idea and return raw results per query,
        in the same `{query, response: {results: [...]}}` shape the rest
        of the pipeline expects (matches what a paid provider like Tavily
        returns, so DataRetrievalAgent doesn't need to know which one ran).

        Raises RuntimeError on a search failure so the caller can surface
        a clear error instead of a confusing stack trace.
        """
        raw_batches = []
        queries = self.build_queries(idea)

        for query in queries:
            results = []
            # 1. Try DDGS package
            if DDGS is not None:
                try:
                    with DDGS() as ddgs:
                        hits = list(ddgs.text(query, max_results=max_results_per_query))
                        results = [
                            {
                                "title": hit.get("title", ""),
                                "url": hit.get("href", ""),
                                "content": hit.get("body", ""),
                                "score": round(1 - (i / max(len(hits), 1)), 2),
                            }
                            for i, hit in enumerate(hits)
                        ]
                except Exception:
                    results = []

            # 2. Fallback to DDG Lite if DDGS returned nothing
            if not results:
                try:
                    results = self._search_ddg_lite(query, max_results=max_results_per_query)
                except Exception as exc:
                    pass

            raw_batches.append({"query": query, "response": {"results": results}})

        # If all batches are empty, attempt a direct search of the idea itself
        total_found = sum(len(b["response"]["results"]) for b in raw_batches)
        if total_found == 0:
            try:
                direct_results = self._search_ddg_lite(idea, max_results=max_results_per_query)
                if direct_results:
                    raw_batches.append({"query": idea, "response": {"results": direct_results}})
            except Exception:
                pass

        return raw_batches

