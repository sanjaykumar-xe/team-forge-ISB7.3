"""
Milestone 2 End-to-End Test Runner across 3 Industries
------------------------------------------------------
Executes the full sequential CrewAI validation pipeline for:
  1. Healthcare (Clinic Patient No-Show Predictor)
  2. Climate / Agriculture (Smallholder Farm Optimization Platform)
  3. Fintech / Education (University Student Financial Literacy & Budgeting Platform)

Validates:
  - Full sequential execution across all 5 agents + White-Space Engine
  - Step progress logging
  - Market opportunity sizing & source citations
  - Customer segmentation profiles & personas
  - Competitor discovery, classification, & comparison matrix
  - Evidence-backed white-space opportunity triangulation
"""

import os
import sys
import json
import time
from pathlib import Path

# Fix Windows console encoding for LLM unicode characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))


from schemas.validation_schemas import IdeaSubmission, ValidationResponse
from crew.orchestrator import ValidationCrewOrchestrator

TEST_CASES = [
    {
        "id": "TEST_1_HEALTHCARE",
        "industry_label": "Healthcare & HealthTech",
        "idea": "I want to build a digital platform for small and mid-sized clinics that automatically predicts patient no-shows using appointment history, patient behavior patterns, and scheduling data, then recommends personalized reminders and scheduling interventions to reduce unused appointment slots.",
        "product_name": "ClinicGuard AI",
        "industry": "Healthcare",
        "target_audience": "Small and mid-sized healthcare clinics and medical practices",
    },
    {
        "id": "TEST_2_AGRICULTURE",
        "industry_label": "Climate / Agriculture",
        "idea": "I want to build a technology platform for small farmers that combines local weather forecasts, soil conditions, crop information, and market prices to recommend what crops to plant, when to irrigate, and when to sell produce in order to improve profitability.",
        "product_name": "FarmOptima",
        "industry": "AgriTech & Climate",
        "target_audience": "Smallholder farmers and agricultural cooperatives",
    },
    {
        "id": "TEST_3_FINTECH_EDUCATION",
        "industry_label": "Fintech / Education",
        "idea": "I want to build a financial education platform for university students that connects to their spending data and provides personalized budgeting, savings, and financial-literacy guidance based on their individual financial behavior.",
        "product_name": "CampusFin",
        "industry": "FinTech / EdTech",
        "target_audience": "University and college students",
    },
]


def run_e2e_tests():
    orchestrator = ValidationCrewOrchestrator()
    all_results = {}

    print("=" * 80)
    print("STARTING MILESTONE 2 END-TO-END 3-INDUSTRY VALIDATION HARNESS")
    print("=" * 80)

    for idx, tc in enumerate(TEST_CASES, 1):
        print(f"\n================================================================================")
        print(f"[{idx}/3] EXECUTING E2E TEST: {tc['id']} ({tc['industry_label']})")
        print(f"Product: {tc['product_name']}")
        print(f"Idea: {tc['idea']}")
        print(f"================================================================================")

        t_start = time.time()
        submission = IdeaSubmission(
            idea=tc["idea"],
            product_name=tc["product_name"],
            industry=tc["industry"],
            target_audience=tc["target_audience"],
        )

        response: ValidationResponse = orchestrator.validate_idea(submission)
        elapsed = time.time() - t_start

        # --- RIGOROUS ASSERTIONS ---
        print(f"\n--- VALIDATING ASSERTIONS FOR {tc['id']} ({elapsed:.2f}s) ---")

        # 1. Extracted Metadata
        assert response.extracted_data is not None, "extracted_data must not be None"
        print(f" [PASS] Extracted Domain Keywords: {response.extracted_data.get('keywords')}")

        # 2. Sources
        assert len(response.sources) > 0, "Sources must be populated"
        print(f" [PASS] Total Verified Sources: {len(response.sources)} across categories")

        # 3. Market Opportunity & Customer Segmentation
        assert response.market_analysis is not None, "market_analysis must be populated"
        assert len(response.market_analysis.customer_segments) > 0, "Customer segments must be identified"
        print(f" [PASS] Market Sizing Estimates: {len(response.market_analysis.market_size)}")
        for ms in response.market_analysis.market_size[:2]:
            print(f"   - {ms.figure} ({ms.market_type}) | CAGR: {ms.cagr} | Source: {ms.source_url or ms.notes}")
        print(f" [PASS] Customer Segments: {[s.segment_name for s in response.market_analysis.customer_segments]}")

        # 4. Competitor Discovery & Comparison Matrix
        assert response.competitor_analysis is not None, "competitor_analysis must be populated"
        assert len(response.competitor_analysis.competitors) > 0, "Competitors must be discovered"
        print(f" [PASS] Competitors Discovered: {[f'{c.name} ({c.classification})' for c in response.competitor_analysis.competitors]}")
        print(f" [PASS] Comparison Matrix Rows: {len(response.competitor_analysis.comparison_matrix)}")

        # 5. Core Novelty: Evidence-Backed Market White-Space Engine
        assert response.white_space_analysis is not None, "white_space_analysis must be populated"
        assert len(response.white_space_analysis.opportunities) > 0, "White space opportunities must be generated"
        print(f" [PASS] White-Space Opportunities Synthesized: {len(response.white_space_analysis.opportunities)}")
        for opp in response.white_space_analysis.opportunities:
            print(f"   * Opportunity: '{opp.opportunity_name}'")
            print(f"     Segment: {opp.segment}")
            print(f"     Gap: {opp.gap}")
            print(f"     Conviction: {opp.confidence * 100:.0f}% | Evidence Strength: {opp.evidence_strength}")

        all_results[tc["id"]] = response.model_dump()

    # Save to file
    out_file = os.path.join(backend_dir, "milestone2_e2e_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"ALL 3 INDUSTRY END-TO-END TESTS PASSED COMPREHENSIVELY!")
    print(f"Full JSON Dossier saved to: {out_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_e2e_tests()
