"""
Evidence-Backed Market White-Space Engine
-----------------------------------------
Core proprietary analytical engine for Milestone 2.
Structurally connects three empirical layers:
  1. CUSTOMER PAIN: Acute unmet customer needs and demand signals from research.
  2. COMPETITOR COVERAGE: What incumbents/alternatives currently offer and where they fall short.
  3. STARTUP CAPABILITY: The distinct technical or operational mechanism of the proposed startup.

Generates a verified "White-Space Map" where:
  Customer Segment -> Pain Point -> Demand Evidence -> Competitor Coverage -> Competitor Weakness -> Startup Capability -> White-Space Opportunity

Calculates evidence strength (High / Medium / Low) and confidence scores grounded in
traceable source citations.
"""

from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    WhiteSpaceAnalysisResult,
    MarketAnalysisResult,
    CompetitorAnalysisResult,
)
from services.llm_service import call_groq_json
from services.text_utils import truncate_at_word_boundary


WHITE_SPACE_SYSTEM_PROMPT = """\
You are an elite startup strategy architect and market opportunity discoverer.
Your mission is to power the "EVIDENCE-BACKED MARKET WHITE-SPACE ENGINE" by mathematically and structurally connecting three evidence vectors:
1. CUSTOMER PAIN (from customer segmentation & demand signals)
2. COMPETITOR COVERAGE (from competitor analysis & incumbent weaknesses)
3. STARTUP CAPABILITY (from the startup pitch & domain extraction)

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION RULES:
1. Every opportunity MUST represent a real structural intersection where customer pain is acute, existing competitors fail to address it, and the startup is uniquely positioned to win.
2. DO NOT write generic platitudes like "The market is growing". Be concrete and precise about the exact gap.
3. Cite actual source URLs and evidence snippets from the provided research evidence in the "demand_evidence" and "evidence" fields.
4. Set "evidence_strength" to "High", "Medium", or "Low" based on the strength and specificity of empirical source backing.
5. Provide a sharp, testable "differentiation_hypothesis" explaining why competitors cannot easily copy this advantage.
6. Identify 2 to 4 high-conviction white-space opportunities.

Respond strictly in valid JSON matching the required schema.
"""


class WhiteSpaceEngine:
    """Analytical engine discovering evidence-backed market gaps through multi-layer triangulation."""

    def __init__(self):
        pass

    def _build_evidence_digest(self, sources: List[Dict[str, Any]]) -> str:
        """Extracts high-signal demand and competitor snippets."""
        if not sources:
            return "No verified research sources available."

        # Prioritize top 3 demand and top 3 competitor sources
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
        """
        Deterministic degraded result when LLM synthesis fails.
        Returns zero fabricated opportunities and explicitly flags the processing error.
        """
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
        """
        Synthesizes evidence-backed white space opportunities by correlating customer pain,
        competitor weaknesses, and startup capabilities.
        """
        evidence_digest = self._build_evidence_digest(sources)

        # Structure context from market and competitor agents
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

        prompt = f"""\
STARTUP IDEA:
Pitch: {idea}
Product Name: {structured_idea.get('product_name', 'N/A')}
Industry: {structured_idea.get('industry', 'N/A')}
Target Audience: {structured_idea.get('target_audience', 'N/A')}
Core Problem: {structured_idea.get('core_problem', 'N/A')}

MARKET & CUSTOMER CONTEXT:
{market_context}

COMPETITOR LANDSCAPE CONTEXT:
{comp_context}

VERIFIED SEARCH SOURCES (Ground Truth Evidence):
{evidence_digest}

TASK:
Identify 2 to 4 evidence-backed Market White-Space Opportunities.
For each opportunity, trace the structural chain:
Customer Segment -> Customer Pain -> Demand Evidence -> Competitor Coverage -> Competitor Gap -> Startup Fit -> Differentiation Hypothesis -> Evidence Strength & Sources.

JSON format must match this structure:
{{
  "opportunities": [
    {{
      "opportunity_name": "Actionable, distinctive title",
      "segment": "Underserved customer segment",
      "pain_point": "Specific acute customer pain point",
      "demand_evidence": ["Empirical quote or signal 1", "Empirical signal 2"],
      "competitor_coverage": ["What existing competitors currently do or lack"],
      "gap": "Precise structural market gap",
      "startup_fit": "Why this startup idea uniquely solves this gap",
      "differentiation_hypothesis": "Strategic thesis for winning and defending this space",
      "evidence_strength": "High" | "Medium" | "Low",
      "confidence": 0.88,
      "potential_risk": "Specific market or execution risk",
      "evidence": ["URL1 from research sources", "URL2"]
    }}
  ]
}}
"""

        try:
            parsed = call_groq_json(
                prompt=prompt,
                system_prompt=WHITE_SPACE_SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.1,
            )
            result = WhiteSpaceAnalysisResult(**parsed)
            result.analysis_status = "completed"
            return result
        except Exception as exc:
            print(f"  [WhiteSpaceEngine] LLM synthesis failed ({exc}), triggering fallback.")
            return self._fallback_opportunities(
                idea=idea,
                structured_idea=structured_idea,
                sources=sources,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
                reason=str(exc),
            )
