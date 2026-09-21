# System Architecture — Startup Idea Validator (v3.0 / Milestone 3)

## 1. Executive Summary & Overview

The **Startup Idea Validator (Team Forge v3.0)** is an enterprise-grade autonomous multi-agent validation engine that transforms natural language startup pitches of arbitrary length into structured, verified market intelligence. It replaces subjective assumptions and superficial LLM summaries with an evidence-grounded, multi-quadrant analytical dossier backed by live search tool-calling.

### Key Milestones & Capabilities Delivered in v3.0:
- **Full 9-Stage Validation Pipeline**:
  1. `IdeaExtractionAgent`: Extracts core problem, solution, target audience, revenue model, and industry vertical.
  2. `MarketResearchAgent`: CrewAI autonomous agent invoking discrete Tavily search tools (`search_market_data`, `search_competitors`, `search_customer_demand`) with selective autonomy.
  3. `MarketAnalysisAgent`: Derives TAM, SAM, SOM, CAGR, growth drivers, and market entry barriers with zero numerical hallucination.
  4. `CompetitorAnalysisAgent`: Identifies direct and indirect competitors, positioning vectors, feature matrices, and source citations using snippet budgeting (1,500 chars/source).
  5. `WhiteSpaceEngine`: Deterministic 2x2 opportunity gap analysis triangulating customer pain points, competitor voids, and startup core capabilities.
  6. `SWOTAgent`: 4-quadrant strategic matrix (Strengths, Weaknesses, Opportunities, Threats) synthesizing empirical market and competitor findings.
  7. `MVPAgent`: Disciplined 3-phase product roadmap (Phase 1 MVP, Phase 2, Phase 3), feature prioritization, and technical risk mitigation.
  8. `GTMAgent`: Comprehensive go-to-market plan covering customer acquisition channels, conversion funnels, CAC strategy, and launch milestones.
  9. `ValidationReportBuilder`: Assembles complete Pydantic contract with composite viability scoring and honest grounding indicators.
- **Externalized Prompt Architecture**: System prompts (`*_system.md`) and task instructions (`*_task.md`) externalized in `backend/prompts/` with runtime template variable interpolation.
- **Modern Editorial Frontend**: React 18 + Vite dashboard with fluid 4-column responsive grid, jump-navigation bar (`§ JUMP TO:`), dynamic 9-stage pipeline visualizer, and live `[HONEST GROUNDING NOTICE]` alerts.
- **Ultra-Fast LPU Inference**: Powered by Groq LPUs utilizing open-weights models (`qwen-2.5-32b` / `llama-3.3-70b-versatile`).

---

## 2. End-to-End System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Client Presentation Tier (React 18 + Vite)                      │
│   - Editorial Light Theme • Fluid 4-Column Layout • Zero Margin Waste                             │
│   - Real-time 9-Stage Pipeline Visualizer                                                         │
│   - Structured Metadata & Industry Decomposition Card                                             │
│   - Evidence-Backed White-Space Map (2x2 Matrix)                                                  │
│   - Market Sizing Scorecard (TAM/SAM/SOM, CAGR, Growth Drivers, Barriers)                        │
│   - Competitor Discovery & Positioning Matrix (Direct & Indirect Rivals)                          │
│   - Customer Segmentation & ICP Personas (with [HONEST GROUNDING NOTICE] banner)                  │
│   - Strategic SWOT Analysis Matrix (Strengths, Weaknesses, Opportunities, Threats)                │
│   - MVP Product Recommendation (Phased Roadmap, Feature Priorities, Risk Mitigation)             │
│   - Go-To-Market (GTM) Strategy (Acquisition Channels, Funnels, Milestones)                       │
│   - Verified Web Citations Drawer & Printable PDF Dossier Generator                              │
└─────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                  │ HTTP POST /api/validate
                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FastAPI Backend Engine                                      │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  API Gateway & Routers (/api/health, /api/validate)                                               │
