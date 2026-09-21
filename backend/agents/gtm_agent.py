"""
Go-To-Market Strategy Agent (Milestone 3)
-------------------------------------------
Produces an actionable, idea-specific go-to-market strategy based on all
upstream analysis. Explicitly avoids generic startup advice — channels and
positioning must be justified against this specific idea's landscape.
"""

from typing import Dict, Any, Optional
from schemas.validation_schemas import (
    GTMStrategy, MarketAnalysisResult, CompetitorAnalysisResult,
    WhiteSpaceAnalysisResult, SWOTAnalysisResult, MVPRecommendation,
)
from services.llm_service import call_groq_json
from prompts.loader import load_prompt


class GTMAgent:
    """Agent that produces idea-specific go-to-market strategies."""

    def _build_segments_summary(self, market: Optional[MarketAnalysisResult]) -> str:
        if not market or not market.customer_segments:
            return "No customer segments identified."
        return "\n".join([f"- {s.segment_name}: {s.who_they_are} | Behavior: {s.buying_behavior}" for s in market.customer_segments[:3]])

    def _build_competitor_summary(self, comp: Optional[CompetitorAnalysisResult]) -> str:
        if not comp or not comp.competitors:
            return "No competitors identified."
        return "\n".join([f"- {c.name}: {c.positioning} | Pricing: {c.pricing}" for c in comp.competitors[:4]])

    def _build_whitespace_summary(self, ws: Optional[WhiteSpaceAnalysisResult]) -> str:
        if not ws or not ws.opportunities:
            return "No white-space opportunities."
        return "\n".join([f"- {o.opportunity_name}: {o.differentiation_hypothesis}" for o in ws.opportunities[:3]])

    def _build_swot_summary(self, swot: Optional[SWOTAnalysisResult]) -> str:
        if not swot:
            return "No SWOT data."
        return swot.strategic_recommendation or "No strategic recommendation."

    def _build_mvp_summary(self, mvp: Optional[MVPRecommendation]) -> str:
        if not mvp or not mvp.core_features:
            return "No MVP recommendations."
        features = ", ".join([f.get("feature", str(f)) if isinstance(f, dict) else str(f) for f in mvp.core_features[:5]])
        return f"MVP: {mvp.mvp_name or 'N/A'} | Core Features: {features}"

    def _fallback_strategy(self, reason: str) -> GTMStrategy:
        return GTMStrategy(
            positioning_statement=f"GTM strategy could not be completed: {reason[:120]}.",
            target_channels=[],
            acquisition_strategy=None,
            pricing_approach=None,
            launch_phases=[],
            key_metrics=[],
            competitive_positioning="N/A",
            analysis_status="processing_error",
            message=f"Processing error: {reason[:120]}",
        )

    def strategize(
        self,
        structured_idea: Dict[str, Any],
        market_analysis: Optional[MarketAnalysisResult] = None,
        competitor_analysis: Optional[CompetitorAnalysisResult] = None,
        white_space_analysis: Optional[WhiteSpaceAnalysisResult] = None,
        swot_analysis: Optional[SWOTAnalysisResult] = None,
        mvp_recommendation: Optional[MVPRecommendation] = None,
    ) -> GTMStrategy:
        system_prompt = load_prompt("gtm_system")
        task_prompt = load_prompt("gtm_task",
            product_name=structured_idea.get("product_name", "N/A"),
            industry=structured_idea.get("industry", "N/A"),
            target_audience=structured_idea.get("target_audience", "N/A"),
            core_problem=structured_idea.get("core_problem", "N/A"),
            market_summary=market_analysis.summary if market_analysis else "No market data.",
            segments_summary=self._build_segments_summary(market_analysis),
            competitor_summary=self._build_competitor_summary(competitor_analysis),
            whitespace_summary=self._build_whitespace_summary(white_space_analysis),
            swot_summary=self._build_swot_summary(swot_analysis),
            mvp_summary=self._build_mvp_summary(mvp_recommendation),
        )

        try:
            parsed = call_groq_json(
                prompt=task_prompt,
                system_prompt=system_prompt,
                max_tokens=3500,
                temperature=0.1,
            )
            result = GTMStrategy(**parsed)
            result.analysis_status = "completed"
            return result
        except Exception as exc:
            print(f"  [GTMAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_strategy(reason=str(exc))
