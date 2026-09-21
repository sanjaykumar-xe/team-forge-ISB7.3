"""
Evidence-Backed Market White-Space Engine (Milestone 3)
-------------------------------------------------------
Externalized prompts, permits honest 'no genuine opportunity' output.
"""

from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    WhiteSpaceAnalysisResult,
    MarketAnalysisResult,
    CompetitorAnalysisResult,
)
from services.llm_service import call_groq_json
from services.text_utils import truncate_at_word_boundary
from prompts.loader import load_prompt


class WhiteSpaceEngine:
    """Analytical engine discovering evidence-backed market gaps through multi-layer triangulation."""

    def __init__(self):
        pass

    def _build_evidence_digest(self, sources: List[Dict[str, Any]]) -> str:
        if not sources:
            return "No verified research sources available."

        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:3]
        comp_items = [s for s in sources if s.get("category") == "Competitors"][:3]
        selected = demand_items + comp_items

        if len(selected) < 4:
            selected = sources[:6]

        lines = []
        for i, s in enumerate(selected[:6], 1):
            category = s.get("category", "General")
            title = truncate_at_word_boundary(s.get("title", "Untitled"), max_length=90)
            url = s.get("url", "")
            raw_snip = s.get("snippet", "") or s.get("content", "")
            snippet = truncate_at_word_boundary(raw_snip, max_length=240)
            lines.append(f"[{i}] [{category}] {title}\nURL: {url}\nExcerpt: {snippet}\n")

        return "\n".join(lines)

    def _fallback_opportunities(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        competitor_analysis: Optional[CompetitorAnalysisResult] = None,
        reason: str = "LLM unavailable",
    ) -> WhiteSpaceAnalysisResult:
        return WhiteSpaceAnalysisResult(
            opportunities=[],
            analysis_status="processing_error",
            message=f"White-space opportunity synthesis could not be completed due to a temporary processing error: {reason[:100]}. Please retry your validation request.",
        )

    def discover(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        competitor_analysis: Optional[CompetitorAnalysisResult] = None,
    ) -> WhiteSpaceAnalysisResult:
        evidence_digest = self._build_evidence_digest(sources)

        market_context = "No previous market analysis."
        if market_analysis:
            segments_info = []
            for seg in market_analysis.customer_segments:
                segments_info.append(f"- Segment: {seg.segment_name} | Pain: {', '.join(seg.pain_points[:2])} | Behavior: {seg.buying_behavior}")
            market_context = f"Market Summary: {market_analysis.summary}\nCustomer Segments:\n" + "\n".join(segments_info)

        comp_context = "No previous competitor analysis."
        if competitor_analysis:
            comps_info = []
            for comp in competitor_analysis.competitors:
                comps_info.append(f"- Competitor: {comp.name} ({comp.classification}) | Weaknesses: {', '.join(comp.weaknesses[:2])} | Complaints: {', '.join(comp.customer_complaints[:2])}")
            gaps_info = "\nIdentified Market Gaps: " + "; ".join(competitor_analysis.market_gaps[:3])
            comp_context = "Competitor Landscape:\n" + "\n".join(comps_info) + gaps_info

        system_prompt = load_prompt("white_space_system")
        task_prompt = load_prompt(
            "white_space_task",
            idea=idea,
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            market_context=market_context,
            comp_context=comp_context,
            evidence_digest=evidence_digest,
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.1,
            )

            # Pre-validation normalization for LLM variations
            for opp in parsed.get("opportunities", []):
                if isinstance(opp, dict) and "customer_segment" not in opp:
                    opp["customer_segment"] = structured_idea.get("target_audience", "Target Market")

            result = WhiteSpaceAnalysisResult(**parsed)
            result.analysis_status = "completed"
            return result

        except Exception as exc:
            print(f"  [WhiteSpaceEngine] Error: {exc}. Using fallback.")
            return self._fallback_opportunities(idea, structured_idea, sources, market_analysis, competitor_analysis, reason=str(exc))
