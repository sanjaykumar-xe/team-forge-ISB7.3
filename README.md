# Startup Idea Validator (Milestone 2)

> An autonomous multi-agent platform for validating early-stage startup concepts against real-time market data, competitive intelligence, customer segmentation, and evidence-backed white-space discovery.

Developed as part of the **Team Forge (ISB7.3)** project.

---

## 📌 System Architecture & Pipeline

The platform utilizes a **CrewAI sequential multi-agent orchestration layer** to transform raw startup pitches into comprehensive market validation intelligence:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   React + Vite UI                                      │
│   (Unlimited Submission, Dossier, White-Space Map, Market Sizing, Competitors Grid)   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ POST /api/validate (JSON)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FastAPI Backend                                     │
│                              (/api/health, /api/validate)                              │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CrewAI Sequential Orchestrator                            │
│                                                                                        │
│  [1] Idea Extraction Agent       ──> Product identity, vertical, problem & keywords    │
│            ↓                                                                           │
│  [2] Web Search Agent            ──> Parallel Tavily queries across 4 categories       │
│            ↓                                                                           │
│  [3] Data Retrieval Agent        ──> Domain blocklist, langdetect English check, rank  │
│            ↓                                                                           │
│  [4] Market Opportunity Agent    ──> TAM/SAM estimates, CAGR, customer persona breakdown│
│            ↓                                                                           │
│  [5] Competitor Analysis Agent   ──> Direct/indirect rivals, comparison matrix, gaps   │
│            ↓                                                                           │
│  Evidence-Backed White-Space Engine ──> Customer Pain ∩ Competitor Void ∩ Startup Fit  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

For complete technical specifications, data contracts, and design diagrams, see [**ARCHITECTURE.md**](ARCHITECTURE.md), [**SYSTEM_ARCHITECTURE.md**](SYSTEM_ARCHITECTURE.md), and [**PROJECT_EXPLANATION.md**](PROJECT_EXPLANATION.md).

---

## 📁 Repository Structure

```
team-forge/
├── backend/                      # Python / FastAPI backend service
│   ├── agents/                   # Autonomous research & intelligence agents
│   │   ├── __init__.py           # Agent module exports
│   │   ├── idea_extraction_agent.py # Groq LLM semantic extraction & failover
│   │   ├── web_search_agent.py   # Multi-category parallel search via Tavily
│   │   ├── data_retrieval_agent.py # Sanitization, deduplication, & scoring
│   │   ├── market_analysis_agent.py # TAM/SAM sizing, CAGR, customer personas
│   │   └── competitor_analysis_agent.py # Direct/indirect rivals, matrix, gaps
│   ├── crew/                     # CrewAI orchestration layer
│   │   ├── __init__.py
│   │   ├── agents.py             # CrewAI Agent factories
│   │   ├── tasks.py              # CrewAI Task definitions
│   │   ├── tools.py              # Custom CrewAI tools
│   │   └── orchestrator.py       # Sequential pipeline orchestrator
│   ├── schemas/                  # Pydantic data contracts
│   │   ├── __init__.py
│   │   └── validation_schemas.py # Request/response typed schemas
│   ├── services/                 # Core analytical services
│   │   ├── __init__.py
│   │   ├── llm_service.py        # Centralized Groq inference with model failover
│   │   └── white_space_engine.py # Evidence-Backed Market White-Space Engine
│   ├── scripts/                  # Evaluation & benchmark runners
│   │   ├── test_milestone2_e2e.py # 3-Industry end-to-end test suite
│   │   ├── run_eval.py           # 10-idea automated benchmark runner
│   │   └── smoke_test.py         # Fast sanity test
│   ├── tests/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_agents.py        # Milestone 1 agent tests
│   │   └── test_milestone2.py    # Milestone 2 agent & schema tests
│   ├── config.py                 # Environment variables & CORS settings
│   ├── main.py                   # FastAPI application gateway
│   └── requirements.txt          # Python dependencies (CrewAI, FastAPI, Groq, Tavily, etc.)
│
├── frontend/                     # React / Vite SPA frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   │   ├── Header.jsx        # Masthead headline & value proposition
│   │   │   ├── ExtractedMetadata.jsx # Stamped AI Dossier metadata card
│   │   │   ├── ExtractedMetadata.css  # Dossier card styling
│   │   │   ├── WhiteSpaceAnalysis.jsx # Centerpiece White-Space Map & Strategy Flow
│   │   │   ├── MarketOpportunity.jsx # Market sizing, CAGR & attractiveness
│   │   │   ├── CustomerSegments.jsx  # Customer persona breakdown (End Users vs Decision Makers)
│   │   │   ├── CompetitorAnalysis.jsx# Direct/indirect rivals & comparison matrix
│   │   │   ├── ResultsSummary.jsx# Summary panel with animated count-up
│   │   │   ├── CategorySection.jsx# 3-column responsive category grid
│   │   │   └── SourceCard.jsx    # Evidence card with snippet cleaner & pinned footer
│   │   ├── App.jsx               # Main state orchestrator (Unlimited Input Length)
│   │   ├── App.css / index.css   # Editorial styling, design tokens & typography
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
| **Backend Framework** | `fastapi==0.115.0`, `uvicorn[standard]>=0.30.6`, `pydantic>=2.9.2` | REST API Gateway & typed data serialization |
| **Agent Orchestration** | `crewai>=1.15.0` (`Agent`, `Task`, `Crew`, `Process.sequential`) | Multi-agent coordination and task handoffs |
| **LLM Inference** | `groq>=0.9.0` (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `allam-2-7b`) | Domain extraction, market sizing, competitive analysis, white space |
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

## 🧪 Running Automated Tests

```bash
# Run Milestone 1 Agent tests
python backend/tests/test_agents.py

# Run Milestone 2 Unit tests
python backend/tests/test_milestone2.py

# Run the 3-Industry End-to-End Benchmark Suite
python backend/scripts/test_milestone2_e2e.py
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
