# 05. AI / Multi-Agent Architecture

## 1. Agent Ecosystem Overview
The intelligence layer of the **Startup Idea Validator** is governed by an autonomous multi-agent pipeline implemented via **CrewAI** and **Groq Cloud LLM** inference.

Each agent possesses specialized system instructions, distinct tool capabilities, and rigorous output data contracts.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MULTI-AGENT EXECUTION GRAPH                        │
│                                                                             │
│  [Idea Pitch]                                                               │
│       │                                                                     │
│       ▼                                                                     │
│  [Agent 1: IdeaExtractionAgent] ──► Extracts Domain Parameters & Keywords   │
│       │                                                                     │
│       ▼                                                                     │
│  [Agent 2: MarketResearchAgent] ──► Autonomous Tool-Calling (3-5 Searches)  │
│       │                             [Competitors, News, Demand, Sizing]     │
│       ▼                                                                     │
│  [Agent 3: DataRetrievalAgent]  ──► Deterministic Filtering & Dedup         │
│       │                                                                     │
│       ├───────────────────────────────────────────────┐                     │
│       ▼                                               ▼                     │
│  [Agent 4: MarketOpportunityAgent]        [Agent 5: CompetitorAgent]        │
│  (TAM/SAM, CAGR, Personas)                (Direct/Indirect, Matrix)         │
│       │                                               │                     │
│       └───────────────────────┬───────────────────────┘                     │
│                               ▼                                             │
│                  [Agent 6: WhiteSpaceEngine]                                │
│                  (Core Novelty Triangulation)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Deep-Dive & Specifications

### 2.1 Agent 1: `IdeaExtractionAgent`
- **Implementation**: [`backend/agents/idea_extraction_agent.py`](../backend/agents/idea_extraction_agent.py)
- **Primary Task**: Converts unstructured conversational pitches into structured domain context.
- **Cascading Failover Architecture**:
  ```
  Primary: qwen/qwen3.8-27b (Groq LPU)
       │ (on HTTP 429 Rate Limit)
       ▼
  Backup 1: allam-2-7b (Groq LPU)
       │ (on HTTP 429 Rate Limit)
       ▼
  Backup 2: groq/compound-mini (Groq LPU)
       │ (on Network Exception)
       ▼
  Fallback: Deterministic Regex Parser & Keyword Extraction
  ```
- **Extracted Contract**:
  - `product_name`: Inferred or normalized brand name.
  - `industry`: Standardized industry vertical (e.g. `DevSecOps`, `EdTech`).
  - `target_audience`: Primary user base profile.
  - `core_problem`: Synthesized acute friction statement.
  - `keywords`: 4–6 high-signal search terms.

### 2.2 Agent 2: Autonomous `MarketResearchAgent` (CrewAI)
- **Implementation**: [`backend/crew/agents.py`](../backend/crew/agents.py), [`backend/crew/tools.py`](../backend/crew/tools.py)
- **Role**: Expert Market Research Agent capable of autonomous reasoning and tool selection.
- **Governing Constraints**:
  - **Budget Cap**: Strictly enforces a maximum of **3 to 5 searches** per execution.
  - **Repetition Filter**: Intercepts queries with high semantic similarity to prior queries and returns a repetition notice directing the agent to analyze existing evidence or select an alternate category.
- **Search Tool Vector**:
  1. `search_competitors(query)`: Queries rivals, alternatives, substitutes.
  2. `search_industry_news(query)`: Queries recent regulatory shifts, venture rounds, tech trends.
  3. `search_customer_demand(query)`: Queries customer reviews, acute pain points, forum discussions.
  4. `search_market_size(query)`: Queries institutional market reports, TAM/SAM, CAGR projections.

### 2.3 Agent 3: `DataRetrievalAgent` (Deterministic Sanitizer)
- **Implementation**: [`backend/agents/data_retrieval_agent.py`](../backend/agents/data_retrieval_agent.py)
- **Design Rule**: Strictly non-LLM to guarantee 100% deterministic reproducibility.
- **Pipeline Stages**:
  1. **Blocked Domain Filter**: Strips non-commercial sources (`wikipedia.org`, `wiktionary.org`, `dictionary.com`, `britannica.com`, `merriam-webster.com`, `quora.com`).
  2. **Language Verification**: Uses seeded `langdetect` to reject non-English documents.
  3. **Canonical Deduplication**: Normalizes URLs (strips query parameters, hashes, trailing slashes) to guarantee cross-category uniqueness.
  4. **Score-Ranked Sorting**: Sorts sources descending by Tavily native semantic relevance score ($0.0 - 1.0$).

### 2.4 Agent 4: `MarketOpportunityAgent`
- **Implementation**: [`backend/agents/market_analysis_agent.py`](../backend/agents/market_analysis_agent.py)
- **Role**: Quantitative market sizing and customer persona modeling.
- **Honest Null-State Clamping (Anti-Hallucination)**:
  - If zero verifiable `Market Size & Trends` sources are returned by the search phase, the agent suppresses generic LLM priors:
    - Sets `market_size = []`
    - Sets `confidence = null`
    - Suppresses the Attractiveness Scorecard (`demand_strength`, `growth_strength`, etc. = `null`)
- **Granular Persona Differentiation**:
  - Daily End Users (hands-on workflow pain, daily friction, emotional frustration)
  - Economic Decision Makers (budget authority, security, compliance, ROI)

### 2.5 Agent 5: `CompetitorAnalysisAgent`
- **Implementation**: [`backend/agents/competitor_analysis_agent.py`](../backend/agents/competitor_analysis_agent.py)
- **Role**: Maps competitive density, positioning gaps, and competitor vulnerabilities.
- **Deliverables**:
  - Classifies players into `direct` competitors vs `indirect` substitutes.
  - Documents pricing models, core strengths, documented weaknesses, and customer complaints.
  - Constructs a multidimensional comparison matrix benchmarking the startup across critical dimensions.

### 2.6 Agent 6: `WhiteSpaceEngine` (Core Novelty)
- **Implementation**: [`backend/services/white_space_engine.py`](../backend/services/white_space_engine.py)
- **Novelty Algorithm**: Deterministically triangulates the three core market dimensions:
  $$\text{White-Space Gap} = \text{Customer Pain Point} \cap \text{Competitor Omission/Void} \cap \text{Startup Unique Capability}$$
- **Opportunity Output Structure**:
  - `opportunity_name`: High-conviction strategy title.
  - `segment`: Target customer persona.
  - `pain_point`: Documented friction point.
  - `competitor_coverage`: How incumbents fail to address it.
  - `differentiation_hypothesis`: Startup's defensible wedge.
  - `evidence_strength`: `High` / `Medium` / `Low`.
  - `confidence`: Calibrated percentage ($0.0 - 1.0$).
  - `evidence`: Direct URL citations proving the claim.
