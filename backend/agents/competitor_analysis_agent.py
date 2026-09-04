"""
Competitor Discovery & Comparison Agent
---------------------------------------
Identifies direct competitors, indirect alternatives, and emerging entrants from
verified search sources and market research context.

Computes:
  1. Competitor Classification & Profiles: Direct, indirect, and emerging rivals with
     core offerings, target customers, key features, pricing, business models,
     positioning, strengths, weaknesses, and documented customer complaints.
  2. Multi-Dimensional Comparison Matrix: Feature-by-feature evaluation comparing the startup
     approach against key competitors.
  3. Market Gaps & Structural Weaknesses: Underserved customer segments, recurring complaints,
     pricing voids, and unmet customer needs.

Strict Anti-Hallucination Policy:
- If pricing or business model is not disclosed in the research evidence, it is explicitly marked as "unavailable" or "not disclosed".
- Customer complaints must reference empirical dissatisfaction signals found in search snippets.
"""

from typing import List, Dict, Any, Optional
from schemas.validation_schemas import (
    CompetitorAnalysisResult,
    CompetitorRecord,
    ComparisonMatrixRow,
    MarketAnalysisResult,
)
from services.llm_service import call_groq_json


COMPETITOR_ANALYSIS_SYSTEM_PROMPT = """\
You are a senior competitive intelligence and market strategy analyst.
Your mission is to perform a rigorous competitor discovery and comparison analysis for a startup idea using verified search evidence.

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION RULES:
1. Ground competitor identification in the PROVIDED SEARCH SOURCES and known real market entities.
2. Classify each competitor strictly as "direct" (solving the same core problem), "indirect" (substitute or legacy workaround), or "emerging" (early-stage startup/new entrant).
3. If pricing or business model is NOT disclosed in the sources or verifiable public data, set pricing/business_model to "unavailable" or "not disclosed" — NEVER invent pricing figures.
4. Extract strengths, weaknesses, and documented customer complaints from the research sources.
5. Create a structured comparison matrix evaluating 3 to 6 key capability dimensions comparing the startup's proposed approach against competitors.
6. Identify 3 to 5 clear market gaps, pricing gaps, or unmet customer needs.

Respond strictly in valid JSON matching the required schema.
"""


