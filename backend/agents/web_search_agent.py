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
import json
import re
from lxml import html as lxml_html, etree

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class WebSearchAgent:
    def build_queries(self, idea: str) -> list[str]:
        """Expand one startup idea into 3 targeted market research angles."""
        clean_idea = re.sub(r'^(a|an|the)\s+', '', idea.strip(), flags=re.IGNORECASE)
        words = clean_idea.split()
        short_idea = " ".join(words[:8]) if len(words) > 8 else clean_idea
        
        return [
            f"{short_idea} market size and industry trends",
            f"{short_idea} competitors and alternatives",
            f"{short_idea} target customers and market demand",
        ]

    def _search_ddg(self, query: str, max_results: int = 5) -> list[dict]:
        """Query DuckDuckGo via DDGS or DDG Lite."""
        results = []
        if DDGS is not None:
            try:
                with DDGS() as ddgs:
                    hits = list(ddgs.text(query, max_results=max_results))
                    for i, hit in enumerate(hits):
                        results.append({
                            "title": hit.get("title", ""),
                            "url": hit.get("href", ""),
                            "content": hit.get("body", ""),
                            "score": round(1.0 - (i * 0.08), 2),
                        })
            except Exception:
                results = []

        if not results:
            try:
                url = "https://lite.duckduckgo.com/lite/"
                data = urllib.parse.urlencode({"q": query}).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                with urllib.request.urlopen(req, timeout=4) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
                    tree = lxml_html.fromstring(content)
                    links = tree.xpath("//a[contains(@class, 'result-link')]")
                    snippets = tree.xpath("//td[contains(@class, 'result-snippet')]")
                    for i, (link, snippet) in enumerate(zip(links[:max_results], snippets[:max_results])):
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
                                "score": round(1.0 - (i * 0.08), 2),
                            })
            except Exception:
                pass

        return results

    def _search_google_news(self, query: str, max_results: int = 4) -> list[dict]:
        """Free keyless Google News Market Intelligence RSS feed."""
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                xml_data = resp.read()
                root = etree.fromstring(xml_data)
                items = root.xpath("//item")
                results = []
                for i, item in enumerate(items[:max_results]):
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    desc = item.findtext("description", "")
                    if desc:
                        try:
                            desc = lxml_html.fromstring(desc).text_content()
                        except Exception:
                            pass
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "content": desc or title,
                            "score": round(0.95 - (i * 0.07), 2),
                        })
                return results
        except Exception:
            return []

    def _search_wikipedia(self, query: str, max_results: int = 3) -> list[dict]:
        """Free keyless Wikipedia Knowledge search for industry & concept definitions."""
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "TeamForgeStartupValidator/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                results = []
                for i, item in enumerate(data.get("query", {}).get("search", [])[:max_results]):
                    snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
                    title = item.get("title", "")
                    page_id = item.get("pageid", "")
                    if title and page_id:
                        results.append({
                            "title": f"{title} — Industry Overview",
                            "url": f"https://en.wikipedia.org/?curid={page_id}",
                            "content": snippet,
                            "score": round(0.85 - (i * 0.08), 2),
                        })
                return results
        except Exception:
            return []

    def search(self, idea: str, max_results_per_query: int = 5) -> list[dict]:
        """
        Run all queries for this idea and return raw results per query,
        in the same `{query, response: {results: [...]}}` shape the rest
        of the pipeline expects (matches what a paid provider like Tavily
        returns, so DataRetrievalAgent doesn't need to know which one ran).
        """
        raw_batches = []
        queries = self.build_queries(idea)

        for query in queries:
            # Step 1: Query DDG
            results = self._search_ddg(query, max_results=max_results_per_query)

            # Step 2: If DDG is sparse, supplement with Google Market News RSS
            if len(results) < 3:
                news_results = self._search_google_news(query, max_results=3)
                results.extend(news_results)

            # Step 3: If still sparse, supplement with Wikipedia industry context
            if len(results) < 3:
                wiki_results = self._search_wikipedia(query, max_results=2)
                results.extend(wiki_results)

            raw_batches.append({"query": query, "response": {"results": results}})

        return raw_batches


