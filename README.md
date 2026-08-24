<<<<<<< HEAD
# team-forge-ISB7.3
AI-based startup idea validator with market analysis assistance, developed as part of the Team Forge project.
=======
# Team Forge — AI-Based Startup Idea Validator

**Milestone 1 deliverable.** This gets the Web Search Agent, Data Retrieval
Agent, and the idea-submission interface working end to end, so the team has
a real pipeline to demo and deploy — not just a plan.

## What's included

| Requirement (from Milestone 1) | Where it lives |
|---|---|
| Interface to submit a startup idea | `frontend/` (React + Vite) |
| Web Search API integration | `backend/agents/web_search_agent.py` (DuckDuckGo via `ddgs`, free & keyless) |
| Data Retrieval Agent | `backend/agents/data_retrieval_agent.py` |
| System architecture (agents, roles, data flow) | see below |

**Note on the search provider:** the whiteboard plan named Tavily, but
Tavily (and most other search APIs) now ask for a card even on the "free"
tier. This uses `ddgs`, a free library that queries DuckDuckGo directly —
no signup, no key, no card. It's fine for development and demoing; if the
team later wants a paid provider for reliability, only
`web_search_agent.py` needs to change, since `DataRetrievalAgent` and
everything downstream only depends on the `{query, response}` shape it
returns.

## How it works

```
User submits idea (frontend)
        │
        ▼
POST /api/validate  (backend/main.py)
        │
        ▼
WebSearchAgent.search(idea)
  - builds 3 search angles: market size, competitors, target customers
  - queries DuckDuckGo (via ddgs) for each — free, no key required
        │
        ▼
DataRetrievalAgent.structure(raw_batches)
  - de-duplicates by URL
  - normalizes into {title, url, snippet, query, score}
  - sorts by relevance score
        │
        ▼
JSON response → rendered as source cards in the UI
```

This structured source list is the contract that Milestone 2's agents
(Market Opportunity, Competitor Discovery, SWOT/Risk) will build on — they
take this same list as input instead of talking to the search provider
directly.

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # no key needed, but keeps ALLOWED_ORIGINS configurable
uvicorn main:app --reload --port 8000
```

Check it's up: open `http://localhost:8000/api/health` — should return `{"status": "ok"}`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`, submit an idea, and you should see live search
results come back as source cards within a few seconds.

## Deploying (staging → preview, main → production)

- **Backend → Render**: New Web Service, root directory `backend`, build
  command `pip install -r requirements.txt`, start command
  `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add `ALLOWED_ORIGINS`
  (your Vercel URL) as an environment variable — no search API key needed.
- **Frontend → Vercel**: New Project, root directory `frontend`, framework
  preset Vite. Add `VITE_API_URL` pointing at your Render backend URL.
- Connect Render/Vercel's preview deployments to the `staging` branch and
  production deployments to `main`, per the team's branching strategy.

## Next milestones build on this

- **Milestone 2**: Market Opportunity & Customer Segmentation Agent,
  Competitor Discovery Agent — both consume `DataRetrievalAgent`'s output.
- **Milestone 3**: SWOT/Risk Agent, MVP Feature Recommendation, Go-To-Market
  Strategy.
- **Milestone 4**: Startup Validation Report Generation Agent (combines all
  agent outputs into one report) and the Conversational Startup Advisor.
>>>>>>> f0679d1 (feat(milestone-1): complete WebSearchAgent, DataRetrievalAgent pipeline and submission interface)