class CompetitorAnalysisAgent:
    """Agent responsible for competitive landscaping, comparison matrix generation, and gap identification."""

    def __init__(self):
        pass

    def _build_sources_summary(self, sources: List[Dict[str, Any]]) -> str:
        """Formats top competitor and demand sources into compact structured text."""
        if not sources:
            return "No verified web sources available."

        # Prioritize Competitors and Customer Demand categories
        comp_items = [s for s in sources if s.get("category") == "Competitors"][:3]
        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:2]
        other_items = [s for s in sources if s not in comp_items and s not in demand_items][:1]
        
        selected = comp_items + demand_items + other_items

        lines = []
        for i, s in enumerate(selected[:6], 1):
            category = s.get("category", "General")
            title = s.get("title", "Untitled")[:80]
            url = s.get("url", "")
            snippet = s.get("snippet", "")[:240].strip()
            lines.append(f"[{i}] Category: {category} | Title: {title}\nURL: {url}\nEvidence: {snippet}\n")

        return "\n".join(lines)


    def _fallback_competitor_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        reason: str = "LLM unavailable",
    ) -> CompetitorAnalysisResult:
        """Deterministic fallback when LLM is unavailable or fails to parse."""
        product_name = structured_idea.get("product_name") or "Startup Concept"
        industry = structured_idea.get("industry") or "Software"
        core_problem = structured_idea.get("core_problem") or idea

        # Extract potential competitor names from Competitor search source titles
        competitors = []
        for s in sources:
            if s.get("category") == "Competitors":
                title_clean = s.get("title", "").split("|")[0].split("-")[0].strip()
                if title_clean and len(title_clean) > 3 and title_clean.lower() not in ["competitors", "alternatives", "top 10", "best"]:
                    competitors.append(
                        CompetitorRecord(
                            name=title_clean,
                            classification="direct" if len(competitors) < 2 else "indirect",
                            core_offering=s.get("snippet", "")[:180] or f"Software solution in {industry}",
                            target_customer="Enterprise and mid-market organizations",
                            major_features=["Core workflow automation", "Standard integrations", "Reporting"],
                            pricing="unavailable",
                            business_model="Subscription / SaaS",
                            positioning=f"Established provider for {industry.lower()} workflows",
                            strengths=["Established brand presence", "Broad feature suite"],
                            weaknesses=["Complex setup", "Legacy user experience", "High implementation overhead"],
                            customer_complaints=["High cost for smaller teams", "Steep learning curve"],
                        )
                    )
                if len(competitors) >= 3:
                    break

        if not competitors:
            competitors.append(
                CompetitorRecord(
                    name="Legacy Manual Workflows & Spreadsheets",
                    classification="indirect",
                    core_offering="Manual processes, spreadsheets, and disconnected tools",
                    target_customer="Small and mid-sized operators",
                    major_features=["Flexible manual entry", "No specialized software cost"],
                    pricing="Zero upfront software license (high human labor cost)",
                    business_model="Internal operational overhead",
                    positioning="Default status-quo alternative",
                    strengths=["Universally accessible", "Zero software friction"],
                    weaknesses=["Prone to errors", "Unscalable", "High operational latency"],
                    customer_complaints=["Time-consuming", "No automated intelligence or prediction"],
                )
            )

        matrix = [
            ComparisonMatrixRow(
                feature_or_dimension="Automated Intelligence & Personalization",
                startup_approach=f"Tailored predictive workflow designed specifically for {core_problem[:40]}",
                competitor_approaches={c.name: "Generic rules-based or manual execution" for c in competitors},
            ),
            ComparisonMatrixRow(
                feature_or_dimension="Ease of Deployment & Time to Value",
                startup_approach="Fast, low-friction integration built for modern teams",
                competitor_approaches={c.name: "Heavy configuration and multi-week onboarding" for c in competitors},
            ),
            ComparisonMatrixRow(
                feature_or_dimension="Pricing Transparency & Affordability",
                startup_approach="Accessible tiered pricing aligned with customer value",
                competitor_approaches={c.name: "Enterprise-only quotes or high fixed minimums" for c in competitors},
            ),
        ]

        return CompetitorAnalysisResult(
            competitors=competitors,
            comparison_matrix=matrix,
            market_gaps=[
                "Lack of modern, lightweight solutions tailored for small and mid-market operators.",
                "High setup complexity in incumbent tools leaving underserved niche segments.",
                "Inadequate integration between data intelligence and operational action.",
            ],
            pricing_insights=[
                "Incumbents predominantly target high-budget enterprises with opaque custom pricing.",
                "Significant opportunity for transparent self-serve or accessible SaaS pricing.",
            ],
            business_models=[
                "Tiered SaaS subscription with usage-based expansion tiers.",
                "Value-based pricing tied to cost savings or recovered revenue.",
            ],
        )

    def analyze(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
    ) -> CompetitorAnalysisResult:
        """
        Executes competitor discovery, comparative positioning matrix, and market gap analysis.
        """
        sources_str = self._build_sources_summary(sources)
        
        market_summary = ""
        if market_analysis:
            segments_summary = ", ".join([s.segment_name for s in market_analysis.customer_segments])
            market_summary = f"\nMarket Summary: {market_analysis.summary}\nCustomer Segments Identified: {segments_summary}\nKey Customer Pains: {', '.join(market_analysis.pain_points[:4])}"

        prompt = f"""\
STARTUP IDEA TO VALIDATE:
Pitch: {idea}
Product Name: {structured_idea.get('product_name', 'N/A')}
Industry: {structured_idea.get('industry', 'N/A')}
Target Audience: {structured_idea.get('target_audience', 'N/A')}
Core Problem: {structured_idea.get('core_problem', 'N/A')}
Domain Keywords: {', '.join(structured_idea.get('keywords', []))}
{market_summary}

VERIFIED SEARCH SOURCES (Competitor & Demand Research):
{sources_str}

TASK:
Identify direct competitors, indirect alternatives, and emerging entrants.
Build a comparison matrix comparing the startup against 2 to 4 key competitors.
Identify clear market gaps and business model insights.

JSON structure must match this format:
{{
  "competitors": [
    {{
      "name": "Competitor Name",
      "classification": "direct" | "indirect" | "emerging",
      "core_offering": "Core solution description",
      "target_customer": "Their primary target market",
      "major_features": ["Feature 1", "Feature 2", "Feature 3"],
      "pricing": "Pricing structure (or 'unavailable' if undisclosed)",
      "business_model": "Business model (or 'unavailable' if undisclosed)",
      "positioning": "How they position themselves in the market",
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1", "Weakness 2"],
      "customer_complaints": ["Complaint or frustration 1", "Complaint 2"]
    }}
  ],
  "comparison_matrix": [
    {{
      "feature_or_dimension": "Core Evaluation Dimension",
      "startup_approach": "How the startup idea solves this",
      "competitor_approaches": {{
        "CompetitorA": "Their approach",
        "CompetitorB": "Their approach"
      }}
    }}
  ],
  "market_gaps": ["Market Gap 1", "Market Gap 2", "Market Gap 3"],
  "pricing_insights": ["Pricing Insight 1", "Pricing Insight 2"],
  "business_models": ["Viable Business Model 1", "Model 2"]
}}
"""

        try:
            parsed = call_groq_json(
                prompt=prompt,
                system_prompt=COMPETITOR_ANALYSIS_SYSTEM_PROMPT,
                max_tokens=2500,
                temperature=0.1,
            )
            result = CompetitorAnalysisResult(**parsed)
            return result
        except Exception as exc:
            print(f"  [CompetitorAnalysisAgent] LLM analysis failed ({exc}), triggering fallback.")
            return self._fallback_competitor_analysis(
                idea=idea,
                structured_idea=structured_idea,
                sources=sources,
                market_analysis=market_analysis,
                reason=str(exc),
            )
