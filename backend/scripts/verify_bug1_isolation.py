"""
verify_bug1_isolation.py
Comprehensive verification script for Bug 1 (Cross-request contamination & honest fallback).
Tests CortexLocal and SolidSleep Zero across both Normal LLM and Forced-Fallback paths.
Checks for zero EcoClean phrases, zero fabricated white-space opportunities,
and honest processing_error status with null confidence when fallback is triggered.
"""

import os
import sys
import json
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine
from schemas.validation_schemas import MarketAnalysisResult, WhiteSpaceAnalysisResult

FORBIDDEN_ECOCLEAN_PHRASES = [
    "refill habits",
    "eco-friendly supplies and refills",
    "single-use plastics",
    "refillable packaging",
    "packaging waste",
    "zero-waste",
    "refillable hardware",
    "excess packaging waste",
]

FORBIDDEN_FABRICATED_WHITESPACE_PHRASES = [
    "static visual dashboards",
    "closed-loop execution layer",
    "Automated Intelligence for Underserved",
    "Actionable Decision Support & Workflow Automation",
]

TEST_IDEAS = [
    {
        "name": "CortexLocal",
        "idea": (
            "CortexLocal: An entirely on-device, zero-cloud personal AI second brain and local knowledge workspace. "
            "It runs open-weight quantized models on local consumer hardware (Mac M-series and RTX PCs), indexes personal "
            "markdown notes, PDFs, and browser history locally, and ensures zero telemetry, zero vector database exfiltration, "
            "and full operational capability completely offline."
        ),
        "structured": {
            "product_name": "CortexLocal",
            "industry": "Personal Knowledge Management & Local AI",
            "target_audience": "Privacy-conscious developers, researchers, and knowledge workers",
            "core_problem": "Privacy violations, subscription lock-in, and cloud exfiltration in modern AI productivity tools.",
            "keywords": ["local AI", "on-device LLM", "privacy PKM", "offline second brain"],
        },
        "mock_sources": [
            {
                "category": "Market Size & Trends",
                "title": "On-Device AI Market Valuation Report 2030",
                "url": "https://example.com/on-device-ai",
                "snippet": "The global on-device AI market size was estimated at USD 14.5 Billion in 2024 and projected to reach USD 78.2 Billion by 2032 with a 23.4% CAGR.",
                "score": 0.92,
            },
            {
                "category": "Competitors",
                "title": "Obsidian Local Notes App and Plugins",
                "url": "https://obsidian.md",
                "snippet": "Obsidian is a private, local-first note-taking tool that stores markdown files directly on device.",
                "score": 0.88,
            },
            {
                "category": "Customer Demand",
                "title": "User discussions on private local LLM search",
                "url": "https://reddit.com/r/localllama",
                "snippet": "Users demand complete privacy for personal financial documents and proprietary code when using LLM assistance.",
                "score": 0.85,
            },
        ],
    },
    {
        "name": "SolidSleep Zero",
        "idea": (
            "SolidSleep Zero: An active solid-state Peltier thermoelectric cooling and dual-zone temperature regulation "
            "mattress pad for menopausal night sweats and athletic recovery, eliminating water leaks and noisy pumps."
        ),
        "structured": {
            "product_name": "SolidSleep Zero",
            "industry": "Sleep Technology & Smart Home Health",
            "target_audience": "Menopausal women suffering from night sweats and athletes requiring active recovery",
            "core_problem": "Existing water-based cooling mattress pads leak, harbor mold, and require loud pumps that disrupt sleep.",
            "keywords": ["Peltier cooling mattress", "solid-state sleep pad", "menopausal night sweats", "dual-zone bed temperature"],
        },
        "mock_sources": [
            {
                "category": "Market Size & Trends",
                "title": "Sleep Tech Devices Market Size and Forecast 2032",
                "url": "https://example.com/sleep-tech",
                "snippet": "The global sleep tech devices market is projected to reach $68.5 Billion by 2030, growing at a 17.8% CAGR driven by smart mattress pads.",
                "score": 0.94,
            },
            {
                "category": "Competitors",
                "title": "Eight Sleep Pod - Smart Temperature Mattress Cover",
                "url": "https://eightsleep.com",
                "snippet": "Eight Sleep uses water-circulating hydro-powered pods for dual-zone temperature regulation.",
                "score": 0.91,
            },
            {
                "category": "Customer Demand",
                "title": "Sleep forum feedback on water cooling mattress pads",
                "url": "https://reddit.com/r/sleep",
                "snippet": "Users report repeated pump failures and water leaks ruining expensive mattresses after 18 months of use.",
                "score": 0.89,
            },
        ],
    },
]


