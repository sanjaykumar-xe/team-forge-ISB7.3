"""
Web Search Agent
-----------------
Takes a startup idea (plus optional product name, industry, and target audience),
validates language coherence, expands it into targeted market research queries,
and retrieves live search results using DuckDuckGo with relevance-filtered fallbacks.
"""

import urllib.request
import urllib.parse
import json
import re
from lxml import html as lxml_html, etree
import wordfreq

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

from concurrent.futures import ThreadPoolExecutor

# Common stopwords and generic tech terms to ignore during fallback relevance checks
GENERIC_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "once", "here", "there", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "can", "will", "just", "should", "now", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would", "could",
    "platform", "service", "system", "app", "application", "tool", "software", "solution",
    "solutions", "services", "platforms", "online", "digital", "based", "startup", "technology", "tech"
}



class WebSearchAgent:
    """Agent responsible for idea validation, multi-angle market research, and live web search."""

    def is_valid_idea(self, text: str) -> bool:
        """
        Validates whether the idea text contains recognizable English words.
        Prevents gibberish or nonsense input from triggering search fallbacks.
        """
        if not text or len(text.strip()) < 5:
            return False

        words = re.findall(r'[a-zA-Z]+', text)
        if not words or len(words) < 2:
            return False

        valid_count = sum(1 for w in words if wordfreq.word_frequency(w.lower(), 'en') > 0)
        ratio = valid_count / len(words)

        return valid_count >= 2 and ratio >= 0.45

    def get_meaningful_keywords(self, idea: str, industry: str | None = None, product_name: str | None = None) -> set[str]:
        """Extracts meaningful non-stopword domain terms for relevance filtering."""
        combined = f"{idea} {industry or ''} {product_name or ''}"
        words = re.findall(r'[a-zA-Z]{3,}', combined)
        return {w.lower() for w in words if w.lower() not in GENERIC_STOPWORDS}

    def build_queries(
        self,
        idea: str,
        product_name: str | None = None,
        industry: str | None = None,
        target_audience: str | None = None,
    ) -> list[str]:
        """
        Expands the startup concept into three targeted research angles,
        incorporating industry and target audience for disambiguation.
        """
        clean_idea = re.sub(r'^(a|an|the)\s+', '', idea.strip(), flags=re.IGNORECASE)
        words = clean_idea.split()
        short_idea = " ".join(words[:8]) if len(words) > 8 else clean_idea

        # Build disambiguated base query
        prefix_parts = []
        if industry and industry.strip():
            ind = industry.strip()
            if ind.lower() not in short_idea.lower():
                prefix_parts.append(ind)
        if product_name and product_name.strip():
            pname = product_name.strip()
            if pname.lower() not in short_idea.lower():
                prefix_parts.append(pname)

        prefix = " ".join(prefix_parts) + " " if prefix_parts else ""
        base = f"{prefix}{short_idea}".strip()

        # Customer demand query customization
        audience_suffix = f" {target_audience.strip()}" if target_audience and target_audience.strip() else ""

        return [
            f"{base} market size and industry trends",
            f"{base} competitors and alternatives",
            f"{base} target customers{audience_suffix} and market demand",
        ]

    def _filter_by_keyword_relevance(self, items: list[dict], keywords: set[str]) -> list[dict]:
        """Ensures fallback results contain at least one meaningful domain term to prevent keyword collisions."""
        if not keywords:
            return items

        filtered = []
        for item in items:
            text = f"{item.get('title', '')} {item.get('content', '')}".lower()
            if any(kw in text for kw in keywords):
                filtered.append(item)
        return filtered

    def _search_ddg(self, query: str, max_results: int = 5) -> list[dict]:
        """Queries DuckDuckGo via the ddgs library, with a lite HTML fallback."""
        results = []
        if DDGS is not None:
            try:
                with DDGS(timeout=4) as ddgs:
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
                with urllib.request.urlopen(req, timeout=3) as resp:
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
        """Fetches market news coverage via RSS for fresh signals."""
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
        """Queries Wikipedia API for industry context and terminology."""
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

    def _execute_single_query(self, query: str, meaningful_keywords: set[str], max_results_per_query: int) -> dict:
        """Executes a single search query with DDG primary and relevance-filtered fallbacks."""
        results = self._search_ddg(query, max_results=max_results_per_query)

        if len(results) < 3:
            news_results = self._search_google_news(query, max_results=3)
            filtered_news = self._filter_by_keyword_relevance(news_results, meaningful_keywords)
            results.extend(filtered_news)

        if len(results) < 3:
            wiki_results = self._search_wikipedia(query, max_results=2)
            filtered_wiki = self._filter_by_keyword_relevance(wiki_results, meaningful_keywords)
            results.extend(filtered_wiki)

        return {"query": query, "response": {"results": results}}

    def search(
        self,
        idea: str,
        product_name: str | None = None,
        industry: str | None = None,
        target_audience: str | None = None,
        max_results_per_query: int = 5,
    ) -> list[dict]:
        """
        Executes search queries for the idea across three research angles in parallel.
        Returns raw query results with keyword-relevance filtered fallbacks.
        """
        queries = self.build_queries(
            idea=idea,
            product_name=product_name,
            industry=industry,
            target_audience=target_audience,
        )
        meaningful_keywords = self.get_meaningful_keywords(idea, industry, product_name)

        raw_batches = []
        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [
                executor.submit(self._execute_single_query, q, meaningful_keywords, max_results_per_query)
                for q in queries
            ]
            for future in futures:
                try:
                    raw_batches.append(future.result())
                except Exception:
                    pass

        return raw_batches

