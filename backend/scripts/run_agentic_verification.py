import sys
import os
import json
import time

# Ensure UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend root is on sys.path and .env is loaded
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))
load_dotenv(os.path.join(backend_dir, "..", ".env"))

from schemas.validation_schemas import IdeaSubmission
from crew.orchestrator import ValidationCrewOrchestrator

def run_test(name: str, idea: str, product_name: str, industry: str, audience: str):
    print(f"\n" + "="*70)
    print(f"BENCHMARK TEST: {name}")
    print("="*70)
    
    orchestrator = ValidationCrewOrchestrator()
    submission = IdeaSubmission(
        idea=idea,
        product_name=product_name,
        industry=industry,
        target_audience=audience
    )
    
    start_time = time.time()
    response = orchestrator.validate_idea(submission)
    elapsed_time = time.time() - start_time
    
    # 1. Raw Tool-Call Trace
    tool_trace = response.summary.get("tool_call_trace", [])
    print(f"\n[A] RAW TOOL-CALL TRACE ({name}):")
    print(f"Wall-clock execution time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Total tools invoked: {len(tool_trace)}")
    for idx, call in enumerate(tool_trace, 1):
        print(f"  {idx}. Tool: [{call.get('tool')}] | Category: [{call.get('category')}]")
        print(f"     Query: \"{call.get('query')}\"")
        
    # 2. Search Breakdown & Providers
    print(f"\n[B] SOURCES BREAKDOWN ({name}):")
    print(f"Total sources retrieved: {len(response.sources)}")
    print(f"Per-category counts: {json.dumps(response.summary.get('sources_per_category', {}), indent=2)}")
    providers = {s.provider for s in response.sources if hasattr(s, 'provider') and s.provider}
    print(f"Distinct search providers: {providers}")
    
    # 3. Competitor Analysis Output
    print(f"\n[C] COMPETITOR ANALYSIS ({name}):")
    if response.competitor_analysis:
        comps = response.competitor_analysis.competitors
        print(f"Competitor count: {len(comps)}")
        for c in comps:
            print(f"  - [{c.classification.upper()}] {c.name}")
            print(f"    Core Offering: {c.core_offering}")
            print(f"    Positioning:   {c.positioning}")
            print(f"    Pricing:       {c.pricing}")
        if not comps:
            print("  (Empty competitor array — no direct commercial competitors found)")
        print(f"Market gaps ({len(response.competitor_analysis.market_gaps)}): {response.competitor_analysis.market_gaps[:2]}")
    else:
        print("Competitor analysis is None")
        
    # 4. Market Opportunity Analysis Output
    print(f"\n[D] MARKET OPPORTUNITY ANALYSIS ({name}):")
    if response.market_analysis:
        ms_list = response.market_analysis.market_size
        print(f"Market size estimates count: {len(ms_list)}")
        for ms in ms_list:
            print(f"  - Valuation: {ms.figure} | CAGR: {ms.cagr} | Forecast Year: {ms.forecast_year}")
            print(f"    Source URL: {ms.source_url}")
            print(f"    Evidence: {ms.evidence_snippet[:100] if ms.evidence_snippet else 'None'}...")
        if not ms_list:
            print("  (Empty market sizing array — no credible empirical reports found)")
        print(f"Confidence score: {response.market_analysis.confidence}")
    else:
        print("Market analysis is None")
        
    return {
        "name": name,
        "wall_clock_seconds": round(elapsed_time, 2),
        "tool_call_trace": tool_trace,
        "sources_count": len(response.sources),
        "sources_per_category": response.summary.get("sources_per_category", {}),
        "distinct_providers": list(providers),
        "competitors": [c.model_dump() for c in response.competitor_analysis.competitors] if response.competitor_analysis else [],
        "market_size": [m.model_dump() for m in response.market_analysis.market_size] if response.market_analysis else [],
        "confidence": response.market_analysis.confidence if response.market_analysis else None,
    }

if __name__ == "__main__":
    results = {}
    
    # Test 1: B2C Consumer Product (EcoClean Direct)
    results["ecoclean"] = run_test(
        name="EcoClean Direct (B2C)",
        idea="A subscription box service that delivers eco-friendly, zero-waste household cleaning supplies in refillable glass containers, with compostable packaging and customizable delivery schedules.",
        product_name="EcoClean Direct",
        industry="Eco-Friendly Household & Consumer Goods",
        audience="Environmentally conscious homeowners and zero-waste enthusiasts"
    )
    
    # Test 2: Ultra-Niche Artisanal Craft (KelpCraft)
    results["kelpcraft"] = run_test(
        name="KelpCraft (Ultra-Niche Craft)",
        idea="Handcrafted artisan sculptures carved exclusively from deep-sea dried kelp and sea kelp roots collected by freedivers in cold Alaskan fjords.",
        product_name="KelpCraft",
        industry="Artisan Marine Sculpture",
        audience="Luxury maritime art collectors"
    )
    
    # Test 3: Pure B2B Cleanroom Metrology (AuraSemicon)
    results["aurasemicon"] = run_test(
        name="AuraSemicon (Pure B2B Infrastructure)",
        idea="In-situ wafer defect metrology API using high-speed multi-beam electron scanning for semiconductor fabrication cleanrooms, integrating with fab MES systems to reduce yield ramp cycle times.",
        product_name="AuraSemicon",
        industry="Semiconductor Manufacturing & Metrology",
        audience="Semiconductor foundry process integration and yield engineering teams"
    )
    
    with open(os.path.join(backend_dir, "scripts", "agentic_verification_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print("\n" + "="*70)
    print("ALL 3 BENCHMARK TESTS COMPLETED. Saved to agentic_verification_results.json")
    print("="*70)
