import json
import os
import sys

# Ensure backend root is on sys.path when run directly
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from agents.idea_extraction_agent import IdeaExtractionAgent
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent

def main():
    iea = IdeaExtractionAgent()
    wsa = WebSearchAgent()
    dra = DataRetrievalAgent()

    idea = "an app that helps you save money by tracking your daily expenses"
    print("--- 1. Testing IdeaExtractionAgent ---")
    extracted = iea.extract(idea)
    print(json.dumps(extracted, indent=2))

    print("\n--- 2. Testing WebSearchAgent (Tavily) ---")
    raw_batches = wsa.search(extracted, max_results_per_category=4)
    for b in raw_batches:
        print("Category:", b["category"], "| Query:", b["query"], "| Count:", len(b["response"]["results"]))

    print("\n--- 3. Testing DataRetrievalAgent ---")
    structured = dra.structure(raw_batches)
    summary = dra.summarize_counts(structured)
    print("Total sources:", summary["total_sources"])
    print("Per category:", summary["sources_per_category"])
    for s in structured[:5]:
        print(f"  [{s['category']}] (score: {s['score']:.3f}) {s['title']} -> {s['url']}")

if __name__ == "__main__":
    main()
