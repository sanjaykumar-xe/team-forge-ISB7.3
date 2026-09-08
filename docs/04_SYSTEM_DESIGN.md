# 04. System Design & Architectural Topology

## 1. Architectural Philosophy
The architecture is based on a **Decoupled Multi-Tier System Topology** combining:
1. An editorial client application (React 18 SPA) deployed to edge CDN infrastructure (Vercel).
2. A high-throughput API gateway and validation controller (FastAPI / Python 3.11) deployed to containerized compute (Render Cloud).
3. An in-process autonomous multi-agent pipeline governed by CrewAI, orchestrating interactions with external intelligence services (Groq Cloud LLM and Tavily Search API).

---

## 2. Multi-Tier Architectural Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TIER 1: PRESENTATION LAYER                      │
│                           (Vercel Cloud Edge)                          │
│                                                                        │
│   • React 18 + Vite SPA                                                │
│   • Editorial Design System (Instrument Serif, Space Mono, Inter)      │
│   • Unlimited Pitch Input Form + Parameter Overrides                   │
│   • Dynamic Case-File AI Dossier                                       │
│   • Interactive White-Space Opportunity Map                            │
│   • Market Sizing & Scorecard Panel                                    │
│   • Persona Cards (Daily End Users vs Economic Decision Makers)        │
│   • Competitor Comparison Matrix                                       │
│   • 4-Category Evidence Grid with Sentence-Boundary Truncation         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ HTTPS POST /api/validate (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        TIER 2: API GATEWAY LAYER                       │
│                           (Render Cloud Compute)                       │
│                                                                        │
│   • FastAPI REST Application (`backend/main.py`)                       │
│   • Input Validation & Gibberish Filter (`wordfreq` density >= 0.45)   │
│   • CORS Middleware & Environment Configuration                        │
│   • Pydantic v2 Schema Enforcement (`ValidationResponse`)              │
│   • In-Process Sequential Controller (`ValidationCrewOrchestrator`)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ In-Process Python Function Execution
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 3: AUTONOMOUS MULTI-AGENT PIPELINE                  │
│                        (In-Process CrewAI Core)                        │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [1] IdeaExtractionAgent (Groq LLM Cascading Failover)          │   │
│   │     • qwen/qwen3.8-27b ➔ allam-2-7b ➔ groq/compound-mini       │   │
│   │     • Normalizes product, industry, problem, audience, keywords│   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [2] MarketResearchAgent (CrewAI Autonomous Tool-Calling)       │   │
│   │     • Query formulation & domain-specific tool selection       │   │
│   │     • Repetition Filter (blocks duplicate intent searches)     │   │
│   │     • Strict Budget Cap: 3 to 5 total Tavily search queries    │   │
│   │     • Tools: search_competitors, search_industry_news,         │   │
│   │              search_customer_demand, search_market_size        │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [3] DataRetrievalAgent (Deterministic Verification Pipeline)   │   │
│   │     • Blocked Domain Filtering (excludes wikis, dictionaries)  │   │
│   │     • Seeded English Verification (`langdetect`)               │   │
│   │     • Cross-Category Canonical URL Deduplication               │   │
│   │     • Descending Semantic Score Ranking ($0.0 - 1.0$)          │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [4] MarketOpportunityAgent (Market Sizing & Segmentation)      │   │
│   │     • TAM/SAM figures, CAGR, forecast years with citations     │   │
│   │     • Persona Segmentation: Daily End Users vs Decision Makers │   │
│   │     • Honest empty-state clamping when market data is sparse   │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [5] CompetitorAnalysisAgent (Competitive Landscape)            │   │
│   │     • Direct rivals vs indirect substitutes & pricing models   │   │
│   │     • Strengths, weaknesses, and customer complaints           │   │
│   │     • Multidimensional side-by-side comparison matrix          │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ [6] WhiteSpaceEngine (Core Novelty Triangulation)              │   │
│   │     • Customer Pain ∩ Competitor Void ∩ Startup Capability     │   │
│   │     • 2-4 High-conviction opportunity gaps with confidence     │   │
│   │     • Traceable citations linking findings to verified URLs    │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Communication Patterns & Protocol Design
- **Client to Backend**: Stateless HTTP/1.1 and HTTP/2 `POST /api/validate` transmitting JSON payloads.
- **Backend to Inference / Search Providers**:
  - `Groq Cloud`: HTTPS REST calls using `groq-python` and raw `httpx` clients with explicit timeout and retry budgets.
  - `Tavily Search API`: HTTPS REST calls using `tavily-python` returning enriched snippets and relevance scores.
- **Inter-Agent Coordination**: In-process synchronous/asynchronous Python memory handoffs. Structured dictionaries conforming strictly to Pydantic models are passed sequentially without intermediary database disk serialization bottlenecks.
