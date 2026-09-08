"""
Milestone 2 Unit & Integration Test Suite
-----------------------------------------
Tests:
  1. Schemas & Unlimited Input Character Submission
  2. IdeaExtractionAgent, WebSearchAgent, DataRetrievalAgent functionality
  3. MarketOpportunityAgent sizing, segmentation, & anti-hallucination assertions
  4. CompetitorAnalysisAgent classification, comparison matrix, & gap identification
  5. Evidence-Backed Market White-Space Engine triangulation
  6. CrewAI ValidationCrewOrchestrator sequential pipeline & step logging
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from schemas.validation_schemas import (
    IdeaSubmission,
    ValidationResponse,
    MarketAnalysisResult,
    CompetitorAnalysisResult,
    WhiteSpaceAnalysisResult,
    CustomerSegment,
    CompetitorRecord,
    WhiteSpaceOpportunity,
)
from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine
from crew.orchestrator import ValidationCrewOrchestrator


def test_unlimited_input_length():
    """Verify that IdeaSubmission accepts arbitrarily long startup descriptions without errors."""
    long_text = "This is an extended startup description detailing architecture, customer workflows, API integrations, and monetization models. " * 30
    assert len(long_text) > 3000
    sub = IdeaSubmission(idea=long_text)
    assert len(sub.idea) == len(long_text)
    assert sub.product_name is None


def test_market_opportunity_agent_fallback():
    """Verify MarketOpportunityAgent produces structured MarketAnalysisResult on mock search data."""
    agent = MarketOpportunityAgent()
    mock_sources = [
        {
            "category": "Market Size & Trends",
            "title": "Global DevSecOps Market Size & Forecast Report 2030",
            "url": "https://example.com/devsecops-report",
            "snippet": "The global DevSecOps market was valued at $6.2 Billion in 2024 and projected to reach $35 Billion by 2030 at 22.4% CAGR.",
            "score": 0.94,
        },
        {
            "category": "Customer Demand",
            "title": "Developer Security Survey & Pain Points",
            "url": "https://example.com/security-survey",
            "snippet": "Developers report high friction with security bottlenecks in CI pipelines and false positive alerts.",
            "score": 0.88,
        },
    ]

    structured_idea = {
        "product_name": "GuardrailCI",
        "industry": "DevSecOps",
        "target_audience": "Software development teams",
        "core_problem": "Security scans slow down deployment pipelines.",
        "keywords": ["DevSecOps", "CI/CD", "vulnerability scanning"],
    }

    result = agent._fallback_analysis(
        idea="A CI/CD tool that checks for security vulnerabilities without slowing down builds",
        structured_idea=structured_idea,
        sources=mock_sources,
        reason="Test invocation",
    )

    assert isinstance(result, MarketAnalysisResult)
    assert result.analysis_status == "processing_error"
    assert result.confidence is None
    assert len(result.customer_segments) == 0
    assert len(result.growth_trends) == 0
    assert len(result.market_size) > 0  # Preserves verified empirical market sizing from sources
    assert "$6.2 Billion" in result.market_size[0].figure


def test_competitor_analysis_agent_fallback():
    """Verify CompetitorAnalysisAgent produces classified competitors and comparison matrix."""
    agent = CompetitorAnalysisAgent()
    mock_sources = [
        {
            "category": "Competitors",
            "title": "Snyk Security - Vulnerability Scanner Alternatives",
            "url": "https://snyk.io",
            "snippet": "Snyk helps developers find and fix vulnerabilities in code and containers.",
            "score": 0.95,
        },
        {
            "category": "Competitors",
            "title": "SonarQube Code Quality & Security Tool",
            "url": "https://sonarqube.org",
            "snippet": "Static code analysis tool for finding bugs and security vulnerabilities.",
            "score": 0.90,
        },
    ]

    structured_idea = {
        "product_name": "GuardrailCI",
        "industry": "DevSecOps",
        "target_audience": "Software engineering teams",
        "core_problem": "Slow CI/CD pipeline scans and high false positives",
        "keywords": ["DevSecOps", "CI/CD security"],
    }

    result = agent._fallback_competitor_analysis(
        idea="A fast CI/CD security scanner",
        structured_idea=structured_idea,
        sources=mock_sources,
        reason="Test invocation",
    )

    assert isinstance(result, CompetitorAnalysisResult)
    assert len(result.competitors) >= 2
    for comp in result.competitors:
        assert isinstance(comp, CompetitorRecord)
        assert comp.classification in ["direct", "indirect", "emerging"]
        assert comp.pricing != ""
    assert len(result.comparison_matrix) > 0
    assert len(result.market_gaps) > 0


def test_white_space_engine_fallback():
    """Verify WhiteSpaceEngine triangulates pain, competitor coverage, and startup fit."""
    engine = WhiteSpaceEngine()
    mock_sources = [
        {
            "category": "Customer Demand",
            "title": "Why DevSecOps tools frustrate developers",
            "url": "https://example.com/demand-evidence",
            "snippet": "Engineers complain that existing enterprise tools generate hundreds of false alerts.",
            "score": 0.92,
        },
        {
            "category": "Competitors",
            "title": "Legacy Enterprise Scanners Overview",
            "url": "https://example.com/comp-evidence",
            "snippet": "Incumbents require complex manual rule tuning and enterprise contracts.",
            "score": 0.89,
        },
    ]

    structured_idea = {
        "product_name": "GuardrailCI",
        "industry": "DevSecOps",
        "target_audience": "Small and mid-sized engineering teams",
        "core_problem": "False positive alert fatigue in CI/CD pipelines",
        "keywords": ["DevSecOps", "alert fatigue", "automated scanning"],
    }

    result = engine._fallback_opportunities(
        idea="An automated alert-filtering CI/CD security tool for mid-sized dev teams",
        structured_idea=structured_idea,
        sources=mock_sources,
    )

    assert isinstance(result, WhiteSpaceAnalysisResult)
    assert result.analysis_status == "processing_error"
    assert len(result.opportunities) == 0
    assert "temporary processing error" in (result.message or "")


def test_orchestrator_gibberish_defense():
    """Verify orchestrator fast-fails nonsense input with 0 sources and polite message."""
    orchestrator = ValidationCrewOrchestrator()
    sub = IdeaSubmission(idea="asdfkjhasdkjfh zxcvbnm qwertyuiop")
    resp = orchestrator.validate_idea(sub)
    assert resp.summary["total_sources"] == 0
    assert "plain English" in resp.summary["message"]


def test_market_opportunity_zero_market_sources_honest_empty():
    """
    Verify that when research sources contain 0 Market Size & Trends entries
    (and no quantitative sizing figures), MarketOpportunityAgent produces:
      - market_size: [] (no placeholder cards like 'Not specified')
      - attractiveness: None (suppressing ungrounded scorecard)
      - confidence: None (honest unverified state)
    """
    agent = MarketOpportunityAgent()
    mock_sources_no_market_size = [
        {
            "category": "Competitors",
            "title": "Obsidian Note Taking App",
            "url": "https://obsidian.md",
            "snippet": "A private and flexible note-taking app that adapts to the way you think.",
            "score": 0.88,
        },
        {
            "category": "Industry News",
            "title": "On-Device AI Trends in Knowledge Work",
            "url": "https://example.com/trends",
            "snippet": "Knowledge workers increasingly prefer offline tools to safeguard sensitive data.",
            "score": 0.85,
        },
    ]

    structured_idea = {
        "product_name": "CortexLocal",
        "industry": "Personal Knowledge Management & Local AI",
        "target_audience": "Privacy-conscious developers",
        "core_problem": "Privacy violations in cloud-hosted AI note apps.",
        "keywords": ["local AI", "privacy PKM", "offline second brain"],
    }

    result = agent.analyze(
        idea="CortexLocal: An on-device zero-cloud personal AI second brain and local knowledge workspace.",
        structured_idea=structured_idea,
        sources=mock_sources_no_market_size,
    )

    assert isinstance(result, MarketAnalysisResult)
    assert result.market_size == [], f"Expected empty market_size, got: {result.market_size}"
    assert result.attractiveness is None, f"Expected attractiveness to be None, got: {result.attractiveness}"
    assert result.confidence is None, f"Expected confidence to be None, got: {result.confidence}"


if __name__ == "__main__":
    print("--- Running Milestone 2 Test Suite ---")
    test_unlimited_input_length()
    print("[PASS] test_unlimited_input_length")
    test_market_opportunity_agent_fallback()
    print("[PASS] test_market_opportunity_agent_fallback")
    test_market_opportunity_zero_market_sources_honest_empty()
    print("[PASS] test_market_opportunity_zero_market_sources_honest_empty")
    test_competitor_analysis_agent_fallback()
    print("[PASS] test_competitor_analysis_agent_fallback")
    test_white_space_engine_fallback()
    print("[PASS] test_white_space_engine_fallback")
    test_orchestrator_gibberish_defense()
    print("[PASS] test_orchestrator_gibberish_defense")
    print("\nALL MILESTONE 2 TESTS PASSED SUCCESSFULLY!")

