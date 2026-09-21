# Team Forge — Autonomous Startup Idea Validator (v3.0)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg)](https://vitejs.dev/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Orchestration-orange.svg)](https://crewai.com)
[![Groq LPU](https://img.shields.io/badge/Groq-LPU%20Inference-f55036.svg)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Team Forge (ISB7.3)**: An autonomous multi-agent validation engine that transforms raw, unvetted startup ideas into comprehensive, evidence-grounded venture dossiers in under 60 seconds.

---

## 📌 System Architecture & Pipeline

Team Forge v3.0 replaces superficial LLM wrappers with an **autonomous 9-stage sequential validation pipeline** combining agentic search tool-calling, deterministic mathematical scoring, and multi-quadrant strategic reasoning:

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   React 18 + Vite Frontend                                        │
│  (Editorial Light Theme • Fluid 4-Col Grid • § Jump Navigation • 12 Analytical Modules • PDF Dossier)│
└─────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                  │ POST /api/validate (JSON)
                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FastAPI Backend Engine                                        │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Stage 1: IdeaExtractionAgent      ── Extract structured problem, solution, ICP, revenue model   │
│  Stage 2: MarketResearchAgent      ── Autonomous Tavily search tool-calling (Market, Comp, Demand)│
│  Stage 3: MarketAnalysisAgent      ── TAM/SAM/SOM sizing, CAGR, drivers, and barriers             │
│  Stage 4: CompetitorAnalysisAgent  ── Direct/indirect competitors, positioning, differentiation   │
│  Stage 5: WhiteSpaceEngine         ── Deterministic 2x2 opportunity gap scoring                   │
│  Stage 6: SWOTAgent                ── 4-quadrant strategic matrix synthesized from real evidence  │
│  Stage 7: MVPAgent                 ── 3-phase product roadmap, core features & risk mitigation    │
│  Stage 8: GTMAgent                 ── Multi-channel acquisition strategy & launch milestones      │
│  Stage 9: ValidationReport Builder ── Schema validation, composite scoring & honest grounding     │
└─────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                  │ Groq LPUs (Qwen 2.5 32B / Llama 3.3 70B)
                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         Verified Market Intelligence & Venture Dossier                            │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Innovations & Engineering Highlights

1. **Autonomous Tool-Calling via CrewAI**:
   - `MarketResearchAgent` autonomously decides query syntax, evaluation criteria, and search iterations across 3 dedicated tools: `search_market_data`, `search_competitors`, and `search_customer_demand`.
   - Built-in **Selective Autonomy**: Automatically executes consumer demand searches for B2C/hybrid concepts while bypassing irrelevant B2C queries for pure enterprise/B2B ideas.

2. **Strict Anti-Hallucination & Snippet Budgeting**:
   - Compiles raw search findings into a rich 1,500-character context budget per source, preventing premature context truncation and guaranteeing named competitors (e.g., Medisafe, MyTherapy, Livongo) are accurately extracted.
   - Dynamic **`[HONEST GROUNDING NOTICE]`**: When web evidence returns 0 citations for a category, the system transparently renders an amber disclaimer banner rather than fabricating synthetic data.

3. **Strategic Synthesis Layer (Milestone 3)**:
   - **`SWOTAgent`**: Transforms empirical market and competitor signals into actionable Strengths, Weaknesses, Opportunities, and Threats.
   - **`MVPAgent`**: Produces a disciplined 3-phase product roadmap (Phase 1 MVP, Phase 2, Phase 3) tied directly to validated market gaps.
   - **`GTMAgent`**: Delivers a concrete go-to-market plan covering customer acquisition channels, funnel strategies, and launch milestones.

4. **Externalized Prompt Architecture**:
   - Modular prompt system (`backend/prompts/*.md`) separating system roles and task instructions with clean template interpolation via `loader.py`.

5. **Ultra-Low Latency Inference**:
   - Powered by **Groq LPUs** serving open-weights foundation models (`qwen-2.5-32b` / `llama-3.3-70b-versatile`) achieving high tokens-per-second generation speeds.

---

## 📁 Repository Organization

```
team-forge/
├── backend/                    # FastAPI backend & multi-agent pipeline
│   ├── agents/                 # 8 Specialized analytical agents (Extraction, Market, SWOT, MVP, etc.)
│   ├── crew/                   # CrewAI orchestration layer, tasks, and Tavily search tools
│   ├── prompts/                # Externalized Markdown prompt templates (*_system.md, *_task.md)
│   ├── schemas/                # Pydantic data models & request/response contracts
│   ├── scripts/                # Benchmark suites, regression scripts, and e2e tests
│   ├── services/               # White-Space Engine, LLM service, and text sanitizers
│   ├── tests/                  # Pytest unit and integration test suites
│   ├── config.py               # Central environment configuration
│   ├── main.py                 # FastAPI application routes & CORS setup
│   └── requirements.txt        # Python dependency manifest
├── frontend/                   # React 18 + Vite frontend application
│   ├── src/
│   │   ├── components/         # 12 Modular analytical presentation components
│   │   ├── App.css             # Global editorial styling rules
│   │   ├── App.jsx             # Core application controller & validation state
│   │   ├── index.css           # Tailwind base rules & CSS variables
│   │   └── main.jsx            # React root mount
│   ├── package.json            # Node.js dependencies
│   ├── tailwind.config.js      # Tailwind design configuration
│   └── vite.config.js          # Vite bundler configuration
└── docs/                       # 14 Comprehensive technical & academic documentation files
    ├── 01_PROJECT_OVERVIEW.md
    ├── 04_SYSTEM_DESIGN.md
    ├── 05_AI_ML_ARCHITECTURE.md
    ├── 13_API_COST_ACCURACY_AND_SYSTEM_METRICS.md
    ├── 14_AI_MODELS_ARCHITECTURE_AND_SELECTION_GUIDE.md
    └── ... (Full suite of architecture diagrams and specs)
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 18.0.0 or higher
- **API Keys**:
  - `GROQ_API_KEY` ([console.groq.com](https://console.groq.com))
  - `TAVILY_API_KEY` ([tavily.com](https://tavily.com))

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY and TAVILY_API_KEY

# Launch FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Backend API interactive docs: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
# In a separate terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Testing & Benchmark Verification

```bash
# Run backend unit & integration tests
pytest backend/tests -v

# Run smoke test
python backend/scripts/smoke_test.py

# Run agentic tool-calling verification
python backend/scripts/run_agentic_verification.py

# Run 5-idea multi-domain regression suite
python backend/scripts/run_5_regression_ideas.py

# Run frontend production build check
cd frontend && npm run build
```

---

## 📚 Technical Documentation Suite

For complete architectural specifications, UML diagrams, academic reports, and cost analyses, visit the [`docs/`](docs/) directory:

| Document | Title | Focus Area |
| :--- | :--- | :--- |
| **`docs/01_PROJECT_OVERVIEW.md`** | Project Overview | Problem statement, value proposition, and user personas. |
| **`docs/04_SYSTEM_DESIGN.md`** | System Design | Detailed component architecture, sequence flows, and contracts. |
| **`docs/05_AI_ML_ARCHITECTURE.md`** | AI/ML Architecture | CrewAI agent configuration, prompt templates, and reasoning chains. |
| **`docs/13_API_COST_ACCURACY_AND_SYSTEM_METRICS.md`** | Cost & Metrics | Token economics, Tavily search costs, latency, and grounding metrics. |
| **`docs/14_AI_MODELS_ARCHITECTURE_AND_SELECTION_GUIDE.md`** | AI Models Guide | LLM selection matrix, Groq LPU benchmark comparisons, and prompt engineering. |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
