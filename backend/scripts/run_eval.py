import json
import os
import sys
import time

# Ensure backend root is on sys.path when run directly
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from dotenv import load_dotenv

load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent

ideas = [
    # Original 7
    {"idea": "A CI/CD tool that automatically checks for security vulnerabilities", "product_name": "GuardrailCI"},
    {"idea": "An AI resume builder and career coach for college students", "product_name": "CareerCraft AI"},
    {"idea": "a mobile app that connects dog owners with local dog walkers"},
    {"idea": "a SaaS platform that helps HR teams automate employee onboarding"},
    {"idea": "an app that helps you save money by tracking your daily expenses"},
    {"idea": "A niche webcam designed specifically for streamers that includes built-in ring lighting", "product_name": "VitaLens"},
    {"idea": "a platform that helps independent musicians book gigs at local venues"},
    # 3 holdout ideas
    {"idea": "a marketplace that lets users find and book local fitness classes"},
    {"idea": "an AI study planner that creates personalized learning paths for students", "product_name": "Lumenpath"},
    {"idea": "a web app that helps freelancers create and send professional invoices"},
]


def run_tests():
    iea = IdeaExtractionAgent()
    wsa = WebSearchAgent()
    dra = DataRetrievalAgent()
    results = {}

    print("=" * 75)
    print("STARTING 10-IDEA EVALUATION SUITE WITH LIVE LLM EXTRACTION LOGGING")
    print("=" * 75)

    for i, test in enumerate(ideas):
        idea = test["idea"]
        product_name = test.get("product_name")
        print(f"\n[{i+1}/10] Testing: '{product_name or idea}'")
        print(f"  Input idea: {idea}")

        t0 = time.time()
        # 1. LLM Extraction
        extracted = iea.extract(
            idea=idea,
            product_name=product_name,
        )
        t_extract = time.time() - t0
        print(f"  Extracted ({t_extract:.2f}s): {json.dumps(extracted)}")

        # 2. Tavily Search
        t1 = time.time()
        raw_batches = wsa.search(extracted, max_results_per_category=6)
        t_search = time.time() - t1

        # 3. Data Retrieval & Structuring
        structured = dra.structure(raw_batches)
        summary = dra.summarize_counts(structured)
        print(f"  Search & Retrieval ({t_search:.2f}s): {summary['total_sources']} sources surfaced")
        print(f"  Breakdown: {summary['sources_per_category']}")

        # Print top 1 per category
        for cat in ["Competitors", "Industry News", "Customer Demand", "Market Size & Trends"]:
            cat_sources = [s for s in structured if s["category"] == cat]
            if cat_sources:
                top = cat_sources[0]
                print(f"    - [{cat}] (score: {top['score']}) {top['title'][:70]}")
            else:
                print(f"    - [{cat}] 0 sources")

        results[idea] = {
            "extracted_data": extracted,
            "total_sources": summary["total_sources"],
            "sources_per_category": summary["sources_per_category"],
            "sources": structured,
        }

    output_path = os.path.join(BACKEND_DIR, "eval_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print(f"EVALUATION COMPLETE. Results saved to {output_path}")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()
