"""
Web Search Agent
-----------------
Executes 4-category market research searches using the Tavily Search API.
Uses structured output from IdeaExtractionAgent (product_name, industry, keywords,
core_problem) to construct precise search queries for:
  1. Competitors
  2. Industry News
  3. Customer Demand
  4. Market Size & Trends
"""

import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import wordfreq
from dotenv import load_dotenv

load_dotenv()

_tavily_lock = threading.Lock()
_tavily_client = None

def get_tavily_client():
    global _tavily_client
    with _tavily_lock:
        if _tavily_client is None:
            from tavily import TavilyClient
            api_key = os.environ.get("TAVILY_API_KEY", "")
            _tavily_client = TavilyClient(api_key=api_key)
        return _tavily_client


class WebSearchAgent:
    """Agent responsible for idea validation and category-specific market search via Tavily."""

    def __init__(self):
        self.search_provider_degraded: bool = False
        self.degraded_reason: str = ""
        self._tavily_auth_or_quota_failed: bool = False
        self._tavily_auth_or_quota_reason: str = ""

    def reset_degraded_state(self):
        """Resets degraded state between validation runs if needed."""
        self.search_provider_degraded = False
        self.degraded_reason = ""
        self._tavily_auth_or_quota_failed = False
        self._tavily_auth_or_quota_reason = ""

    def is_valid_idea(self, text: str) -> bool:
        """
        Validates whether the idea text contains recognizable English words.
        Prevents gibberish or nonsense input from triggering search requests.
        """
        if not text or len(text.strip()) < 5:
            return False
        words = re.findall(r'[a-zA-Z]+', text)
        if not words or len(words) < 2:
            return False
        valid_count = sum(1 for w in words if wordfreq.word_frequency(w.lower(), 'en') > 0)
        ratio = valid_count / len(words)
        return valid_count >= 2 and ratio >= 0.45

    def extract_core_keywords(self, idea: str) -> str:
        """Extracts high-signal domain keywords from natural language text, stripping conversational stop words."""
        cleaned = re.sub(
            r'^(i want to (build|create|make|launch|develop|start)\s+|'
            r'(a|an )?[a-z]+ (app|platform|tool|service|system|web app|website|marketplace|saas|startup|product|solution) (that|which|to|for|helping)\s+|'
            r'(a|an) (startup|product|solution) (that|to|for)\s+)',
            '', idea.strip(), flags=re.IGNORECASE
        )
        words = [w for w in re.findall(r'[a-zA-Z0-9]+', cleaned) if len(w) > 2]
        generic = {
            "app", "platform", "tool", "service", "system", "that", "helps", "help", "with", "for",
            "and", "the", "you", "your", "our", "their", "user", "users", "people", "built", "designed",
            "want", "create", "suggests", "suggest", "based"
        }
        filtered = [w.lower() for w in words if w.lower() not in generic]
        return " ".join(filtered[:5]) or " ".join(words[:4])


    def _sanitize_query_part(self, text: str) -> str:
        """Strips accidental form labels, colons, slashes, and noisy prompt prefixes."""
        if not text:
            return ""
        cleaned = re.sub(
            r'^(describe(\s+the)?\s+(startup\s+)?(concept|idea)|startup(\s+/\s+product)?\s+name|industry(\s+or\s+vertical)?|target\s+customer(\s+profile)?|core\s+problem(\s+statement)?):\s*',
            '', text.strip(), flags=re.IGNORECASE
        )
        # Remove embedded label prefixes like "Industry or Vertical:"
        cleaned = re.sub(r'(industry\s+or\s+vertical|product\s+name|target\s+audience):\s*', ' ', cleaned, flags=re.IGNORECASE)
        # Replace slashes and colons with spaces
        cleaned = re.sub(r'[/\\:;|\-_]+', ' ', cleaned)
        # Collapse whitespace
        return re.sub(r'\s+', ' ', cleaned).strip()

    def build_queries(self, structured_idea: dict) -> dict[str, str]:
        """
        Constructs tailored search queries for each of the 4 research categories
        using extracted domain keywords, industry, and product name.
        """
        generic_stopwords = {
            "app", "platform", "tool", "service", "system", "that", "helps", "help", "with", "for",
            "and", "the", "you", "your", "our", "their", "user", "users", "people", "built", "designed",
            "describe", "startup", "concept", "idea", "product", "name", "industry", "vertical",
            "target", "customer", "profile", "solution", "none", "delivers", "deliver", "delivering",
            "provides", "provide", "providing", "offers", "offering"
        }

        keywords = structured_idea.get("keywords", [])
        if isinstance(keywords, list) and keywords:
            filtered_kws = [k.strip() for k in keywords if k.strip().lower() not in generic_stopwords]
            kw_str = " ".join(filtered_kws[:6]) or " ".join(keywords[:6])
        else:
            kw_str = "startup technology"

        kw_str = self._sanitize_query_part(kw_str)

        # Ensure high-signal domain nouns from core problem are retained if missing
        core_problem = structured_idea.get("core_problem", "").lower()
        for domain_word in ["cleaning", "detergent", "refill", "cosmetics", "skincare", "coffee", "grocery", "supplies"]:
            if domain_word in core_problem and domain_word not in kw_str.lower():
                kw_str = f"{domain_word} {kw_str}".strip()
                break

        industry_raw = structured_idea.get("industry", "").strip()
        industry = self._sanitize_query_part(industry_raw)

        # Enrich kw_str with specific domain words from industry if not already present
        if industry and industry.lower() not in ["software", "technology", "none"]:
            domain_terms = [w.lower() for w in re.findall(r'[a-zA-Z]+', industry) if len(w) > 3 and w.lower() not in generic_stopwords]
            for dt in domain_terms[:2]:
                if dt not in kw_str.lower():
                    kw_str = f"{kw_str} {dt}"

        # Build category-specific queries focusing on industry concept rather than unlaunched product name
        comp_query = f"{kw_str} competitors alternatives brands"
        news_query = f"{kw_str} industry trends startup news"
        demand_query = f"{kw_str} customer complaints reviews problems"
        market_query = f"{kw_str} market size growth forecast"
        if industry and industry.lower() not in ["software", "technology", "none", "technology software", "software technology"]:
            market_query = f"{kw_str} {industry} market size growth forecast"

        return {
            "Competitors": comp_query.strip(),
            "Industry News": news_query.strip(),
            "Customer Demand": demand_query.strip(),
            "Market Size & Trends": market_query.strip(),
        }

    def _ddg_lite_search(self, query: str, max_results: int = 6) -> list[dict]:
        """Performs search via DuckDuckGo Lite endpoint without requiring an API key."""
        import urllib.parse
        import urllib.request
        from lxml import html

        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": query}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        results = []
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                tree = html.fromstring(content)
                links = tree.xpath("//a[contains(@class, 'result-link')]")
                snippets = tree.xpath("//td[contains(@class, 'result-snippet')]")
                for l, s in zip(links[:max_results], snippets[:max_results]):
                    title = l.text_content().strip()
                    href = l.get("href", "").strip()
                    snippet = s.text_content().strip()
                    if href and title:
                        score = round(max(0.60, 0.88 - len(results) * 0.03), 2)
                        results.append({
                            "title": title,
                            "url": href,
                            "content": snippet,
                            "score": score,
                        })
        except Exception as exc:
            print(f"[WebSearchAgent] DDG Lite search error for query '{query}': {exc}")

        return results

    def _google_news_rss(self, query: str, max_results: int = 6) -> list[dict]:
        """Fetches industry news via Google News RSS search endpoint."""
        import urllib.parse
        import urllib.request
        from lxml import html, etree

        news_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(news_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        results = []
        try:
            with urllib.request.urlopen(req, timeout=7) as resp:
                root = etree.fromstring(resp.read())
                items = root.xpath("//item")
                for item in items[:max_results]:
                    desc = item.findtext("description") or ""
                    snippet = ""
                    if desc:
                        try:
                            snippet = html.fromstring(desc).text_content().strip()
                        except Exception:
                            snippet = desc.strip()
                    title = item.findtext("title") or ""
                    link = item.findtext("link") or ""
                    if title and link:
                        score = round(max(0.55, 0.85 - len(results) * 0.03), 2)
                        results.append({
                            "title": title,
                            "url": link,
                            "content": snippet,
                            "score": score,
                            "provider": "google_news",
                        })
        except Exception as exc:
            print(f"[WebSearchAgent] Google News RSS error for query '{query}': {exc}")

        return results

    def _execute_single_category_search(
        self,
        category: str,
        query: str,
        max_results: int = 6,
    ) -> dict:
        """
        Executes a category-targeted search using Tavily as the primary provider.
        DuckDuckGo Lite and Google News RSS serve as a genuine last-resort safety net
        that only fires if Tavily itself throws an error or is unconfigured.
        """
        results = []
        api_key = os.environ.get("TAVILY_API_KEY", "").strip()
        tavily_error = None
        tavily_attempted = False
        is_quota_or_auth_error = False

        # If Tavily was previously confirmed dead in this process run (e.g. 401/402/403), skip re-hitting it
        if getattr(self, "_tavily_auth_or_quota_failed", False):
            tavily_attempted = False
            should_fallback = True
            is_quota_or_auth_error = True
            self.search_provider_degraded = True
            self.degraded_reason = getattr(self, "_tavily_auth_or_quota_reason", "Tavily API credits exhausted or invalid key.")
        else:
            if api_key:
                tavily_attempted = True
                try:
                    client = get_tavily_client()
                    topic = "news" if category == "Industry News" else "general"
                    kwargs = {
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": max_results,
                    }
                    if topic == "news":
                        try:
                            kwargs["topic"] = "news"
                            response = client.search(**kwargs)
                        except Exception:
                            kwargs.pop("topic", None)
                            response = client.search(**kwargs)
                    else:
                        response = client.search(**kwargs)

                    raw_items = response.get("results", [])
                    for item in raw_items:
                        results.append({
                            "title": item.get("title", "").strip(),
                            "url": item.get("url", "").strip(),
                            "content": item.get("content", "").strip(),
                            "score": float(item.get("score", 0.0) or 0.0),
                            "category": category,
                            "provider": "tavily",
                        })
                except Exception as exc:
                    tavily_error = exc
                    err_str = str(exc).lower()
                    
                    # Check specifically for permanent auth/quota/credit exhaustion (401, 402, 403)
                    if any(code in err_str for code in ["401", "402", "403", "unauthorized", "quota", "credit", "payment", "rate limit"]):
                        is_quota_or_auth_error = True
                        self._tavily_auth_or_quota_failed = True
                        self._tavily_auth_or_quota_reason = f"Tavily API quota/auth error: {exc}"
                        self.search_provider_degraded = True
                        self.degraded_reason = self._tavily_auth_or_quota_reason
                        print(f"\n[CRITICAL] Tavily API key invalid or credits exhausted (HTTP 401/402/403) — falling back to degraded search. Details: {exc}\n")
                    else:
                        print(f"[WebSearchAgent] Tavily search error for '{category}' (query: '{query}'): {exc}")

            should_fallback = (not api_key) or (tavily_attempted and tavily_error is not None)

        if should_fallback:
            if not self.search_provider_degraded:
                self.search_provider_degraded = True
                self.degraded_reason = f"Tavily exception: {tavily_error}" if tavily_error else "TAVILY_API_KEY is not configured"

            # =========================================================================
            # LAST-RESORT EMERGENCY FALLBACK (DuckDuckGo / Google News RSS)
            # =========================================================================
            needed = max_results
            fallback_items = []

            if is_quota_or_auth_error:
                # FAST-FAIL PATH for 401/402/403: Run SINGLE fastest fallback (DDG Lite) without cascading 3 retries
                ddg_items = self._ddg_lite_search(query, max_results=needed)
                for it in ddg_items:
                    it["provider"] = "duckduckgo"
                fallback_items.extend(ddg_items)
            else:
                # Standard transient retry cascade (for timeouts/network blips)
                # 1. Attempt DDG Lite
                ddg_items = self._ddg_lite_search(query, max_results=needed)
                for it in ddg_items:
                    it["provider"] = "duckduckgo"
                fallback_items.extend(ddg_items)

                # 2. Attempt Google News RSS for news or if still under capacity
                if len(fallback_items) < needed or category in ("Industry News", "Market Size & Trends"):
                    rem = max(3, needed - len(fallback_items))
                    gnews_items = self._google_news_rss(query, max_results=rem)
                    fallback_items.extend(gnews_items)

                # 3. Third attempt: broader query if still under 3 results
                if len(fallback_items) < 3:
                    words = [w for w in query.split() if len(w) > 2]
                    broad_query = f"{' '.join(words[:3])} {category.lower()}"
                    broader_ddg = self._ddg_lite_search(broad_query, max_results=needed)
                    for it in broader_ddg:
                        it["provider"] = "duckduckgo"
                    fallback_items.extend(broader_ddg)

            existing_urls = {r.get("url") for r in results}
            for item in fallback_items:
                if item.get("url") and item.get("url") not in existing_urls:
                    item["category"] = category
                    results.append(item)
                    existing_urls.add(item.get("url"))

        return {
            "category": category,
            "query": query,
            "response": {"results": results[:max_results]},
        }

    def search(
        self,
        structured_idea: dict,
        max_results_per_category: int = 6,
    ) -> list[dict]:
        """
        Executes parallel Tavily searches across the 4 distinct market categories:
          - Competitors
          - Industry News
          - Customer Demand
          - Market Size & Trends
        """
        queries = self.build_queries(structured_idea)

        raw_batches = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    self._execute_single_category_search,
                    cat,
                    q,
                    max_results_per_category,
                )
                for cat, q in queries.items()
            ]
            for future in futures:
                try:
                    raw_batches.append(future.result())
                except Exception as exc:
                    print(f"[WebSearchAgent] Error collecting search batch: {exc}")

        return raw_batches
