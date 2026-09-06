"""
Team Forge — CrewAI Custom Tools
--------------------------------
Provides discrete, tool-callable search functions for the Market Research Agent:
  - search_competitors(query: str)
  - search_industry_news(query: str)
  - search_customer_demand(query: str)
  - search_market_size(query: str)

Each tool wraps the verified Tavily search engine (with last-resort fallback)
and records tool invocation traces (tool name, query, result count).

Also provides tools wrapping downstream reasoning engines while keeping
DataRetrievalAgent strictly deterministic (non-LLM).
"""

import os
import json
from typing import Dict, Any, List, Optional
from crewai.tools import tool

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine


class MarketResearchToolKit:
    """
    Stateful toolkit maintaining search batches, query deduplication,
    a hard search budget cap, and an execution trace of every tool call.
    """

    def __init__(
        self,
        search_agent: Optional[WebSearchAgent] = None,
        retrieval_agent: Optional[DataRetrievalAgent] = None,
        max_total_calls: int = 8,
    ):
        self.search_agent = search_agent or WebSearchAgent()
        self.retrieval_agent = retrieval_agent or DataRetrievalAgent()
        self.max_total_calls = max_total_calls
        self.collected_batches: List[Dict[str, Any]] = []
        self.tool_call_trace: List[Dict[str, Any]] = []
        self.past_queries: List[Dict[str, Any]] = []
        self.budget_limit_reached: bool = False

    def reset(self):
        """Clears accumulated batches and traces between runs."""
        self.collected_batches = []
        self.tool_call_trace = []
        self.past_queries = []
        self.budget_limit_reached = False

    def _is_repetitive(self, category: str, query: str) -> Optional[str]:
        """Checks if a query is identical or near-identical to an already executed query."""
        import re
        q_tokens = set(re.findall(r'[a-zA-Z0-9]+', query.lower()))
        noise = {"search", "find", "who", "what", "is", "the", "a", "an", "and", "or", "for", "in", "of", "to", "price", "pricing", "cost", "vs", "site", "pdf"}
        sig_tokens = q_tokens - noise
        if not sig_tokens:
            sig_tokens = q_tokens

        for past in self.past_queries:
            if past["category"] == category:
                past_tokens = past["sig_tokens"]
                overlap = len(sig_tokens & past_tokens)
                union = len(sig_tokens | past_tokens)
                jaccard = overlap / union if union > 0 else 0
                if jaccard >= 0.65 or (len(sig_tokens) >= 3 and sig_tokens.issubset(past_tokens)) or (len(past_tokens) >= 3 and past_tokens.issubset(sig_tokens)):
                    return past["query"]
        return None

    def _record_query(self, category: str, query: str):
        import re
        q_tokens = set(re.findall(r'[a-zA-Z0-9]+', query.lower()))
        noise = {"search", "find", "who", "what", "is", "the", "a", "an", "and", "or", "for", "in", "of", "to", "price", "pricing", "cost", "vs", "site", "pdf"}
        sig_tokens = q_tokens - noise
        if not sig_tokens:
            sig_tokens = q_tokens
        self.past_queries.append({
            "category": category,
            "query": query,
            "sig_tokens": sig_tokens,
        })

    def get_structured_sources(self) -> List[Dict[str, Any]]:
        """
        DETERMINISTIC STEP: Sanitizes, validates English coherence, deduplicates URLs,
        and ranks collected search results without ANY LLM call.
        """
        return self.retrieval_agent.structure(self.collected_batches)

    def get_sources_summary(self) -> Dict[str, Any]:
        """Returns categorized count summary of structured sources."""
        sources = self.get_structured_sources()
        summary = self.retrieval_agent.summarize_counts(sources)
        if len(self.tool_call_trace) >= self.max_total_calls:
            self.budget_limit_reached = True
        summary["budget_limit_reached"] = self.budget_limit_reached
        summary["search_status"] = "budget_limited" if self.budget_limit_reached else "completed"
        if self.budget_limit_reached:
            summary["budget_notice"] = (
                f"Search space was bounded by the query budget limit ({self.max_total_calls} queries). "
                "Sparse evidence or undiscovered competitors may reflect search budget constraints rather than true market absence."
            )
        return summary

    def create_tools(self) -> List[Any]:
        """Constructs the 4 discrete CrewAI search tools with repetition protection and budget cap."""
        toolkit = self

        @tool("search_competitors")
        def search_competitors(query: str) -> str:
            """Searches verified web sources for direct competitors, alternative solutions, and rival brands.
            WHEN TO USE: Always use when an idea operates in a market with existing commercial products, substitutes, or legacy competitors.
            WHEN TO SKIP: Skip only if the idea is a novel foundational scientific breakthrough with literally zero existing market solutions or substitutes.
            REPETITION RULE: Review your past queries before calling. NEVER re-issue queries with similar keywords or repeat a query for the same brand.
            """
            if len(toolkit.tool_call_trace) >= toolkit.max_total_calls:
                toolkit.budget_limit_reached = True
                return f"[BUDGET LIMIT REACHED]: Maximum search budget of {toolkit.max_total_calls} queries reached. Do not invoke more search tools; immediately synthesize your findings from the collected evidence."

            dup = toolkit._is_repetitive("Competitors", query)
            if dup:
                return f"[REPETITION NOTICE]: You already executed a near-identical query ('{dup}'). Avoid repeating queries. Analyze the evidence you already received or choose another category."

            toolkit.tool_call_trace.append({
                "tool": "search_competitors",
                "category": "Competitors",
                "query": query,
            })
            toolkit._record_query("Competitors", query)
            batch = toolkit.search_agent._execute_single_category_search("Competitors", query, max_results=6)
            toolkit.collected_batches.append(batch)
            items = batch.get("response", {}).get("results", [])
            titles = [i.get("title", "") for i in items[:3]]
            return f"Found {len(items)} competitor sources: " + (", ".join(titles) if titles else "No results found.")

        @tool("search_industry_news")
        def search_industry_news(query: str) -> str:
            """Searches verified industry trade publications, startup news, and regulatory reports.
            WHEN TO USE: Use when the idea vertical is impacted by recent market dynamics, regulatory changes, venture investments, or supply chain shifts.
            WHEN TO SKIP: Skip for timeless, hyper-local, or traditional artisanal crafts without active regulatory or high-velocity market news.
            REPETITION RULE: Review your past queries before calling. NEVER re-issue queries with similar keywords or repeat a query for the same topic.
            """
            if len(toolkit.tool_call_trace) >= toolkit.max_total_calls:
                toolkit.budget_limit_reached = True
                return f"[BUDGET LIMIT REACHED]: Maximum search budget of {toolkit.max_total_calls} queries reached. Do not invoke more search tools; immediately synthesize your findings from the collected evidence."

            dup = toolkit._is_repetitive("Industry News", query)
            if dup:
                return f"[REPETITION NOTICE]: You already executed a near-identical query ('{dup}'). Avoid repeating queries. Analyze the evidence you already received or choose another category."

            toolkit.tool_call_trace.append({
                "tool": "search_industry_news",
                "category": "Industry News",
                "query": query,
            })
            toolkit._record_query("Industry News", query)
            batch = toolkit.search_agent._execute_single_category_search("Industry News", query, max_results=6)
            toolkit.collected_batches.append(batch)
            items = batch.get("response", {}).get("results", [])
            titles = [i.get("title", "") for i in items[:3]]
            return f"Found {len(items)} industry news sources: " + (", ".join(titles) if titles else "No results found.")

        @tool("search_customer_demand")
        def search_customer_demand(query: str) -> str:
            """Searches customer reviews, buyer complaints, community discussions, and unmet user demand signals.
            WHEN TO USE: Use for B2C consumer products, eCommerce, mobile/web consumer apps, and user-facing SaaS where retail consumers voice feedback.
            WHEN TO SKIP: Skip for pure enterprise B2B infrastructure, semiconductor manufacturing, industrial hardware, or deep-tech cleanroom tools where retail end-consumers do not exist.
            REPETITION RULE: Review your past queries before calling. NEVER re-issue queries with similar keywords or repeat a query for the same brand.
            """
            if len(toolkit.tool_call_trace) >= toolkit.max_total_calls:
                toolkit.budget_limit_reached = True
                return f"[BUDGET LIMIT REACHED]: Maximum search budget of {toolkit.max_total_calls} queries reached. Do not invoke more search tools; immediately synthesize your findings from the collected evidence."

            dup = toolkit._is_repetitive("Customer Demand", query)
            if dup:
                return f"[REPETITION NOTICE]: You already executed a near-identical query ('{dup}'). Avoid repeating queries. Analyze the evidence you already received or choose another category."

            toolkit.tool_call_trace.append({
                "tool": "search_customer_demand",
                "category": "Customer Demand",
                "query": query,
            })
            toolkit._record_query("Customer Demand", query)
            batch = toolkit.search_agent._execute_single_category_search("Customer Demand", query, max_results=6)
            toolkit.collected_batches.append(batch)
            items = batch.get("response", {}).get("results", [])
            titles = [i.get("title", "") for i in items[:3]]
            return f"Found {len(items)} customer demand sources: " + (", ".join(titles) if titles else "No results found.")

        @tool("search_market_size")
        def search_market_size(query: str) -> str:
            """Searches commercial market research reports for market size valuations (USD billions), CAGR percentages, and forecasts.
            WHEN TO USE: Use for commercial industries with established analyst coverage (e.g. consumer goods, software, semiconductors, medical devices).
            WHEN TO SKIP: Skip for tiny personal micro-hobbies, individual folk crafts, or non-commercial research projects lacking institutional analyst reports.
            REPETITION RULE: Review your past queries before calling. NEVER re-issue queries with similar keywords or repeat a query for the same market.
            """
            if len(toolkit.tool_call_trace) >= toolkit.max_total_calls:
                toolkit.budget_limit_reached = True
                return f"[BUDGET LIMIT REACHED]: Maximum search budget of {toolkit.max_total_calls} queries reached. Do not invoke more search tools; immediately synthesize your findings from the collected evidence."

            dup = toolkit._is_repetitive("Market Size & Trends", query)
            if dup:
                return f"[REPETITION NOTICE]: You already executed a near-identical query ('{dup}'). Avoid repeating queries. Analyze the evidence you already received or choose another category."

            toolkit.tool_call_trace.append({
                "tool": "search_market_size",
                "category": "Market Size & Trends",
                "query": query,
            })
            toolkit._record_query("Market Size & Trends", query)
            batch = toolkit.search_agent._execute_single_category_search("Market Size & Trends", query, max_results=6)
            toolkit.collected_batches.append(batch)
            items = batch.get("response", {}).get("results", [])
            titles = [i.get("title", "") for i in items[:3]]
            return f"Found {len(items)} market size sources: " + (", ".join(titles) if titles else "No results found.")

        return [search_competitors, search_industry_news, search_customer_demand, search_market_size]