def check_forbidden_phrases(obj: Any, forbidden: List[str], context: str) -> List[str]:
    """Recursively search any string in obj for forbidden phrases."""
    text_corpus = json.dumps(obj if isinstance(obj, (dict, list)) else obj.model_dump(), default=str).lower()
    violations = []
    for phrase in forbidden:
        if phrase.lower() in text_corpus:
            violations.append(f"[{context}] Found forbidden phrase: '{phrase}'")
    return violations


def run_verification():
    print("=" * 80)
    print("STARTING BUG 1 ISOLATION VERIFICATION")
    print("=" * 80)

    market_agent = MarketOpportunityAgent()
    comp_agent = CompetitorAnalysisAgent()
    whitespace_engine = WhiteSpaceEngine()

    all_passed = True
    results_summary = []

    for test_case in TEST_IDEAS:
        name = test_case["name"]
        idea_text = test_case["idea"]
        struct = test_case["structured"]
        sources = test_case["mock_sources"]

        print(f"\n[{name}] Running verification tests...")

        # -------------------------------------------------------------
        # TEST 1: FORCED FALLBACK PATH
        # -------------------------------------------------------------
        print(f"  --> Testing FORCED FALLBACK PATH for {name}...")
        fb_market = market_agent._fallback_analysis(
            idea=idea_text,
            structured_idea=struct,
            sources=sources,
            reason="Forced verification test: Groq API 429 timeout simulation",
        )
        fb_comp = comp_agent._fallback_competitor_analysis(
            idea=idea_text,
            structured_idea=struct,
            sources=sources,
            market_analysis=fb_market,
            reason="Forced verification test",
        )
        fb_ws = whitespace_engine._fallback_opportunities(
            idea=idea_text,
            structured_idea=struct,
            sources=sources,
            market_analysis=fb_market,
            competitor_analysis=fb_comp,
            reason="Forced verification test: LLM token limit error simulation",
        )

        # 1. Market Opportunity Fallback assertions
        m_violations = check_forbidden_phrases(fb_market, FORBIDDEN_ECOCLEAN_PHRASES, f"{name} Market Fallback")
        if m_violations:
            for v in m_violations:
                print(f"    FAIL: {v}")
            all_passed = False
        else:
            print(f"    PASS: Zero EcoClean phrases in {name} market fallback.")

        assert fb_market.analysis_status == "processing_error", f"Expected processing_error, got {fb_market.analysis_status}"
        assert fb_market.confidence is None, f"Expected confidence None, got {fb_market.confidence}"
        assert len(fb_market.customer_segments) == 0, f"Expected 0 customer_segments, got {len(fb_market.customer_segments)}"
        assert len(fb_market.growth_trends) == 0, f"Expected 0 growth_trends, got {len(fb_market.growth_trends)}"
        assert fb_market.attractiveness is None, f"Expected attractiveness None, got {fb_market.attractiveness}"
        assert "LLM processing error" in (fb_market.message or ""), "Expected diagnostic message in market fallback"
        print(f"    PASS: Market fallback correctly returned processing_error with confidence=None and 0 fabricated segments.")

        # 2. White Space Fallback assertions
        ws_violations = check_forbidden_phrases(fb_ws, FORBIDDEN_FABRICATED_WHITESPACE_PHRASES, f"{name} WhiteSpace Fallback")
        if ws_violations:
            for v in ws_violations:
                print(f"    FAIL: {v}")
            all_passed = False
        else:
            print(f"    PASS: Zero fabricated SaaS phrases in {name} white space fallback.")

        assert fb_ws.analysis_status == "processing_error", f"Expected processing_error, got {fb_ws.analysis_status}"
        assert len(fb_ws.opportunities) == 0, f"Expected 0 opportunities, got {len(fb_ws.opportunities)}"
        assert "temporary processing error" in (fb_ws.message or ""), "Expected diagnostic message in white space fallback"
        print(f"    PASS: WhiteSpace fallback correctly returned processing_error with 0 fabricated opportunities.")

        # -------------------------------------------------------------
        # TEST 2: NORMAL LLM PATH
        # -------------------------------------------------------------
        print(f"\n  --> Testing NORMAL LLM PATH for {name}...")
        try:
            live_market = market_agent.analyze(
                idea=idea_text,
                structured_idea=struct,
                sources=sources,
            )
            print(f"    Market Analysis LLM status: {live_market.analysis_status} (confidence: {live_market.confidence})")
            
            # Check for contamination in normal output as well
            live_m_violations = check_forbidden_phrases(live_market, FORBIDDEN_ECOCLEAN_PHRASES, f"{name} Live Market")
            if live_m_violations:
                for v in live_m_violations:
                    print(f"    FAIL: {v}")
                all_passed = False
            else:
                print(f"    PASS: Zero EcoClean phrases in live {name} market analysis.")

            assert live_market.analysis_status == "completed", f"Expected completed, got {live_market.analysis_status}"
            assert len(live_market.customer_segments) > 0, "Expected customer segments generated by LLM"
            print(f"    PASS: Live market analysis generated {len(live_market.customer_segments)} segments without token cutoff.")

            # Live WhiteSpace
            live_comp = comp_agent.analyze(
                idea=idea_text,
                structured_idea=struct,
                sources=sources,
                market_analysis=live_market,
            )
            live_ws = whitespace_engine.discover(
                idea=idea_text,
                structured_idea=struct,
                sources=sources,
                market_analysis=live_market,
                competitor_analysis=live_comp,
            )
            print(f"    WhiteSpace Engine LLM status: {live_ws.analysis_status} (opportunities: {len(live_ws.opportunities)})")

            live_ws_violations = check_forbidden_phrases(live_ws, FORBIDDEN_FABRICATED_WHITESPACE_PHRASES, f"{name} Live WhiteSpace")
            if live_ws_violations:
                for v in live_ws_violations:
                    print(f"    FAIL: {v}")
                all_passed = False
            else:
                print(f"    PASS: Zero fabricated boilerplate phrases in live {name} white space.")

            assert live_ws.analysis_status == "completed", f"Expected completed, got {live_ws.analysis_status}"
            assert len(live_ws.opportunities) > 0, "Expected white-space opportunities generated by LLM"
            print(f"    PASS: Live white space generated {len(live_ws.opportunities)} valid opportunities.")

            results_summary.append({
                "name": name,
                "forced_fallback": {
                    "market_status": fb_market.analysis_status,
                    "market_confidence": fb_market.confidence,
                    "market_segments_count": len(fb_market.customer_segments),
                    "whitespace_status": fb_ws.analysis_status,
                    "whitespace_opportunities_count": len(fb_ws.opportunities),
                    "ecoclean_phrases_found": len(m_violations),
                    "fabricated_whitespace_phrases_found": len(ws_violations),
                },
                "normal_llm": {
                    "market_status": live_market.analysis_status,
                    "market_confidence": live_market.confidence,
                    "market_segments_count": len(live_market.customer_segments),
                    "sample_segment": live_market.customer_segments[0].segment_name if live_market.customer_segments else None,
                    "whitespace_status": live_ws.analysis_status,
                    "whitespace_opportunities_count": len(live_ws.opportunities),
                    "sample_opportunity": live_ws.opportunities[0].opportunity_name if live_ws.opportunities else None,
                    "ecoclean_phrases_found": len(live_m_violations),
                    "fabricated_whitespace_phrases_found": len(live_ws_violations),
                }
            })

        except Exception as e:
            print(f"    ERROR during live LLM execution: {e}")
            all_passed = False

    print("\n" + "=" * 80)
    print("VERIFICATION RUN SUMMARY")
    print("=" * 80)
    print(json.dumps(results_summary, indent=2))

    if all_passed:
        print("\n[SUCCESS] ALL BUG 1 ISOLATION CHECKS PASSED PERFECTLY!")
        sys.exit(0)
    else:
        print("\n[FAILURE] ONE OR MORE VERIFICATION CHECKS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    run_verification()
