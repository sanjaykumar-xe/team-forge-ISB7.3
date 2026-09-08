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
from services.text_utils import truncate_at_word_boundary


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
            title = truncate_at_word_boundary(s.get("title", "Untitled"), max_length=90)
            url = s.get("url", "")
            snippet = s.get("snippet", "") or s.get("content", "")
            snippet = truncate_at_word_boundary(snippet, max_length=280)
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

        # Regex supporting comma-separated values like $1,870 Million, USD 1,870.5M, 1,870 Million USD, $101.81 Billion
        figures_pattern = re.compile(
            r'(?:(?:USD\s*|US\$\s*|\$\s*)((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*(Billion|Million|Trillion|B|M|T)?)'
            r'|'
            r'(?:((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*(Billion|Million|Trillion|B|M|T)\s*(?:USD|dollars|\$))',
            re.IGNORECASE
        )

        for s in relevant_sources:
            raw_snippet = s.get("snippet", "") or s.get("content", "")
            title = s.get("title", "")
            text = f"{title}. {raw_snippet}"
            url = s.get("url", "")

            raw_matches = []
            for m in figures_pattern.finditer(text):
                v = m.group(1) or m.group(3)
                u = m.group(2) or m.group(4) or ""
                raw_matches.append((v, u))

            # Look for CAGR percentages: e.g. 19.6% CAGR, CAGR of 15.2%
            cagr_match = re.search(
                r'((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*%\s*CAGR|CAGR\s*(?:of\s*)?((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*%',
                text,
                re.IGNORECASE
            )
            # Look for forecast years: e.g. by 2030, through 2034, 2025 to 2032
            year_match = re.search(r'\b(202[5-9]|203[0-9]|2040)\b', text)

            if raw_matches:
                v1, u1 = raw_matches[0]
                u1_clean = u1.capitalize() if u1 else ""
                if u1 and u1.lower() == "b":
                    u1_clean = "Billion"
                elif u1 and u1.lower() == "m":
                    u1_clean = "Million"
                elif u1 and u1.lower() == "t":
                    u1_clean = "Trillion"

                if len(raw_matches) > 1:
                    v2, u2 = raw_matches[1]
                    u2_clean = u2.capitalize() if u2 else ""
                    if u2 and u2.lower() == "b":
                        u2_clean = "Billion"
                    elif u2 and u2.lower() == "m":
                        u2_clean = "Million"
                    elif u2 and u2.lower() == "t":
                        u2_clean = "Trillion"

                    # Bidirectional unit inheritance between endpoints
                    if not u1_clean and u2_clean:
                        u1_clean = u2_clean
                    elif not u2_clean and u1_clean:
                        u2_clean = u1_clean

                    figure_str = f"${v1}{f' {u1_clean}' if u1_clean else ''} to ${v2}{f' {u2_clean}' if u2_clean else ''}"
                else:
                    figure_str = f"${v1}{f' {u1_clean}' if u1_clean else ''}"

                if figure_str in seen_figures:
                    continue
                seen_figures.add(figure_str)

                cagr_str = None
                if cagr_match:
                    cagr_val = cagr_match.group(1) or cagr_match.group(2)
                    cagr_str = f"{cagr_val}%"

                forecast_yr = year_match.group(1) if year_match else None
                market_type = "global" if any(w in text.lower() for w in ["global", "worldwide", "international"]) else "niche"

                evidence_text = truncate_at_word_boundary(raw_snippet, max_length=260) if raw_snippet else title

                estimates.append(
                    MarketSizeEstimate(
                        figure=figure_str,
                        market_type=market_type,
                        cagr=cagr_str,
                        forecast_year=forecast_yr,
                        source_url=url,
                        evidence_snippet=evidence_text,
                        notes="Quantitative market sizing extracted from verified research source.",
                    )
                )

        return estimates[:6]

    def _fallback_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        reason: str = "LLM unavailable",
    ) -> MarketAnalysisResult:
        """
        Deterministic degraded result when LLM analysis fails.
        Preserves verified empirical market sizing from sources if available,
        but outputs NO fabricated trends, demand signals, or customer segments.
        """
        product_name = structured_idea.get("product_name") or "Startup"
        industry = structured_idea.get("industry") or "the sector"

        # Deterministically extract real empirical market sizing from sources (zero LLM involved)
        market_size_estimates = self._extract_market_sizing(sources)

        summary = (
            f"Market opportunity analysis for {product_name} ({industry}) could not be completed "
            f"due to a temporary LLM processing error. Please retry your validation request."
        )

        return MarketAnalysisResult(
            summary=summary,
            market_size=market_size_estimates,
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
Produce a concise, grounded Market Opportunity & Customer Segmentation analysis.
CONSTRAINTS:
- Keep evidence snippets concise (1-2 sentences).
- Limit customer_segments to top 2 segments max.
- Maintain valid JSON syntax.
- If VERIFIED SEARCH SOURCES contain no quantitative market size figures or market size sources are missing, return "market_size": [], "attractiveness": null, and "confidence": null. Do NOT synthesize placeholder entries (such as "Not specified", "Unavailable", "N/A", "No data") or ungrounded scorecard ratings without empirical evidence.

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
      "who_they_are": "Concise profile description",
      "end_users": "Who uses it daily",
      "decision_makers": "Who buys / signs off",
      "primary_needs": ["Need 1", "Need 2", "Need 3"],
      "pain_points": ["Pain point 1", "Pain point 2"],
      "motivations": ["Motivation 1", "Motivation 2"],
      "buying_behavior": "Procurement cycle and purchasing habits",
      "industry_terminology": ["term1", "term2"]
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
                max_tokens=4096,
                temperature=0.1,
            )
            
            # Validate and construct typed Pydantic result
            result = MarketAnalysisResult(**parsed)
            result.analysis_status = "completed"

            # Filter out any market_size entries where 'figure' contains placeholder phrases or lacks numbers
            PLACEHOLDER_FIGURE_PHRASES = [
                "not specified",
                "unavailable",
                "n/a",
                "no data",
                "none",
                "unknown",
                "not available",
                "not explicitly quantified",
                "tbd",
                "not mentioned",
                "not quantified",
                "unspecified",
                "not provided",
                "pending",
            ]
            valid_market_size = []
            for item in (result.market_size or []):
                fig = (item.figure or "").strip()
                fig_lower = fig.lower()
                is_placeholder = (
                    not fig
                    or any(p in fig_lower for p in PLACEHOLDER_FIGURE_PHRASES)
                    or not any(c.isdigit() for c in fig)
                )
                if not is_placeholder:
                    valid_market_size.append(item)

            result.market_size = valid_market_size

            # If LLM returned empty market_size but sources contain market sizing figures, supplement them
            if not result.market_size:
                extracted = self._extract_market_sizing(sources)
                if extracted:
                    result.market_size = extracted
                    if not result.confidence:
                        result.confidence = round(min(0.85, 0.45 + 0.10 * len(extracted)), 2)

            # When filtered market_size is empty (0 real entries with 0 real Market Size sources),
            # clamp confidence to None and suppress/nullify the attractiveness scorecard
            if not result.market_size:
                result.market_size = []
                result.confidence = None
                result.attractiveness = None

            return result
        except Exception as exc:
            print(f"  [MarketOpportunityAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_analysis(idea, structured_idea, sources, reason=str(exc))
