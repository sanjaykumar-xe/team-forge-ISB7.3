"""
Team Forge — CrewAI Orchestration Engine (Milestone 3)
-------------------------------------------------------
End-to-end multi-agent execution pipeline with 9 sequential stages:
  [1] Idea Extraction Agent (extracts structured metadata + extraction confidence)
  [2] Autonomous Market Research Agent (CrewAI Agent with tool calling & crew.kickoff())
  [3] Data Retrieval Agent (Deterministic sanitization, deduplication, categorization)
  [4] Market Opportunity & Customer Segmentation Agent (Market sizing, customer segments, attractiveness)
  [5] Competitor Discovery & Comparison Agent (Competitor profiling, capability matrix, gaps)
  [6] Evidence-Backed Market White-Space Engine (Triangulates pain, coverage, and capability)
  [7] SWOT & Risk Analysis Agent (Synthesizes judgment-driven SWOT matrix & risks)
  [8] MVP Recommendation Agent (Prioritized features with upstream justifications)
  [9] Go-To-Market Strategy Agent (Idea-specific channels, positioning, launch phases)
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from schemas.validation_schemas import (
    ValidationResponse,
    SourceRecord,
    MarketAnalysisResult,
    CompetitorAnalysisResult,
    WhiteSpaceAnalysisResult,
    SWOTAnalysisResult,
    MVPRecommendation,
    GTMStrategy,
)
from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine
from agents.swot_agent import SWOTAgent
from agents.mvp_agent import MVPAgent
from agents.gtm_agent import GTMAgent
from .agents import ValidationAgentFactory
from .tasks import ValidationTaskFactory

logger = logging.getLogger("team_forge.orchestrator")


class ValidationCrewOrchestrator:
    """Coordinates the 9-stage validation pipeline."""

    def __init__(self):
        self.idea_extractor = IdeaExtractionAgent()
        self.web_searcher = WebSearchAgent()
        self.data_retriever = DataRetrievalAgent()
        self.market_analyst = MarketOpportunityAgent()
        self.competitor_analyst = CompetitorAnalysisAgent()
        self.white_space_engine = WhiteSpaceEngine()
        self.swot_agent = SWOTAgent()
        self.mvp_agent = MVPAgent()
        self.gtm_agent = GTMAgent()

    def validate_idea(self, submission: Any) -> ValidationResponse:
        return self.run(
            idea_text=submission.idea,
            product_name=getattr(submission, 'product_name', None),
            industry=getattr(submission, 'industry', None),
            target_audience=getattr(submission, 'target_audience', None),
        )

    def run(
        self,
        idea_text: str,
        product_name: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> ValidationResponse:
        def _log(msg: str):
            logger.info(msg)
            if log_callback:
                try:
                    log_callback(msg)
                except Exception:
                    pass

        _log("=== Starting Team Forge Startup Validation Pipeline (Milestone 3) ===")

        # Fast heuristic check for non-idea input
        if len(idea_text.split()) < 3 and not product_name and not industry:
            _log("  Input contains too few words (< 3). Returning graceful empty response.")
            return ValidationResponse(
                idea=idea_text,
                extracted_data={
                    "product_name": "Unknown",
                    "industry": "Unknown",
                    "target_audience": "Unknown",
                    "core_problem": idea_text,
                    "keywords": [],
                    "extraction_confidence": "low",
                    "confidence_reason": "Idea text contains fewer than 3 words and no supplementary details were provided.",
                },
                sources=[],
                market_analysis=MarketAnalysisResult(
                    summary="Input text does not contain a discernible startup idea.",
                    analysis_status="completed",
                    message="Please provide a more detailed startup pitch.",
                ),
                competitor_analysis=CompetitorAnalysisResult(
                    summary="No competitors analyzed for uninterpretable input.",
                    analysis_status="completed",
                    message="Please provide a more detailed startup pitch.",
                ),
                white_space_analysis=WhiteSpaceAnalysisResult(
                    opportunities=[],
                    analysis_status="completed",
                    message="No white space opportunities can be synthesized from incomplete input.",
                ),
                swot_analysis=SWOTAnalysisResult(
                    strategic_recommendation="Cannot formulate SWOT analysis for uninterpretable input.",
                    analysis_status="completed",
                ),
                mvp_recommendation=MVPRecommendation(
                    mvp_thesis="Input too brief to recommend MVP features.",
                    analysis_status="completed",
                ),
                gtm_strategy=GTMStrategy(
                    positioning_statement="Input too brief to define GTM strategy.",
                    analysis_status="completed",
                ),
                summary={
                    "total_sources": 0,
                    "categories_searched": 0,
                    "tool_call_trace": [],
                    "counts": {
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
                "extraction_confidence": "low",
                "confidence_reason": f"Exception occurred during extraction: {exc}",
            }
        _log(f"[1] Idea Extraction completed (confidence: {extracted_data.get('extraction_confidence')})")

        # [2] Autonomous Market Research Agent (CrewAI Agent with tool calling & crew.kickoff())
        _log("\n[2] CrewAI Market Research Agent started (Autonomous Tool-Calling via crew.kickoff())")
        from .tools import MarketResearchToolKit
        from crewai import Crew, Process

        toolkit = MarketResearchToolKit(
            search_agent=self.web_searcher,
            retrieval_agent=self.data_retriever,
        )
        search_tools = toolkit.create_tools()

        def _step_callback(step: Any):
            if hasattr(step, "tool") and hasattr(step, "tool_input"):
                _log(f"  [MarketResearchAgent Tool Call] {step.tool}({step.tool_input})")
            elif hasattr(step, "output"):
                _log(f"  [MarketResearchAgent Step] {str(step.output)[:120]}...")

        research_agent = ValidationAgentFactory.create_market_research_agent(
            tools=search_tools,
            step_callback=_step_callback,
        )

        research_task = ValidationTaskFactory.create_market_research_task(
            agent=research_agent,
            idea=idea_text,
            structured_idea=extracted_data,
        )

        crew = Crew(
            agents=[research_agent],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            crew_result = crew.kickoff()
            _log(f"[2] CrewAI Market Research completed. Result: {str(crew_result)[:150]}...")
        except Exception as exc:
            _log(f"  [2] CrewAI kickoff error: {exc}. Using direct search fallback.")
            if not toolkit.collected_batches:
                fallback_batches = self.web_searcher.search(extracted_data, max_results_per_category=6)
                toolkit.collected_batches.extend(fallback_batches)

        # [3] Data Retrieval Agent (DETERMINISTIC NON-LLM STEP)
        _log("\n[3] Data Retrieval (Deterministic Sanitization, Filtering, Deduplication)")
        structured_sources_raw = toolkit.get_structured_sources()
        summary = toolkit.get_sources_summary()
        summary["tool_call_trace"] = toolkit.tool_call_trace
        _log(f"[3] Data Retrieval completed: {len(structured_sources_raw)} sanitized sources across categories.")
        _log(f"    Tool-call trace: {toolkit.tool_call_trace}")

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
                search_agent=self.web_searcher,
                tool_call_trace=toolkit.tool_call_trace,
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
                search_agent=self.web_searcher,
                tool_call_trace=toolkit.tool_call_trace,
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

        # Budget-limit annotations
        if toolkit.budget_limit_reached:
            _log("  [Orchestrator Notice] Flagging downstream results as budget-limited.")
            if market_analysis:
                if market_analysis.confidence and market_analysis.confidence > 0.60:
                    market_analysis.confidence = 0.60
                if hasattr(market_analysis, "growth_trends") and isinstance(market_analysis.growth_trends, list):
                    market_analysis.growth_trends.insert(
                        0,
                        f"[Budget Limited Note]: Search space was bounded by the maximum query limit ({toolkit.max_total_calls} calls). Evidence is preliminary."
                    )
            if competitor_analysis and hasattr(competitor_analysis, "market_gaps") and isinstance(competitor_analysis.market_gaps, list):
                competitor_analysis.market_gaps.insert(
                    0,
                    f"Search budget exhausted ({toolkit.max_total_calls} queries). Additional competitors or alternative solutions may exist beyond this bounded discovery set."
                )

        # [6] Evidence-Backed Market White-Space Engine
        _log("\n[6] WhiteSpaceEngine started")
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
        _log("[6] White-space opportunities synthesized successfully.")

        # [7] SWOT & Risk Analysis Agent (Milestone 3)
        _log("\n[7] SWOT & Risk Analysis started")
        try:
            swot_analysis = self.swot_agent.analyze(
                structured_idea=extracted_data,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
                white_space_analysis=white_space_analysis,
            )
        except Exception as exc:
            _log(f"  [7] SWOT Analysis error: {exc}")
            swot_analysis = self.swot_agent._fallback_analysis(str(exc))
        _log("[7] SWOT & Risk Analysis completed.")

        # [8] MVP Recommendation Agent (Milestone 3)
        _log("\n[8] MVP Feature Recommendation started")
        try:
            mvp_recommendation = self.mvp_agent.recommend(
                structured_idea=extracted_data,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
                white_space_analysis=white_space_analysis,
                swot_analysis=swot_analysis,
            )
        except Exception as exc:
            _log(f"  [8] MVP Recommendation error: {exc}")
            mvp_recommendation = self.mvp_agent._fallback_recommendation(str(exc))
        _log("[8] MVP Feature Recommendation completed.")

        # [9] Go-To-Market Strategy Agent (Milestone 3)
        _log("\n[9] Go-To-Market Strategy started")
        try:
            gtm_strategy = self.gtm_agent.strategize(
                structured_idea=extracted_data,
                market_analysis=market_analysis,
                competitor_analysis=competitor_analysis,
                white_space_analysis=white_space_analysis,
                swot_analysis=swot_analysis,
                mvp_recommendation=mvp_recommendation,
            )
        except Exception as exc:
            _log(f"  [9] Go-To-Market Strategy error: {exc}")
            gtm_strategy = self.gtm_agent._fallback_strategy(str(exc))
        _log("[9] Go-To-Market Strategy completed.")

        # Update summary with any additional tool calls made by downstream agents
        summary["tool_call_trace"] = toolkit.tool_call_trace

        # Assemble unified response object
        return ValidationResponse(
            idea=idea_text,
            extracted_data=extracted_data,
            sources=typed_sources,
            market_analysis=market_analysis,
            competitor_analysis=competitor_analysis,
            white_space_analysis=white_space_analysis,
            swot_analysis=swot_analysis,
            mvp_recommendation=mvp_recommendation,
            gtm_strategy=gtm_strategy,
            summary=summary,
        )
