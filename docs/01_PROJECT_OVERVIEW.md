# 01. Project Overview

## 1. Executive Summary
**Team Forge — Startup Idea Validator** is an autonomous multi-agent intelligence platform that automates the discovery, stress-testing, and market validation of early-stage startup concepts. 

Traditional startup ideation relies on manual Google searches, fragmented market research reports, intuition, and subjective founder bias. This platform converts an unstructured natural-language startup pitch into structured market intelligence in under 90–120 seconds. It autonomously queries the live web across 4 dimensions, cleanses and deduplicates evidence, sizes addressable markets, segments customers, categorizes competitors, and synthesizes an **evidence-backed White-Space Map** with traceable citations.

---

## 2. Key Value Propositions
1. **Autonomous Web Research**: Rather than issuing static queries, an autonomous CrewAI agent evaluates the specific domain and selectively executes live searches across Competitors, Industry News, Customer Demand, and Market Sizing under a strict budget cap (3–5 tool calls).
2. **Deterministic Data Integrity**: A strictly non-LLM `DataRetrievalAgent` enforces blocked-domain filtering (rejecting Wikipedia, dictionaries, non-commercial sites), seeded language coherence verification (`langdetect`), canonical URL deduplication, and semantic relevance sorting.
3. **Multi-Model LLM Resilience**: Leverages Groq Cloud's ultra-low-latency LPU infrastructure with an automated cascading failover stack (`qwen/qwen3.8-27b` $\rightarrow$ `allam-2-7b` $\rightarrow$ `groq/compound-mini` $\rightarrow$ deterministic regex fallback) preventing downtime from HTTP 429 rate limits.
4. **Honest Market Sizing (Zero Hallucination)**: When market size coverage is absent in niche or early domains, the platform honestly returns an empty array, suppresses confident scorecards, and nulls confidence rather than generating speculative hallucinated numbers.
5. **Core Novelty — White-Space Engine**: Computes deterministic opportunity intersections:
   $$\text{White-Space Opportunity} = \text{Customer Pain} \cap \text{Competitor Void} \cap \text{Startup Capability}$$
   Outputs 2–4 high-conviction opportunity gaps supported by traceable web citations.

---

## 3. Technology Stack Summary

### Frontend Application Layer
- **Framework**: React 18 with Vite
- **Styling**: Pure Vanilla CSS design tokens (Warm editorial aesthetic: Instrument Serif, Space Mono, Inter)
- **Deployment Target**: Vercel Cloud (SPA Edge Hosting)

### Backend API & Orchestration Layer
- **Framework**: FastAPI (Python 3.11) with Uvicorn ASGI
- **Multi-Agent Framework**: CrewAI (Agent, Task, ToolKit orchestration)
- **Data Validation**: Pydantic v2
- **Input Defense**: `wordfreq` English dictionary token density verification ($\ge 0.45$)
- **Deployment Target**: Render Cloud (Docker containerized)

### Cloud Intelligence & Search Services
- **Inference Cloud**: Groq Cloud LPU (Ultra-low latency LLM inference)
- **Web Search Engine**: Tavily AI Search API (Semantic relevance scoring $0.0 - 1.0$)

---

## 4. Intended Audience & Stakeholders
- **Startup Founders & Product Managers**: Conduct pre-seed and seed idea validation, identify customer pain points, and discover defensible market positioning before writing code.
- **Venture Capital Analysts & Accelerators**: Rapidly screen incoming pitches, benchmark competing startups, and verify market sizing claims with live citations.
- **Academic Evaluators & Mentors**: Demonstrates real-world multi-agent coordination, tool calling, API resiliency, and defensible architectural design.
