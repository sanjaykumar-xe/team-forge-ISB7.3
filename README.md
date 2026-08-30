# Startup Idea Validator

> An intelligent multi-agent platform for validating early-stage startup concepts against real-time market data.

Developed as part of the **Team Forge (ISB7.3)** project.

---

## 📌 System Architecture & Pipeline

The platform uses an in-process multi-agent pipeline to transform raw startup ideas into structured market intelligence across 4 strategic dimensions:

```
┌────────────────────────────────────────────────────────┐
│                   React + Vite UI                      │
│   (Submission Form, AI Dossier Card, Evidence Grid)    │
└───────────────────────────┬────────────────────────────┘
                            │ POST /api/validate (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│               (/api/health, /api/validate)             │
└─────────────┬────────────────────────────▲─────────────┘
              │ 1. Ingest Idea & Metadata  │ 4. Verified Sources
              ▼                            │
┌───────────────────────────┐  ┌─────────────────────────┐
│   IdeaExtractionAgent     │  │   DataRetrievalAgent    │
│   (Groq LLM: Qwen-27B)    │  │  - Blocked Domain Filter│
│  - Extracts Domain Context│  │  - langdetect English   │
│  - Identifies Keywords    │  │  - URL Deduplication    │
└─────────────┬─────────────┘  └───────────▲─────────────┘
              │ 2. Structured Parameters   │ 3. Raw Batches
              ▼                            │
┌──────────────────────────────────────────┴─────────────┐
│                    WebSearchAgent                      │
│                  (Tavily Search API)                   │
│  - Parallel ThreadPool Searches across 4 Categories:   │
│    * Competitors & Alternatives                        │
│    * Industry News & Trends (topic="news")             │
│    * Customer Demand & Problem Signals                 │
│    * Market Size & Growth Forecasts                    │
└────────────────────────────────────────────────────────┘
```

For complete technical specifications, data contracts, and design diagrams, see [**ARCHITECTURE.md**](ARCHITECTURE.md) and [**SYSTEM_ARCHITECTURE.md**](SYSTEM_ARCHITECTURE.md).

---

## 📁 Repository Structure

```
team-forge/
├── backend/                      # Python / FastAPI backend service
│   ├── agents/                   # Autonomous research agents
│   │   ├── __init__.py           # Agent module exports
│   │   ├── idea_extraction_agent.py # Groq LLM semantic extraction & failover
│   │   ├── web_search_agent.py   # Multi-category parallel search via Tavily
│   │   └── data_retrieval_agent.py # Sanitization, deduplication, & scoring
│   ├── scripts/                  # Evaluation & testing scripts
│   │   ├── run_eval.py           # 10-idea automated benchmark runner
│   │   └── smoke_test.py         # Fast pipeline sanity test
│   ├── tests/                    # Unit tests
│   │   ├── __init__.py
│   │   └── test_agents.py
│   ├── config.py                 # Environment variables & CORS settings
│   ├── main.py                   # FastAPI routes & in-process agent pipeline
│   ├── requirements.txt          # Python dependencies (FastAPI, Groq, Tavily, etc.)
│   └── README.md                 # Backend technical documentation
│
├── frontend/                     # React / Vite SPA frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   │   ├── Header.jsx        # Masthead headline & value proposition
│   │   │   ├── ExtractedMetadata.jsx # Stamped AI Dossier metadata card
│   │   │   ├── ExtractedMetadata.css  # Dossier card styling
│   │   │   ├── ResultsSummary.jsx# Summary panel with animated count-up
│   │   │   ├── CategorySection.jsx# 3-column responsive category grid
│   │   │   └── SourceCard.jsx    # Evidence card with snippet cleaner & pinned footer
│   │   ├── App.jsx               # Main state orchestrator
│   │   ├── App.css / index.css   # Styling, design tokens & typography
│   │   └── main.jsx              # React mounting root
│   ├── vercel.json               # Vercel SPA routing configuration
│   ├── vite.config.js            # Vite configuration
│   └── README.md                 # Frontend technical documentation
│
├── ARCHITECTURE.md               # Detailed system architecture document
├── SYSTEM_ARCHITECTURE.md        # Comprehensive multi-agent specification & diagrams
├── PROJECT_EXPLANATION.md        # Complete technical guide & mentor walkthrough
├── DEPLOYMENT.md                 # Production deployment guide
├── render.yaml                   # Infrastructure as Code (Render Web Service)
└── README.md                     # Project overview (this file)
```

---

## 🛠️ Technology Stack

| Layer | Technologies & Dependencies | Purpose |
| :--- | :--- | :--- |
| **Backend** | `fastapi==0.115.0`, `uvicorn[standard]==0.30.6`, `pydantic==2.9.2` | REST API Gateway & schema serialization |
| **LLM Extraction** | `groq>=0.9.0` (`qwen/qwen3.8-27b`, `allam-2-7b`, `groq/compound-mini`) | Domain context extraction & polysemy disambiguation |
| **Search Engine** | `tavily-python>=0.3.0` | 4-category AI-native search with calibrated relevance scoring |
| **Sanitization** | `langdetect>=1.0.9`, `wordfreq>=3.1.0`, `lxml>=5.0.0` | Language check, gibberish filter, HTML processing |
| **Frontend** | React 18, Vite `5.4.x`, Vanilla CSS | Fast, responsive editorial SPA |
| **Typography** | Instrument Serif, Inter, Space Mono | High-contrast editorial aesthetic |
| **Deployment** | Render (Backend Web Service), Vercel (Frontend SPA) | Cloud hosting & continuous deployment |

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
