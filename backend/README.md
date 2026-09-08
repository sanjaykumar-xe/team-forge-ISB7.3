# Backend Service — Startup Idea Validator

The backend is a high-performance **FastAPI** service that manages autonomous multi-agent intelligence for startup market validation.

---

## 🏗️ Architecture & Modules

```
backend/
├── agents/
│   ├── __init__.py                  # Agent package exports
│   ├── idea_extraction_agent.py     # Groq LLM semantic extraction & multi-model failover
│   ├── web_search_agent.py          # Tavily search wrapper with query category routing
│   ├── data_retrieval_agent.py      # Blocklist filtering, English check, dedup, & ranking
│   ├── market_analysis_agent.py     # TAM/SAM sizing, CAGR estimation, & customer personas
│   └── competitor_analysis_agent.py # Competitor mapping, feature matrix, & gap analysis
├── crew/
│   ├── agents.py                    # CrewAI Agent definitions
│   ├── orchestrator.py              # CrewAI autonomous execution & milestone logging
│   ├── tasks.py                     # CrewAI Task definitions & context handoffs
│   └── tools.py                     # Search & retrieval tools exposed to the CrewAI Agent
├── schemas/
│   ├── __init__.py                  # Schema package exports
│   └── validation.py                # Pydantic models & validation contracts
├── services/
│   ├── __init__.py                  # Service package exports
│   ├── llm_service.py               # Resilient Groq LLM client with JSON validation & failover
│   └── white_space_engine.py        # Triangulation engine: Customer Pain × Competitor Void × Startup
├── scripts/
│   ├── test_milestone2_e2e.py       # 3-industry end-to-end benchmark evaluation
│   ├── run_5_regression_ideas.py    # Multi-idea regression test suite
│   ├── run_eval.py                  # Evaluation harness
│   └── smoke_test.py                # Single-idea smoke test script
├── tests/
│   ├── test_agents.py               # Unit tests for agents
│   └── test_milestone2.py           # Milestone 2 regression & data integrity tests
├── config.py                        # Environment loading & CORS policies
├── main.py                          # FastAPI entrypoint, input validation, & router
├── requirements.txt                 # Python dependencies (FastAPI, CrewAI, Groq, Tavily, etc.)
└── .env.example                     # Environment configuration template
```

---

## 🔍 In-Process Agent Pipeline

1. **`IdeaExtractionAgent`** ([`agents/idea_extraction_agent.py`](agents/idea_extraction_agent.py))
   - Ingests raw conversational startup descriptions.
   - Uses **Groq Cloud LLM** with automatic failover across models (`qwen/qwen3.8-27b`, `allam-2-7b`, `groq/compound-mini`) on rate limits.
   - Extracts structured domain context: *Product Name*, *Industry Vertical*, *Target Audience*, *Core Problem*, and *Contextual Keywords*.

2. **Autonomous `MarketResearchAgent` via CrewAI** ([`crew/orchestrator.py`](crew/orchestrator.py))
   - Given the extracted domain context, the agent autonomously plans and issues targeted search queries across 4 dimensions:
     1. *Competitors & Alternatives*
     2. *Industry News & Trends*
     3. *Customer Demand & User Pain Points*
     4. *Market Size & Growth Forecasts*
   - Interacts with **Tavily Search API** through discrete tool definitions, governed by a query repetition filter and budget cap.

3. **`DataRetrievalAgent`** ([`agents/data_retrieval_agent.py`](agents/data_retrieval_agent.py))
   - Strips non-commercial dictionary, encyclopedia, and forum domains (`BLOCKED_DOMAINS`).
   - Validates English text coherence deterministically via seeded `langdetect`.
   - Deduplicates identical canonical URLs across queries and category boundaries.
   - Sorts records strictly by relevance score descending and computes summary distributions.

4. **`MarketOpportunityAgent`** ([`agents/market_analysis_agent.py`](agents/market_analysis_agent.py))
   - Synthesizes market sizing estimates (TAM/SAM), CAGR projections, and market attractiveness scores.
   - Constructs detailed customer personas separating Daily End Users from Economic Decision Makers.
   - Honest empty states: suppresses scorecards and nulls confidence when 0 market size sources exist.

5. **`CompetitorAnalysisAgent`** ([`agents/competitor_analysis_agent.py`](agents/competitor_analysis_agent.py))
   - Identifies direct competitors and indirect substitutes.
   - Extracts business models, strengths, weaknesses, and customer complaints.
   - Constructs a side-by-side comparison matrix evaluating the startup's approach against key rivals.

6. **`WhiteSpaceEngine`** ([`services/white_space_engine.py`](services/white_space_engine.py))
   - Computes deterministic opportunity gaps at the intersection:
     $$\text{White-Space Opportunity} = \text{Customer Pain} \cap \text{Competitor Void} \cap \text{Startup Capability}$$
   - Outputs 2–4 high-conviction opportunity gaps with evidence strength, confidence ratings, and source citations.

---

## 📡 API Reference

### `GET /api/health`
Health check endpoint.
- **Response**: `{"status": "ok"}`

### `POST /api/validate`
Validates a startup concept and returns structured market sources.
- **Request Body (`IdeaSubmission`)**:
  ```json
  {
    "idea": "A CI/CD tool that automatically checks for security vulnerabilities",
    "product_name": "GuardrailCI",
    "industry": null,
    "target_audience": null
  }
  ```
- **Response (200 OK — `ValidationResponse`)**:
  ```json
  {
    "idea": "A CI/CD tool that automatically checks for security vulnerabilities",
    "extracted_data": {
      "product_name": "GuardrailCI",
      "industry": "DevSecOps",
      "target_audience": "Software development teams and DevOps engineers",
      "core_problem": "Software development teams struggle to identify and remediate security vulnerabilities early in the CI/CD pipeline.",
      "keywords": [
        "continuous integration",
        "vulnerability scanning",
        "DevSecOps",
        "security automation"
      ]
    },
    "sources": [
      {
        "title": "DevSecOps Market Size, Share, Growth, Analysis, Report, 2034",
        "url": "https://straitsresearch.com/report/devsecops-market",
        "snippet": "The global DevSecOps market size was valued at USD 6.2 billion in 2024 and is projected to reach USD 37.32 billion by 2034...",
        "query": "continuous integration vulnerability scanning DevSecOps security automation DevSecOps market size growth forecast",
        "category": "Market Size & Trends",
        "score": 0.9257
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

## 🚀 Local Development

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables in backend/.env:
# GROQ_API_KEY=gsk_...
# TAVILY_API_KEY=tvly-...

# 5. Start local server
uvicorn main:app --reload --port 8000
```

- Health check: `http://127.0.0.1:8000/api/health`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
