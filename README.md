# Team Forge — AI-Based Startup Idea Validator

AI-based startup idea validator with market analysis assistance, developed as part of the **Team Forge (ISB7.3)** project.

---

## 📌 Repository & Branching Structure

- **`staging`**: Active development branch. All new feature code and integration work is pushed here. Connected to staging/preview deployments.
- **`main`**: Production-ready, reviewed code only. No direct commits allowed. Updates to `main` are merged via Pull Requests from `staging`.

---

## 🚀 Current Architecture & Features

| Component | Description | Location |
| :--- | :--- | :--- |
| **Startup Submission UI** | React + Vite interface to submit startup ideas and view validation sources | `frontend/` |
| **FastAPI Backend** | REST API providing validation endpoints and orchestrating agent pipeline | `backend/main.py` |
| **Web Search Agent** | Multi-angle search across market size, competitors, and target audience | `backend/agents/web_search_agent.py` |
| **Data Retrieval Agent** | De-duplicates, normalizes, and scores search results into structured data | `backend/agents/data_retrieval_agent.py` |

### Pipeline Flow

```
User submits idea (frontend)
        │
        ▼
POST /api/validate  (FastAPI backend)
        │
        ▼
WebSearchAgent.search(idea)
  - Generates targeted queries (market size, competitors, target audience)
  - Queries search engine
        │
        ▼
DataRetrievalAgent.structure(raw_batches)
  - De-duplicates by URL
  - Normalizes into {title, url, snippet, query, score}
  - Ranks by relevance
        │
        ▼
JSON response → Rendered dynamically in frontend
```

---

## 💻 Running Locally

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

Verify backend health: `http://localhost:8000/api/health` → `{"status": "ok"}`.

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🌐 Deployment Pipeline

### Backend (Render)
- **Staging Web Service**:
  - Branch: `staging`
  - Root Directory: `backend`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Production Web Service**:
  - Branch: `main`
  - Configuration identical to staging, connected to the `main` branch.

### Frontend (Vercel)
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Preview Environment**: `VITE_API_URL` pointing to Render staging backend.
- **Production Environment**: `VITE_API_URL` pointing to Render production backend.
