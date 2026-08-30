# Backend Service — Startup Idea Validator

The backend is a high-performance **FastAPI** service that manages autonomous multi-agent intelligence for startup market validation.

---

## 🏗️ Architecture & Modules

```
backend/
├── agents/
│   ├── __init__.py               # Agent package exports
│   ├── idea_extraction_agent.py  # Groq LLM semantic extraction & multi-model failover
│   ├── web_search_agent.py       # Multi-category parallel search execution via Tavily
│   └── data_retrieval_agent.py   # Blocklist filtering, English check, dedup, & ranking
├── scripts/
│   ├── run_eval.py               # 10-idea automated benchmark evaluation harness
│   └── smoke_test.py             # Single-idea smoke test script
├── tests/
│   └── test_agents.py            # Unit tests for agents and validation logic
├── config.py                     # Environment loading & CORS policies
├── main.py                       # FastAPI entrypoint, Pydantic models & in-process pipeline
├── requirements.txt              # Python dependencies (FastAPI, Groq, Tavily, etc.)
└── .env.example                  # Environment configuration template
```

---

## 🔍 In-Process Agent Pipeline

1. **`IdeaExtractionAgent`** ([`agents/idea_extraction_agent.py`](agents/idea_extraction_agent.py))
   - Ingests raw conversational startup descriptions.
   - Uses **Groq Cloud LLM** (`qwen/qwen3.8-27b`) with automatic failover to `allam-2-7b` and `groq/compound-mini` on HTTP 429 rate limits.
   - Extracts structured domain context: *Product Name*, *Industry Vertical*, *Target Audience*, *Core Problem*, and *Contextual Keywords*.

2. **`WebSearchAgent`** ([`agents/web_search_agent.py`](agents/web_search_agent.py))
   - Synthesizes 4 distinct search queries across strategic market categories:
     1. *Competitors & Alternatives*
     2. *Industry News & Trends* (`topic="news"`)
     3. *Customer Demand & User Pain Points*
     4. *Market Size & Growth Forecasts*
   - Queries the **Tavily Search API** in parallel using `ThreadPoolExecutor(max_workers=4)` with `search_depth="advanced"`.
   - Uses Tavily's native calibrated semantic relevance scores (`0.0` to `1.0`).

3. **`DataRetrievalAgent`** ([`agents/data_retrieval_agent.py`](agents/data_retrieval_agent.py))
   - Strips non-commercial dictionary, encyclopedia, and forum domains (`BLOCKED_DOMAINS`).
   - Validates English text coherence deterministically via seeded `langdetect`.
   - Deduplicates identical canonical URLs across queries and category boundaries.
   - Sorts records strictly by relevance score descending and computes summary distributions.

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
