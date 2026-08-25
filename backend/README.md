# ⚙️ Team Forge — Backend Service

The backend is a high-performance **FastAPI** service orchestrating an autonomous multi-agent pipeline for startup market intelligence and validation.

---

## 🏗️ Architecture & Modules

```
backend/
├── agents/
│   ├── __init__.py               # Agent package exports
│   ├── web_search_agent.py       # Query decomposition & multi-source web intelligence
│   └── data_retrieval_agent.py   # Deduplication, scoring, & data normalization
├── config.py                     # Environment loading & CORS policies
├── main.py                       # FastAPI entrypoint & endpoint routing
└── requirements.txt              # Pinned Python dependencies
```

---

## 🤖 Agent Pipeline Explained

1. **`WebSearchAgent`** ([`agents/web_search_agent.py`](agents/web_search_agent.py))
   - Decomposes the user's startup idea into 3 strategic market research queries:
     1. *Market Size & Industry Trends*
     2. *Competitors & Alternatives*
     3. *Target Customers & Market Demand*
   - Queries multiple search mechanisms with automated fallbacks:
     - DuckDuckGo (`ddgs` library)
     - DuckDuckGo Lite (HTML parsing)
     - Google News Market Intelligence RSS (`lxml`)
     - Wikipedia Knowledge API

2. **`DataRetrievalAgent`** ([`agents/data_retrieval_agent.py`](agents/data_retrieval_agent.py))
   - Ingests raw batches across all query angles.
   - Normalizes search items into structured records:
     ```json
     {
       "title": "Smart Irrigation Controllers Market Size Report",
       "url": "https://example.com/report",
       "snippet": "The global smart irrigation market is projected to reach...",
       "query": "smart irrigation controller market size and industry trends",
       "score": 0.95
     }
     ```
   - Filters duplicate URLs and ranks sources by relevance score.
   - Produces query distribution summaries for the frontend dashboard.

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
    "idea": "An AI-powered smart garden irrigation controller that adjusts watering based on weather forecasts and soil moisture."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "idea": "...",
    "sources": [
      {
        "title": "...",
        "url": "...",
        "snippet": "...",
        "query": "...",
        "score": 0.92
      }
    ],
    "summary": {
      "total_sources": 15,
      "sources_per_query": {
        "... market size ...": 5,
        "... competitors ...": 5,
        "... target customers ...": 5
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
Swagger UI documentation available at: `http://localhost:8000/docs`
