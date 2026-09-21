"""
Market Opportunity & Customer Segmentation Agent (Milestone 3)
--------------------------------------------------------------
Externalized prompts, autonomous additional search capability,
grounding flags on market size estimates.
"""

import re
from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    MarketAnalysisResult,
    MarketSizeEstimate,
)
from services.llm_service import call_groq_json
from services.text_utils import truncate_at_word_boundary
from prompts.loader import load_prompt


class MarketOpportunityAgent:
    """Agent responsible for market sizing, customer segmentation, and market attractiveness analysis."""

    def __init__(self):
        self._additional_searches_made = 0

    def _build_context_from_sources(self, sources: List[Dict[str, Any]]) -> str:
        if not sources:
            return "No verified web sources available."

        market_items = [s for s in sources if s.get("category") == "Market Size & Trends"][:5]
        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:3]
        news_items = [s for s in sources if s.get("category") == "Industry News"][:2]
        selected = market_items + demand_items + news_items

        if len(selected) < 4:
            selected = sources[:7]

        lines = []
        for i, s in enumerate(selected, 1):
            category = s.get("category", "General")
            title = truncate_at_word_boundary(s.get("title", "Untitled"), max_length=90)
            url = s.get("url", "")
            raw_snip = s.get("snippet", "") or s.get("content", "")
            snippet = truncate_at_word_boundary(raw_snip, max_length=260)
            lines.append(f"[{i}] [{category}] {title}\nURL: {url}\nEvidence: {snippet}\n")

        return "\n".join(lines)

    def request_additional_search(
        self,
        query: str,
        search_agent: Any = None,
        tool_call_trace: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Autonomous tool: requests an additional targeted search if sources are insufficient.
        Budget-limited to at most 1 call per run.
        """
        if self._additional_searches_made >= 1:
            print("  [MarketOpportunityAgent] Additional search budget reached (1 call max).")
            return []

        self._additional_searches_made += 1
        print(f"  [MarketOpportunityAgent Autonomous Search] Query: '{query}'")

        if tool_call_trace is not None:
            tool_call_trace.append({
                "tool": "request_additional_search",
                "caller": "MarketOpportunityAgent",
                "category": "Market Size & Trends",
                "query": query,
            })

        if search_agent and hasattr(search_agent, "_execute_single_category_search"):
            try:
                batch = search_agent._execute_single_category_search("Market Size & Trends", query, max_results=4)
                results = batch.get("response", {}).get("results", [])
                new_sources = []
                for r in results:
                    new_sources.append({
                        "url": r.get("url", ""),
                        "title": r.get("title", ""),
                        "snippet": r.get("content", "") or r.get("snippet", ""),
                        "category": "Market Size & Trends",
                    })
                return new_sources
            except Exception as exc:
                print(f"  [MarketOpportunityAgent] Additional search failed: {exc}")
                return []
        return []

    def _fallback_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        reason: str = "LLM unavailable",
    ) -> MarketAnalysisResult:
        product_name = structured_idea.get("product_name") or "Startup"
        industry = structured_idea.get("industry") or "the sector"

        summary = (
            f"Market opportunity analysis for {product_name} ({industry}) could not be completed "
            f"due to a temporary LLM processing error. Please retry your validation request."
        )

        return MarketAnalysisResult(
            summary=summary,
            market_size=[],
            growth_trends=[],
            demand_signals=[],
            customer_segments=[],
            pain_points=[],
            buying_behavior=[],
            market_risks=[],
            attractiveness=None,
            confidence=None,
            analysis_status="processing_error",
            message=f"LLM processing error: {reason[:120]}. Please retry.",
        )

    def analyze(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        search_agent: Any = None,
        tool_call_trace: Optional[List[Dict[str, Any]]] = None,
    ) -> MarketAnalysisResult:
        """
        Executes market opportunity analysis and customer segmentation.
        Uses externalized prompts and exercises autonomous additional search if evidence is thin.
        """
        self._additional_searches_made = 0
        working_sources = list(sources)

        # Autonomy check: if fewer than 2 market size sources, trigger additional search
        market_sources = [s for s in working_sources if s.get("category") == "Market Size & Trends"]
        if len(market_sources) < 2 and search_agent:
            kw = ", ".join(structured_idea.get("keywords", [])[:2])
            ind = structured_idea.get("industry", "")
            pname = structured_idea.get("product_name", "")
            query = f"{pname} {ind} {kw} market size CAGR forecast".strip()
            extra = self.request_additional_search(query, search_agent=search_agent, tool_call_trace=tool_call_trace)
            working_sources.extend(extra)

        context_str = self._build_context_from_sources(working_sources)

        system_prompt = load_prompt("market_analysis_system")
        task_prompt = load_prompt(
            "market_analysis_task",
            idea=idea,
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            keywords=", ".join(structured_idea.get("keywords", [])),
            context_str=context_str,
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.1,
            )

            # Ensure grounding conviction on MarketSizeEstimate items
            if "market_size" in parsed and isinstance(parsed["market_size"], list):
                for est in parsed["market_size"]:
                    if isinstance(est, dict):
                        has_url = bool(est.get("source_url"))
                        has_snip = bool(est.get("evidence_snippet"))
                        est["grounding"] = "strong" if (has_url and has_snip) else "tentative"

            result = MarketAnalysisResult(**parsed)
            result.analysis_status = "completed"
            return result

        except Exception as exc:
            print(f"  [MarketOpportunityAgent] Analysis error: {exc}. Using fallback.")
            return self._fallback_analysis(idea, structured_idea, working_sources, reason=str(exc))
