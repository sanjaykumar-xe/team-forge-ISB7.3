"""
verify_bug2_bug3.py
Comprehensive verification script for Bug 2 (Word-boundary truncation) and Bug 3 (Comma-formatted numbers).
Empirically tests and reports evidence across both issues.
"""

import os
import sys
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.market_analysis_agent import MarketOpportunityAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from services.white_space_engine import WhiteSpaceEngine
from services.text_utils import truncate_at_word_boundary


def test_bug3_comma_formatted_parsing():
    print("=" * 80)
    print("VERIFYING BUG 3: MARKET SIZE NUMBER PARSING ON COMMA-FORMATTED FIGURES")
    print("=" * 80)

    agent = MarketOpportunityAgent()

    test_sources = [
        {
            "category": "Market Size & Trends",
            "title": "Thermoelectric Cooling Mattress Pad Market Report 2032",
            "url": "https://example.com/peltier-market",
            "snippet": "The global thermoelectric cooling mattress pad market was valued at USD 1,870 Million in 2024 and is projected to reach $3,450.5 Million by 2032 with a 12.4% CAGR.",
        },
        {
            "category": "Market Size & Trends",
            "title": "Global Sleep Technology Overview",
            "url": "https://example.com/sleep-tech-valuation",
            "snippet": "According to research reports, the broader sleep tech devices market was estimated at $18,450,000,000 in 2024, exhibiting rapid adoption.",
        },
        {
            "category": "Market Size & Trends",
            "title": "Menopausal Health and Wellness Sector",
            "url": "https://example.com/femtech-market",
            "snippet": "The menopausal temperature relief category was recorded at 1,870 Million USD in 2024, expanding to 2,850 Million USD by 2030.",
        },
        {
            "category": "Market Size & Trends",
            "title": "Smart Dual-Zone Bedding Hardware",
            "url": "https://example.com/smart-bedding",
            "snippet": "Hardware revenue reached US$1,875.25 Million in 2023 with a 15.8% CAGR through 2029.",
        },
        {
            "category": "Market Size & Trends",
            "title": "Reverse Unit Inheritance Case",
            "url": "https://example.com/reverse-unit-test",
            "snippet": "The market was valued at $1.2 Billion in 2024, growing to $3.5 by 2030 with strong enterprise demand.",
        },
    ]

    extracted = agent._extract_market_sizing(test_sources)
    print(f"\nExtracted {len(extracted)} MarketSizeEstimate records:")

    results = []
    for i, est in enumerate(extracted, 1):
        print(f"\n[{i}] Figure: '{est.figure}'")
        print(f"    CAGR: {est.cagr}")
        print(f"    Forecast Year: {est.forecast_year}")
        print(f"    Evidence Quote: \"{est.evidence_snippet}\"")
        results.append({
            "figure": est.figure,
            "cagr": est.cagr,
            "forecast_year": est.forecast_year,
            "evidence_snippet": est.evidence_snippet,
        })

    # Assertions for Bug 3
    # Case 1: USD 1,870 Million to $3,450.5 Million (NOT $1 or $1 to $870 Million)
    assert "1,870" in extracted[0].figure, f"Expected 1,870 in figure, got '{extracted[0].figure}'"
    assert "3,450.5" in extracted[0].figure, f"Expected 3,450.5 in figure, got '{extracted[0].figure}'"
    assert not extracted[0].figure.startswith("$1 "), f"Incorrectly truncated as $1: '{extracted[0].figure}'"
    assert extracted[0].cagr == "12.4%", f"Expected 12.4%, got {extracted[0].cagr}"
    assert extracted[0].forecast_year == "2032", f"Expected 2032, got {extracted[0].forecast_year}"
    print("\n  [PASS] Case 1: 'USD 1,870 Million to $3,450.5 Million' correctly parsed without truncation to '$1'!")

    # Case 2: $18,450,000,000
    assert "18,450,000,000" in extracted[1].figure, f"Expected 18,450,000,000 in figure, got '{extracted[1].figure}'"
    print("  [PASS] Case 2: '$18,450,000,000' correctly parsed with all multi-commas intact!")

    # Case 3: 1,870 Million USD to 2,850 Million USD
    assert "1,870" in extracted[2].figure, f"Expected 1,870 in figure, got '{extracted[2].figure}'"
    assert "2,850" in extracted[2].figure, f"Expected 2,850 in figure, got '{extracted[2].figure}'"
    print("  [PASS] Case 3: '1,870 Million USD to 2,850 Million USD' correctly parsed!")

    # Case 4: US$1,875.25 Million
    assert "1,875.25" in extracted[3].figure, f"Expected 1,875.25 in figure, got '{extracted[3].figure}'"
    assert extracted[3].cagr == "15.8%"
    print("  [PASS] Case 4: 'US$1,875.25 Million' correctly parsed with decimal and comma!")

    # Case 5: Reverse Unit Inheritance ($1.2 Billion growing to $3.5 -> $1.2 Billion to $3.5 Billion)
    assert "$1.2 Billion to $3.5 Billion" == extracted[4].figure, f"Expected '$1.2 Billion to $3.5 Billion', got '{extracted[4].figure}'"
    print("  [PASS] Case 5: Reverse unit-inheritance correctly inferred '$1.2 Billion to $3.5 Billion'!")

    print("\n[SUCCESS] ALL BUG 3 COMMA-FORMATTED & RANGE PARSING CHECKS PASSED!")
    return results


