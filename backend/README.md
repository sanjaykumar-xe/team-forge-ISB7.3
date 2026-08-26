# Backend Service — Startup Idea Validator

The backend is a high-performance **FastAPI** service that manages web search and data retrieval agents for startup market intelligence.

---

## 🏗️ Architecture & Modules

```
backend/
├── agents/
│   ├── __init__.py               # Agent package exports
│   ├── web_search_agent.py       # Query decomposition & DuckDuckGo search execution
│   └── data_retrieval_agent.py   # Deduplication, scoring, & data normalization
├── config.py                     # Environment loading & CORS policies
├── main.py                       # FastAPI entrypoint & endpoint routing
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment configuration template
```

---

## 🔍 Agent Pipeline

1. **`WebSearchAgent`** ([`agents/web_search_agent.py`](agents/web_search_agent.py))
   - Deconstructs the startup concept into 3 strategic market queries:
     1. *Market Size & Industry Trends*
     2. *Competitors & Alternatives*
     3. *Target Customers & Market Demand*
   - Queries DuckDuckGo with fallback mechanisms to Google News RSS and Wikipedia search.

2. **`DataRetrievalAgent`** ([`agents/data_retrieval_agent.py`](agents/data_retrieval_agent.py))
   - Ingests raw batches across all query angles.
   - De-duplicates identical URLs and cleans snippets.
   - Assigns rank-based relevance scores.
   - Aggregates category distribution metrics.

---

## 📡 API Reference

### `GET /api/health`
Health check endpoint.
- **Response**: `{"status": "ok"}`

### `POST /api/validate`
Validates a startup concept and returns structured market sources.
- **Request Body**:
  ```json
  {
    "idea": "A subscription box for pre-portioned spices for weeknight recipes, sourced directly from small farms."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "idea": "...",
    "sources": [
      {
        "title": "Global Spice Market Report 2026-2033",
        "url": "https://example.com/spice-report",
        "snippet": "The market for direct-to-consumer culinary ingredients...",
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

## 🚀 Local Development

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start local server
uvicorn main:app --reload --port 8000
```

Interactive Swagger UI documentation is available at `http://localhost:8000/docs`.
