import sys
import os
import json
import time
from pathlib import Path

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from schemas.validation_schemas import IdeaSubmission
from crew.orchestrator import ValidationCrewOrchestrator

TEST_CASES = [
    {
        "name": "GuardrailCI",
        "idea": "A CI/CD tool that automatically checks for security vulnerabilities without slowing down builds",
        "product_name": "GuardrailCI",
    },
    {
        "name": "CareerCraft AI",
        "idea": "An AI resume builder and career coach for college students",
        "product_name": "CareerCraft AI",
    },
    {
        "name": "dog walkers",
        "idea": "a mobile app that connects dog owners with local dog walkers",
        "product_name": None,
    },
    {
        "name": "HR SaaS",
        "idea": "a SaaS platform that helps HR teams automate employee onboarding",
        "product_name": None,
    },
    {
        "name": "save-money app",
        "idea": "an app that helps you save money by tracking your daily expenses",
        "product_name": None,
    },
    {
        "name": "gibberish test",
        "idea": "asdfkjhasdkjfh zxcvbnm qwertyuiop",
        "product_name": None,
    }
]

def main():
    print("=" * 80)
    print("RUNNING 5 REGRESSION IDEAS + GIBBERISH TEST")
    print("=" * 80)

    orchestrator = ValidationCrewOrchestrator()
    summary_report = []

    for idx, tc in enumerate(TEST_CASES, 1):
        name = tc["name"]
        idea = tc["idea"]
        prod = tc["product_name"]
        print(f"\n--- [{idx}/6] TESTING: {name} ---")
        print(f"Idea: '{idea}'")

        start = time.time()
        sub = IdeaSubmission(idea=idea, product_name=prod)
        resp = orchestrator.validate_idea(sub)
        duration = time.time() - start

        if name == "gibberish test":
            assert resp.summary["total_sources"] == 0, "Gibberish should have 0 sources"
            assert "plain English" in resp.summary.get("message", ""), "Gibberish should return plain English notice"
            assert resp.market_analysis is None, "Market analysis should be None for gibberish"
            assert resp.competitor_analysis is None, "Competitor analysis should be None for gibberish"
            assert resp.white_space_analysis is None, "White space analysis should be None for gibberish"
            print(f"[PASS] Gibberish correctly fast-failed in {duration:.2f}s: {resp.summary.get('message')}")
            summary_report.append({
                "test": name,
                "duration_seconds": round(duration, 2),
                "status": "rejected_as_gibberish",
                "total_sources": 0,
                "message": resp.summary.get("message")
            })
            continue

        # Valid idea assertions
        extracted = resp.extracted_data
        total_sources = resp.summary.get("total_sources", 0)
        sources_by_cat = resp.summary.get("sources_per_category", {})
        market_analysis = resp.market_analysis
        comp_analysis = resp.competitor_analysis
        ws_analysis = resp.white_space_analysis

        prod_name = extracted.get("product_name") if isinstance(extracted, dict) else getattr(extracted, "product_name", "Unknown")
        industry = extracted.get("industry") if isinstance(extracted, dict) else getattr(extracted, "industry", "Unknown")
        keywords = extracted.get("keywords", []) if isinstance(extracted, dict) else getattr(extracted, "keywords", [])

        print(f"Extraction: {prod_name} | {industry} | {keywords[:3]}")
        print(f"Sources: Total {total_sources} {sources_by_cat}")
        print(f"Market Sizing: {len(market_analysis.market_size)} figures, Confidence: {market_analysis.confidence}")
        print(f"Customer Segments: {len(market_analysis.customer_segments)}")
        print(f"Competitors: {len(comp_analysis.competitors)}, Matrix Rows: {len(comp_analysis.comparison_matrix)}")
        print(f"White-Space Opportunities: {len(ws_analysis.opportunities)}")
        print(f"Duration: {duration:.2f}s")

        # Structural integrity checks
        assert extracted is not None, "Extracted data must be present"
        assert total_sources > 0, "Should have retrieved sources"
        assert len(market_analysis.customer_segments) > 0, "Should have customer segments"
        assert len(comp_analysis.competitors) > 0, "Should have discovered competitors"
        assert len(ws_analysis.opportunities) > 0, "Should have white space opportunities"

        summary_report.append({
            "test": name,
            "product_name": prod_name,
            "industry": industry,
            "duration_seconds": round(duration, 2),
            "total_sources": total_sources,
            "sources_per_category": sources_by_cat,
            "market_figures_count": len(market_analysis.market_size),
            "market_confidence": market_analysis.confidence,
            "customer_segments_count": len(market_analysis.customer_segments),
            "sample_segment": market_analysis.customer_segments[0].segment_name if market_analysis.customer_segments else None,
            "competitors_count": len(comp_analysis.competitors),
            "sample_competitor": comp_analysis.competitors[0].name if comp_analysis.competitors else None,
            "whitespace_count": len(ws_analysis.opportunities),
            "sample_whitespace": ws_analysis.opportunities[0].opportunity_name if ws_analysis.opportunities else None
        })

    print("\n" + "=" * 80)
    print("ALL 6 REGRESSION TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(json.dumps(summary_report, indent=2))

if __name__ == "__main__":
    main()