│  Schema Validation Layer (Pydantic v2 Models: ValidationRequest / ValidationResponse)             │
│                                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 9-Stage Multi-Agent Validation Pipeline                                                     │  │
│  │                                                                                             │  │
│  │ 1. IdeaExtractionAgent ───► Structured Pitch Extraction (Problem, Solution, Audience)     │  │
│  │                                                                                             │  │
│  │ 2. ValidationCrewOrchestrator (CrewAI)                                                      │  │
│  │    └─► MarketResearchAgent ──► Autonomous Tool-Calling via Tavily Search API               │  │
│  │        ├── search_market_data()                                                             │  │
│  │        ├── search_competitors()                                                             │  │
│  │        └── search_customer_demand() (Selective Autonomy: B2C vs B2B)                       │  │
│  │                                                                                             │  │
│  │ 3. MarketAnalysisAgent ────► TAM/SAM/SOM, CAGR, Market Drivers & Barriers                  │  │
│  │                                                                                             │  │
│  │ 4. CompetitorAnalysisAgent ─► Direct & Indirect Rivals (1500 char snippet budgeting)        │  │
│  │                                                                                             │  │
│  │ 5. WhiteSpaceEngine ───────► Deterministic 2x2 Opportunity Gap Mapping                     │  │
│  │                                                                                             │  │
│  │ 6. SWOTAgent ──────────────► 4-Quadrant Strategic Synthesis Matrix                          │  │
│  │                                                                                             │  │
│  │ 7. MVPAgent ───────────────► 3-Phase Product Roadmap & Technical Risk Mitigation            │  │
│  │                                                                                             │  │
│  │ 8. GTMAgent ───────────────► Channel Strategy, Conversion Funnels, Launch Milestones        │  │
│  │                                                                                             │  │
│  │ 9. Response Synthesizer ───► Composite Scoring (0-100), Citation Mapping & Packaging       │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                   │
│  Shared Infrastructure & Services:                                                                │
│  ├── PromptLoader (backend/prompts/*.md)                                                          │
│  ├── LLMService (Groq LPU API: Qwen 2.5 32B / Llama 3.3 70B)                                    │
│  ├── WhiteSpaceEngine (Deterministic scoring & triangulation)                                     │
│  └── TextUtils (Sanitization, JSON extraction, character budgeting)                               │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Agent Specifications

| Agent | Responsibility | Prompt Template | Primary LLM Model |
| :--- | :--- | :--- | :--- |
| **`IdeaExtractionAgent`** | Converts raw pitch text into clean semantic entities: problem, solution, ICP, revenue model, industry vertical. | `idea_extraction_system.md` | `qwen-2.5-32b` |
| **`MarketResearchAgent`** | Autonomous CrewAI research agent invoking Tavily search tools. Dynamically forms queries and iterates based on context. | CrewAI Task Prompt | `qwen-2.5-32b` |
| **`MarketAnalysisAgent`** | Extracts empirical market size figures (TAM/SAM/SOM), growth CAGR, drivers, and barriers from search citations. | `market_analysis_system.md`<br>`market_analysis_task.md` | `qwen-2.5-32b` |
| **`CompetitorAnalysisAgent`** | Discovers named direct and indirect market competitors, extracting strengths, weaknesses, and differentiation. | `competitor_analysis_system.md`<br>`competitor_analysis_task.md` | `qwen-2.5-32b` |
| **`WhiteSpaceEngine`** | Deterministic algorithmic triangulation of customer pain vs competitor omissions vs pitch capabilities. | Algorithmic Service | Pure Python Service |
| **`SWOTAgent`** | Synthesizes Strengths, Weaknesses, Opportunities, and Threats from empirical market and competitor findings. | `swot_system.md`<br>`swot_task.md` | `qwen-2.5-32b` |
| **`MVPAgent`** | Translates validated white-space gaps into an actionable 3-phase product development roadmap with risk mitigation. | `mvp_system.md`<br>`mvp_task.md` | `qwen-2.5-32b` |
| **`GTMAgent`** | Formulates go-to-market acquisition channels, conversion funnels, CAC optimization, and launch milestones. | `gtm_system.md`<br>`gtm_task.md` | `qwen-2.5-32b` |

---

## 4. Anti-Hallucination & Data Integrity Invariants

1. **Strict Snippet Budgeting**: Raw search snippets from Tavily are allocated 1,500 characters per source, preventing premature context truncation while preserving token economy on Groq LPUs.
2. **Selective Autonomy Guard**: B2C and hybrid consumer concepts automatically trigger consumer demand exploration, while pure B2B/enterprise concepts skip consumer demand searches to avoid generic consumer noise.
3. **Honest Grounding Notice**: When search tools return 0 valid sources for a category (e.g., emerging consumer niche), the frontend displays a prominent amber disclaimer banner (`[HONEST GROUNDING NOTICE]`) and marks personas as theoretical rather than asserting empirical validation.
4. **Deterministic White-Space Triangulation**: White-space scoring is computed mathematically through vector alignment rather than single-shot LLM guesswork.
