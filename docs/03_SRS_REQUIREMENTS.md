# 03. Software Requirements Specification (SRS)

## 1. Introduction & Scope
This Software Requirements Specification (SRS) documents the functional and non-functional requirements for the **Startup Idea Validator (Milestone 2)**. The system provides an end-to-end analytical pipeline connecting a client SPA frontend to an asynchronous multi-agent backend service.

---

## 2. User Personas & Roles

```
┌──────────────────┐     ┌────────────────────────────────────────────────────────┐
│      User        │ ──► │ • Submits arbitrary natural-language startup pitch     │
│ (Founder / PM /  │     │ • Reviews AI Dossier, White-Space Map, Market Sizing   │
│    Investor)     │     │ • Inspects Competitor Matrix and Traceable Sources     │
└──────────────────┘     └────────────────────────────────────────────────────────┘
```

---

## 3. Functional Requirements (FR)

### FR-1: Pitch Ingestion & Coherence Defense
- **FR-1.1**: The system shall accept a mandatory `idea` field of arbitrary length (minimum 5 characters, no upper ceiling).
- **FR-1.2**: The system shall accept optional user-specified overrides: `product_name`, `industry`, `target_audience`.
- **FR-1.3**: The system shall analyze the token distribution of the `idea` string using `wordfreq`. If the recognized English dictionary word ratio is below $0.45$, the system shall reject the submission with an explanatory user guidance message (`"This doesn't look like a real idea description — try describing it in plain English."`) within 50ms without initiating agent LLM or search calls.

### FR-2: Structured Domain Extraction
- **FR-2.1**: The `IdeaExtractionAgent` shall extract normalized domain entities: `product_name`, `industry`, `target_audience`, `core_problem`, and an array of domain `keywords`.
- **FR-2.2**: The agent shall execute against Groq Cloud LLM (`qwen/qwen3.8-27b`) and automatically failover to `allam-2-7b`, `groq/compound-mini`, and deterministic fallback upon encountering HTTP 429 rate limits or network exceptions.

### FR-3: Autonomous Market Research & Tool-Calling
- **FR-3.1**: The CrewAI `MarketResearchAgent` shall autonomously evaluate domain characteristics and formulate high-signal web queries.
- **FR-3.2**: The agent shall be constrained to a strict budget of **3 to 5 total search queries** per execution.
- **FR-3.3**: The agent shall be prohibited from executing near-identical or duplicate queries via a query repetition filter.
- **FR-3.4**: The agent shall access four distinct search tools wrapping the Tavily Search API:
  - `search_competitors`
  - `search_industry_news`
  - `search_customer_demand`
  - `search_market_size`

### FR-4: Deterministic Data Retrieval & Sanitization
- **FR-4.1**: The `DataRetrievalAgent` shall filter out non-commercial domains (e.g. `wikipedia.org`, `wiktionary.org`, `merriam-webster.com`, `dictionary.com`, `quora.com`, `reddit.com` unless commercial reviews).
- **FR-4.2**: The system shall enforce English language verification using seeded `langdetect`.
- **FR-4.3**: The system shall perform canonical URL deduplication across all search categories.
- **FR-4.4**: Sources shall be sorted in descending order of their native semantic relevance score ($0.0 - 1.0$).

### FR-5: Market Opportunity Sizing & Personas
- **FR-5.1**: The `MarketOpportunityAgent` shall estimate TAM/SAM figures, CAGR percentages, and forecast years with source citations.
- **FR-5.2**: The agent shall generate granular customer personas explicitly separating **Daily End Users** from **Economic Decision Makers**.
- **FR-5.3**: If zero verifiable market size sources are found, the agent shall clamp confidence to `null`, suppress the attractiveness scorecard, and return an empty `market_size` array.

### FR-6: Competitor Analysis & Dimension Matrix
- **FR-6.1**: The `CompetitorAnalysisAgent` shall identify direct rivals and indirect substitutes.
- **FR-6.2**: The agent shall evaluate business models, strengths, weaknesses, and documented customer complaints.
- **FR-6.3**: The agent shall construct a side-by-side comparison matrix evaluating the startup against competitors across critical feature dimensions.

### FR-7: Evidence-Backed White-Space Engine (Core Novelty)
- **FR-7.1**: The `WhiteSpaceEngine` shall compute deterministic opportunity intersections between Customer Pain, Competitor Omissions, and Startup Capabilities.
- **FR-7.2**: The engine shall synthesize 2–4 high-conviction opportunity gaps with Evidence Strength (`High`/`Medium`/`Low`), Confidence ratings, differentiation hypotheses, and traceable citations.

### FR-8: Client Presentation Layer
- **FR-8.1**: The React frontend shall render the Stamped AI Dossier, Evidence-Backed White-Space Map, Market Sizing & CAGR Scorecard, Customer Segmentation Persona Cards, Competitor Comparison Matrix, and 4-Category Evidence Grid.
- **FR-8.2**: Snippets shall be stripped of markdown artifacts and cleanly truncated at sentence boundaries with inline "Read more" expansion toggles.

---

## 4. Non-Functional Requirements (NFR)

| ID | Category | Requirement Description | Target Metric |
| :--- | :--- | :--- | :--- |
| **NFR-1** | **Performance** | API response turnaround under normal network conditions | $< 150$ seconds |
| **NFR-2** | **Availability** | Graceful failover on third-party LLM rate limit (HTTP 429) | 100% failover survival |
| **NFR-3** | **Cost & Quota** | Web search API call bounds per submission | $3 - 5$ tool executions |
| **NFR-4** | **Data Integrity** | Zero duplicate URLs in returned source records | 0 duplicate canonical URLs |
| **NFR-5** | **Portability** | Cross-browser compatible single page application | Chrome, Firefox, Safari, Edge |
| **NFR-6** | **Security** | Secure environment variable handling for API keys | Zero client-side API key leakage |
