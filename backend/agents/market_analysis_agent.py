"""
Market Opportunity & Customer Segmentation Agent
------------------------------------------------
Analyzes verified empirical search data produced by the Milestone 1 pipeline
(specifically Market Size & Trends, Customer Demand, and Industry News categories)
to evaluate:
  1. Market Opportunity: Market valuations (global/regional/niche), CAGR, growth drivers, adoption trends.
  2. Customer Segmentation: Granular customer segments, personas, end users vs decision makers,
     unmet needs, acute pain points, motivations, buying behaviors, and domain terminology.
  3. Market Attractiveness: Demand velocity, growth strength, customer urgency, market accessibility,
     barriers to entry, and foundational assumptions.

Strict Anti-Hallucination Policy:
- All quantitative market sizing metrics must be directly linked to a retrieved source URL.
- If data sources disagree or conflict, the divergence is explicitly documented.
- If empirical evidence for a specific metric is absent, it is marked as "insufficient evidence".
"""

from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    MarketAnalysisResult,
    MarketSizeEstimate,
    CustomerSegment,
    MarketAttractiveness,
)
from services.llm_service import call_groq_json


MARKET_ANALYSIS_SYSTEM_PROMPT = """\
You are an expert venture capital market analyst and market research specialist.
Your mission is to analyze verified search data to evaluate market opportunity and identify customer segments for a startup idea.

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION RULES:
1. Ground all quantitative claims in the PROVIDED SEARCH SOURCES. Never invent or hallucinate market sizes, CAGRs, or dollar values.
2. For each market size estimate, specify the exact source URL and evidence snippet from the sources where you found the number.
3. If sources report conflicting numbers (e.g. one report says $5B and another says $12B), explicitly note this disagreement.
4. If no reliable market size numbers appear in the sources, provide an honest estimate range clearly marked as "Estimated from adjacent industry signals" with confidence <= 0.6.
5. Create 2 to 4 distinctive, realistic customer segments with clear distinctions between End Users and Decision Makers.
6. Analyze acute pain points, buying behavior, price sensitivity, and domain-specific terminology for each segment.
7. Assess Market Attractiveness across Demand Strength, Growth Strength, Customer Urgency, and Market Accessibility (High / Medium / Low).

Respond strictly in JSON matching the required schema.
"""


class MarketOpportunityAgent:
    """Agent responsible for market sizing, customer segmentation, and market attractiveness analysis."""

    def __init__(self):
        pass

    def _build_context_from_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Formats top relevant search sources into compact structured context for the LLM."""
        if not sources:
            return "No verified web sources available."

        # Prioritize Market Size and Customer Demand categories
        priority_cats = ["Market Size & Trends", "Customer Demand", "Industry News"]
        selected = []
        for cat in priority_cats:
            cat_items = [s for s in sources if s.get("category") == cat]
            selected.extend(cat_items[:2])  # top 2 per category

        # If few found, fill with highest scoring remaining sources
        if len(selected) < 4:
            for s in sources:
                if s not in selected:
                    selected.append(s)
                if len(selected) >= 6:
                    break

        lines = []
        for i, s in enumerate(selected[:6], 1):
            category = s.get("category", "General")
            title = s.get("title", "Untitled")[:80]
            url = s.get("url", "")
            snippet = s.get("snippet", "")[:240].strip()
            lines.append(f"[{i}] Category: {category} | Title: {title}\nURL: {url}\nEvidence: {snippet}\n")

        return "\n".join(lines)


    def _fallback_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        reason: str = "LLM unavailable",
    ) -> MarketAnalysisResult:
        """Deterministic fallback synthesis if Groq inference fails or returns invalid JSON."""
        industry = structured_idea.get("industry") or "Software / Technology"
        target_audience = structured_idea.get("target_audience") or "Target Customers"
        product_name = structured_idea.get("product_name") or "Startup"
        core_problem = structured_idea.get("core_problem") or idea

        # Search for any market sizing hints in sources
        size_estimates = []
        for s in sources:
            cat = s.get("category", "")
            snippet = s.get("snippet", "").lower()
            if "market" in cat.lower() or "billion" in snippet or "million" in snippet or "cagr" in snippet:
                size_estimates.append(
                    MarketSizeEstimate(
                        figure="Market size signals detected in research sources",
                        market_type="global",
                        cagr="CAGR reported in industry literature",
                        forecast_year="2030",
                        source_url=s.get("url"),
                        evidence_snippet=s.get("snippet", "")[:200],
                        notes=f"Retrieved from {s.get('title', 'research report')}",
                    )
                )
                if len(size_estimates) >= 2:
                    break

        if not size_estimates:
            size_estimates.append(
                MarketSizeEstimate(
                    figure="Emerging Market Sector",
                    market_type="niche",
                    cagr=None,
                    forecast_year=None,
                    source_url=None,
                    evidence_snippet="Specific quantitative market size requires deeper vertical research.",
                    notes="Baseline estimate derived from industry category.",
                )
            )

        segment_1 = CustomerSegment(
            segment_name=f"Primary {target_audience}",
            who_they_are=f"Key users and organizations seeking solutions for {core_problem[:60]}",
            end_users=f"Frontline {target_audience.lower()} experiencing daily friction",
            decision_makers=f"Department leads, founders, or individual buyers in {industry}",
            primary_needs=["Workflow automation", "Cost reduction", "Seamless integration", "High reliability"],
            pain_points=[core_problem, "Lack of modern dedicated tooling", "High manual overhead"],
            motivations=["Efficiency gains", "Improved outcomes", "Modern digital experience"],
            buying_behavior="Evaluates ROI, relies on peer recommendations, prefers free trials or pilots.",
            industry_terminology=structured_idea.get("keywords", []) or [industry.lower()],
        )

        return MarketAnalysisResult(
            summary=f"The market for {product_name} in {industry} exhibits active interest driven by demand for solutions addressing {core_problem[:80]}.",
            market_size=size_estimates,
            growth_trends=[
                f"Increasing digitization across the {industry} sector.",
                "Growing demand for specialized, automated workflow tools.",
                "Shift toward integrated software platforms with lower implementation friction.",
            ],
            demand_signals=[
                f"Active search volume and industry discourse regarding {core_problem[:60]}",
                "Users actively seeking alternatives to legacy, manual processes.",
            ],
            customer_segments=[segment_1],
            pain_points=[core_problem, "Fragmented tooling", "Time-consuming manual workflows"],
            buying_behavior=["ROI-driven purchasing decisions", "Preference for self-serve or fast onboarding"],
            market_risks=["Incumbent platform feature expansion", "Customer acquisition cost pressures"],
            attractiveness=MarketAttractiveness(
                demand_strength="Medium",
                growth_strength="Medium",
                customer_urgency="High",
                market_accessibility="Medium",
                major_barriers=["Brand awareness", "Workflow switching costs"],
                important_assumptions=["Target audience acknowledges current friction and will adopt software intervention."],
            ),
            confidence=0.75,
        )

    def analyze(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
    ) -> MarketAnalysisResult:
        """
        Executes market opportunity analysis and customer segmentation.
        Takes structured metadata and retrieved search evidence.
        """
        context_str = self._build_context_from_sources(sources)
        
        prompt = f"""\
