# System Architecture — Milestone 1: Startup Idea Research Engine

## 1. Executive Summary
The Startup Idea Validator platform delivers automated early-stage market research and idea validation. By pairing LLM-driven structured domain extraction with AI-native web search, the system transforms unstructured startup descriptions into organized market evidence across four essential research dimensions:
1. **Competitors & Alternatives**
2. **Industry News & Trends**
3. **Customer Demand & Problem Signals**
4. **Market Size & Forecasts**

---

## 2. Multi-Agent Pipeline Architecture

```
                               +-----------------------------+
                               |     User Interface (UI)     |
                               |    React + Vite Frontend    |
                               +-----------------------------+
                                              |
                                     POST /api/validate
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                              1. IdeaExtractionAgent (Groq)                              |
|  - Ingests raw idea text + optional user metadata                                       |
|  - Uses primary model `qwen/qwen3.8-27b` with auto-failover to backup models on Groq    |
|  - Returns structured JSON: product_name, industry, target_audience, core_problem,     |
|    and 3-5 specific domain keywords                                                     |
|  - Prevents word-sense collisions (e.g., distinguishing "booking" a class vs. "books")  |
+-----------------------------------------------------------------------------------------+
                                              |
                                    Structured Metadata
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                              2. WebSearchAgent (Tavily)                                 |
|  - Synthesizes 4 targeted search queries from extracted domain keywords and industry     |
|  - Dispatches parallel API calls via ThreadPoolExecutor                                 |
|  - Configuration: search_depth="advanced", max_results=6 per category                   |
|  - Topic routing: Uses topic="news" for Industry News to retrieve recent signals        |
|  - Preserves Tavily native relevance scoring (0.0 to 1.0)                               |
+-----------------------------------------------------------------------------------------+
                                              |
                                     Raw Result Batches
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                              3. DataRetrievalAgent                                      |
|  - Normalizes search outputs into canonical schemas                                     |
|  - Filters out dictionary/generic aggregator domains via BLOCKED_DOMAINS               |
|  - Enforces English language validation (`langdetect`)                                  |
|  - Deduplicates sources by canonical URL                                                |
|  - Computes summary metrics and category breakdowns                                     |
+-----------------------------------------------------------------------------------------+
                                              |
                                   ValidationResponse Payload
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                                  Frontend Presentation                                  |
|  - Extracted Metadata Card: Visualizes AI domain understanding & keyword chips          |
|  - High-contrast Summary Bar: Real-time source counts across all 4 categories           |
|  - Categorized Evidence Sections: Score-ranked source cards with outbound links         |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Core Agent Specifications

### Agent 1: `IdeaExtractionAgent`
- **File:** `backend/agents/idea_extraction_agent.py`
- **Purpose:** Converts free-form, conversational startup descriptions into high-precision market research parameters.
- **LLM Engine:** Groq API using `qwen/qwen3.8-27b` (with automatic failover to `allam-2-7b` and `groq/compound-mini` on rate limits).
- **Extracted Schema:**
  - `product_name`: Inferred or explicit product title.
  - `industry`: Inferred industry vertical (e.g. "DevSecOps", "Health & Fitness", "Personal Finance").
  - `target_audience`: Target demographic or customer profile.
  - `core_problem`: Precise one-sentence definition of the customer pain point.
  - `keywords`: 3–5 specific domain terms (e.g. `["continuous integration", "vulnerability scanning", "DevSecOps"]`).
- **Resilience:** Thread-safe execution with exponential backoff on HTTP 429 and deterministic stopword/token parser fallback.

### Agent 2: `WebSearchAgent`
- **File:** `backend/agents/web_search_agent.py`
- **Purpose:** Executes multi-angle research queries through Tavily's AI-native search infrastructure.
- **Execution:**
  - Queries are assembled dynamically per category using extracted domain concepts rather than raw user text.
  - 4 categories queried concurrently via `ThreadPoolExecutor(max_workers=4)`.
  - `search_depth="advanced"` ensures retrieval of comprehensive content snippets.
  - Native relevance scores from Tavily are preserved directly on source records.

### Component 3: `DataRetrievalAgent`
- **File:** `backend/agents/data_retrieval_agent.py`
- **Purpose:** Sanitizes and groups search findings into clean, presentation-ready structures.
- **Rules & Filters:**
  - **Blocklist Filtering:** Drops low-utility reference and dictionary sites (`wiktionary.org`, `dictionary.com`, etc.).
  - **Language Verification:** Verifies English content to prevent foreign-language noise.
  - **Canonical URL Deduplication:** Prevents duplicate entries across queries and categories.

---

## 4. Why Tavily Was Chosen

1. **AI-Optimized Search:** Tailored specifically for LLM and agentic workflows, returning rich text snippets and authentic market intelligence without SEO clickbait or ad clutter.
2. **Native Relevance Scoring:** Provides reliable, calibrated relevance scores out of the box, eliminating the need for fragile local embedding comparisons or slow LLM judge passes.
3. **Structured Research Angles:** First-class support for advanced search depth and topical news filtering (`topic="news"`) provides timely insights for competitor tracking and market sizing.
4. **Reliability & Performance:** Eliminates fragile HTML scraping and CAPTCHA rate-limiting in favor of a fast, SLA-backed API.

---

## 5. API & Data Flow Contracts

### `POST /api/validate` Request
```json
{
  "idea": "a marketplace that lets users find and book local fitness classes",
  "product_name": null,
  "industry": null,
  "target_audience": null
}
```

### `ValidationResponse`
```json
{
  "idea": "a marketplace that lets users find and book local fitness classes",
  "extracted_data": {
    "product_name": "LocalFit Marketplace",
    "industry": "Health & Fitness",
    "target_audience": "Urban residents seeking flexible, local fitness options",
    "core_problem": "Users struggle to discover and book diverse local fitness classes due to fragmented information and lack of a centralized booking system.",
    "keywords": [
      "fitness classes",
      "local booking",
      "wellness marketplace",
      "class discovery"
    ]
  },
  "sources": [
    {
      "title": "Health and Fitness Club Market Growth & Trends Analysis, 2034",
      "url": "https://www.fortunebusinessinsights.com/health-and-fitness-club-market-108652",
      "snippet": "...",
      "query": "fitness classes local booking wellness marketplace class discovery Health & Fitness market size growth forecast",
      "category": "Market Size & Trends",
      "score": 0.665
    }
  ],
  "summary": {
    "total_sources": 24,
    "sources_per_category": {
      "Competitors": 6,
      "Industry News": 6,
      "Customer Demand": 6,
      "Market Size & Trends": 6
    },
    "sources_by_category": { ... }
  }
}
```
