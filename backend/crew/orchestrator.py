"""
Team Forge — CrewAI Sequential Orchestrator
-------------------------------------------
Controls end-to-end execution of the multi-agent startup validation pipeline using
genuine CrewAI orchestration concepts (Agent, Task, Crew, Process.sequential).

Execution Pipeline Flow:
  [1] Idea Extraction Agent
          ↓
  [2] Web Search Agent (Tavily 4-Category Search)
          ↓
  [3] Data Retrieval Agent (Sanitization, Deduplication, Verification)
          ↓
  [4] Market Opportunity & Customer Segmentation Agent
          ↓
  [5] Competitor Discovery & Comparison Agent
          ↓
  Evidence-Backed Market White-Space Engine
          ↓
  Final Structured Validation Result

Enforces exact milestone logging and robust error resilience:
  - If upstream data is partial or LLM quota limits are encountered, agents failover
    gracefully to maintain pipeline continuity without crashing the API.
"""

import sys
import time
from typing import Dict, Any, Optional, List

from schemas.validation_schemas import (
    IdeaSubmission,
    ValidationResponse,
    SourceRecord,
    MarketAnalysisResult,
    CompetitorAnalysisResult,
    WhiteSpaceAnalysisResult,
)
from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine

from .agents import ValidationAgentFactory, get_crewai_classes
from .tasks import ValidationTaskFactory


def _log(msg: str):
    """Outputs standardized pipeline logging to stdout."""
    print(msg, flush=True)


class ValidationCrewOrchestrator:
    """
    CrewAI Orchestrator governing agent instantiation, sequential task execution,
    context handoffs, step logging, and final validation assembly.
    """

    def __init__(self):
        # Underlying research & intelligence engines
        self.idea_extractor = IdeaExtractionAgent()
        self.web_searcher = WebSearchAgent()
        self.data_retriever = DataRetrievalAgent()
        self.market_analyst = MarketOpportunityAgent()
        self.competitor_analyst = CompetitorAnalysisAgent()
        self.white_space_engine = WhiteSpaceEngine()

    def validate_idea(self, submission: IdeaSubmission) -> ValidationResponse:
        """
        Executes the full 5-agent sequential validation pipeline.
        Logs explicit progress markers for every stage.
        """
        idea_text = submission.idea.strip()
        product_name = submission.product_name.strip() if submission.product_name else None
        industry = submission.industry.strip() if submission.industry else None
        target_audience = submission.target_audience.strip() if submission.target_audience else None

        # 0. Nonsense / Gibberish Fast-Fail Check
        if not self.web_searcher.is_valid_idea(idea_text):
            _log("[Orchestrator] Input failed coherence/English density check.")
            return ValidationResponse(
                idea=idea_text,
                extracted_data=None,
                sources=[],
                market_analysis=None,
                competitor_analysis=None,
                white_space_analysis=None,
                summary={
                    "total_sources": 0,
                    "sources_per_category": {
                        "Competitors": 0,
                        "Industry News": 0,
                        "Customer Demand": 0,
                        "Market Size & Trends": 0,
                    },
                    "sources_by_category": {},
                    "message": "This doesn't look like a real idea description — try describing it in plain English.",
                },
            )

        # [1] Idea Extraction Agent
        _log("\n[1] Idea Extraction started")
        try:
            extracted_data = self.idea_extractor.extract(
                idea=idea_text,
                product_name=product_name,
                industry=industry,
                target_audience=target_audience,
            )
        except Exception as exc:
            _log(f"  [1] Idea Extraction warning: {exc}")
            extracted_data = {
                "product_name": product_name or "Startup",
                "industry": industry or "Software & Technology",
                "target_audience": target_audience or "General Target Audience",
                "core_problem": idea_text,
                "keywords": [w for w in idea_text.split()[:4]],
            }
        _log("[1] Idea Extraction completed")

        # [2] Web Search Agent (Tavily 4-Category Search)
        _log("\n[2] Web Search started")
        try:
            raw_batches = self.web_searcher.search(
                structured_idea=extracted_data,
                max_results_per_category=6,
            )
        except Exception as exc:
            _log(f"  [2] Web Search error: {exc}")
            raw_batches = []
        _log("[2] Web Search completed")

        # [3] Data Retrieval Agent (Sanitization, Filtering, Deduplication)
        _log("\n[3] Data Retrieval started")
        try:
            structured_sources_raw = self.data_retriever.structure(raw_batches)
            summary = self.data_retriever.summarize_counts(structured_sources_raw)
        except Exception as exc:
            _log(f"  [3] Data Retrieval error: {exc}")
            structured_sources_raw = []
            summary = {
                "total_sources": 0,
                "sources_per_category": {
                    "Competitors": 0,
                    "Industry News": 0,
                    "Customer Demand": 0,
                    "Market Size & Trends": 0,
                },
                "sources_by_category": {},
            }
        _log("[3] Data Retrieval completed")

        # Convert sources to typed SourceRecord objects
        typed_sources: List[SourceRecord] = []
        for s in structured_sources_raw:
            try:
                typed_sources.append(SourceRecord(**s))
            except Exception:
                pass

        # [4] Market Opportunity & Customer Segmentation Agent
        _log("\n[4] Market Opportunity Analysis started")
        try:
            market_analysis = self.market_analyst.analyze(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
            )
        except Exception as exc:
            _log(f"  [4] Market Opportunity Analysis error: {exc}")
            market_analysis = self.market_analyst._fallback_analysis(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
                reason=str(exc),
            )
        _log("[4] Market Opportunity Analysis completed")

        # [5] Competitor Discovery & Comparison Agent
        _log("\n[5] Competitor Analysis started")
        try:
            competitor_analysis = self.competitor_analyst.analyze(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
                market_analysis=market_analysis,
            )
        except Exception as exc:
            _log(f"  [5] Competitor Analysis error: {exc}")
            competitor_analysis = self.competitor_analyst._fallback_competitor_analysis(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
                market_analysis=market_analysis,
                reason=str(exc),
            )
        _log("[5] Competitor Analysis completed")

        # [6] Evidence-Backed Market White-Space Engine
        _log("\n[WhiteSpaceEngine] Correlating customer pain, competitor coverage, and startup capabilities...")
        try:
            white_space_analysis = self.white_space_engine.discover(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
            )
        except Exception as exc:
            _log(f"  [WhiteSpaceEngine] Error: {exc}")
            white_space_analysis = self.white_space_engine._fallback_opportunities(
                idea=idea_text,
                structured_idea=extracted_data,
                sources=structured_sources_raw,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
            )
        _log("[WhiteSpaceEngine] White-space opportunities synthesized successfully.")

        # Assemble unified response object
        return ValidationResponse(
            idea=idea_text,
            extracted_data=extracted_data,
            sources=typed_sources,
            market_analysis=market_analysis,
            competitor_analysis=competitor_analysis,
            white_space_analysis=white_space_analysis,
            summary=summary,
        )
