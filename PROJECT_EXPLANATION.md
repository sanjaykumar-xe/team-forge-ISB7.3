# Team Forge — Startup Idea Validator: Complete Technical Guide & Codebase Explanation

> **Document Purpose**: A comprehensive, step-by-step technical guide explaining the Team Forge codebase, multi-agent architecture, data contracts, and frontend-backend lifecycle for team members, evaluators, and contributors.

---

## 📑 Table of Contents
1. [Project Overview & Core Mission](#1-project-overview--core-mission)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Multi-Agent Pipeline Deep-Dive](#3-multi-agent-pipeline-deep-dive)
   - [3.1 IdeaExtractionAgent (Groq LLM)](#31-ideaextractionagent-groq-llm)
   - [3.2 WebSearchAgent (Tavily Search API)](#32-websearchagent-tavily-search-api)
   - [3.3 DataRetrievalAgent (Verification & Deduplication)](#33-dataretrievalagent-verification--deduplication)
4. [Frontend Architecture & User Interface](#4-frontend-architecture--user-interface)
5. [Backend Architecture & API Endpoints](#5-backend-architecture--api-endpoints)
6. [Data Contracts & Payload Specifications](#6-data-contracts--payload-specifications)
7. [Environment Variables & Configuration](#7-environment-variables--configuration)
8. [Testing, Benchmarking & Evaluation](#8-testing-benchmarking--evaluation)
9. [Deployment Architecture](#9-deployment-architecture)

---

## 1. Project Overview & Core Mission

Before founders commit substantial capital, time, and engineering resources to a startup idea, they must validate three fundamental market assumptions:
1. **Market Size & Economic Trajectory**: Is there an addressable market with quantifiable growth or market tailwinds?
2. **Competitive Landscape**: Who are the direct rivals, incumbent platforms, and potential substitute solutions?
3. **Customer Demand & Unmet Needs**: Are target users actively voicing pain points, seeking alternatives, or expressing dissatisfaction with existing tools?
4. **Industry News & Momentum**: Are there recent venture investments, regulatory developments, or macro shifts validating the space?

The **Startup Idea Validator** automates this preliminary discovery phase. It converts an unstructured natural-language startup pitch into structured market parameters, queries the web across 4 strategic intelligence vectors, cleans and deduplicates the results, and displays verifiable source evidence in a clean editorial interface.

---

## 2. High-Level System Architecture

The application is built on a decoupled, production-ready client-server architecture:

```
                                 ┌─────────────────────────────────────────┐
                                 │          Client Browser (SPA)           │
                                 │     React 18 + Vite (Vanilla CSS)       │
                                 │   - Natural language submission form    │
                                 │   - Stamped AI Dossier metadata view    │
                                 │   - 4-category evidence source cards    │
                                 └────────────────────┬────────────────────┘
                                                      │
                                                      │ HTTP POST /api/validate
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              FastAPI Application Layer                                                 │
│                                                (backend/main.py)                                                       │
│                                                                                                                        │
│  1. Input Validation & Gibberish Filter:                                                                               │
│     - Verifies minimum length (>= 5 chars) and dictionary word ratio (wordfreq >= 0.45)                                │
│     - Fast-fails non-English nonsense strings with 200 OK + explanatory UX guidance                                   │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Raw Idea Text + Optional Fields
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       1. IdeaExtractionAgent (Groq LLM)                                                │
│                                   (backend/agents/idea_extraction_agent.py)                                            │
│                                                                                                                        │
│  - Extracts structured product name, industry, target audience, core problem, and contextual keywords                   │
│  - Multi-Model Failover: Primary (`qwen/qwen3.8-27b`) -> Backup 1 (`allam-2-7b`) -> Backup 2 (`groq/compound-mini`)    │
│  - Exponential backoff on HTTP 429 rate limit triggers                                                                 │
│  - Deterministic Fallback: Multi-pass regex & opener-stripping fallback parser                                         │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Structured Metadata
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         2. WebSearchAgent (Tavily API)                                                 │
│                                     (backend/agents/web_search_agent.py)                                               │
│                                                                                                                        │
│  - Parallel search across 4 research categories via ThreadPoolExecutor(max_workers=4)                                  │
│  - Category 1: Competitors (search_depth="advanced", topic="general")                                                   │
│  - Category 2: Industry News (search_depth="advanced", topic="news")                                                    │
│  - Category 3: Customer Demand (search_depth="advanced", topic="general")                                               │
│  - Category 4: Market Size & Trends (search_depth="advanced", topic="general")                                         │
│  - Native Relevance Scoring: Preserves calibrated Tavily float scores (0.0 to 1.0)                                     │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Raw Result Batches
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           3. DataRetrievalAgent                                                        │
│                                   (backend/agents/data_retrieval_agent.py)                                             │
│                                                                                                                        │
│  - Blocklist Filtering: Drops non-commercial dictionaries, encyclopedias, and generic portals (BLOCKED_DOMAINS)         │
│  - Language Verification: Enforces English results using langdetect with deterministic seed                             │
│  - Canonical Deduplication: Drops duplicate URLs across queries and category boundaries                                │
│  - Ranking & Summary: Sorts sources descending by relevance score; aggregates counts                                   │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ ValidationResponse (JSON)
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Frontend Presentation Layer (React)                                              │
│                                                                                                                        │
│  - ExtractedMetadata.jsx: Case-file stamped dossier displaying extracted domain entities & keyword chips               │
│  - ResultsSummary.jsx: Smooth count-up counter showing total sources surfaced                                         │
│  - CategorySection.jsx & SourceCard.jsx: Equal-height 3-column card grid with cleaned snippets & read-more toggle      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-Agent Pipeline Deep-Dive

### 3.1 `IdeaExtractionAgent` (Groq LLM)
- **Source File**: [`backend/agents/idea_extraction_agent.py`](backend/agents/idea_extraction_agent.py)
- **Problem Solved**: Unstructured natural language inputs frequently include ambiguous phrasing, filler words (*"I want to build an app that..."*), and polysemous terms. For example, in *"a marketplace that lets users find and book local fitness classes"*, simple token splitters grab *"book"*, polluting results with physical book reviews and bookstores. The LLM understands that *"book"* is an action verb in the fitness domain and extracts `["fitness classes", "local booking", "wellness marketplace"]`.
- **Multi-Model Failover Strategy**:
  1. `qwen/qwen3.8-27b` (Primary: high semantic comprehension, strict JSON compliance).
  2. `allam-2-7b` (Backup 1: fast, high throughput failover).
  3. `groq/compound-mini` (Backup 2: emergency failover).
  4. `_fallback_extraction` (Deterministic heuristic regex parser if all external network calls fail).

### 3.2 `WebSearchAgent` (Tavily Search API)
- **Source File**: [`backend/agents/web_search_agent.py`](backend/agents/web_search_agent.py)
- **Problem Solved**: General search scrapers (e.g. DuckDuckGo, Bing scraping) suffer from IP throttling, CAPTCHAs, and lack of relevance scoring. The Web Search Agent connects to the Tavily AI-native search engine.
- **Concurrency**: Dispatches 4 parallel threads via `ThreadPoolExecutor(max_workers=4)`.
- **Query Construction**:
  - *Competitors*: `{keywords} [{product_name}] competitors alternatives`
  - *Industry News*: `{keywords} industry trends startup news` (`topic="news"`)
  - *Customer Demand*: `{keywords} customer problems user demand reviews`
  - *Market Size*: `{keywords} [{industry}] market size growth forecast`

### 3.3 `DataRetrievalAgent` (Sanitization & Deduplication)
- **Source File**: [`backend/agents/data_retrieval_agent.py`](backend/agents/data_retrieval_agent.py)
- **Filters & Verification**:
  - **`BLOCKED_DOMAINS`**: Strips encyclopedias, dictionaries, and generic forums (`wiktionary.org`, `wikipedia.org`, `dictionary.com`, `yelp.com`, `quora.com`, `medicinesfaq.com`).
  - **Language Filtering**: Evaluates combined title and snippet text with `langdetect` seeded with `DetectorFactory.seed = 0` to discard non-English search noise.
  - **Canonical Deduplication**: Maintains a `seen_urls` set across all category batches to ensure that a source is never displayed twice.
  - **Relevance Sorting**: Orders records strictly by their native relevance score descending.

---

## 4. Frontend Architecture & User Interface

The frontend is located in [`frontend/src/`](frontend/src/) and built with React 18 and Vite:

### 📁 Component Hierarchy & Structure
```
frontend/src/
├── components/
│   ├── Header.jsx                 # Masthead hero banner & tagline
│   ├── ExtractedMetadata.jsx      # Case-file stamped dossier card showing extracted metadata
│   ├── ExtractedMetadata.css      # Warm charcoal-brown dossier styles & stamped badges
│   ├── ResultsSummary.jsx         # Summary stats bar with animated count-up counter
│   ├── CategorySection.jsx        # 3-column responsive category grid with collapsible items
│   └── SourceCard.jsx             # Individual evidence card with snippet cleaner & pinned footer
├── App.jsx                        # Main state orchestrator & form management
├── App.css                        # Layout grid, animations, and typography tokens
├── index.css                      # Global theme variables, reset, and reduced-motion rules
└── main.jsx                       # Application DOM root mount
```

### 🎨 Key Frontend Features
1. **Snippet Sanitizer & Sentence Truncation ([`SourceCard.jsx`](frontend/src/components/SourceCard.jsx)):**
   - Strips markdown hashes (`###`), pipe-table lines (`| | |`), and bracket citations (`[...]`).
   - Truncates text at sentence boundaries (`.`, `!`, `?`) within ~180–220 characters.
   - Provides an inline `"Read more ↓"` / `"Read less ↑"` toggle for longer excerpts.
2. **Equal-Height Grid & Pinned Footers ([`App.css`](frontend/src/App.css)):**
   - `.category-grid` enforces `grid-auto-rows: 1fr` and `align-items: stretch`.
   - `.source-footer` uses `margin-top: auto` to anchor hostname tags and relevance percentages to the bottom of each card.
3. **Micro-Interactions & Accessibility:**
   - Smooth animated count-up for "Sources Surfaced" (`ResultsSummary.jsx`).
   - Gentle hover elevation on source cards (`transform: translateY(-3px)`).
   - Full support for `@media (prefers-reduced-motion: reduce)`.

---

## 5. Backend Architecture & API Endpoints

The backend is located in [`backend/`](backend/) and powered by FastAPI and Uvicorn:

### Endpoints
- **`GET /api/health`**: Simple health check returning `{"status": "ok"}`.
- **`POST /api/validate`**: Main research pipeline endpoint accepting `IdeaSubmission` and returning `ValidationResponse`.

---

## 6. Data Contracts & Payload Specifications

### Input Schema (`POST /api/validate`)
```json
{
  "idea": "a marketplace that lets users find and book local fitness classes",
  "product_name": null,
  "industry": null,
  "target_audience": null
}
```

### Response Schema (`ValidationResponse`)
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
      "snippet": "The global health and fitness club market size was valued at USD 104.05 billion in 2024 and is projected to grow to USD 202.92 billion by 2034, exhibiting a CAGR of 6.9%...",
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

---

## 7. Environment Variables & Configuration

### Backend (`backend/.env`)
```bash
# Groq API key for LLM idea understanding (https://console.groq.com)
GROQ_API_KEY=gsk_...

# Tavily API key for AI web research (https://tavily.com)
TAVILY_API_KEY=tvly-...

# Allowed frontend origins for CORS
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend (`frontend/.env`)
```bash
# Backend URL (do not include trailing slash)
VITE_API_URL=http://127.0.0.1:8000
```

---

## 8. Testing, Benchmarking & Evaluation

The repository includes an evaluation benchmark suite in [`backend/scripts/run_eval.py`](backend/scripts/run_eval.py).

### How to Run the 10-Idea Evaluation Suite:
```bash
python backend/scripts/run_eval.py
```
This tests 10 diverse startup concepts across B2B SaaS, DevSecOps, EdTech, Pet Care, Personal Finance, Consumer Electronics, and Gig Economy verticals, logging LLM extraction status and verifying category source distributions.

---

## 9. Deployment Architecture

| Tier | Platform | Build Command | Start / Run Command | Required Environment Variables |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | **Render** (Web Service) | `pip install -r requirements.txt` | `uvicorn main:app --host 0.0.0.0 --port $PORT` | `GROQ_API_KEY`, `TAVILY_API_KEY`, `ALLOWED_ORIGINS` |
| **Frontend** | **Vercel** (Static SPA) | `npm run build` | Serves `dist/` | `VITE_API_URL` (points to Render backend URL) |

For complete step-by-step deployment instructions, see [**`DEPLOYMENT.md`**](DEPLOYMENT.md).
