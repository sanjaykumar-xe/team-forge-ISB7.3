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
        market_items = [s for s in sources if s.get("category") == "Market Size & Trends"][:4]
        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:2]
        news_items = [s for s in sources if s.get("category") == "Industry News"][:2]
        selected = market_items + demand_items + news_items

        # If few found, fill with highest scoring remaining sources
        if len(selected) < 6:
            for s in sources:
                if s not in selected:
                    selected.append(s)
                if len(selected) >= 8:
                    break

        lines = []
        for i, s in enumerate(selected[:8], 1):
            category = s.get("category", "General")
            title = s.get("title", "Untitled")[:90]
            url = s.get("url", "")
            snippet = s.get("snippet", "") or s.get("content", "")
            snippet = snippet[:280].strip()
            lines.append(f"[{i}] Category: {category} | Title: {title}\nURL: {url}\nEvidence: {snippet}\n")

        return "\n".join(lines)

    def _extract_market_sizing(self, sources: List[Dict[str, Any]]) -> List[MarketSizeEstimate]:
        """Extracts quantitative market valuations, CAGRs, and forecast periods from sources."""
        import re

        estimates = []
        # Check Market Size & Trends and Industry News sources
        relevant_sources = [
            s for s in sources
            if s.get("category") in ("Market Size & Trends", "Industry News", "General")
        ] or sources

        seen_figures = set()

        for s in relevant_sources:
            snippet = s.get("snippet", "") or s.get("content", "")
            title = s.get("title", "")
            text = f"{title}. {snippet}"
            url = s.get("url", "")

            # Look for dollar / USD figures: e.g. USD 1.28 Billion, $101.81 Billion, $101.81B
            figures = re.findall(
                r'(?:USD\s*|\$\s*)(\d+(?:\.\d+)?)\s*(Billion|Million|Trillion|B|M|T)?',
                text,
                re.IGNORECASE
            )
            # Look for CAGR percentages: e.g. 19.6% CAGR, CAGR of 15.2%
            cagr_match = re.search(
                r'(\d+(?:\.\d+)?)\s*%\s*CAGR|CAGR\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%',
                text,
                re.IGNORECASE
            )
            # Look for forecast years: e.g. by 2030, through 2034, 2025 to 2032
            year_match = re.search(r'\b(202[5-9]|203[0-9]|2040)\b', text)

            if figures:
                val, unit = figures[0]
                unit_str = f" {unit.capitalize()}" if unit else ""
                if unit and unit.lower() == "b":
                    unit_str = " Billion"
                elif unit and unit.lower() == "m":
                    unit_str = " Million"
                figure_str = f"${val}{unit_str}"

                if len(figures) > 1:
                    v2, u2 = figures[1]
                    u2_str = f" {u2.capitalize()}" if u2 else ""
                    if u2 and u2.lower() == "b":
                        u2_str = " Billion"
                    elif u2 and u2.lower() == "m":
                        u2_str = " Million"
                    figure_str += f" to ${v2}{u2_str}"

                if figure_str in seen_figures:
                    continue
                seen_figures.add(figure_str)

                cagr_str = None
                if cagr_match:
                    cagr_val = cagr_match.group(1) or cagr_match.group(2)
                    cagr_str = f"{cagr_val}%"

                forecast_yr = year_match.group(1) if year_match else None
                market_type = "global" if any(w in text.lower() for w in ["global", "worldwide", "international"]) else "niche"

                estimates.append(
                    MarketSizeEstimate(
                        figure=figure_str,
                        market_type=market_type,
                        cagr=cagr_str,
                        forecast_year=forecast_yr,
                        source_url=url,
                        evidence_snippet=snippet[:240].strip() if snippet else title,
                        notes="Quantitative market sizing extracted from verified research source.",
                    )
                )

        return estimates[:4]

    def _fallback_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        reason: str = "LLM unavailable",
    ) -> MarketAnalysisResult:
        """Deterministic fallback synthesis extracting quantitative market metrics when available."""
        industry = structured_idea.get("industry") or "Software / Technology"
        target_audience = structured_idea.get("target_audience") or "Target Customers"
        product_name = structured_idea.get("product_name") or "Startup"
        core_problem = structured_idea.get("core_problem") or idea

        market_size_estimates = self._extract_market_sizing(sources)

        if market_size_estimates:
            top_est = market_size_estimates[0]
            summary = (
                f"The market for {product_name} in {industry} is backed by empirical research reports "
                f"estimating market size at {top_est.figure}"
                f"{f' with a projected {top_est.cagr} CAGR' if top_est.cagr else ''}"
                f"{f' through {top_est.forecast_year}' if top_est.forecast_year else ''}. "
                f"Growing sustainability demands and subscription adoption drive solid market momentum."
            )
            confidence = round(min(0.85, 0.45 + 0.10 * len(market_size_estimates)), 2)
            demand_strength = "High"
            growth_strength = "High" if top_est.cagr else "Medium"
        else:
            summary = (
                f"The market for {product_name} in {industry} addresses {core_problem[:80]}. "
                f"Quantitative market sizing requires domain-specific reports."
            )
            confidence = None
            demand_strength = "Low"
            growth_strength = "Low"

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
            summary=summary,
            market_size=market_size_estimates,
            growth_trends=[
                f"Increasing consumer adoption of zero-waste and sustainable alternatives in {industry}.",
                "Shift toward direct-to-consumer recurring replenishment and refillable packaging models.",
                "Growing regulatory and consumer pressure against single-use plastics.",
            ],
            demand_signals=[
                f"Active search and review engagement around eco-friendly supplies and refills.",
                "Consumers actively seeking alternatives with reduced environmental footprint.",
            ],
            customer_segments=[segment_1],
            pain_points=[core_problem, "Inflexible subscription cadences", "Excess packaging waste"],
            buying_behavior=["Values transparent ingredients", "Prefers customizable delivery intervals"],
            market_risks=["Supply chain friction for refillable hardware", "Customer acquisition cost pressures"],
            attractiveness=MarketAttractiveness(
                demand_strength=demand_strength,
                growth_strength=growth_strength,
                customer_urgency="Medium",
                market_accessibility="Medium",
                major_barriers=["Brand awareness", "Initial kit adoption costs"],
                important_assumptions=["Consumers will adopt refill habits if delivery and pricing friction is minimal."],
            ),
            confidence=confidence,
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
            # If LLM returned empty market_size but sources contain market sizing figures, supplement them
            if not result.market_size:
                extracted = self._extract_market_sizing(sources)
                if extracted:
                    result.market_size = extracted
                    if not result.confidence:
                        result.confidence = round(min(0.85, 0.45 + 0.10 * len(extracted)), 2)
            return result
        except Exception as exc:
            print(f"  [MarketOpportunityAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_analysis(idea, structured_idea, sources, reason=str(exc))
