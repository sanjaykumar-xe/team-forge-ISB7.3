"""
SWOT & Risk Analysis Agent (Milestone 3)
-----------------------------------------
Synthesizes upstream analysis outputs into a judgment-driven SWOT matrix
and strategic risk assessment. Only elevates findings with genuine evidence backing.
"""

from typing import Dict, Any, List, Optional
from schemas.validation_schemas import SWOTAnalysisResult, MarketAnalysisResult, CompetitorAnalysisResult, WhiteSpaceAnalysisResult
from services.llm_service import call_groq_json
from services.text_utils import truncate_at_word_boundary
from prompts.loader import load_prompt


class SWOTAgent:
    """Agent that synthesizes a judgment-driven SWOT analysis from upstream pipeline outputs."""

    def _build_market_summary(self, market: Optional[MarketAnalysisResult]) -> str:
        if not market:
            return "No market analysis available."
        parts = [f"Summary: {market.summary}"]
        if market.market_size:
            sizes = "; ".join([f"{s.figure} ({s.market_type})" for s in market.market_size[:3]])
            parts.append(f"Market Size: {sizes}")
        if market.growth_trends:
            parts.append(f"Growth Trends: {'; '.join(market.growth_trends[:3])}")
        if market.demand_signals:
            parts.append(f"Demand Signals: {'; '.join(market.demand_signals[:3])}")
        if market.market_risks:
            parts.append(f"Market Risks: {'; '.join(market.market_risks[:3])}")
        if market.attractiveness:
            a = market.attractiveness
            parts.append(f"Attractiveness: Demand={a.demand_strength}, Growth={a.growth_strength}, Urgency={a.customer_urgency}, Accessibility={a.market_accessibility}")
        return "\n".join(parts)

    def _build_segments_summary(self, market: Optional[MarketAnalysisResult]) -> str:
        if not market or not market.customer_segments:
            return "No customer segments identified."
        lines = []
        for seg in market.customer_segments[:3]:
            lines.append(f"- {seg.segment_name}: {seg.who_they_are} | Pains: {', '.join(seg.pain_points[:3])}")
        return "\n".join(lines)

    def _build_competitor_summary(self, comp: Optional[CompetitorAnalysisResult]) -> str:
        if not comp:
            return "No competitor analysis available."
        parts = []
        for c in comp.competitors[:5]:
            parts.append(f"- {c.name} ({c.classification}): {c.core_offering} | Weaknesses: {', '.join(c.weaknesses[:2])}")
        if comp.market_gaps:
            parts.append(f"Market Gaps: {'; '.join(comp.market_gaps[:3])}")
        return "\n".join(parts) if parts else "No competitors identified."

    def _build_whitespace_summary(self, ws: Optional[WhiteSpaceAnalysisResult]) -> str:
        if not ws or not ws.opportunities:
            return "No white-space opportunities identified."
        lines = []
        for opp in ws.opportunities[:4]:
            lines.append(f"- {opp.opportunity_name} (Evidence: {opp.evidence_strength}, Confidence: {opp.confidence}): {opp.gap}")
        return "\n".join(lines)

    def _fallback_analysis(self, reason: str) -> SWOTAnalysisResult:
        return SWOTAnalysisResult(
            strengths=[],
            weaknesses=[],
            opportunities=[],
            threats=[],
            risk_assessment=[],
            strategic_recommendation=f"SWOT analysis could not be completed: {reason[:120]}. Please retry.",
            analysis_status="processing_error",
            message=f"Processing error: {reason[:120]}",
        )

    def analyze(
        self,
        structured_idea: Dict[str, Any],
        market_analysis: Optional[MarketAnalysisResult] = None,
        competitor_analysis: Optional[CompetitorAnalysisResult] = None,
        white_space_analysis: Optional[WhiteSpaceAnalysisResult] = None,
    ) -> SWOTAnalysisResult:
        system_prompt = load_prompt("swot_system")
        task_prompt = load_prompt("swot_task",
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            market_summary=self._build_market_summary(market_analysis),
            segments_summary=self._build_segments_summary(market_analysis),
            competitor_summary=self._build_competitor_summary(competitor_analysis),
            whitespace_summary=self._build_whitespace_summary(white_space_analysis),
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=3500,
                temperature=0.1,
            )
            result = SWOTAnalysisResult(**parsed)
            result.analysis_status = "completed"
            return result
        except Exception as exc:
            print(f"  [SWOTAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_analysis(reason=str(exc))
