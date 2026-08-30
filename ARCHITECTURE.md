# System Architecture — Startup Idea Validator

## 1. System Overview

The **Startup Idea Validator** is an automated multi-agent research engine that evaluates early-stage startup ideas against real-time market data. The system transforms unstructured startup descriptions into structured domain parameters, executes parallel web intelligence retrieval across four strategic market vectors, and presents verified source evidence with full traceability.

Milestone 1 delivers:
- **Frontend**: A fast, responsive editorial Single Page Application built with **React 18 + Vite** (Vanilla CSS).
- **Backend API**: A high-performance REST service built with **FastAPI (Python 3.11)**.
- **Idea Extraction Agent**: An upstream Groq LLM agent that extracts product identity, domain vertical, audience profile, core problem statement, and contextual keywords.
- **Web Search Agent**: An AI-native search coordinator querying the **Tavily Search API** in parallel across four market categories.
- **Data Retrieval Agent**: A sanitization and verification engine that filters blocked domains, verifies English language, deduplicates canonical URLs, and ranks sources by native relevance scores.

---

## 2. In-Process Multi-Agent Architecture

The backend operates as an **in-process monolithic pipeline** inside FastAPI. `main.py` imports the three agent classes and calls their methods sequentially within the `POST /api/validate` request handler (no gRPC, protobuf, or external RPC layers):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Client Layer                                    │
│                    React 18 + Vite (Vanilla CSS SPA)                        │
│   - Natural language submission form with character count & input defense   │
│   - AI Domain Extraction dossier card with case-file stamped badge          │
│   - Total Sources Surfaced stats panel with animated count-up               │
│   - 4-category responsive evidence grid with sentence-boundary truncation   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ HTTP POST /api/validate (JSON)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Application Layer                             │
│                         (backend/main.py)                                   │
│                                                                             │
│   1. English Coherence & Gibberish Filter (`is_valid_idea` via wordfreq)    │
│   2. In-process agent execution & error handling                            │
│   3. Pydantic request/response serialization                                │
└───────────────────┬─────────────────────────────────────▲───────────────────┘
                    │                                     │
                    │ In-Process Call 1                   │ In-Process Call 3
                    ▼                                     │
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     1. IdeaExtractionAgent           │  │      3. DataRetrievalAgent        │
│   (Groq LLM: qwen/qwen3.8-27b)       │  │   - Blocked domain filter         │
│   - Ingests raw idea + optional meta │  │   - langdetect English check      │
│   - Model failover stack             │  │   - Canonical URL deduplication   │
│   - Outputs structured JSON          │  │   - Computes category metrics     │
└───────────────────┬──────────────────┘  └───────────────────▲───────────────┘
                    │                                         │
                    │ Structured Metadata                     │ Raw Batches
                    ▼                                         │
┌─────────────────────────────────────────────────────────────┴───────────────┐
│                          2. WebSearchAgent                                  │
│                        (Tavily Search API)                                  │
│                                                                             │
│   - Synthesizes 4 distinct category queries from domain keywords            │
│   - Concurrent execution via ThreadPoolExecutor(max_workers=4):             │
│       * Vector 1: Competitors (search_depth="advanced")                     │
│       * Vector 2: Industry News (search_depth="advanced", topic="news")     │
│       * Vector 3: Customer Demand (search_depth="advanced")                 │
│       * Vector 4: Market Size & Trends (search_depth="advanced")            │
│   - Preserves Tavily native semantic relevance score directly (0.0 to 1.0)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Agent Specifications & Pipeline Flow

### Step 1: Input Validation & Gibberish Defense (`main.py`)
- When a request hits `POST /api/validate`, `web_search_agent.is_valid_idea()` checks that the text contains at least 5 characters and has a recognizable English dictionary word density ($\ge 45\%$ via `wordfreq`).
- Nonsense strings fast-fail with an explanatory message, protecting downstream API quotas.

### Step 2: Structured Domain Extraction (`IdeaExtractionAgent`)
- **File**: `backend/agents/idea_extraction_agent.py`
- **Method**: `extract(idea, product_name=None, industry=None, target_audience=None) -> dict`
- **LLM Engine**: Groq Cloud Inference with automatic cascading failover:
  1. **Primary**: `qwen/qwen3.8-27b` (High accuracy, strict JSON output adherence)
  2. **Backup 1**: `allam-2-7b` (Fast, high-throughput secondary model)
  3. **Backup 2**: `groq/compound-mini` (Compact tertiary backup)
  4. **Deterministic Fallback**: Regex opener/stopword stripping parser if all network calls fail
- **Exponential Backoff**: Handles HTTP 429 rate limits with $2^{\text{attempt}}$ backoff delay.
- **Output Schema**:
  ```json
  {
    "product_name": "GuardrailCI",
    "industry": "DevSecOps",
    "target_audience": "Software development teams and DevOps engineers",
    "core_problem": "Software development teams struggle to identify and remediate security vulnerabilities early in the CI/CD pipeline.",
    "keywords": ["continuous integration", "vulnerability scanning", "DevSecOps", "security automation"]
  }
  ```

### Step 3: Multi-Category Parallel Search (`WebSearchAgent`)
- **File**: `backend/agents/web_search_agent.py`
- **Method**: `search(structured_idea: dict, max_results_per_category: int = 6) -> list[dict]`
- **Query Assembly**: Constructs 4 tailored search queries using extracted domain keywords and entities:
  - **Competitors**: `{keywords} [{product_name}] competitors alternatives`
  - **Industry News**: `{keywords} industry trends startup news` (`topic="news"`)
  - **Customer Demand**: `{keywords} customer problems user demand reviews`
  - **Market Size & Trends**: `{keywords} [{industry}] market size growth forecast`
