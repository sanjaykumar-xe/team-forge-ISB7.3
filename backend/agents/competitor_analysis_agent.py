"""
Competitor Discovery & Comparison Agent (Milestone 3)
-----------------------------------------------------
Externalized prompts, autonomous additional search capability,
honest list length without forced padding.
"""

from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    CompetitorAnalysisResult,
    CompetitorRecord,
    ComparisonMatrixRow,
    MarketAnalysisResult,
)
from services.llm_service import call_groq_json
from services.text_utils import truncate_at_word_boundary
from prompts.loader import load_prompt


class CompetitorAnalysisAgent:
    """Agent responsible for competitive landscaping, comparison matrix generation, and gap identification."""

    def __init__(self):
        self._additional_searches_made = 0

    def _build_sources_summary(self, sources: List[Dict[str, Any]]) -> str:
        if not sources:
            return "No verified web sources available."

        comp_items = [s for s in sources if s.get("category") == "Competitors"][:14]
        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:4]
        selected = comp_items + demand_items

        if len(selected) < 4:
            selected = sources[:14]

        lines = []
        for i, s in enumerate(selected, 1):
            category = s.get("category", "General")
            title = truncate_at_word_boundary(s.get("title", "Untitled"), max_length=120)
            url = s.get("url", "")
            raw_snip = s.get("snippet", "") or s.get("content", "")
            # Preserve generous excerpt window (up to 1,500 chars) so specific product names, 
            # app listings, and competitor matrices are visible to the LLM
            snippet = truncate_at_word_boundary(raw_snip, max_length=1500)
            lines.append(f"[{i}] [{category}] {title}\nURL: {url}\nExcerpt: {snippet}\n")

        return "\n".join(lines)

    def request_additional_search(
        self,
        query: str,
        search_agent: Any = None,
        tool_call_trace: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Autonomous tool: requests an additional search if competitor sources are sparse.
        Budget-limited to at most 1 call per run.
        """
        if self._additional_searches_made >= 1:
            print("  [CompetitorAnalysisAgent] Additional search budget reached (1 call max).")
            return []

        self._additional_searches_made += 1
        print(f"  [CompetitorAnalysisAgent Autonomous Search] Query: '{query}'")

        if tool_call_trace is not None:
            tool_call_trace.append({
                "tool": "request_additional_search",
                "caller": "CompetitorAnalysisAgent",
                "category": "Competitors",
                "query": query,
            })

        if search_agent and hasattr(search_agent, "_execute_single_category_search"):
            try:
                batch = search_agent._execute_single_category_search("Competitors", query, max_results=4)
                results = batch.get("response", {}).get("results", [])
                new_sources = []
                for r in results:
                    new_sources.append({
                        "url": r.get("url", ""),
                        "title": r.get("title", ""),
                        "snippet": r.get("content", "") or r.get("snippet", ""),
                        "category": "Competitors",
                    })
                return new_sources
            except Exception as exc:
                print(f"  [CompetitorAnalysisAgent] Additional search failed: {exc}")
                return []
        return []

    def _fallback_competitor_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        reason: str = "LLM unavailable",
    ) -> CompetitorAnalysisResult:
        product_name = structured_idea.get("product_name") or "Startup"
        industry = structured_idea.get("industry") or "the sector"

        summary = (
            f"Competitor discovery and comparison for {product_name} ({industry}) could not be completed "
            f"due to a temporary LLM processing error. Please retry your validation request."
        )

        return CompetitorAnalysisResult(
            summary=summary,
            competitors=[],
            comparison_matrix=[],
            market_gaps=[],
            pricing_gaps=[],
            unmet_customer_needs=[],
            confidence=None,
            analysis_status="processing_error",
            message=f"LLM processing error: {reason[:120]}. Please retry.",
        )

    def analyze(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        search_agent: Any = None,
        tool_call_trace: Optional[List[Dict[str, Any]]] = None,
    ) -> CompetitorAnalysisResult:
        self._additional_searches_made = 0
        working_sources = list(sources)

        # Autonomy check: if fewer than 2 competitor sources, trigger additional search
        comp_sources = [s for s in working_sources if s.get("category") == "Competitors"]
        if len(comp_sources) < 2 and search_agent:
            pname = structured_idea.get("product_name", "")
            ind = structured_idea.get("industry", "")
            cp = structured_idea.get("core_problem", "")
            query = f"{pname} {ind} competitors alternatives {cp[:30]}".strip()
            extra = self.request_additional_search(query, search_agent=search_agent, tool_call_trace=tool_call_trace)
            working_sources.extend(extra)

        sources_str = self._build_sources_summary(working_sources)

        market_summary = ""
        if market_analysis and market_analysis.summary:
            market_summary = f"Upstream Market Analysis Summary: {market_analysis.summary}"

        system_prompt = load_prompt("competitor_analysis_system")
        task_prompt = load_prompt(
            "competitor_analysis_task",
            idea=idea,
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            keywords=", ".join(structured_idea.get("keywords", [])),
            market_summary=market_summary,
            sources_str=sources_str,
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.1,
            )

            # Pre-validation normalization for LLM variations
            if "summary" not in parsed or not parsed["summary"]:
                parsed["summary"] = f"Identified {len(parsed.get('competitors', []))} competitors and structural market gaps."
            for c in parsed.get("competitors", []):
                if isinstance(c, dict) and "target_customers" not in c:
                    c["target_customers"] = structured_idea.get("target_audience", "Target market")
            for row in parsed.get("comparison_matrix", []):
                if isinstance(row, dict) and "dimension" not in row and "feature_or_dimension" in row:
                    row["dimension"] = row["feature_or_dimension"]

            result = CompetitorAnalysisResult(**parsed)
            result.analysis_status = "completed"
            return result

        except Exception as exc:
            print(f"  [CompetitorAnalysisAgent] Analysis error: {exc}. Using fallback.")
            return self._fallback_competitor_analysis(idea, structured_idea, working_sources, market_analysis, reason=str(exc))
