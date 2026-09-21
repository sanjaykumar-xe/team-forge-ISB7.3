"""
MVP Feature Recommendation Agent (Milestone 3)
------------------------------------------------
Prioritizes core features for a minimum viable product based on upstream
market, competitor, white-space, and SWOT analysis. Every recommendation
must cite its justifying upstream evidence.
"""

from typing import Dict, Any, Optional
from schemas.validation_schemas import (
    MVPRecommendation, MarketAnalysisResult, CompetitorAnalysisResult,
    WhiteSpaceAnalysisResult, SWOTAnalysisResult,
)
from services.llm_service import call_groq_json
from prompts.loader import load_prompt


class MVPAgent:
    """Agent that recommends a focused MVP with justified feature prioritization."""

    def _build_pain_points(self, market: Optional[MarketAnalysisResult]) -> str:
        if not market or not market.pain_points:
            return "No specific pain points identified."
        return "\n".join([f"- {p}" for p in market.pain_points[:6]])

    def _build_competitor_gaps(self, comp: Optional[CompetitorAnalysisResult]) -> str:
        if not comp:
            return "No competitor analysis available."
        parts = []
        for c in comp.competitors[:4]:
            parts.append(f"- {c.name}: Weaknesses = {', '.join(c.weaknesses[:2])}")
        if comp.market_gaps:
            parts.append(f"Market Gaps: {'; '.join(comp.market_gaps[:3])}")
        return "\n".join(parts) if parts else "No competitor gaps identified."

    def _build_whitespace_summary(self, ws: Optional[WhiteSpaceAnalysisResult]) -> str:
        if not ws or not ws.opportunities:
            return "No white-space opportunities."
        return "\n".join([f"- {o.opportunity_name}: {o.gap}" for o in ws.opportunities[:4]])

    def _build_swot_summary(self, swot: Optional[SWOTAnalysisResult]) -> str:
        if not swot:
            return "No SWOT analysis available."
        parts = []
        if swot.strengths:
            parts.append("Strengths: " + "; ".join([s.get("item", s) if isinstance(s, dict) else str(s) for s in swot.strengths[:3]]))
        if swot.weaknesses:
            parts.append("Weaknesses: " + "; ".join([w.get("item", w) if isinstance(w, dict) else str(w) for w in swot.weaknesses[:3]]))
        if swot.opportunities:
            parts.append("Opportunities: " + "; ".join([o.get("item", o) if isinstance(o, dict) else str(o) for o in swot.opportunities[:3]]))
        if swot.threats:
            parts.append("Threats: " + "; ".join([t.get("item", t) if isinstance(t, dict) else str(t) for t in swot.threats[:3]]))
        return "\n".join(parts) if parts else "No SWOT data."

    def _fallback_recommendation(self, reason: str) -> MVPRecommendation:
        return MVPRecommendation(
            mvp_name="N/A",
            mvp_thesis=f"MVP recommendation could not be completed: {reason[:120]}.",
            core_features=[],
            nice_to_haves=[],
            technical_considerations=[],
            resource_estimate=None,
            success_metrics=[],
            analysis_status="processing_error",
            message=f"Processing error: {reason[:120]}",
        )

    def recommend(
        self,
        structured_idea: Dict[str, Any],
        market_analysis: Optional[MarketAnalysisResult] = None,
        competitor_analysis: Optional[CompetitorAnalysisResult] = None,
        white_space_analysis: Optional[WhiteSpaceAnalysisResult] = None,
        swot_analysis: Optional[SWOTAnalysisResult] = None,
    ) -> MVPRecommendation:
        system_prompt = load_prompt("mvp_system")
        task_prompt = load_prompt("mvp_task",
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            market_summary=market_analysis.summary if market_analysis else "No market data.",
            pain_points=self._build_pain_points(market_analysis),
            competitor_gaps=self._build_competitor_gaps(competitor_analysis),
            whitespace_summary=self._build_whitespace_summary(white_space_analysis),
            swot_summary=self._build_swot_summary(swot_analysis),
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=3500,
                temperature=0.1,
            )
            result = MVPRecommendation(**parsed)
            result.analysis_status = "completed"
            return result
        except Exception as exc:
            print(f"  [MVPAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_recommendation(reason=str(exc))
