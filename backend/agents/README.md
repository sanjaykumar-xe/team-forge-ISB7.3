# Team Forge — Backend Specialized Agents

This directory contains the discrete intelligence and processing agents that drive the Startup Idea Validation pipeline. Each agent is responsible for a specialized phase of market research, data synthesis, or strategic modeling.

---

## Agent Directory & Responsibilities

| Agent File | Class Name | Pipeline Stage | Primary Responsibility |
|---|---|---|---|
| `idea_extraction_agent.py` | `IdeaExtractionAgent` | Stage 1 | Parses unstructured natural language pitches into structured domain context (`product_name`, `industry`, `target_audience`, `core_problem`, `keywords`) with extraction confidence scoring. |
| `web_search_agent.py` | `WebSearchAgent` | Stage 2 | Executes verified search queries across 4 categories (Competitors, Industry News, Customer Demand, Market Size) using Tavily Search API with automated DDG/Google News safety fallbacks. |
| `data_retrieval_agent.py` | `DataRetrievalAgent` | Stage 3 | **Deterministic non-LLM step**: Sanitizes, cleans English coherence, deduplicates URLs, and groups web evidence into categorical batches. |
| `market_analysis_agent.py` | `MarketOpportunityAgent` | Stage 4 | Analyzes TAM/SAM/SOM sizing, compound annual growth rates (CAGR), market drivers, and granular customer persona profiles (daily end-users vs. economic buyers). |
| `competitor_analysis_agent.py` | `CompetitorAnalysisAgent` | Stage 5 | Identifies direct and indirect competitors from verified web evidence, generates comparison positioning matrices, and extracts competitor strengths and weaknesses. |
| `swot_agent.py` | `SWOTAgent` | Stage 7 | Synthesizes an evidence-backed SWOT matrix (Strengths, Weaknesses, Opportunities, Threats) and maps out high-severity strategic risks with mitigation roadmaps. |
| `mvp_agent.py` | `MVPAgent` | Stage 8 | Recommends a prioritized Minimum Viable Product (MVP) feature set (P0/P1/P2) with explicit upstream grounding back to verified market evidence, plus deferred v2 items and resource estimates. |
| `gtm_agent.py` | `GTMAgent` | Stage 9 | Generates idea-specific Go-To-Market strategies, including primary acquisition channels with fit scoring, core positioning statement, and phased launch milestones. |

---

## Architectural Principles
1. **Externalized Prompts**: Agents load modular system and task prompt templates from `backend/prompts/` via `loader.py`.
2. **Strict Anti-Hallucination**: Agents ground findings strictly in verified web excerpts. When evidence is absent (e.g. no market size figures), agents return honest empty lists rather than fabricating estimates.
3. **Autonomous Follow-Up**: Agents possess autonomous tool-calling capabilities (`request_additional_search`) to query further evidence if initial batches are insufficient.
