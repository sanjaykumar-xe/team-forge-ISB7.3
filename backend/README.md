# Backend Service — Startup Idea Validator (Team Forge v3.0)

The backend is a high-performance **FastAPI** service that coordinates an autonomous 9-stage multi-agent intelligence pipeline for early-stage startup market research, strategic positioning, and validation.

---

## 🏛️ Architecture & Directory Layout

```
backend/
├── agents/                       # Specialized domain intelligence agents
│   ├── idea_extraction_agent.py  # Stage 1: Groq LLM semantic extraction & confidence scoring
│   ├── web_search_agent.py       # Stage 2: Tavily search engine with category routing & fallbacks
│   ├── data_retrieval_agent.py   # Stage 3: Deterministic URL dedup, sanitization & ranking
│   ├── market_analysis_agent.py  # Stage 4: TAM/SAM sizing, CAGR, and customer personas
│   ├── competitor_analysis_agent.py # Stage 5: Competitor mapping, feature matrix & gap analysis
│   ├── swot_agent.py             # Stage 7: Evidence-backed SWOT matrix & strategic risk roadmap
│   ├── mvp_agent.py              # Stage 8: Prioritized P0/P1/P2 MVP scoping with upstream grounding
│   └── gtm_agent.py              # Stage 9: Idea-specific Go-To-Market strategy & launch phases
├── crew/                         # CrewAI multi-agent orchestration layer
│   ├── agents.py                 # Autonomous MarketResearchAgent definition
│   ├── orchestrator.py           # 9-stage pipeline execution coordinator
│   ├── tasks.py                  # Structured research task specifications
│   └── tools.py                  # Custom tool suite (search_competitors, etc.) with budget cap
├── prompts/                      # Externalized prompt templates (.md)
│   ├── loader.py                 # Safe template interpolation utility
│   ├── idea_extraction_system.md
│   ├── web_search_system.md / web_search_task.md
│   ├── market_analysis_system.md / market_analysis_task.md
│   ├── competitor_analysis_system.md / competitor_analysis_task.md
│   ├── white_space_system.md / white_space_task.md
│   ├── swot_system.md / swot_task.md
│   ├── mvp_system.md / mvp_task.md
│   └── gtm_system.md / gtm_task.md
├── schemas/                      # Strict Pydantic data contracts
│   └── validation_schemas.py     # Request/response validation & serialization schemas
├── services/                     # Standalone analytical engines & utilities
│   ├── llm_service.py            # Resilient Groq LLM client with JSON validation & failover
│   ├── text_utils.py             # Word-boundary truncation & string formatting
│   └── white_space_engine.py     # Stage 6: Triangulates Customer Pain × Competitor Void × Solution Fit
├── scripts/                      # Evaluation harnesses & benchmark runners
│   ├── run_agentic_verification.py # 3-persona agentic verification suite
│   ├── run_5_regression_ideas.py # 5-idea multi-domain regression suite
│   ├── run_eval.py               # Grounding accuracy evaluation harness
│   └── smoke_test.py             # Single-idea fast sanity test
├── tests/                        # Automated unit & integration tests
│   ├── test_agents.py            # Unit tests for individual agent classes
│   └── test_milestone2.py        # Pipeline regression tests
├── config.py                     # Environment variables & CORS settings
├── main.py                       # FastAPI application entrypoint
└── requirements.txt              # Production Python dependencies
```

---

## ⚡ 9-Stage Validation Pipeline

```
[User Input Pitch]
         │
         ▼
[1] Idea Extraction Agent       ──> Parses problem, industry, audience, keywords
         │
         ▼
[2] Autonomous Research Agent   ──> CrewAI agent selectively invokes Tavily search tools
         │
         ▼
[3] Data Retrieval Agent        ──> Deterministic sanitization, URL dedup, categorizes sources
         │
         ▼
[4] Market Opportunity Agent    ──> TAM/SAM/SOM, CAGR, End User vs Buyer personas
         │
         ▼
[5] Competitor Discovery Agent  ──> Maps direct/indirect rivals, capability matrix, gaps
         │
         ▼
[6] White-Space Engine          ──> Triangulates Pain × Coverage Voids × Defensibility
         │
         ▼
[7] SWOT & Risk Agent           ──> 4-quadrant strategic matrix + risk mitigations
         │
         ▼
[8] MVP Scoping Agent           ──> Prioritized P0/P1/P2 feature set + v2 deferrals
         │
         ▼
[9] Go-To-Market Agent          ──> Channel fit rankings, positioning, launch phases
         │
         ▼
[ValidationResponse JSON]
```

---

## 🛡️ Anti-Hallucination & Honest Grounding Invariants

1. **Deterministic Cleansing**: Raw search results are scrubbed, validated for English coherence, and deduplicated using pure Python algorithms (zero LLM hallucination risk).
2. **Generous Excerpt Windows**: Source snippets are budgeted up to 1,500 characters so that specific product names, app store listings, and competitor matrices are never prematurely cut off.
3. **Honest Empty Sizing**: If verified web sources contain no quantitative market size figures, the system returns an empty list (`market_size: []`) with `confidence: null` rather than fabricating figures.
4. **Honest Customer Demand Notice**: If 0 direct customer demand/review sources are retrieved (e.g. in pure B2B verticals), the system surfaces an explicit `[HONEST GROUNDING NOTICE]` banner indicating personas are inferentially derived from market trends and competitor voids.
5. **Selective Search Autonomy**: The autonomous research agent selectively skips irrelevant tools (e.g. skipping consumer review searches for pure B2B semiconductor cleanroom metrology).

---

## 🔌 API Endpoints

### `POST /api/validate`
Validates a natural language startup concept and returns a comprehensive Validation Dossier.

**Request Payload (`IdeaSubmission`):**
```json
{
  "idea": "In-situ wafer defect metrology API using high-speed multi-beam electron scanning...",
  "product_name": "AuraSemicon",
  "industry": "Semiconductor Manufacturing & Metrology",
  "target_audience": "Semiconductor foundry process integration and yield engineering teams"
}
```

**Response (`ValidationResponse`):**
Returns extracted domain dossier, categorized sources, market opportunity analysis, competitor landscape, white-space map, SWOT matrix, MVP recommendation, and GTM strategy.

### `GET /api/health`
Returns service status and API version (`{"status": "ok", "version": "2.0.0"}`).

### `GET /docs`
Interactive Swagger OpenAPI documentation.

---

## 🚀 Setup & Local Execution

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11)
- Valid API keys for **Groq** and **Tavily**

### 2. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 3. Installation
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Running the Dev Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
