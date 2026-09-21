"""
Team Forge — CrewAI Task Definitions (Milestone 3)
----------------------------------------------------
Loads task template from backend/prompts/web_search_task.md.
"""

from typing import Any, Dict
from crewai import Task
from prompts.loader import load_prompt


class ValidationTaskFactory:
    """Factory for creating structured validation tasks."""

    @staticmethod
    def create_market_research_task(
        agent: Any,
        idea: str,
        structured_idea: Dict[str, Any],
    ) -> Task:
        product_name = structured_idea.get("product_name") or "Startup"
        industry = structured_idea.get("industry") or "General"
        audience = structured_idea.get("target_audience") or "Target Customers"
        core_problem = structured_idea.get("core_problem") or idea
        keywords = ", ".join(structured_idea.get("keywords") or [])

        description = load_prompt(
            "web_search_task",
            idea=idea,
            product_name=product_name,
            industry=industry,
            audience=audience,
            core_problem=core_problem,
            keywords=keywords,
        )

        return Task(
            description=description,
            expected_output="A structured summary of verified market findings and signals gathered from the selected search tools.",
            agent=agent,
        )
