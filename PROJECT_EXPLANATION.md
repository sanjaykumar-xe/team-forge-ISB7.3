# Team Forge — Startup Idea Validator: Complete Technical Guide & System Explanation (Milestone 4 / v3.1)

> **Document Purpose**: Comprehensive, rigorously verified technical guide explaining the Team Forge Startup Idea Validator codebase, CrewAI multi-agent tool-calling architecture, deterministic sanitization pipeline, anti-hallucination grounding logic, SQLite relational persistence, Google OAuth 2.0 authentication, asynchronous background email delivery, publication-grade PDF export, empirical benchmarks, and hybrid cloud topology. Every claim in this document is directly verified against the active codebase.

---

## 📑 Document Structure & Index
1. [Project Overview & Core Mission](#1-project-overview--core-mission)
2. [Verified Architecture & Execution Flow (10-Stage Pipeline)](#2-verified-architecture--execution-flow-10-stage-pipeline)
3. [Design Decisions & Trade-Off Rationale](#3-design-decisions--trade-off-rationale)
4. [Data Honesty & Anti-Hallucination Grounding](#4-data-honesty--anti-hallucination-grounding)
5. [Authentication, Persistence & Async Email Automation ($0 Stack)](#5-authentication-persistence--async-email-automation-0-stack)
6. [Verified Technology Stack & LLM Configuration](#6-verified-technology-stack--llm-configuration)
7. [Testing & Verification Methodology](#7-testing--verification-methodology)
8. [Known Limitations & Current Constraints](#8-known-limitations--current-constraints)
9. [Milestone 1–4 Deliverables Checklist](#9-milestone-14-deliverables-checklist)
10. [Anticipated Mentor Q&A Reference](#10-anticipated-mentor-qa-reference)

---

## 1. Project Overview & Core Mission

### 1.1 Plain Language Value Proposition
When entrepreneurs evaluate a new startup concept, they typically spend 15–20 hours manually querying search engines, reading fragmented blogs, looking up analyst reports, and compiling competitor matrices. Traditional LLMs (e.g., vanilla ChatGPT) fail at this task because:
1. **Knowledge Cutoffs**: They cannot access live market data, new entrants, or recent market sizing reports.
2. **Hallucination Risk**: When asked for TAM/SAM or competitor names, they confidently invent plausible-sounding companies and market size numbers.
3. **Superficial Analysis**: They output generic advice ("Focus on marketing│ "Build an MVP") without triangulating actual customer pain, competitive voids, and distribution feasibility.

**Team Forge v3.1** automates this entire diligence workflow into an autonomous 10-stage intelligence pipeline that executes in under 60 seconds. It autonomously searches live web data, extracts empirical numbers, maps white-space gaps, generates a strategic SWOT matrix, formulates a 3-phase product MVP roadmap, crafts an actionable go-to-market strategy, provides an ongoing conversational startup advisor, and emails the complete executive report directly to the founder's Gmail.

### 1.2 The Core Problem Solved: Word-Sense Ambiguity & Naive Search Failures
A fundamental engineering challenge in automated market research is **word-sense ambiguity**. For example, a pitch for an AI compiler might generate searches for "compiler alternatives│ which returns programming language compilers (GCC, Clang) instead of AI inference compilers (TVM, TensorRT). 

Team Forge solves this by first executing an **Idea Extraction stage** that identifies the exact industry vertical, technical problem statement, target audience, and domain keywords before formulating search queries.

---

## 2. Verified Architecture & Execution Flow (10-Stage Pipeline)

### 2.1 Genuine CrewAI Tool-Calling vs. Sequential In-Process Scripting
Unlike naive multi-agent wrappers that merely chain static prompt templates, Team Forge incorporates genuine **CrewAI autonomous tool-calling**:
- `MarketResearchAgent` is instantiated as a CrewAI Agent with autonomous access to 4 discrete Tavily search tools (`search_competitors`, `search_industry_news`, `search_customer_demand`, `search_market_size`).
- The agent independently decides search query formulation, evaluates returned payloads, tracks query repetition to avoid redundant requests, and autonomously selects which category to research next.
- Once raw research is ingested and sanitized, downstream domain agents (`MarketAnalysisAgent`, `CompetitorAnalysisAgent`, `WhiteSpaceEngine`, `SWOTAgent`, `MVPAgent`, `GTMAgent`, and `StartupAdvisorAgent`) execute deterministic synthesis grounded strictly in the gathered citations.

### 2.2 System Topology Diagram

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                CLIENT / PRESENTATION LAYER                                        │
│  React 18 + Vite SPA (Deployed on Vercel) • Auto-Routing to Localhost/Render • Editorial UI Theme  │
│  [Google OAuth Login] • [Pitch Form & Async Toggle] • [Live 9-Stage Stepper] • [Dossier Library]  │
│  [Download as PDF (A4 Print)] • [View Email Preview] • [Interactive Startup Advisor Drawer]       │
└─────────────────────────────────┬─────────────────────────────────▲───────────────────────────────┘
                                  │ HTTP POST /api/validate (Sync)  │ HTTP Polling /api/jobs/{id}
                                  │ HTTP POST /api/validate/async   │ SSE / JSON Responses
                                  │ POST /api/advisor/chat          │ JWT Auth /api/auth/me
                                  ▼                                 │
┌───────────────────────────────────────────────────────────────────┴───────────────────────────────┐
│                           FASTAPI BACKEND ORCHESTRATOR (Render)                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Stage 1: IdeaExtractionAgent      ── Extract structured problem, solution, ICP, domain keywords  │
│  Stage 2: MarketResearchAgent      ── Autonomous Tavily multi-vector tool-calling (4 categories)   │
│  Stage 3: DataRetrievalAgent       ── Deduplication, 1,500 char snippet cap & domain sanitization  │
│  Stage 4: MarketAnalysisAgent      ── TAM/SAM/SOM sizing, CAGR, drivers, and user personas        │
│  Stage 5: CompetitorAnalysisAgent  ── Direct/indirect competitors, pricing & feature matrices     │
│  Stage 6: WhiteSpaceEngine         ── Triangulated customer demand vs competitor void engine      │
│  Stage 7: SWOTAgent                ── 4-quadrant strategic SWOT matrix & 12-month risk mitigation │
│  Stage 8: MVPAgent                 ── 3-phase product roadmap, core features & risk mitigation    │
│  Stage 9: GTMAgent                 ── Multi-channel customer acquisition strategy & launch plan   │
│  Stage 10: StartupAdvisorAgent     ── Multi-turn interactive chat grounded in report (Bounded LRU)│
└─────────────────────────────────┬─────────────────────────────────┬───────────────────────────────┘
                                  │                                 │
            ┌─────────────────────▼───────────────┐   ┌─────────────▼───────────────────────────────┐
            │   EXTERNAL RESEARCH & EMAIL LAYER   │   │  PERSISTENCE & LLM INFERENCE LAYER          │
            ├─────────────────────────────────────┤   ├─────────────────────────────────────────────┤
            │ • Tavily AI Search (Primary RAG)    │   │ • Groq Cloud LPUs (Qwen 2.5 / Llama 3.3)   │
            │ • DuckDuckGo (Fallback Search)      │   │ • SQLite DB (team_forge.db: Users & Jobs)   │
            │ • Gmail TLS SMTP (smtp.gmail.com)   │   │ • Bounded Session Cache (LRU <= 100 entries)│
            │ • Google Identity Services (OAuth)  │   │ • 14 Externalized Prompts (backend/prompts/)│
            └─────────────────────────────────────┘   └─────────────────────────────────────────────┘
```

### 2.3 The 10 Specialized Agents & Pipeline Components
1. **`IdeaExtractionAgent`**: Decomposes natural language pitches into structured entities: problem, proposed solution, target audience, revenue model, and domain search keywords.
2. **`MarketResearchAgent` (CrewAI)**: Autonomously searches live web data across 4 specialized categories (Competitors, Industry News, Customer Demand, Market Size).
3. **`DataRetrievalAgent` / Sanitizer**: Deterministic engine that deduplicates sources, enforces a strict 1,500-character snippet budget per competitor, and strips promotional web boilerplate.
4. **`MarketAnalysisAgent`**: Synthesizes market sizing estimates (TAM/SAM/SOM), compound annual growth rate (CAGR), drivers, and barriers.
5. **`CompetitorAnalysisAgent`**: Discovers direct and indirect competitors, maps feature/pricing comparisons, and identifies differentiation vectors.
6. **`WhiteSpaceEngine`**: Mathematical and semantic engine that triangulates unaddressed customer demand against competitor voids to produce defensible opportunities.
7. **`SWOTAgent`**: Formulates a 4-quadrant strategic SWOT matrix (Strengths, Weaknesses, Opportunities, Threats) grounded in empirical findings.
8. **`MVPAgent`**: Designs a disciplined 3-phase product roadmap (Phase 1 MVP, Phase 2, Phase 3), feature prioritization, and technical risk mitigation.
9. **`GTMAgent`**: Produces a go-to-market plan covering customer acquisition channels, conversion funnels, CAC strategy, and launch milestones.
10. **`StartupAdvisorAgent`**: Interactive conversational advisor endpoint (`POST /api/advisor/chat`) allowing founders to ask multi-turn questions grounded in their active dossier.

### 2.4 Externalized Prompt Template System
In Team Forge, all system and task instructions are externalized into 14 dedicated Markdown files under `backend/prompts/`:
- `*_system.md`: Defines agent identity, analytical framework, and strict output schema constraints.
- `*_task.md`: Formulates dynamic task directives with variable interpolation placeholders (`{idea_text}`, `{market_data}`, etc.).
- Managed cleanly by `backend/prompts/loader.py`, eliminating monolithic hardcoded prompt strings.

---

## 3. Design Decisions & Trade-Off Rationale

### 3.1 Why Tavily Search API Over Raw Web Scraping
Raw web scraping (e.g., BeautifulSoup, Playwright) suffers from frequent CAPTCHAs, bot blocks, high latency (10–30s per page), and unstructured DOM noise. Tavily provides clean, pre-extracted, relevance-ranked markdown snippets specifically optimized for LLM RAG pipelines in under 1 second.

### 3.2 Snippet Budgeting (1,500 Characters / Source)
In earlier iterations, competitor extraction occasionally produced generic categories ("Manual Workflows") instead of named products because raw search snippets were truncated too aggressively (e.g., 200–300 characters). 

We introduced a disciplined **Snippet Budgeting** mechanism allocating up to 1,500 characters per search source. This guarantees that named competitors mentioned deeper in articles (such as Medisafe, MyTherapy, Philips, Proteus, and Propeller Health in health-tech pitches) are fully visible to `CompetitorAnalysisAgent`.

### 3.3 Selective Autonomy for Customer Demand
A naive search strategy executes customer demand queries for every idea. However, for deep B2B or semiconductor concepts (e.g., AuraSemicon), consumer forums (Reddit, Quora) contain zero relevant signal. 

We calibrated the prompt directive to ensure:
- Consumer and hybrid health/fintech ideas (e.g., VitalSync) actively trigger customer demand queries.
- Pure B2B/enterprise infrastructure concepts correctly bypass customer demand queries, preventing hallucinations.

### 3.4 Bounded Cache Eviction Policy (LRU)
To prevent slow memory leaks on long-running deployed servers (such as Render's 512MB RAM tier), the `advisor_service` and validation caches implement an active bounded eviction policy:
- `MAX_CACHE_ENTRIES = 100`
- When either `VALIDATION_CACHE` or `SESSION_CONVERSATIONS` exceeds 100 entries, the oldest entries are evicted first (FIFO/LRU), guaranteeing constant $O(1)$ memory consumption.

---

## 4. Data Honesty & Anti-Hallucination Grounding

### 4.1 The "Insufficient Evidence" Honesty Principle
Most commercial AI tools fabricate answers when data is missing. Team Forge enforces an **Honest Grounding Invariant**:
- If web searches return 0 citations for customer demand or market size, the system explicitly outputs an empty or flagged result.
- The frontend dynamically detects 0-source categories and renders an amber **`[HONEST GROUNDING NOTICE]`** disclaimer banner directly above the personas section:
  > *"Notice: Zero direct web sources were found for Customer Demand. Personas shown below are theoretical profiles derived from problem analysis, not empirical user surveys."*

### 4.2 Production Bugs Identified & Resolved
1. **Case 1: Fabricated Competitors**: Early prompts allowed the LLM to list "Legacy Spreadsheets" as a competitor. Fixed by enforcing a strict named-entity validation filter in `CompetitorAnalysisAgent`.
2. **Case 2: Irrelevant Citations**: Fixed by introducing domain blacklists and relevance scoring in search result sanitization.
3. **Case 3: Truncated Competitor Extraction**: Resolved via the 1,500-character snippet budget, unlocking real product names across all benchmark runs.
4. **Case 4: False Positive Demand Searches**: Calibrated prompt gating to prevent unnecessary customer searches on pure B2B ideas.

---

## 5. Authentication, Persistence & Async Email Automation ($0 Stack)

### 5.1 Zero-Cost Architecture Principles
All features added in Milestone 4 operate at **$0 cost** with zero required paid cloud infrastructure:
- **Authentication**: Google OAuth 2.0 with 7-day signed HMAC-SHA256 JWT session tokens.
- **Relational Storage**: Embedded SQLite database (`backend/data/team_forge.db`) storing `users` and `validation_jobs`.
- **Asynchronous Execution**: Native FastAPI `BackgroundTasks` running 60-second multi-agent pipelines in the background without Redis or Celery.
- **Email Delivery**: Standard Gmail TLS SMTP (`smtp.gmail.com:587`) with automatic local HTML preview storage (`backend/data/emails/{job_id}.html`) when live credentials are not set.

### 5.2 Database Schema

#### `users` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | `PRIMARY KEY` | Unique user ID (`usr_...`) |
| `email` | `TEXT` | `UNIQUE NOT NULL` | Verified founder email |
| `name` | `TEXT` | - | Display name |
| `avatar_url` | `TEXT` | - | Profile avatar URL |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Account creation timestamp |

#### `validation_jobs` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `job_id` | `TEXT` | `PRIMARY KEY` | Job identifier (`val_...`) |
| `user_id` | `TEXT` | `FOREIGN KEY` | Linked user ID |
| `idea_text` | `TEXT` | `NOT NULL` | Startup concept pitch |
| `email` | `TEXT` | `NOT NULL` | Recipient email for report |
| `status` | `TEXT` | `NOT NULL` | `queued` \| `processing` \| `completed` \| `failed` |
| `result_json` | `TEXT` | - | Full serialized validation dossier |
| `error_message` | `TEXT` | - | Failure explanation if any |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Submission time |
| `completed_at` | `TIMESTAMP` | - | Completion time |

### 5.3 Asynchronous Execution Flow
1. Founder checks *"Asynchronous Research & Gmail Delivery"*, enters their Gmail, and clicks submit.
2. Frontend dispatches `POST /api/validate/async`. The backend immediately returns `HTTP 202 Accepted` with `{ job_id, status: "queued│ eta: "45-60s" }`.
3. The founder can safely close their browser tab or navigate away.
4. FastAPI `BackgroundTasks` runs the full 9-stage multi-agent pipeline in the background.
5. On completion, the result is saved to SQLite and an executive HTML email is compiled and dispatched via TLS SMTP to the founder's inbox.
6. If the founder remains on the page, real-time polling (`GET /api/jobs/{id}`) seamlessly transitions the UI to the completed dossier.

### 5.4 Publication-Grade PDF Export
- Prominent **`[📄 Download as PDF]`** toolbar button at the top of the dossier.
- Custom `@media print` CSS rules automatically hide all web chrome (forms, buttons, inputs, jump navigation, advisor textareas) and format the report cards with `page-break-inside: avoid` for crisp A4 PDF export.

---

## 6. Verified Technology Stack & LLM Configuration

### 6.1 Technology Stack Table

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | 0.115.0 | High-performance async REST API & BackgroundTasks |
| **Language Runtime** | Python | 3.11+ | Multi-agent execution engine |
| **Agent Orchestration** | CrewAI | 1.15.0+ | Autonomous tool-calling research agent |
| **LLM Inference** | Groq LPU Cloud | API | Ultra-low latency open-weights inference |
| **Search Engine** | Tavily Search API | 0.3.0+ | Real-time web research & source grounding |
| **Authentication** | PyJWT / google-auth | 2.8+ / 2.27+ | 7-day session JWTs & Google OAuth verification |
| **Database** | SQLite3 | Native | Zero-config relational persistence |
| **Email Dispatcher** | smtplib (TLS) | Native | Gmail SMTP executive dossier delivery |
| **Data Contracts** | Pydantic | 2.9.2+ | Strict type validation & JSON schemas |
| **Frontend Framework** | React | 18.3.1 | Single-page reactive application |
| **Build Tool** | Vite | 5.4.21 | Fast HMR and production bundler |
| **OAuth Component** | @react-oauth/google | 0.13.5 | Google Sign-In button and token provider |
| **Styling** | Vanilla CSS | Modern | Editorial Light design system & @media print |

### 6.2 Active Groq LLM Model Configuration Per Agent

| Agent / Service | Active Model | Rationale |
| :--- | :--- | :--- |
| `IdeaExtractionAgent` | `qwen-2.5-32b` | Superior JSON formatting and structured extraction accuracy |
| `MarketResearchAgent` | `qwen-2.5-32b` | Fast reasoning for autonomous query planning and tool selection |
| `MarketAnalysisAgent` | `qwen-2.5-32b` | Strong quantitative comprehension of TAM/SAM/SOM data |
| `CompetitorAnalysisAgent` | `qwen-2.5-32b` | Accurate entity extraction from multi-source search snippets |
| `SWOTAgent` | `qwen-2.5-32b` | Balanced synthesis of strategic strengths, weaknesses, and risks |
| `MVPAgent` | `qwen-2.5-32b` | Structured roadmap planning and technical feasibility analysis |
| `GTMAgent` | `qwen-2.5-32b` | Channel distribution modeling and milestone sequencing |
| `StartupAdvisorAgent` | `qwen-2.5-32b` | Context-grounded advisory conversation with bounded memory |
| Central Fallback | `llama-3.3-70b-versatile` | High-capacity fallback for complex edge cases |

---

## 7. Testing & Verification Methodology

### 7.1 Automated Test Suite Structure
```bash
# Unit & integration tests
pytest backend/tests -v

# Smoke test
python backend/scripts/smoke_test.py

# CrewAI agentic tool-calling verification
python backend/scripts/run_agentic_verification.py

# Evidence grounding & anti-hallucination verification
python backend/scripts/run_evidence_verification.py

# 5-Idea regression benchmark
python backend/scripts/run_5_regression_ideas.py

# Auth, SQLite & Async Email verification suite
python scratch/test_auth_and_async.py

# Frontend production build check
cd frontend && npm run build
```

### 7.2 Benchmark Results Summary
The system has been evaluated against diverse test cases across multiple verticals:
- **VitalSync** (Consumer Health / Med-Tech): Discovered Medisafe, MyTherapy, Philips, Proteus, Propeller Health.
- **AuraSemicon** (Enterprise Deep-Tech / EDA): Correctly skipped consumer demand searches and surfaced enterprise EDA competitors (Cadence, Synopsys).
- **EduFlow** (B2B SaaS / EdTech): Extracted realistic LMS competitors (Canvas, Blackboard) and enterprise pricing models.

---

## 8. Known Limitations & Current Constraints
1. **Third-Party API Rate Limits**: Groq and Tavily free-tier rate limits may cause intermittent 429 errors during heavy parallel benchmarking.
2. **Private Market Data**: Privately funded pre-seed startups that lack public press releases or web presence may not be indexed by Tavily.
3. **Complex Regulatory Nuances**: High-risk medical or financial regulatory assessments require specialized human legal counsel beyond high-level LLM analysis.
4. **Gmail Daily Quotas**: Standard Gmail SMTP accounts permit sending up to 500 emails/day for free, which is ideal for testing and MVP use. High-volume enterprise scaling can seamlessly transition to Brevo or Resend.

---

## 9. Milestone 1–4 Deliverables Checklist

### Milestone 1: Core Foundation & Research Engine
- [x] Natural language pitch input form & basic extraction.
- [x] Tavily search integration with category-based queries.
- [x] Initial React + Vite dashboard and results display.

### Milestone 2: Market Analysis & Competitor Intelligence
- [x] Multi-agent pipeline with Market Analysis Agent (TAM/SAM/SOM, CAGR).
- [x] Competitor Analysis Agent with feature & pricing comparison matrix.
- [x] Deterministic White-Space Engine computing defensible voids.
- [x] Anti-hallucination Grounding Invariant and `[HONEST GROUNDING NOTICE]` banner.

### Milestone 3: Strategic SWOT, MVP, GTM & Conversational Advisor
- [x] Full 9-stage validation pipeline with CrewAI autonomous tool-calling.
- [x] Strategic SWOT Matrix Agent (Strengths, Weaknesses, Opportunities, Threats).
- [x] MVP Recommendation Agent (Phase-1 scope, architecture, 60-day roadmap).
- [x] Go-To-Market Strategy Agent (ICP, viral channels, monetization).
- [x] Externalized prompt template architecture (`backend/prompts/*.md`).
- [x] Conversational Startup Advisor (`POST /api/advisor/chat`) with bounded memory.
- [x] Snippet budgeting (1,500 chars/source) eliminating competitor truncation.

### Milestone 4: Auth, SQLite Persistence & Async Email Automation
- [x] Google OAuth 2.0 & signed 7-day HMAC-SHA256 JWT session management.
- [x] SQLite relational storage (`backend/data/team_forge.db` — `users` & `validation_jobs`).
- [x] User Dossier Library & "📁 My Reports" modal drawer.
- [x] Asynchronous background validation (`POST /api/validate/async`) via FastAPI `BackgroundTasks`.
- [x] Real-time job polling endpoint (`GET /api/jobs/{id}`).
- [x] Automated responsive HTML email generator & TLS Gmail SMTP dispatcher.
- [x] Automatic local HTML preview fallback (`backend/data/emails/{job_id}.html`).
- [x] Publication-grade "Download as PDF" button with tailored `@media print` CSS.
- [x] Smart backend auto-routing (Localhost vs. live Render cloud auto-detection).

---

## 10. Anticipated Mentor Q&A Reference

### Q1: "Is this system genuinely agentic, or is it just a hardcoded sequential script—"
**Answer**: It is genuinely agentic at the search layer. The `MarketResearchAgent` is an autonomous CrewAI agent equipped with specialized search tools. It decides what queries to generate, evaluates the incoming data, detects repetitive searches, and autonomously determines if additional iterations are necessary. Downstream agents execute deterministic synthesis grounded strictly in the gathered citations to prevent cascading hallucinations.

### Q2: "How do you guarantee that market size numbers and competitors aren't hallucinated—"
**Answer**: Through our **Anti-Hallucination Grounding Invariant**:
1. Every market size figure (TAM, SAM, SOM, CAGR) must include a direct URL citation from the web search results.
2. If no source cites a specific number, the system explicitly returns `null` or an empty array rather than inventing an estimate.
3. Competitor entities are extracted strictly from search snippets using a 1,500-character budget per source, preventing the LLM from making up fictional rivals.

### Q3: "How does asynchronous email delivery work at $0 cost without paid message queues like Redis or Celery—"
**Answer**: By leveraging native **FastAPI `BackgroundTasks`**. When a request hits `POST /api/validate/async`, FastAPI immediately returns an HTTP 202 Accepted response and runs the multi-agent validation pipeline concurrently in Python's internal event loop. Once completed, the worker uses Python's standard `smtplib` over TLS to dispatch the report via Gmail SMTP (`smtp.gmail.com:587`). This completely eliminates the need for external queue infrastructure or paid brokers.

### Q4: "How are user reports and accounts persisted without a paid cloud database—"
**Answer**: Using an embedded **SQLite relational database** (`backend/data/team_forge.db`). It provides ACID compliance, fast local querying, and zero operational cost. Validation jobs are indexed by both `user_id` and `email`, allowing seamless dossier retrieval under "My Reports" regardless of authentication state.

### Q5: "How does the app prevent memory leaks with ongoing multi-turn advisor chat and background tasks—"
**Answer**: The backend implements an explicit **LRU eviction policy** (`MAX_CACHE_ENTRIES = 100`). Both the validation result cache and the multi-turn conversational session cache automatically evict the oldest entries once 100 idea IDs are stored, guaranteeing stable memory consumption on memory-constrained cloud environments like Render.