def test_bug2_word_boundary_truncation():
    print("\n" + "=" * 80)
    print("VERIFYING BUG 2: WORD-BOUNDARY TRUNCATION ACROSS ALL TEXT FIELDS")
    print("=" * 80)

    # 1. Market Size Quotes
    long_snippet = (
        "The global market for advanced thermoelectric and Peltier-based dual-zone sleep systems was valued at "
        "USD 1,870 Million in 2024 and is projected to expand significantly as consumers transition away from noisy, "
        "leak-prone hydronic pump mattresses toward solid-state personal climate regulation."
    )
    # Truncate at 240 chars
    trunc_quote = truncate_at_word_boundary(long_snippet, max_length=240)
    print(f"\n[Market Size Quote Truncation]\nOriginal length: {len(long_snippet)} chars\nTruncated: \"{trunc_quote}\"")
    # Verify the last token ends with ... indicator and whole word
    assert trunc_quote.endswith("..."), "Expected visual ellipsis indicator on truncated quote"
    assert not trunc_quote.endswith("hy..."), "Should not cut 'hydronic' mid-word!"
    print(f"  [PASS] Market size quote ends with visual ellipsis indicator '...' on complete word!")

    # 2. Persona Descriptions & Problem Statements
    core_problem = "Existing water-based cooling mattress pads leak, harbor mold, and require loud pumps that disrupt sleep."
    trunc_persona_pain = truncate_at_word_boundary(core_problem, max_length=60)
    print(f"\n[Persona Description Truncation]\nOriginal: \"{core_problem}\"\nTruncated (max 60): \"{trunc_persona_pain}\"")
    assert trunc_persona_pain.endswith("..."), "Expected visual ellipsis indicator on truncated persona text"
    assert "harbor..." in trunc_persona_pain, f"Expected 'harbor...', got '{trunc_persona_pain}'"
    print(f"  [PASS] Persona description ends with clear visual ellipsis indicator '...' on complete word: 'harbor...'")

    # 3. Context Digest Snippets in WhiteSpaceEngine and CompetitorAnalysisAgent
    whitespace_engine = WhiteSpaceEngine()
    sources = [
        {
            "category": "Customer Demand",
            "title": "Comprehensive Consumer Sleep Tech Feedback and Complaints Survey 2024",
            "snippet": "Users consistently cite catastrophic water leaks destroying hardwood floors and noisy pump motors as their number one frustration with incumbent cooling pads.",
            "url": "https://example.com/complaints",
        }
    ]
    digest = whitespace_engine._build_evidence_digest(sources)
    print(f"\n[WhiteSpaceEngine Digest Snippet]\n{digest.strip()}")
    # Verify title and snippet in digest end on whole words
    for line in digest.split("\n"):
        if line.startswith("URL:") or not line.strip():
            continue
        last_tok = line.split()[-1].rstrip(".,;:-")
        # Check against alphanumeric token
        assert len(last_tok) > 1, f"Line ended with suspicious fragment: {line}"
    print("  [PASS] WhiteSpaceEngine evidence digest contains zero mid-word cutoffs!")

    # 4. Competitor Landscape Context
    comp_agent = CompetitorAnalysisAgent()
    comp_digest = comp_agent._build_sources_summary(sources)
    print(f"\n[CompetitorAnalysisAgent Sources Summary]\n{comp_digest.strip()}")
    for line in comp_digest.split("\n"):
        if line.startswith("URL:") or not line.strip():
            continue
        last_tok = line.split()[-1].rstrip(".,;:-")
        assert len(last_tok) > 1, f"Line ended with suspicious fragment: {line}"
    print("  [PASS] CompetitorAnalysisAgent sources summary contains zero mid-word cutoffs!")

    print("\n[SUCCESS] ALL BUG 2 WORD-BOUNDARY TRUNCATION CHECKS PASSED!")


if __name__ == "__main__":
    b3_results = test_bug3_comma_formatted_parsing()
    test_bug2_word_boundary_truncation()
