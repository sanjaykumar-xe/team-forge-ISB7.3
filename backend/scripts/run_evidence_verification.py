import sys
import os
import json

# Ensure UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend root is on sys.path and backend/.env is loaded
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.competitor_analysis_agent import CompetitorAnalysisAgent
from agents.market_analysis_agent import MarketOpportunityAgent

def run_test_case(name: str, idea: str, product_name: str, industry: str, audience: str):
    print(f"\n=======================================================")
    print(f"TEST CASE: {name}")
    print(f"=======================================================")
    
    # 1. Extraction
    iea = IdeaExtractionAgent()
    extracted = iea.extract(
        idea=idea,
        product_name=product_name,
        industry=industry,
        target_audience=audience,
    )
    print(f"\n[1] EXTRACTED METADATA:")
    print(json.dumps(extracted, indent=2))
    
    # 2. Search
    wsa = WebSearchAgent()
    queries = wsa.build_queries(extracted)
    print(f"\n[2] GENERATED QUERIES:")
    print(json.dumps(queries, indent=2))
    
    raw_batches = wsa.search(extracted, max_results_per_category=6)
    
    # 3. Retrieval & Categorization
    dra = DataRetrievalAgent()
    structured = dra.structure(raw_batches)
    counts = dra.summarize_counts(structured)
    
    print(f"\n[3] SEARCH RESULTS BREAKDOWN:")
    print(f"Total structured sources returned: {len(structured)}")
    print(f"Per category: {json.dumps(counts['sources_per_category'], indent=2)}")
    
    print(f"\n[4] SOURCES WITH PROVIDER LABELS (Sample up to 2 per category):")
    by_cat = {}
    for s in structured:
        by_cat.setdefault(s["category"], []).append(s)
        
    for cat, items in by_cat.items():
        print(f"\n--- Category: {cat} ({len(items)} sources) ---")
        for it in items[:2]:
            print(f"  * Provider: [{it.get('provider')}] | Score: {it.get('score')}")
            print(f"    Title: {it.get('title')}")
            print(f"    URL:   {it.get('url')}")
            
    # Check providers
    providers = {s.get("provider") for s in structured}
    print(f"\nDistinct search providers in results: {providers}")
    
    # 4. Competitor Analysis
    caa = CompetitorAnalysisAgent()
    comp_res = caa.analyze(idea, extracted, structured)
    print(f"\n[5] COMPETITOR ANALYSIS:")
    print(f"Competitors count: {len(comp_res.competitors)}")
    for c in comp_res.competitors:
        print(f"  - Competitor: {c.name} ({c.classification}) | Positioning: {c.positioning}")
        print(f"    Core offering: {c.core_offering}")
        print(f"    Source: {getattr(c, 'source_url', 'N/A')}")
    if not comp_res.competitors:
        print("  - (No competitors detected; fallback empty state correctly preserved)")
    if hasattr(comp_res, 'empty_notice') and comp_res.empty_notice:
        print(f"  - Empty notice: {comp_res.empty_notice}")
        
    # 5. Market Opportunity Analysis
    moa = MarketOpportunityAgent()
    market_res = moa.analyze(idea, extracted, structured)
    print(f"\n[6] MARKET OPPORTUNITY ANALYSIS:")
    print(f"Market size estimates count: {len(market_res.market_size)}")
    for ms in market_res.market_size:
        print(f"  - Valuation: {ms.figure} | CAGR: {ms.cagr} | Forecast Year: {ms.forecast_year}")
        print(f"    Source URL: {ms.source_url}")
        print(f"    Evidence: {ms.evidence_snippet[:120] if ms.evidence_snippet else 'None'}...")
    if not market_res.market_size:
        print("  - (No market sizing figures detected; fallback empty state correctly preserved)")
    print(f"Confidence score: {market_res.confidence}")
    if hasattr(market_res, 'empty_notice') and market_res.empty_notice:
        print(f"  - Empty notice: {market_res.empty_notice}")
        
    return {
        "extracted": extracted,
        "structured": structured,
        "competitors": [c.model_dump() for c in comp_res.competitors],
        "market_size": [m.model_dump() for m in market_res.market_size],
        "confidence": market_res.confidence,
    }

if __name__ == "__main__":
    # Test 1: EcoClean Direct
    ecoclean_res = run_test_case(
        name="EcoClean Direct",
        idea="A subscription box service that delivers eco-friendly, zero-waste household cleaning supplies in refillable glass containers, with compostable packaging and customizable delivery schedules.",
        product_name="EcoClean Direct",
        industry="Eco-Friendly Household & Consumer Goods",
        audience="Environmentally conscious homeowners and zero-waste enthusiasts"
    )
    
    # Save output for EcoClean
    with open(os.path.join(backend_dir, "ecoclean_verified_response.json"), "w", encoding="utf-8") as f:
        json.dump(ecoclean_res, f, indent=2)

    # Test 2: KelpCraft
    kelpcraft_res = run_test_case(
        name="KelpCraft",
        idea="Handcrafted artisan sculptures carved exclusively from deep-sea dried kelp and sea kelp roots collected by freedivers in cold Alaskan fjords.",
        product_name="KelpCraft",
        industry="Artisan Marine Sculpture",
        audience="Luxury maritime art collectors"
    )
    
    # Save output for KelpCraft
    with open(os.path.join(backend_dir, "kelpcraft_verified_response.json"), "w", encoding="utf-8") as f:
        json.dump(kelpcraft_res, f, indent=2)