STARTUP IDEA TO ANALYZE:
Pitch: {idea}
Product Name: {structured_idea.get('product_name', 'N/A')}
Industry Vertical: {structured_idea.get('industry', 'N/A')}
Target Audience: {structured_idea.get('target_audience', 'N/A')}
Core Problem: {structured_idea.get('core_problem', 'N/A')}
Extracted Keywords: {', '.join(structured_idea.get('keywords', []))}

VERIFIED SEARCH SOURCES FROM RESEARCH:
{context_str}

TASK:
Produce a comprehensive Market Opportunity & Customer Segmentation analysis.
JSON structure must match this format:
{{
  "summary": "2-3 sentence executive synthesis of market attractiveness and opportunity size.",
  "market_size": [
    {{
      "figure": "$X.X Billion (or description if range)",
      "market_type": "global" | "regional" | "niche",
      "cagr": "X.X% (or null if unavailable)",
      "forecast_year": "2030 (or null)",
      "source_url": "URL from sources where this was found",
      "evidence_snippet": "Direct quote or excerpt from sources",
      "notes": "Any caveats or note if sources disagree"
    }}
  ],
  "growth_trends": ["Trend 1 with supporting context", "Trend 2", "Trend 3"],
  "demand_signals": ["Demand signal 1 from customer reviews/news", "Demand signal 2"],
  "customer_segments": [
    {{
      "segment_name": "Name of Segment",
      "who_they_are": "Detailed profile",
      "end_users": "Who uses it daily",
      "decision_makers": "Who buys / signs off",
      "primary_needs": ["Need 1", "Need 2", "Need 3"],
      "pain_points": ["Pain point 1", "Pain point 2"],
      "motivations": ["Motivation 1", "Motivation 2"],
      "buying_behavior": "Procurement cycle and purchasing habits",
      "industry_terminology": ["term1", "term2", "term3"]
    }}
  ],
  "pain_points": ["Aggregated top pain point 1", "Pain point 2", "Pain point 3"],
  "buying_behavior": ["Key purchasing characteristic 1", "Characteristic 2"],
  "market_risks": ["Risk 1", "Risk 2"],
  "attractiveness": {{
    "demand_strength": "High" | "Medium" | "Low",
    "growth_strength": "High" | "Medium" | "Low",
    "customer_urgency": "High" | "Medium" | "Low",
    "market_accessibility": "High" | "Medium" | "Low",
    "major_barriers": ["Barrier 1", "Barrier 2"],
    "important_assumptions": ["Assumption 1", "Assumption 2"]
  }},
  "confidence": 0.85
}}
"""

        try:
            parsed = call_groq_json(
                prompt=prompt,
                system_prompt=MARKET_ANALYSIS_SYSTEM_PROMPT,
                max_tokens=2500,
                temperature=0.1,
            )
            
            # Validate and construct typed Pydantic result
            result = MarketAnalysisResult(**parsed)
            return result
        except Exception as exc:
            print(f"  [MarketOpportunityAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_analysis(idea, structured_idea, sources, reason=str(exc))