- **Parallel Dispatch**: Fires all 4 category searches concurrently using `ThreadPoolExecutor(max_workers=4)` with `search_depth="advanced"`.
- **Native Scoring**: Directly preserves Tavily's calibrated semantic relevance score (`float` between `0.0` and `1.0`) on each result record with no custom filtering layer on top.

### Step 4: Verification & Normalization (`DataRetrievalAgent`)
- **File**: `backend/agents/data_retrieval_agent.py`
- **Method**: `structure(raw_batches: list[dict]) -> list[dict]` and `summarize_counts(structured: list[dict]) -> dict`
- **Operations**:
  1. **Blocklist Filtering**: Strips generic dictionaries, encyclopedias, and non-commercial portals (`BLOCKED_DOMAINS` including `wiktionary.org`, `wikipedia.org`, `dictionary.com`, `yelp.com`, `quora.com`, `medicinesfaq.com`).
  2. **Language Verification**: Evaluates combined title and snippet text with `langdetect` (seeded with `DetectorFactory.seed = 0`) to discard non-English results.
  3. **Canonical Deduplication**: Tracks seen URLs across all 4 category streams to ensure zero duplicate sources.
  4. **Score-Ranked Sorting**: Sorts sources strictly by relevance score descending.

---

## 4. Data Contracts & Pydantic Schemas

Directly aligned with [`backend/main.py`](backend/main.py):

### Request Schema: `IdeaSubmission`
```python
class IdeaSubmission(BaseModel):
    idea: str = Field(..., min_length=3, description="Startup description to validate.")
    product_name: str | None = Field(default=None, description="Optional product or startup name.")
    industry: str | None = Field(default=None, description="Optional industry or category.")
    target_audience: str | None = Field(default=None, description="Optional target audience.")
```

### Source Record Schema: `SourceRecord`
```python
class SourceRecord(BaseModel):
    title: str
    url: str
    snippet: str
    query: str
    category: str
    score: float
```

### Full API Response Schema: `ValidationResponse`
```python
class ValidationResponse(BaseModel):
    idea: str
    extracted_data: dict | None = Field(default=None, description="Structured extraction output from LLM.")
    sources: list[SourceRecord]
    summary: dict
```

#### Example Response JSON:
```json
{
  "idea": "A CI/CD tool that automatically checks for security vulnerabilities",
  "extracted_data": {
    "product_name": "GuardrailCI",
    "industry": "DevSecOps",
    "target_audience": "Software development teams and DevOps engineers",
    "core_problem": "Software development teams struggle to identify and remediate security vulnerabilities early in the CI/CD pipeline.",
    "keywords": [
      "continuous integration",
      "vulnerability scanning",
      "DevSecOps",
      "security automation"
    ]
  },
  "sources": [
    {
      "title": "DevSecOps Market Size, Share, Growth, Analysis, Report, 2034",
      "url": "https://straitsresearch.com/report/devsecops-market",
      "snippet": "The global DevSecOps market size was valued at USD 6.2 billion in 2024 and is projected to reach USD 37.32 billion by 2034...",
      "query": "continuous integration vulnerability scanning DevSecOps security automation DevSecOps market size growth forecast",
      "category": "Market Size & Trends",
      "score": 0.92
    }
  ],
  "summary": {
    "total_sources": 24,
    "sources_per_category": {
      "Competitors": 6,
      "Industry News": 6,
      "Customer Demand": 6,
      "Market Size & Trends": 6
    },
    "sources_by_category": {
      "Competitors": [ ... ],
      "Industry News": [ ... ],
      "Customer Demand": [ ... ],
      "Market Size & Trends": [ ... ]
    }
  }
}
```

---

## 5. Architectural Rationale: Why Tavily Over Web Scraping

Per the project requirements and milestone specification, the search architecture migrated from legacy HTML scraping (DuckDuckGo / Google News RSS) to the **Tavily Search API** for five key reasons:

1. **Elimination of Anti-Bot & Rate Limits**: Scraping search engine HTML is brittle, subject to unpredictable DOM layout changes, and frequently blocked by IP bans or CAPTCHAs on cloud hosts (Render/AWS). Tavily provides an SLA-backed developer API.
2. **AI-Native Content Extraction**: Traditional search scraping returns truncated snippet fragments (often under 80 characters) cluttered with navigation menus and cookie notices. Tavily returns clean, full-sentence editorial passages.
3. **Calibrated Semantic Relevance Scoring**: Scraping engines provide no relevance score, requiring heavy local embeddings or secondary LLM judge passes. Tavily outputs a calibrated relevance float (`0.0` to `1.0`) out-of-the-box.
4. **First-Class Topic-Based News Routing**: Tavily supports `topic="news"` natively, enabling fresh real-time industry news retrieval without fragile RSS feed parsing.
5. **Parallel High-Throughput Retrieval**: Concurrent multi-threaded execution across all 4 categories (`search_depth="advanced"`) retrieves 20–24 comprehensive source records in ~5–7 seconds end-to-end.

---

## 6. Technology Stack

- **Backend**: Python 3.11, FastAPI (`0.115.0`), Uvicorn (`0.30.6`), Pydantic (`2.9.2`), Groq SDK (`>=0.9.0`), Tavily Python (`>=0.3.0`), langdetect (`>=1.0.9`), wordfreq (`>=3.1.0`), lxml (`>=5.0.0`), python-dotenv (`1.0.1`).
- **Frontend**: React 18, Vite (`5.4.x`), Vanilla CSS design system.
- **Typography**: Instrument Serif, Inter, Space Mono.
- **Deployment**: Render (Backend Web Service), Vercel (Frontend SPA).
