"""
Team Forge — CrewAI Agent Definitions (Milestone 3)
-----------------------------------------------------
Loads prompt from backend/prompts/web_search_system.md.
"""

import os
from typing import Optional, Any, List, Callable
from crewai import Agent, LLM
from prompts.loader import load_prompt


def get_crewai_classes():
    try:
        from crewai import Agent, LLM
        return Agent, LLM
    except ImportError:
        return None, None


def get_default_llm() -> Any:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    return LLM(
        model="openai/openai/gpt-oss-120b",
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        max_tokens=1500,
        temperature=0.1,
    )


class ValidationAgentFactory:
    """Factory for creating configured CrewAI validation agents."""

    @staticmethod
    def create_market_research_agent(
        tools: List[Any],
        step_callback: Optional[Callable[[Any], None]] = None,
        llm: Optional[Any] = None,
    ) -> Agent:
        backstory = load_prompt("web_search_system")
        return Agent(
            role="Market Research Agent",
            goal=(
                "Gather targeted market intelligence by thoughtfully selecting and executing "
                "only the search tools relevant to the startup's specific domain and customer model."
            ),
            backstory=backstory,
            tools=tools,
            llm=llm or get_default_llm(),
            verbose=True,
            step_callback=step_callback,
            allow_delegation=False,
            max_iter=8,
        )
