"""
Team Forge — CrewAI Agent Definitions
-------------------------------------
Defines specialized CrewAI agents participating in startup validation:
  1. Market Research Agent (Autonomous tool-calling agent with selective search tools)
  2. Concept & Strategy Specialists
"""

import os
from typing import Optional, Any, List, Callable
from crewai import Agent, LLM


def get_crewai_classes():
    """Dynamically imports CrewAI classes to guarantee compatibility."""
    try:
        from crewai import Agent, LLM
        return Agent, LLM
    except ImportError:
        return None, None


def get_default_llm() -> Any:
    """Configures high-performance Groq LLM through OpenAI-compatible endpoint."""
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
        """
        Creates the autonomous Market Research Agent equipped with the 4 discrete search tools:
          - search_competitors
          - search_industry_news
          - search_customer_demand
          - search_market_size
        """
        return Agent(
            role="Market Research Agent",
            goal=(
                "Gather targeted market intelligence by thoughtfully selecting and executing "
                "only the search tools relevant to the startup's specific domain and customer model."
            ),
            backstory=(
                "You are an elite competitive intelligence researcher operating under a strict budget of 4-6 queries. "
                "Not every idea requires all 4 categories — only call tools that will produce genuinely useful evidence for this "
                "specific idea. For example, if an idea is pure B2B enterprise infrastructure or deep-tech "
                "with no retail consumers, skip customer demand reviews. If an idea is an uncommercialized "
                "micro-artisan craft, skip institutional market size reports. "
                "CRITICAL: Never re-issue near-identical queries or re-query for the same brand/terms. "
                "Once you receive search results, analyze them immediately and synthesize your final output without endless searching."
            ),
            tools=tools,
            llm=llm or get_default_llm(),
            verbose=True,
            step_callback=step_callback,
            allow_delegation=False,
            max_iter=8,
        )
