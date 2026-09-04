"""
Team Forge — CrewAI Agent Definitions
-------------------------------------
Defines specialized autonomous agents participating in the startup idea validation workflow:
  1. Idea Extractor Agent
  2. Web Search Researcher Agent
  3. Data Verification Agent
  4. Market Opportunity & Segmentation Agent
  5. Competitor Discovery & Strategy Agent
"""

from typing import Optional, Any, List


def get_crewai_classes():
    """Dynamically imports CrewAI classes to guarantee compatibility."""
    try:
        from crewai import Agent, LLM
        return Agent, LLM
    except ImportError:
        return None, None


class ValidationAgentFactory:
    """Factory for creating configured CrewAI validation agents."""

    @staticmethod
    def create_idea_extractor(llm: Optional[Any] = None) -> Any:
        Agent, _ = get_crewai_classes()
        if Agent is None:
            return None
        return Agent(
            role="Startup Concept & Domain Intelligence Specialist",
            goal="Extract unambiguous product parameters, industry vertical, audience profile, core problem, and high-signal research keywords from raw startup descriptions.",
            backstory="A seasoned product architect with deep domain intuition for deconstructing early-stage business models into structured research vectors.",
            verbose=False,
            allow_delegation=False,
            llm=llm,
        )

    @staticmethod
    def create_web_searcher(tools: Optional[List[Any]] = None, llm: Optional[Any] = None) -> Any:
        Agent, _ = get_crewai_classes()
        if Agent is None:
            return None
        return Agent(
            role="AI Market Intelligence Researcher",
            goal="Execute parallel web intelligence queries across 4 strategic categories (Competitors, Industry News, Customer Demand, and Market Size & Trends).",
            backstory="An AI-native research analyst skilled at constructing targeted queries to surface fresh market dynamics and real-world signals.",
            verbose=False,
            allow_delegation=False,
            tools=tools or [],
            llm=llm,
        )

    @staticmethod
    def create_data_verifier(tools: Optional[List[Any]] = None, llm: Optional[Any] = None) -> Any:
        Agent, _ = get_crewai_classes()
        if Agent is None:
            return None
        return Agent(
            role="Evidence Verification & Data Sanitization Specialist",
            goal="Filter domain blocklists, verify English coherence, deduplicate canonical URLs, and rank sources by native relevance.",
            backstory="A meticulous data integrity analyst dedicated to eliminating encyclopedic noise, forum scrapers, and duplicate evidence.",
            verbose=False,
            allow_delegation=False,
            tools=tools or [],
            llm=llm,
        )

    @staticmethod
    def create_market_analyst(tools: Optional[List[Any]] = None, llm: Optional[Any] = None) -> Any:
        Agent, _ = get_crewai_classes()
        if Agent is None:
            return None
        return Agent(
            role="Market Opportunity & Customer Segmentation Analyst",
            goal="Evaluate empirical market size valuations, CAGR trajectories, customer personas, end users vs decision makers, and market attractiveness without hallucinating numbers.",
            backstory="A senior venture capital researcher specializing in market sizing, customer persona breakdown, and attractiveness evaluation grounded in empirical sources.",
            verbose=False,
            allow_delegation=False,
            tools=tools or [],
            llm=llm,
        )

    @staticmethod
    def create_competitor_analyst(tools: Optional[List[Any]] = None, llm: Optional[Any] = None) -> Any:
        Agent, _ = get_crewai_classes()
        if Agent is None:
            return None
        return Agent(
            role="Competitive Intelligence & Strategy Specialist",
            goal="Discover direct, indirect, and emerging rivals, generate feature comparison matrices, and identify structural market gaps.",
            backstory="A competitive strategy consultant specializing in positioning dynamics, competitor feature matrices, and pricing gap identification.",
            verbose=False,
            allow_delegation=False,
            tools=tools or [],
            llm=llm,
        )
