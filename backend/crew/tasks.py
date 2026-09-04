"""
Team Forge — CrewAI Task Definitions
------------------------------------
Defines structured tasks executed sequentially by the CrewAI validation pipeline.
Each task defines clear objectives, inputs, and expected structured output formats.
"""

from typing import Optional, List, Any


def get_crewai_task_class():
    try:
        from crewai import Task
        return Task
    except ImportError:
        return None


class ValidationTaskFactory:
    """Factory for creating structured validation tasks with explicit handoffs."""

    @staticmethod
    def create_idea_extraction_task(
        agent: Any,
        idea: str,
        product_name: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> Any:
        Task = get_crewai_task_class()
        if Task is None:
            return None
        return Task(
            description=f"Deconstruct the startup idea into structured parameters (product name, vertical, audience, core problem, and 3-5 high-signal keywords).\nIdea: {idea}\nProduct Name: {product_name or 'N/A'}\nIndustry: {industry or 'N/A'}\nTarget Audience: {target_audience or 'N/A'}",
            expected_output="Structured JSON containing product_name, industry, target_audience, core_problem, and keywords list.",
            agent=agent,
        )

    @staticmethod
    def create_web_search_task(
        agent: Any,
        context_tasks: Optional[List[Any]] = None,
    ) -> Any:
        Task = get_crewai_task_class()
        if Task is None:
            return None
        return Task(
            description="Query the Tavily Search API across 4 strategic categories (Competitors, Industry News, Customer Demand, Market Size & Trends) using structured domain parameters.",
            expected_output="Raw batch results categorized across the 4 research vectors.",
            agent=agent,
            context=context_tasks or [],
        )

    @staticmethod
    def create_data_retrieval_task(
        agent: Any,
        context_tasks: Optional[List[Any]] = None,
    ) -> Any:
        Task = get_crewai_task_class()
        if Task is None:
            return None
        return Task(
            description="Sanitize raw search results: enforce domain blocklists, verify English language coherence, deduplicate canonical URLs, and rank sources by native relevance.",
            expected_output="List of sanitized SourceRecords with summary breakdown metrics.",
            agent=agent,
            context=context_tasks or [],
        )

    @staticmethod
    def create_market_analysis_task(
        agent: Any,
        context_tasks: Optional[List[Any]] = None,
    ) -> Any:
        Task = get_crewai_task_class()
        if Task is None:
            return None
        return Task(
            description="Synthesize verified search evidence to evaluate Market Opportunity (TAM/SAM estimates, CAGR, adoption drivers) and generate granular Customer Personas with acute pain points and buying behaviors.",
            expected_output="Structured MarketAnalysisResult with cited market sizing, customer segments, and market attractiveness scorecard.",
            agent=agent,
            context=context_tasks or [],
        )

    @staticmethod
    def create_competitor_analysis_task(
        agent: Any,
        context_tasks: Optional[List[Any]] = None,
    ) -> Any:
        Task = get_crewai_task_class()
        if Task is None:
            return None
        return Task(
            description="Discover direct, indirect, and emerging competitors, build a multidimensional comparison matrix, and uncover structural market and pricing gaps.",
            expected_output="Structured CompetitorAnalysisResult containing classified competitor profiles, comparison matrix, and market gap vectors.",
            agent=agent,
            context=context_tasks or [],
        )
