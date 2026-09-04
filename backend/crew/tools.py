"""
Team Forge — CrewAI Custom Tools
--------------------------------
Wraps Milestone 1 and Milestone 2 research, retrieval, and intelligence engines
into tools that can be invoked by CrewAI Agents.
"""

from typing import Dict, Any, List, Optional
import json

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine


class IdeaExtractionTool:
    """Tool for extracting structured domain context from raw idea text."""
    name: str = "idea_extraction_tool"
    description: str = "Extracts product_name, industry, target_audience, core_problem, and domain keywords from startup descriptions."

    def __init__(self, agent: Optional[IdeaExtractionAgent] = None):
        self._agent = agent or IdeaExtractionAgent()

    def run(self, idea: str, product_name: Optional[str] = None, industry: Optional[str] = None, target_audience: Optional[str] = None) -> Dict[str, Any]:
        return self._agent.extract(
            idea=idea,
            product_name=product_name,
            industry=industry,
            target_audience=target_audience,
        )


class TavilySearchTool:
    """Tool for querying Tavily search across 4 market categories in parallel."""
    name: str = "tavily_search_tool"
    description: str = "Executes multi-category Tavily searches across Competitors, Industry News, Customer Demand, and Market Size & Trends."

    def __init__(self, agent: Optional[WebSearchAgent] = None):
        self._agent = agent or WebSearchAgent()

    def run(self, structured_idea: Dict[str, Any], max_results_per_category: int = 6) -> List[Dict[str, Any]]:
        return self._agent.search(
            structured_idea=structured_idea,
            max_results_per_category=max_results_per_category,
        )


class DataRetrievalTool:
    """Tool for sanitizing, language filtering, deduplicating, and scoring web search sources."""
    name: str = "data_retrieval_tool"
    description: str = "Filters blocked domains, validates English text, removes duplicate URLs, and structures sources by relevance."

    def __init__(self, agent: Optional[DataRetrievalAgent] = None):
        self._agent = agent or DataRetrievalAgent()

    def run(self, raw_batches: List[Dict[str, Any]]) -> Dict[str, Any]:
        structured = self._agent.structure(raw_batches)
        summary = self._agent.summarize_counts(structured)
        return {
            "sources": structured,
            "summary": summary,
        }


class MarketAnalysisTool:
    """Tool for market opportunity sizing, growth trends, and customer segmentation."""
    name: str = "market_analysis_tool"
    description: str = "Evaluates market size, CAGR, growth drivers, customer personas, pain points, and market attractiveness."

    def __init__(self, agent: Optional[MarketOpportunityAgent] = None):
        self._agent = agent or MarketOpportunityAgent()

    def run(self, idea: str, structured_idea: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        result = self._agent.analyze(
            idea=idea,
            structured_idea=structured_idea,
            sources=sources,
        )
        return result.model_dump()


class CompetitorAnalysisTool:
    """Tool for competitor discovery, classification, and comparison matrix generation."""
    name: str = "competitor_analysis_tool"
    description: str = "Identifies direct, indirect, and emerging competitors, generates comparison matrix, and uncovers market gaps."

    def __init__(self, agent: Optional[CompetitorAnalysisAgent] = None):
        self._agent = agent or CompetitorAnalysisAgent()

    def run(self, idea: str, structured_idea: Dict[str, Any], sources: List[Dict[str, Any]], market_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from schemas.validation_schemas import MarketAnalysisResult
        market_obj = MarketAnalysisResult(**market_analysis) if market_analysis else None
        result = self._agent.analyze(
            idea=idea,
            structured_idea=structured_idea,
            sources=sources,
            market_analysis=market_obj,
        )
        return result.model_dump()


class WhiteSpaceEngineTool:
    """Tool for synthesizing evidence-backed white space opportunities."""
    name: str = "white_space_engine_tool"
    description: str = "Discovers high-conviction white-space gaps by triangulating customer pain, competitor weaknesses, and startup capabilities."

    def __init__(self, engine: Optional[WhiteSpaceEngine] = None):
        self._engine = engine or WhiteSpaceEngine()

    def run(
        self,
        idea: str,
        structured_idea: Dict[str, Any],
        sources: List[Dict[str, Any]],
        market_analysis: Optional[Dict[str, Any]] = None,
        competitor_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        from schemas.validation_schemas import MarketAnalysisResult, CompetitorAnalysisResult
        market_obj = MarketAnalysisResult(**market_analysis) if market_analysis else None
        comp_obj = CompetitorAnalysisResult(**competitor_analysis) if competitor_analysis else None
        result = self._engine.discover(
            idea=idea,
            structured_idea=structured_idea,
            sources=sources,
            market_analysis=market_obj,
            competitor_analysis=comp_obj,
        )
        return result.model_dump()
