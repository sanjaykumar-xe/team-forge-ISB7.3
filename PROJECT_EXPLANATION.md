# Team Forge — Startup Idea Validator: Complete Technical Guide & Codebase Explanation (Milestone 2)

> **Document Purpose**: A comprehensive, step-by-step technical guide explaining the Team Forge codebase, CrewAI multi-agent orchestration, data contracts, White-Space Engine novelty, and frontend-backend lifecycle for team members, evaluators, and contributors.

---

## 📑 Table of Contents
1. [Project Overview & Core Mission](#1-project-overview--core-mission)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Multi-Agent Pipeline Deep-Dive](#3-multi-agent-pipeline-deep-dive)
   - [3.1 IdeaExtractionAgent (Groq LLM)](#31-ideaextractionagent-groq-llm)
   - [3.2 WebSearchAgent (Tavily Search API)](#32-websearchagent-tavily-search-api)
   - [3.3 DataRetrievalAgent (Verification & Deduplication)](#33-dataretrievalagent-verification--deduplication)
   - [3.4 MarketOpportunityAgent (Market Sizing & Segmentation)](#34-marketopportunityagent-market-sizing--segmentation)
   - [3.5 CompetitorAnalysisAgent (Competitive Mapping & Matrix)](#35-competitoranalysisagent-competitive-mapping--matrix)
   - [3.6 Evidence-Backed Market White-Space Engine (Core Novelty)](#36-evidence-backed-market-white-space-engine-core-novelty)
4. [CrewAI Orchestration Architecture](#4-crewai-orchestration-architecture)
5. [Frontend Architecture & User Interface](#5-frontend-architecture--user-interface)
6. [Backend Architecture & Data Contracts](#6-backend-architecture--data-contracts)
7. [Testing, Benchmarking & 3-Industry Evaluation](#7-testing-benchmarking--3-industry-evaluation)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. Project Overview & Core Mission

Before founders commit capital, engineering hours, and operational resources to a startup idea, they must validate four critical market pillars:
1. **Market Size & Economic Trajectory**: Is there a quantifiable addressable market with visible growth tailwinds and CAGR?
2. **Customer Segmentation & Urgent Pain**: Who are the daily end users vs economic decision makers, and what acute friction drives them to switch?
3. **Competitive Landscape & Omissions**: Who are the direct rivals and indirect substitutes, and what weaknesses or pricing voids do they leave unaddressed?
4. **Defensible White-Space Opportunity**: Where specifically does an opportunity gap exist that triangulates customer pain, competitor weaknesses, and startup capabilities?

The **Startup Idea Validator (Milestone 2)** automates this discovery phase. It converts an unstructured natural language startup pitch of arbitrary length into structured intelligence, queries the web across 4 strategic dimensions, analyzes market sizing and customer personas, maps competitors into a comparison matrix, and synthesizes an evidence-backed White-Space Map with traceable citations.

---

## 2. High-Level System Architecture

```
                                 ┌─────────────────────────────────────────┐
                                 │          Client Browser (SPA)           │
                                 │     React 18 + Vite (Vanilla CSS)       │
                                 │   - Submission Form (Unlimited Length)  │
                                 │   - Stamped AI Dossier metadata view    │
                                 │   - Evidence-Backed White-Space Map     │
                                 │   - Market Opportunity & Sizing Panel   │
                                 │   - Customer Segmentation Breakdown     │
                                 │   - Competitor Comparison Matrix        │
                                 │   - 4-category evidence source cards    │
                                 └────────────────────┬────────────────────┘
                                                      │
                                                      │ HTTP POST /api/validate
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              FastAPI Application Layer                                 │
│                                                (backend/main.py)                                       │
│                                                                                                        │
│  1. Input Validation & Gibberish Filter:                                                               │
│     - Verifies minimum length (>= 5 chars) and dictionary word ratio (wordfreq >= 0.45)                │
│     - Fast-fails non-English nonsense strings with 200 OK + explanatory UX guidance                   │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                          │
                                          │ Raw Idea Text (Arbitrary Length)
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CrewAI Sequential Orchestrator                                     │
│                                     (backend/crew/orchestrator.py)                                     │
│                                                                                                        │
│  [1] Idea Extraction Agent: Groq LLM domain parameter extraction with cascading model failover         │
│  [2] Web Search Agent: Parallel 4-category search via Tavily Search API (ThreadPoolExecutor)           │
│  [3] Data Retrieval Agent: Blocklist filtering, langdetect English check, canonical deduplication     │
│  [4] Market Opportunity Agent: TAM/SAM estimation, CAGR growth trends, customer personas               │
│  [5] Competitor Analysis Agent: Direct/indirect rivals, comparison matrix, market gaps                 │
│  [6] White-Space Engine: Triangulates Customer Pain × Competitor Void × Startup Capability             │
└─────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                          │
                                          │ ValidationResponse (JSON)
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Frontend Presentation Layer (React)                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-Agent Pipeline Deep-Dive

### 3.1 `IdeaExtractionAgent` (Groq LLM)
- **Source File**: [`backend/agents/idea_extraction_agent.py`](backend/agents/idea_extraction_agent.py)
- Ingests raw startup descriptions of arbitrary length and optional user parameters (product name, industry, target audience).
- Extracts clean domain keywords, normalized industry category, audience profile, and refined core problem statement using Groq inference with cascading model failovers.

### 3.2 `WebSearchAgent` (Tavily Search API)
- **Source File**: [`backend/agents/web_search_agent.py`](backend/agents/web_search_agent.py)
- Dispatches 4 concurrent search threads across:
  - *Competitors*: `{keywords} [{product_name}] competitors alternatives` (`search_depth="advanced"`)
  - *Industry News*: `{keywords} industry trends startup news` (`topic="news"`)
  - *Customer Demand*: `{keywords} customer problems user demand reviews` (`search_depth="advanced"`)
  - *Market Size & Trends*: `{keywords} [{industry}] market size growth forecast` (`search_depth="advanced"`)

### 3.3 `DataRetrievalAgent` (Sanitization & Deduplication)
- **Source File**: [`backend/agents/data_retrieval_agent.py`](backend/agents/data_retrieval_agent.py)
- Filters generic dictionaries, encyclopedias, and non-commercial portals (`BLOCKED_DOMAINS`).
- Seeded language verification (`langdetect`) rejects non-English noise.
- Canonical URL deduplication guarantees zero duplicate sources across all categories.
- Ranks sources descending by native semantic relevance score.

### 3.4 `MarketOpportunityAgent` (Market Sizing & Segmentation)
- **Source File**: [`backend/agents/market_analysis_agent.py`](backend/agents/market_analysis_agent.py)
- Synthesizes verified search sources to estimate market size valuations (global, regional, or niche).
- Extracts CAGR trajectories, growth drivers, and demand signals.
- Constructs granular customer segments with explicit distinctions between **End Users** and **Decision Makers**, acute pain points, motivations, buying behaviors, and industry jargon.
- Evaluates Market Attractiveness across Demand Strength, Growth Strength, Customer Urgency, and Accessibility.
- Strict anti-hallucination: every quantitative figure links to a source URL; conflicting sources are explicitly documented.

### 3.5 `CompetitorAnalysisAgent` (Competitive Mapping & Matrix)
- **Source File**: [`backend/agents/competitor_analysis_agent.py`](backend/agents/competitor_analysis_agent.py)
- Discovers and categorizes direct rivals, indirect substitutes, and emerging startups.
- Evaluates core offerings, features, pricing (marked "unavailable" if undisclosed), business models, strengths, weaknesses, and documented customer complaints.
- Generates a multidimensional comparison matrix evaluating the startup against key competitors.
- Uncovers market gaps, pricing voids, and unmet customer needs.

### 3.6 `WhiteSpaceEngine` (Core Novelty)
- **Source File**: [`backend/services/white_space_engine.py`](backend/services/white_space_engine.py)
- Computes deterministic opportunity intersections:
  $$\text{White-Space Opportunity} = \text{Customer Pain} \cap \text{Competitor Void} \cap \text{Startup Capability}$$
- Generates 2–4 high-conviction opportunity gaps with evidence strength ratings (High/Medium/Low), confidence percentages, differentiation hypotheses, and traceable citations.

---

## 4. CrewAI Orchestration Architecture

The orchestration layer is located in [`backend/crew/`](backend/crew/):
- **`agents.py`**: Factory creating CrewAI `Agent` instances for Idea Extraction, Web Research, Data Verification, Market Opportunity Analysis, and Competitor Discovery.
- **`tasks.py`**: Factory creating CrewAI `Task` instances with explicit context handoffs.
- **`tools.py`**: Custom CrewAI tools wrapping underlying agents and services.
- **`orchestrator.py`**: Sequential orchestrator executing the 5-agent pipeline with standardized logging:
  ```
  [1] Idea Extraction started -> [1] Idea Extraction completed
  [2] Web Search started -> [2] Web Search completed
  [3] Data Retrieval started -> [3] Data Retrieval completed
  [4] Market Opportunity Analysis started -> [4] Market Opportunity Analysis completed
  [5] Competitor Analysis started -> [5] Competitor Analysis completed
  ```

---

## 5. Frontend Architecture & User Interface

The frontend is located in [`frontend/src/`](frontend/src/) and built with React 18 and Vite:

```
frontend/src/
├── components/
│   ├── Header.jsx                 # Masthead hero banner & tagline
│   ├── ExtractedMetadata.jsx      # Case-file stamped dossier card showing extracted metadata
│   ├── ExtractedMetadata.css      # Warm charcoal-brown dossier styles
│   ├── WhiteSpaceAnalysis.jsx     # Centerpiece: Evidence-Backed Market White-Space Map
│   ├── MarketOpportunity.jsx      # Market sizing, CAGR, and attractiveness scorecard
│   ├── CustomerSegments.jsx       # Customer persona cards (End Users vs Decision Makers)
│   ├── CompetitorAnalysis.jsx     # Competitor cards & comparison matrix
│   ├── ResultsSummary.jsx         # Summary stats bar with animated count-up counter
│   ├── CategorySection.jsx        # Responsive category grid with collapsible items
│   └── SourceCard.jsx             # Individual evidence card with cleaned snippets
├── App.jsx                        # Main state orchestrator & form management (Unlimited Length)
├── App.css                        # Layout grid, animations, and typography tokens
├── index.css                      # Global theme variables, reset, and reduced-motion rules
└── main.jsx                       # Application DOM root mount
```

---

## 6. Backend Architecture & Data Contracts

### Full Response Schema (`ValidationResponse`)
```json
{
  "idea": "...",
  "extracted_data": {
    "product_name": "...",
    "industry": "...",
    "target_audience": "...",
    "core_problem": "...",
    "keywords": [...]
  },
  "sources": [
    {
      "title": "...",
      "url": "...",
      "snippet": "...",
      "query": "...",
      "category": "...",
      "score": 0.92
    }
  ],
  "market_analysis": {
    "summary": "...",
    "market_size": [
      {
        "figure": "$X.X Billion",
        "market_type": "global",
        "cagr": "X.X%",
        "forecast_year": "2030",
        "source_url": "https://...",
        "evidence_snippet": "...",
        "notes": "..."
      }
    ],
    "growth_trends": [...],
    "demand_signals": [...],
    "customer_segments": [
      {
        "segment_name": "...",
        "who_they_are": "...",
        "end_users": "...",
        "decision_makers": "...",
        "primary_needs": [...],
        "pain_points": [...],
        "motivations": [...],
        "buying_behavior": "...",
        "industry_terminology": [...]
      }
    ],
    "pain_points": [...],
    "buying_behavior": [...],
    "market_risks": [...],
    "attractiveness": {
      "demand_strength": "High",
      "growth_strength": "High",
      "customer_urgency": "High",
      "market_accessibility": "Medium",
      "major_barriers": [...],
      "important_assumptions": [...]
    },
    "confidence": 0.88
  },
  "competitor_analysis": {
    "competitors": [
      {
        "name": "...",
        "classification": "direct",
        "core_offering": "...",
        "target_customer": "...",
        "major_features": [...],
        "pricing": "...",
        "business_model": "...",
        "positioning": "...",
        "strengths": [...],
        "weaknesses": [...],
        "customer_complaints": [...]
      }
    ],
    "comparison_matrix": [
      {
        "feature_or_dimension": "...",
        "startup_approach": "...",
        "competitor_approaches": { ... }
      }
    ],
    "market_gaps": [...],
    "pricing_insights": [...],
    "business_models": [...]
  },
  "white_space_analysis": {
    "opportunities": [
      {
        "opportunity_name": "...",
        "segment": "...",
        "pain_point": "...",
        "demand_evidence": [...],
        "competitor_coverage": [...],
        "gap": "...",
        "startup_fit": "...",
        "differentiation_hypothesis": "...",
        "evidence_strength": "High",
        "confidence": 0.90,
        "potential_risk": "...",
        "evidence": [...]
      }
    ]
  },
  "summary": {
    "total_sources": 24,
    "sources_per_category": { ... },
    "sources_by_category": { ... }
  }
}
```

---

## 7. Testing, Benchmarking & 3-Industry Evaluation

The repository includes an automated 3-industry benchmark suite located in [`backend/scripts/test_milestone2_e2e.py`](backend/scripts/test_milestone2_e2e.py):

### How to Run the 3-Industry End-to-End Suite:
```bash
python backend/scripts/test_milestone2_e2e.py
```
This tests three distinct startup prompts:
1. **Healthcare**: `ClinicGuard AI` (Patient No-Show Predictor & Intervention System)
2. **Climate / Agriculture**: `FarmOptima` (Smallholder Crop, Irrigation, and Market Pricing Decision Platform)
3. **Fintech / Education**: `CampusFin` (Student Spending Analytics & Personalized Financial Literacy Platform)

All three prompts execute through the complete 5-agent sequential pipeline, verifying market sizing, customer personas, competitor classification, white-space synthesis, and source traceability.
