"""
Team Forge — CrewAI Task Definitions
------------------------------------
Defines structured tasks executed by the CrewAI validation pipeline.
"""

from typing import Any, Dict
from crewai import Task


class ValidationTaskFactory:
    """Factory for creating structured validation tasks."""

    @staticmethod
    def create_market_research_task(
        agent: Any,
        idea: str,
        structured_idea: Dict[str, Any],
    ) -> Task:
        """
        Creates the autonomous market research task where the agent assesses the idea
        and selectively calls relevant search tools.
        """
        product_name = structured_idea.get("product_name") or "Startup"
        industry = structured_idea.get("industry") or "General"
        audience = structured_idea.get("target_audience") or "Target Customers"
        core_problem = structured_idea.get("core_problem") or idea
        keywords = ", ".join(structured_idea.get("keywords") or [])

        description = f"""\
Evaluate the following startup concept and collect targeted market evidence using your search tools:

STARTUP CONCEPT:
Pitch: {idea}
Product Name: {product_name}
Industry / Vertical: {industry}
Target Audience: {audience}
Core Problem: {core_problem}
Domain Keywords: {keywords}

TASK INSTRUCTIONS:
1. Review the concept's market structure, business model, and customer type.
2. Selectively execute ONLY the tools that yield real, actionable evidence for this specific concept:
   - Use 'search_competitors' if commercial competitors, alternatives, or legacy substitutes exist.
   - Use 'search_industry_news' if the vertical has active industry trends, regulations, or recent venture activity.
   - Use 'search_customer_demand' ONLY if the product serves end-consumers or retail users who write reviews. SKIP this tool if the idea is pure enterprise B2B infrastructure, industrial manufacturing, or deep-tech hardware where retail consumers do not exist.
   - Use 'search_market_size' if commercial market sizing reports (TAM/SAM, CAGR) exist for this industry. SKIP this tool for personal micro-hobbies or non-commercial crafts lacking institutional analyst coverage.
3. Formulate high-signal queries using domain nouns and problem terms (avoid generic buzzwords or unlaunched brand names).

BUDGET & REPETITION CONSTRAINTS:
- You operate under a STRICT BUDGET of 3 to 5 total search queries.
- NEVER execute near-identical queries, rephrased searches, or follow-up queries for the same brand. Once a search returns results, analyze what you have.
- Immediately stop searching and write your final summary once you have gathered 3-4 distinct evidence points across the relevant categories.
"""

        return Task(
            description=description,
            expected_output="A structured summary of verified market findings and signals gathered from the selected search tools.",
            agent=agent,
        )
