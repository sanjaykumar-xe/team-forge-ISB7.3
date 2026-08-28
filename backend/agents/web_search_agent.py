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

    def build_queries(self, structured_idea: dict) -> dict[str, str]:
        """
        Constructs tailored search queries for each of the 4 research categories
        using extracted domain keywords, industry, and product name.
        """
        keywords = structured_idea.get("keywords", [])
        if isinstance(keywords, list) and keywords:
            kw_str = " ".join(keywords[:4])
        else:
            kw_str = structured_idea.get("product_name", "startup")

        pname = structured_idea.get("product_name", "").strip()
        industry = structured_idea.get("industry", "").strip()

        # Build category-specific queries
        # For Competitors: combine keywords + competitors alternatives
        comp_query = f"{kw_str} competitors alternatives"
        if pname and pname.lower() not in ["startup", "app", "platform", "tool", "none"]:
            comp_query = f"{kw_str} {pname} competitors alternatives"

        news_query = f"{kw_str} industry trends startup news"
        demand_query = f"{kw_str} customer problems user demand reviews"
        market_query = f"{kw_str} market size growth forecast"
        if industry and industry.lower() not in ["software", "technology", "none", "technology / software"]:
            market_query = f"{kw_str} {industry} market size growth forecast"

        return {
            "Competitors": comp_query.strip(),
            "Industry News": news_query.strip(),
            "Customer Demand": demand_query.strip(),
            "Market Size & Trends": market_query.strip(),
        }

    def _execute_single_category_search(
        self,
        category: str,
        query: str,
        max_results: int = 6,
    ) -> dict:
        """Executes a single Tavily search call for a specific category."""
        client = get_tavily_client()
        topic = "news" if category == "Industry News" else "general"

        results = []
        try:
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
                })
        except Exception as exc:
            print(f"[WebSearchAgent] Tavily search error for '{category}' (query: '{query}'): {exc}")

        return {
            "category": category,
            "query": query,
            "response": {"results": results},
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
