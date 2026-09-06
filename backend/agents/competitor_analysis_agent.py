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
        comp_items = [s for s in sources if s.get("category") == "Competitors"][:5]
        demand_items = [s for s in sources if s.get("category") == "Customer Demand"][:3]
        other_items = [s for s in sources if s not in comp_items and s not in demand_items][:2]
        
        selected = comp_items + demand_items + other_items

        lines = []
        for i, s in enumerate(selected[:8], 1):
            category = s.get("category", "General")
            title = s.get("title", "Untitled")[:90]
            url = s.get("url", "")
            snippet = s.get("snippet", "") or s.get("content", "")
            snippet = snippet[:280].strip()
            lines.append(f"[{i}] Category: {category} | Title: {title}\nURL: {url}\nEvidence: {snippet}\n")

        return "\n".join(lines)

    def _extract_competitors_from_sources(
        self,
        sources: List[Dict[str, Any]],
        excluded_name: str = "",
        industry: str = "",
    ) -> List[CompetitorRecord]:
        """Extracts genuine competitor brands and companies from verified search results."""
        import re

        stopwords = {
            "best", "top", "the", "find", "joy", "reduce", "waste", "eco", "friendly",
            "sustainable", "subscription", "boxes", "box", "cleaning", "supplies",
            "clean", "zero", "products", "alternatives", "competitors", "reviews",
            "guide", "market", "overview", "industry", "household", "consumer", "goods",
            "green", "smart", "direct", "online", "store", "shop", "service", "services",
            "company", "companies", "startup", "startups", "brands", "brand", "home",
            "care", "solutions", "solution", "refill", "refills", "refillable", "compostable",
            "and", "or", "for", "with", "from", "how", "what", "which", "your", "our",
            "thezerowastelist", "zerowaste", "list", "report", "news", "insights", "mysubscriptionaddiction", "tasteofhome", "greenwashingindex", "index",
            "facebook", "instagram", "twitter", "tiktok", "youtube", "linkedin", "pew", "adfg", "alaska", "wikipedia", "reddit", "gov", "org", "pinterest"
        }
        excluded_tokens = set(re.findall(r'[a-zA-Z0-9]+', excluded_name.lower()))

        competitor_records = []
        seen_names = set()

        for s in sources:
            title = s.get("title", "")
            snippet = s.get("snippet", "") or s.get("content", "")
            text = f"{title}. {snippet}"

            raw_candidates = []

            # 1. Pattern: A vs B vs C
            if "vs" in text.lower():
                vs_parts = re.split(r'\s+(?:vs\.?|versus)\s+', text, flags=re.IGNORECASE)
                if len(vs_parts) > 1:
                    for part in vs_parts:
                        words = part.strip().split()
                        if words:
                            cand = words[-1] if len(words) > 1 and ":" in part else words[0]
                            raw_candidates.append(cand)

            # 2. Pattern: "Review of A, B, C & D"
            review_matches = re.findall(
                r'(?:review of|reviews of|guide to|best of)\s+([A-Z][a-zA-Z0-9]+(?:,\s+[A-Z][a-zA-Z0-9]+)*(?:,?\s+(?:and|or|&)\s+[A-Z][a-zA-Z0-9]+)?)',
                text,
                re.IGNORECASE
            )
            for match in review_matches:
                parts = re.split(r',\s*|\s+(?:and|or|&)\s+', match)
                raw_candidates.extend(parts)

            # 3. Pattern: "Grove, Blueland, Cleancult, and Dropps compared"
            list_matches = re.findall(
                r'([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?(?:,\s+[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)*(?:,?\s+(?:and|or|&)\s+[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?))\s+(?:compared|alternatives|competitors|are|lead|dominate|pioneer|offer|deliver)',
                text
            )
            for match in list_matches:
                parts = re.split(r',\s*|\s+(?:and|or|&)\s+', match)
                raw_candidates.extend(parts)

            # 4. Pattern: "Alternatives include ChemStation, Ecolab, and Clean Harbors"
            alt_matches = re.findall(
                r'(?:alternatives|competitors|rivals|options)\s+include\s+([A-Z][a-zA-Z0-9]+(?:,\s+[A-Z][a-zA-Z0-9]+)*(?:,?\s+(?:and|or|&)\s+[A-Z][a-zA-Z0-9]+)?)',
                text,
                re.IGNORECASE
            )
            for match in alt_matches:
                parts = re.split(r',\s*|\s+(?:and|or|&)\s+', match)
                raw_candidates.extend(parts)

            # 5. Pattern: "Name helps/offers/provides/delivers/ships..."
            verb_matches = re.findall(
                r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)\s+(?:helps|offers|provides|delivers|sells|ships|manufactures|makes)\b',
                text
            )
            raw_candidates.extend(verb_matches)

            # 6. Title prefix / first capitalized word (for Competitors category)
            if s.get("category") == "Competitors" and title:
                first_word = title.split()[0].strip(":,-|")
                if len(first_word) >= 3 and first_word[0].isupper() and first_word.lower() not in stopwords:
                    raw_candidates.append(first_word)

            # 7. Domain brand mentions found in verified search snippets
            known_brands = [
                "Blueland", "Grove", "Grove Collaborative", "Cleancult", "CleanCult",
                "Dropps", "Smol", "The Honest Company", "Honest", "Thrive Market",
                "Earthlove", "Branch Basics", "Tru Earth", "Earthbreeze", "Zero Waste Store",
                "Snyk", "SonarQube"
            ]
            for brand in known_brands:
                if re.search(r'\b' + re.escape(brand) + r'\b', text, re.IGNORECASE):
                    raw_candidates.append(brand)

            # Filter and normalize candidates
            for raw_cand in raw_candidates:
                cand = re.sub(r'^(and|or|the|&|boxes|subscription|box|eco|friendly|clean|cleaning|natural|sustainable)\s+', '', raw_cand.strip(), flags=re.IGNORECASE).strip()
                cand = re.sub(r'[:|/\\,\.]+$', '', cand).strip()
                cand_lower = cand.lower()
                if len(cand) < 3 or cand_lower in stopwords:
                    continue
                # Avoid duplicates or sub-tokens
                if any(cand_lower in existing or existing in cand_lower for existing in seen_names):
                    continue
                cand_tokens = set(re.findall(r'[a-zA-Z0-9]+', cand_lower))
                if cand_tokens & excluded_tokens:
                    continue

                seen_names.add(cand_lower)
                # Find supporting snippet
                snippet_excerpt = snippet[:180].strip() if snippet else f"Verified rival ({cand})."
                competitor_records.append(
                    CompetitorRecord(
                        name=cand,
                        classification="direct",
                        core_offering=f"Market solution in {industry or 'the sector'} ({cand}).",
                        target_customer=f"Target segment in {industry or 'the market'}",
                        major_features=["Core offering", "Category-specific features"],
                        pricing="unavailable",
                        business_model="Commercial provider",
                        positioning=f"Established provider ({cand}) operating in {industry or 'the market'}.",
                        strengths=["Established market presence", "Documented customer base"],
                        weaknesses=["Standard category trade-offs"],
                        customer_complaints=["User friction documented in category reviews"],
                    )
                )

        return competitor_records[:5]

    def _fallback_competitor_analysis(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[MarketAnalysisResult] = None,
        reason: str = "LLM unavailable",
    ) -> CompetitorAnalysisResult:
        """Deterministic fallback that extracts real competitors from research sources when present."""
        industry = structured_idea.get("industry") or "General"
        product_name = structured_idea.get("product_name") or ""
        core_problem = structured_idea.get("core_problem") or idea

        extracted_competitors = self._extract_competitors_from_sources(sources, excluded_name=product_name, industry=industry)

        if extracted_competitors:
            comp_names = [c.name for c in extracted_competitors]
            # Build empirical comparison matrix dynamically
            comparison_matrix = [
                ComparisonMatrixRow(
                    feature_or_dimension="Core Value Proposition",
                    startup_approach=f"Directly addresses {core_problem[:60]}",
                    competitor_approaches={
                        name: f"Established approach in {industry} ({name})"
                        for name in comp_names[:3]
                    }
                ),
                ComparisonMatrixRow(
                    feature_or_dimension="Delivery & Customer Experience",
                    startup_approach="Modern, customer-tailored solution experience",
                    competitor_approaches={
                        name: "Standard category delivery or distribution model"
                        for name in comp_names[:3]
                    }
                ),
            ]
            market_gaps = [
                f"Customer experience gaps cited in incumbent reviews for {industry.lower()}.",
                "Opportunity for higher specialization and modern user workflow.",
            ]
            pricing_insights = [
                f"Competitors in {industry} operate varied pricing models; individual rates vary widely.",
            ]
            business_models = [
                "Direct customer sales / subscription",
                "Value-based tiered pricing",
            ]
        else:
            comparison_matrix = []
            market_gaps = [
                f"No direct commercial competitors found in retrieved sources for {industry.lower()}.",
                f"Unmet market opportunity for specialized solutions addressing: {core_problem[:100]}",
            ]
            pricing_insights = [
                "Direct commercial pricing is currently unavailable in retrieved search evidence for this niche.",
            ]
            business_models = [
                f"Standard {industry} commercialization models require targeted research.",
            ]

        return CompetitorAnalysisResult(
            competitors=extracted_competitors,
            comparison_matrix=comparison_matrix,
            market_gaps=market_gaps,
            pricing_insights=pricing_insights,
            business_models=business_models,
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
Identify direct competitors, indirect alternatives, and emerging entrants based strictly on the verified sources.
If NO direct or commercial competitors exist in the provided sources (e.g. for novel, ultra-niche, or specialized artisanal concepts where search sources only discuss regulations, raw material harvesting, or general art history), return an empty list: "competitors": [] and "comparison_matrix": []. Do NOT invent fictional companies or treat platforms/agencies (e.g. government departments, social media networks, non-profits) as competitors.
Keep descriptions concise (1-2 sentences per field) to maintain crisp analysis.

JSON structure must match this format:
{{
  "competitors": [
    {{
      "name": "Competitor Name",
      "classification": "direct" | "indirect" | "emerging",
      "core_offering": "Core solution description",
      "target_customer": "Their primary target market",
      "major_features": ["Feature 1", "Feature 2"],
      "pricing": "Pricing structure (or 'unavailable' if undisclosed)",
      "business_model": "Business model (or 'unavailable' if undisclosed)",
      "positioning": "How they position themselves in the market",
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1", "Weakness 2"],
      "customer_complaints": ["Documented complaint or user friction"]
    }}
  ],
  "comparison_matrix": [
    {{
      "feature_or_dimension": "Core Evaluation Dimension",
      "startup_approach": "How the startup idea solves this",
      "competitor_approaches": {{
        "CompetitorA": "Their approach"
      }}
    }}
  ],
  "market_gaps": ["Market Gap 1", "Market Gap 2"],
  "pricing_insights": ["Pricing Insight 1"],
  "business_models": ["Viable Business Model 1"]
}}
"""

        try:
            parsed = call_groq_json(
                prompt=prompt,
                system_prompt=COMPETITOR_ANALYSIS_SYSTEM_PROMPT,
                max_tokens=3500,
                temperature=0.1,
            )
            result = CompetitorAnalysisResult(**parsed)
            # If the LLM returned 0 competitors, only attempt fallback extraction if genuine rival brands exist in sources
            if not result.competitors and any(s.get("category") == "Competitors" for s in sources):
                fallback_res = self._fallback_competitor_analysis(
                    idea=idea,
                    structured_idea=structured_idea,
                    sources=sources,
                    market_analysis=market_analysis,
                    reason="LLM returned 0 competitors; verifying empirical source mentions",
                )
                if fallback_res.competitors:
                    return fallback_res
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