# Legacy wrappers for backward compatibility with crew/__init__.py
class IdeaExtractionTool:
    def __init__(self, agent=None):
        self._agent = agent or IdeaExtractionAgent()
    def run(self, idea: str, product_name=None, industry=None, target_audience=None):
        return self._agent.extract(idea=idea, product_name=product_name, industry=industry, target_audience=target_audience)

class TavilySearchTool:
    def __init__(self, agent=None):
        self._agent = agent or WebSearchAgent()
    def run(self, structured_idea, max_results_per_category=6):
        return self._agent.search(structured_idea=structured_idea, max_results_per_category=max_results_per_category)

class DataRetrievalTool:
    def __init__(self, agent=None):
        self._agent = agent or DataRetrievalAgent()
    def run(self, raw_batches):
        structured = self._agent.structure(raw_batches)
        summary = self._agent.summarize_counts(structured)
        return {"sources": structured, "summary": summary}

class MarketAnalysisTool:
    def __init__(self, agent=None):
        self._agent = agent or MarketOpportunityAgent()
    def run(self, idea, structured_idea, sources):
        return self._agent.analyze(idea=idea, structured_idea=structured_idea, sources=sources).model_dump()

class CompetitorAnalysisTool:
    def __init__(self, agent=None):
        self._agent = agent or CompetitorAnalysisAgent()
    def run(self, idea, structured_idea, sources, market_analysis=None):
        from schemas.validation_schemas import MarketAnalysisResult
        market_obj = MarketAnalysisResult(**market_analysis) if market_analysis else None
        return self._agent.analyze(idea=idea, structured_idea=structured_idea, sources=sources, market_analysis=market_obj).model_dump()

class WhiteSpaceEngineTool:
    def __init__(self, engine=None):
        self._engine = engine or WhiteSpaceEngine()
    def run(self, idea, structured_idea, sources, market_analysis=None, competitor_analysis=None):
        from schemas.validation_schemas import MarketAnalysisResult, CompetitorAnalysisResult
        market_obj = MarketAnalysisResult(**market_analysis) if market_analysis else None
        comp_obj = CompetitorAnalysisResult(**competitor_analysis) if competitor_analysis else None
        return self._engine.discover(idea=idea, structured_idea=structured_idea, sources=sources, market_analysis=market_obj, competitor_analysis=comp_obj).model_dump()
