# Team Forge — CrewAI Orchestration Engine

This directory contains the multi-agent orchestration layer that coordinates autonomous tool calling, sequential pipeline stages, and execution traces.

---

## Module Overview

| File | Purpose |
|---|---|
| `orchestrator.py` | Main pipeline coordinator (`ValidationCrewOrchestrator`). Manages the full 9-stage workflow from raw pitch submission to the complete `ValidationResponse` JSON artifact. |
| `agents.py` | `ValidationAgentFactory` creating the autonomous CrewAI `MarketResearchAgent` configured with tools, memory, and LLM backends. |
| `tasks.py` | `ValidationTaskFactory` defining the structured research task executed by the autonomous research agent. |
| `tools.py` | Custom tool suite (`MarketResearchToolKit`) exposing 4 discrete search tools (`search_competitors`, `search_industry_news`, `search_customer_demand`, `search_market_size`) with repetition protection and a hard query budget cap (3–5 queries). |

---

## Execution Flow
1. **Extraction**: `IdeaExtractionAgent` parses input.
2. **Autonomous Research**: CrewAI kicks off `MarketResearchAgent` which selectively queries search tools based on idea type (e.g. skipping consumer reviews for pure B2B industrial ideas).
3. **Data Cleansing**: Deterministic `DataRetrievalAgent` processes collected results without any LLM hallucination risk.
4. **Downstream Synthesis**: Sequentially invokes `MarketOpportunityAgent`, `CompetitorAnalysisAgent`, `WhiteSpaceEngine`, `SWOTAgent`, `MVPAgent`, and `GTMAgent`.
