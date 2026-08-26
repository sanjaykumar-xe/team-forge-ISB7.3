# System Architecture — Startup Idea Validator

## 1. System Overview

The **Startup Idea Validator** is a multi-agent system designed to help founders validate early-stage startup ideas before building. The system takes a startup concept, breaks it down into three market research angles, executes live web queries, and structures the findings for evaluation.

Milestone 1 delivers:
- **Frontend**: A fast, responsive user interface built with React + Vite.
- **Backend API**: A high-performance REST API built with FastAPI.
- **Web Search Agent**: Generates targeted query angles and queries live web data using DuckDuckGo.
- **Data Retrieval Agent**: Cleans, de-duplicates, ranks, and structures raw search results into standard source records.

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Client Layer                              │
│             React + Vite Single Page Application                │
│       - Idea Submission Form & Validation                       │
│       - Live Results Dashboard & Skeleton Loaders               │
│       - High-contrast Summary & Source Cards                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ HTTP POST /api/validate
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway Layer                         │
│                     FastAPI (Python 3.11)                       │
│       - CORS Middleware & Request Validation (Pydantic)         │
│       - Health Check Endpoint (/api/health)                     │
│       - Orchestration of Agent Execution Pipeline               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Execution Layer                      │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 1. Web Search Agent                     │   │
│   │   - Generates 3 query angles (Market Trends,            │   │
│   │     Competitors, Customer Demand)                       │   │
│   │   - Searches web via DuckDuckGo (DDGS & Lite API)       │   │
│   │   - Secondary fallbacks (Google News, Wikipedia)        │   │
│   └────────────────────────────┬────────────────────────────┘   │
│                                │ Raw Batch Results              │
│                                ▼                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │               2. Data Retrieval Agent                   │   │
│   │   - URL Normalization & Deduplication                   │   │
│   │   - Content Extraction & Snippet Cleaning               │   │
│   │   - Relevance Scoring & Query Categorization            │   │
│   │   - Coverage Metric Computation                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   [Future Milestones]:                                          │
│   - Market Opportunity Agent                                    │
│   - Competitor Discovery Agent                                  │
│   - SWOT & Risk Analysis Agent                                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ Return Structured ValidationResponse
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Display                        │
│   - Total Sources Surfaced & Category Breakdown                 │
│   - Direct Hostname Attribution & Link-outs                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Details & Data Flow

### Step 1: Idea Submission (Frontend)
1. The user inputs a concise description of their startup idea (10–1000 characters).
2. The client validates input length and transitions into a loading state, rendering animated skeleton cards.
3. A `POST` request is dispatched to `/api/validate` with payload `{ "idea": "..." }`.

### Step 2: Query Generation & Execution (Web Search Agent)
1. The `WebSearchAgent` decomposes the idea into 3 research queries:
   - **Market Size & Trends**: `{idea} market size and industry trends`
   - **Competitor Landscape**: `{idea} competitors and alternatives`
   - **Customer Demand**: `{idea} target customers and market demand`
2. Search Execution:
   - Queries DuckDuckGo via the `ddgs` library.
   - If results are sparse, supplements with Google News RSS and Wikipedia search.

### Step 3: Normalization & Deduplication (Data Retrieval Agent)
1. The `DataRetrievalAgent` processes the raw search batches.
2. It tracks unique URLs to prevent duplicate entries across overlapping search queries.
3. Clean titles, hostnames, snippets, and relevance scores are extracted into standard source records.
4. It aggregates total source counts and per-query distributions.

### Step 4: Response & Presentation
1. FastAPI returns a validated `ValidationResponse` JSON payload.
2. React renders the structured sources with category tags, clean hostnames, and a dark summary panel.

---

## 4. Data Contracts & Schemas

### Request Model: `IdeaSubmission`
```json
{
  "idea": "A subscription box for pre-portioned spices for weeknight recipes, sourced directly from small farms."
}
```

### Response Model: `ValidationResponse`
```json
{
  "idea": "A subscription box for pre-portioned spices for weeknight recipes, sourced directly from small farms.",
  "sources": [
    {
      "title": "Global Online Spice & Condiments Market Size 2026-2033",
      "url": "https://example.com/spice-market-report",
      "snippet": "The global spice subscription and direct-to-consumer market is expanding...",
      "query": "subscription spice box market size and industry trends",
      "score": 1.0
    }
  ],
  "summary": {
    "total_sources": 15,
    "sources_per_query": {
      "subscription spice box market size and industry trends": 5,
      "subscription spice box competitors and alternatives": 5,
      "subscription spice box target customers and market demand": 5
    }
  }
}
```

---

## 5. Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic, lxml, ddgs, python-dotenv
- **Frontend**: React 18, Vite, Vanilla CSS
- **Typography**: Instrument Serif, Inter, Space Mono
- **Deployment**: Render (Backend Web Service), Vercel (Frontend SPA)
