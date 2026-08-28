# Startup Idea Validator

> An intelligent multi-agent platform for validating startup concepts against real-time market data.

Developed as part of the **Team Forge (ISB7.3)** project.

---

## 📌 System Architecture & Pipeline

The system decomposes startup concepts into targeted market research strategies and fetches real-time intelligence using an agent pipeline:

```
┌────────────────────────────────────────────────────────┐
│                   React + Vite UI                      │
│     (Idea Form, Live Dashboard, Structured Sources)    │
└───────────────────────────┬────────────────────────────┘
                            │ POST /api/validate
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│               (/api/health, /api/validate)             │
└─────────────┬────────────────────────────▲─────────────┘
              │ 1. Search Query Angles     │ 4. Structured Sources
              ▼                            │
┌───────────────────────────┐  ┌─────────────────────────┐
│     WebSearchAgent        │  │   DataRetrievalAgent    │
│  - Market Size Trends     │─►│  - URL Deduplication    │
│  - Competitor Discovery   │  │  - Relevance Scoring    │
│  - Customer Demand        │  │  - Category Summary     │
└───────────────────────────┘  └─────────────────────────┘
```

For complete technical specifications, data contracts, and design diagrams, see [**ARCHITECTURE.md**](ARCHITECTURE.md).

---

## 📁 Repository Structure

```
team-forge/
├── backend/                      # Python / FastAPI backend service
│   ├── agents/                   # Market research agents
│   │   ├── __init__.py           # Agent module exports
│   │   ├── web_search_agent.py   # Multi-angle query search via DuckDuckGo
│   │   └── data_retrieval_agent.py # Normalization, deduplication, & scoring
│   ├── config.py                 # Environment variables & CORS settings
│   ├── main.py                   # API routes & middleware
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend technical documentation
│
├── frontend/                     # React / Vite SPA frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   │   ├── Header.jsx        # Masthead headline & value proposition
│   │   │   ├── ResultsSummary.jsx# Summary panel & category breakdown
│   │   │   └── SourceCard.jsx    # Source display card with external link
│   │   ├── App.jsx               # Main state controller
│   │   ├── App.css / index.css   # Styling & typography
│   │   └── main.jsx              # React mounting root
│   ├── vercel.json               # Vercel SPA routing configuration
│   ├── vite.config.js            # Vite configuration
│   └── README.md                 # Frontend technical documentation
│
├── ARCHITECTURE.md               # Detailed system architecture document
├── DEPLOYMENT.md                 # Production deployment guide
├── render.yaml                   # Infrastructure as Code (Render Web Service)
└── README.md                     # Project overview (this file)
```

---

## 🚀 Quickstart: Running Locally

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies & run
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- **Health Check**: `http://127.0.0.1:8000/api/health`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
- **Frontend UI**: `http://localhost:5173`

---

## 🌐 Production Deployment

| Component | Platform | Build Command | Output / Start | Guide |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | **Render** | `pip install -r requirements.txt` | `uvicorn main:app --host 0.0.0.0 --port $PORT` | [DEPLOYMENT.md](DEPLOYMENT.md#1️⃣-part-1-deploy-backend-to-render) |
| **Frontend** | **Vercel** | `npm run build` | `dist/` | [DEPLOYMENT.md](DEPLOYMENT.md#2️⃣-part-2-deploy-frontend-to-vercel) |

For complete step-by-step deployment instructions, see [**DEPLOYMENT.md**](DEPLOYMENT.md).

---

## 📌 Branching Strategy

- **`staging`**: Active development branch. All feature implementations and testing occur here.
- **`main`**: Production release branch. Merged from `staging` via Pull Requests.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

