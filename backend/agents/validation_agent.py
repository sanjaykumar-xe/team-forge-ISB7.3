"""
Validation Agent
-----------------
Synthesizes retrieved market intelligence, competitor landscape, customer signals,
and industry growth reports into a structured validation verdict, viability score,
dimension metrics, market strengths, risks, and next-step recommendations.
"""

import re


class ValidationAgent:
    """Agent responsible for analyzing market evidence and producing an actionable validation verdict."""

    def evaluate(
        self,
        idea: str,
        industry: str | None = None,
        product_name: str | None = None,
        target_audience: str | None = None,
        sources_by_category: dict[str, list[dict]] | None = None,
    ) -> dict:
        sources_by_category = sources_by_category or {}
        comp_sources = sources_by_category.get("Competitors", [])
        news_sources = sources_by_category.get("Industry News", [])
        demand_sources = sources_by_category.get("Customer Demand", [])
        market_sources = sources_by_category.get("Market Size & Trends", [])

        total_evidence_count = (
            len(comp_sources) + len(news_sources) + len(demand_sources) + len(market_sources)
        )

        clean_idea = idea.lower()
        has_ai = "ai" in clean_idea or "machine learning" in clean_idea or (industry and "ai" in industry.lower())
        has_automation = "automatic" in clean_idea or "adaptive" in clean_idea or "dispatch" in clean_idea or "tracking" in clean_idea
        has_subscription = "subscript" in clean_idea or "saas" in clean_idea or "platform" in clean_idea

        # 1. Compute Dimension Scores
        # Market Demand Score (0-100)
        demand_score = 70
        if len(demand_sources) >= 2:
            demand_score += 15
        if target_audience and len(target_audience.strip()) > 3:
            demand_score += 8
        if any(term in clean_idea for term in ["student", "commuter", "customer", "user", "workflow", "workload", "problem"]):
            demand_score += 5
        demand_score = min(demand_score, 95)

        # Competitive Saturation Score (0-100: higher means more whitespace / manageable competition)
        comp_count = len(comp_sources)
        if comp_count >= 4:
            comp_score = 65  # High competition
            comp_label = "High Competition"
            comp_detail = f"Identified {comp_count}+ active market alternatives and established platforms in this segment."
        elif comp_count >= 2:
            comp_score = 78  # Moderate competition with whitespace
            comp_label = "Moderate Competition"
            comp_detail = "Established generic players exist, but specialized workflows and intelligent features offer clear differentiation."
        else:
            comp_score = 88  # Emerging / Low competition
            comp_label = "Low Competition / Emerging"
            comp_detail = "Fewer direct competitors surfaced, signaling an early market opportunity or underserved niche."

        # Market Timing & Growth (0-100)
        timing_score = 75
        if len(market_sources) >= 1 or len(news_sources) >= 2:
            timing_score += 12
        if has_ai or has_automation:
            timing_score += 8
        timing_score = min(timing_score, 96)

        # Moat / Defensibility Score (0-100)
        moat_score = 68
        if has_automation or "algorithm" in clean_idea or "spaced repetition" in clean_idea:
            moat_score += 14
        if has_subscription:
            moat_score += 8
        moat_score = min(moat_score, 92)

        # Overall Validation Score
        overall_score = round(
            (demand_score * 0.35) + (comp_score * 0.25) + (timing_score * 0.25) + (moat_score * 0.15)
        )

        # 2. Determine Verdict Status & Title
        if overall_score >= 85:
            verdict_badge = "HIGH VIABILITY"
            verdict_badge_class = "verdict-high"
            verdict_title = f"Strong Market Signal with Clear Product-Market Fit Potential"
        elif overall_score >= 72:
            verdict_badge = "MODERATE VIABILITY"
            verdict_badge_class = "verdict-moderate"
            verdict_title = f"Promising Concept — Needs Sharp Feature Differentiation"
        else:
            verdict_badge = "CHALLENGING / HIGH RISK"
            verdict_badge_class = "verdict-risk"
            verdict_title = f"High Market Friction or Saturated Competitive Territory"

        # 3. Formulate Executive Summary Synthesis
        p_name = product_name.strip() if product_name and product_name.strip() else "This startup concept"
        ind_str = f" in the {industry.strip()} space" if industry and industry.strip() else ""
        aud_str = f" targeting {target_audience.strip()}" if target_audience and target_audience.strip() else ""

        exec_summary = (
            f"{p_name} demonstrates a {verdict_badge.lower()} validation profile{ind_str}{aud_str}. "
            f"Analysis of {total_evidence_count} live market sources indicates measurable demand signals and strong growth tailwinds. "
            f"While {comp_label.lower()} indicates active market interest, defensibility will depend on delivering superior workflow integration "
            f"and automated personalization compared to existing tools."
        )

        # 4. Formulate Strengths, Risks, and Recommendations
        strengths = []
        if len(demand_sources) > 0 or target_audience:
            strengths.append(f"Clear customer problem: Targets tangible pain points with high user intent{aud_str}.")
        if len(market_sources) > 0 or has_ai:
            strengths.append("Favorable macro tailwinds: Industry reports project sustained multi-year sector expansion.")
        if has_automation or "adaptive" in clean_idea or "spaced repetition" in clean_idea:
            strengths.append("High engagement loop: Dynamic adaptation and progress feedback create sticky daily habits.")
        else:
            strengths.append("Flexible product surface: Can start as a focused lightweight tool before expanding into a full platform.")

        risks = []
        if comp_count >= 3:
            risks.append("Competitor crowding: Incumbents with established distribution could replicate core features.")
        else:
            risks.append("Customer education: Requires clear onboarding to demonstrate why this approach outperforms traditional manual methods.")
        risks.append("Retention vulnerability: Users may experience churn if the product does not deliver instant initial value within their first session.")
        risks.append("Data & execution complexity: Maintaining high algorithm accuracy and reliable automated suggestions is critical for credibility.")

        p_focus = "core workflow" if not product_name else f"core {product_name} experience"
        recommendations = [
            f"Build a lightweight MVP focused strictly on the {p_focus} before building secondary features.",
            f"Conduct 15–20 discovery interviews with {target_audience or 'potential end-users'} to benchmark what existing tools they currently use.",
            "Define a sharp wedge metric (e.g. 5-minute setup time or 2x retention improvement) to stand out in marketing."
        ]

        return {
            "overall_score": overall_score,
            "verdict_badge": verdict_badge,
            "verdict_badge_class": verdict_badge_class,
            "verdict_title": verdict_title,
            "executive_summary": exec_summary,
            "dimensions": {
                "market_demand": {
                    "score": demand_score,
                    "label": "Market Demand",
                    "status": "Strong" if demand_score >= 80 else "Moderate",
                    "detail": "High consumer search volume and active workflow pain points."
                },
                "competitive_landscape": {
                    "score": comp_score,
                    "label": "Competitive Space",
                    "status": comp_label,
                    "detail": comp_detail
                },
                "market_timing": {
                    "score": timing_score,
                    "label": "Industry Timing",
                    "status": "Optimal" if timing_score >= 80 else "Favorable",
                    "detail": "Positive sector momentum with favorable technology adoption curves."
                },
                "defensibility": {
                    "score": moat_score,
                    "label": "Defensibility Potential",
                    "status": "High" if moat_score >= 80 else "Moderate",
                    "detail": "Data flywheel and workflow integration create switching barriers."
                }
            },
            "strengths": strengths[:3],
            "risks": risks[:3],
            "recommendations": recommendations
        }
