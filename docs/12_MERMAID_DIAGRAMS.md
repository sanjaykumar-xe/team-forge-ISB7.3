# 12. Complete Mermaid Diagrams Reference (All 13 Diagrams)

This document contains all **13 professional, editable Mermaid diagrams** modeling the Startup Idea Validator system. Evaluators and students can copy and edit these diagram blocks directly in GitHub, Mermaid Live Editor, or presentation tools.

---

## 📑 Diagram Index
1. [System Architecture Diagram](#1-system-architecture-diagram)
2. [Use Case Diagram](#2-use-case-diagram)
3. [Data Flow Diagram (DFD) — Level 0](#3-dfd-level-0-context-level)
4. [Data Flow Diagram (DFD) — Level 1](#4-dfd-level-1-detailed-pipeline)
5. [Activity Diagram](#5-activity-diagram-process-flow)
6. [Sequence Diagram](#6-sequence-diagram-end-to-end-runtime)
7. [Entity-Relationship (ER) Diagram](#7-entity-relationship-er-diagram)
8. [AI Evaluation Pipeline Diagram](#8-ai-evaluation-pipeline-diagram)
9. [AI / Multi-Agent Architecture Diagram](#9-ai--multi-agent-architecture-diagram)
10. [API Architecture Diagram](#10-api-architecture-diagram)
11. [Deployment Architecture Diagram](#11-deployment-architecture-diagram)
12. [Component Diagram](#12-component-diagram)
13. [Class Diagram](#13-class-diagram-python-backend)

---

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph ClientLayer["Client Presentation Layer (Vercel Cloud)"]
        UI["React 18 + Vite SPA<br/>• Idea Submission Form<br/>• Stamped AI Dossier<br/>• Evidence-Backed White-Space Map<br/>• Market Sizing & Scorecard<br/>• Customer Personas<br/>• Competitor Matrix<br/>• 4-Category Evidence Grid"]
    end

    subgraph APILayer["Backend API & Gateway Layer (Render Cloud)"]
        Router["FastAPI Application (/api/validate)"]
        Defense["Input Validator & Gibberish Filter<br/>(wordfreq ratio >= 0.45)"]
        Orchestrator["ValidationCrewOrchestrator<br/>(Sequential Multi-Agent Controller)"]
    end

    subgraph AgentPipeline["Autonomous Multi-Agent Pipeline (In-Process)"]
        A1["Agent 1: IdeaExtractionAgent<br/>(Groq LLM Domain Parser)"]
        A2["Agent 2: MarketResearchAgent (CrewAI)<br/>(Autonomous Tool Planning & Budget Cap: 3-5)"]
        
        subgraph Tools["MarketResearchToolKit (4 Discrete Vectors)"]
            T1["search_competitors"]
            T2["search_industry_news"]
            T3["search_customer_demand"]
            T4["search_market_size"]
        end

        A3["Agent 3: DataRetrievalAgent<br/>(Deterministic Non-LLM Filter & Dedup)"]
        A4["Agent 4: MarketOpportunityAgent<br/>(TAM/SAM, CAGR, Personas)"]
        A5["Agent 5: CompetitorAnalysisAgent<br/>(Rivals, Positioning, Matrix)"]
        A6["Agent 6: WhiteSpaceEngine (Core Novelty)<br/>(Customer Pain ∩ Competitor Void ∩ Startup)"]
    end

    subgraph ExternalClouds["External Cloud Services"]
        Groq["Groq Cloud LLM Inference<br/>(Qwen-27B / Allam-7B Failover)"]
        Tavily["Tavily Search API<br/>(Clean Index & Semantic Rank)"]
    end

    %% Connections
    UI -- "HTTPS POST /api/validate" --> Router
    Router --> Defense
    Defense -- "Valid Text" --> Orchestrator
    Defense -- "Nonsense (<0.45)" --> UI
    Orchestrator --> A1
    A1 <--> Groq
    A1 --> A2
    A2 --> Tools
    Tools <--> Tavily
    Tools --> A3
    A3 --> A4 & A5
    A4 & A5 --> A6
    A6 --> Orchestrator
    Orchestrator -- "ValidationResponse (JSON)" --> UI
```

---

## 2. Use Case Diagram

```mermaid
flowchart LR
    User((Founder / Product Manager / Investor))
    Admin((System Administrator))

    subgraph IdeaValidatorSystem["Startup Idea Validator Platform"]
        UC1["Submit Startup Pitch (Arbitrary Length)"]
        UC2["Specify Brand/Audience Overrides (Optional)"]
        UC3["View Extracted AI Dossier"]
        UC4["Inspect Evidence-Backed White-Space Map"]
        UC5["Analyze TAM/SAM & CAGR Growth"]
        UC6["Review Customer Personas (Users vs Buyers)"]
        UC7["Benchmark Competitor Comparison Matrix"]
        UC8["Inspect Verified Research Sources & Citations"]
        UC9["Trigger Fast-Fail on Incoherent Input"]
        UC10["Configure LLM Failover & API Keys"]
        UC11["Monitor System Health (/api/health)"]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8

    IdeaValidatorSystem --> UC9
    Admin --> UC10
    Admin --> UC11
```

---

## 3. DFD Level 0 (Context Level)

```mermaid
flowchart TD
    User["Founder / Client Browser"]
    System(("Startup Idea Validator<br/>System (Process 0.0)"))
    GroqService["Groq Cloud LLM Service"]
    TavilyService["Tavily Search API"]

    User -- "Idea Pitch & Optional Overrides (HTTP POST)" --> System
    System -- "Prompts & Context JSON" --> GroqService
    GroqService -- "Extracted Semantics & Inferred Personas" --> System
    System -- "Targeted Market Queries" --> TavilyService
    TavilyService -- "Raw Search Result Batches & Scores" --> System
    System -- "ValidationResponse (Dossier, White-Space, Market, Competitors, Sources)" --> User
```

---

## 4. DFD Level 1 (Detailed Pipeline)

```mermaid
flowchart TD
    User["User Pitch"]
    
    P1["1.0 Input Validation & Coherence Defense"]
    P2["2.0 Domain Parameter Extraction"]
    P3["3.0 Autonomous Multi-Angle Search"]
    P4["4.0 Data Cleansing & Deduplication"]
    P5["5.0 Market & Competitor Modeling"]
    P6["6.0 White-Space Triangulation"]
    
    DS1[("In-Memory State Store")]
    
    ExtGroq["Groq Cloud LPU"]
    ExtTavily["Tavily Web Search"]
    
    User --> P1
    P1 -- "Gibberish (< 0.45)" --> Reject["200 OK Fast-Fail Notice"]
    P1 -- "Valid Pitch" --> P2
    
    P2 <--> ExtGroq
    P2 -- "Extracted Domain Context" --> DS1
    
    DS1 --> P3
    P3 <--> ExtTavily
    P3 -- "Raw Multi-Category Results" --> P4
    
    P4 -- "Deduplicated English Sources" --> DS1
    
    DS1 --> P5
    P5 <--> ExtGroq
    P5 -- "Market Sizing & Competitor Records" --> DS1
    
    DS1 --> P6
    P6 <--> ExtGroq
    P6 -- "White-Space Gaps & Citations" --> Response["ValidationResponse JSON"]
    Response --> Display["React Editorial UI"]
```

---

## 5. Activity Diagram (Process Flow)

```mermaid
flowchart TD
    Start([User Submits Pitch]) --> CheckInput{Input >= 5 Chars?}
    CheckInput -- No --> Err422[Return HTTP 422 Error]
    CheckInput -- Yes --> CheckGibberish{wordfreq Ratio >= 0.45?}
    
    CheckGibberish -- No (<0.45) --> FastFail[Fast-Fail in <0.01s with Friendly Guidance]
    FastFail --> RenderEmpty[Render Empty Case State]
    
    CheckGibberish -- Yes --> CallIdeaExtraction[Agent 1: Extract Domain Parameters via Groq]
    
    CallIdeaExtraction --> LLMFailover{Groq Primary Succeeded?}
    LLMFailover -- 429 Rate Limit --> BackupModel[Failover to allam-2-7b / compound-mini]
    LLMFailover -- Success --> PlanSearch[Agent 2: CrewAI Autonomous Search Planning]
    BackupModel --> PlanSearch
    
    PlanSearch --> ExecuteTools[Execute 3-5 Search Queries via Tavily]
    ExecuteTools --> RepetitionCheck{Near-Duplicate Query?}
    RepetitionCheck -- Yes --> SkipRepetition[Repetition Notice: Skip Repeat Call]
    RepetitionCheck -- No --> FetchTavily[Fetch Live Search Results]
    SkipRepetition --> CheckBudget{Budget (3-5) Reached?}
    FetchTavily --> CheckBudget
    
    CheckBudget -- No --> PlanSearch
    CheckBudget -- Yes --> Agent3Sanitize[Agent 3: Blocklist Filter, langdetect, Canonical Dedup]
    
    Agent3Sanitize --> ParallelAnalysis[Run Downstream Analysis]
    
    subgraph DownstreamAnalysis["Downstream Reasoning"]
        Agent4Market[Agent 4: Market Opportunity & Personas]
        Agent5Comp[Agent 5: Competitor Mapping & Matrix]
    end
    
    ParallelAnalysis --> DownstreamAnalysis
    DownstreamAnalysis --> CheckMarketSize{Market Sources > 0?}
    CheckMarketSize -- No --> HonestNull[Clamp Confidence = Null, Suppress Scorecard]
    CheckMarketSize -- Yes --> PopulateMarket[Populate TAM/SAM & Attractiveness]
    
    HonestNull --> Agent6WhiteSpace[Agent 6: WhiteSpaceEngine Triangulation]
    PopulateMarket --> Agent6WhiteSpace
    
    Agent6WhiteSpace --> AssembleResponse[Assemble ValidationResponse Contract]
    AssembleResponse --> RenderDashboard([Render React 18 Dynamic Editorial View])
```

---

## 6. Sequence Diagram (End-to-End Runtime)

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant App as React Frontend (App.jsx)
    participant API as FastAPI Backend (main.py)
    participant Orch as ValidationCrewOrchestrator
    participant IEA as IdeaExtractionAgent
    participant Groq as Groq Cloud LPU
    participant Crew as MarketResearchAgent
    participant Tavily as Tavily Search API
    participant DRA as DataRetrievalAgent
    participant MOA as MarketOpportunityAgent
    participant CAA as CompetitorAnalysisAgent
    participant WSE as WhiteSpaceEngine

    User->>App: Enters startup pitch & clicks Validate
    App->>API: POST /api/validate { idea, product_name? }
    API->>API: Coherence Check (wordfreq >= 0.45)
    
    alt Incoherent Gibberish
        API-->>App: 200 OK { message: "Try describing in plain English." }
        App-->>User: Displays helpful guidance note (< 0.01s)
    else Valid English Pitch
        API->>Orch: orchestrator.validate_idea()
        Orch->>IEA: extract_idea(idea)
        IEA->>Groq: ChatCompletion (qwen/qwen3.8-27b)
        Groq-->>IEA: Structured JSON { product, industry, keywords }
        IEA-->>Orch: Extracted Domain Context
        
        Orch->>Crew: crew.kickoff(domain_context)
        loop Autonomous Querying (3-5 queries)
            Crew->>Tavily: Search Category Tools (Competitors, News, Demand, Sizing)
            Tavily-->>Crew: Category Results + Relevance Scores
        end
        Crew-->>Orch: Research Dossier & Search Batches
        
        Orch->>DRA: sanitize_and_deduplicate(raw_batches)
        DRA->>DRA: Apply Blocklist, langdetect, Canonical Dedup
        DRA-->>Orch: Clean Unique Source Records
        
        par Downstream Intelligence
            Orch->>MOA: analyze_market(sources, extracted_data)
            MOA->>Groq: Synthesize TAM/SAM & Personas
            Groq-->>MOA: Market Sizing JSON
            MOA-->>Orch: MarketAnalysisResult
        and
            Orch->>CAA: analyze_competitors(sources, extracted_data)
            CAA->>Groq: Classify Rivals & Build Matrix
            Groq-->>CAA: Competitor JSON
            CAA-->>Orch: CompetitorAnalysisResult
        end
        
        Orch->>WSE: triangulate(market_analysis, competitor_analysis)
        WSE->>Groq: Compute Intersections (Pain ∩ Void ∩ Wedge)
        Groq-->>WSE: 2-4 Opportunity Gaps with Citations
        WSE-->>Orch: WhiteSpaceAnalysisResult
        
        Orch-->>API: Complete ValidationResponse JSON
        API-->>App: HTTP 200 OK (ValidationResponse)
        App-->>User: Renders AI Dossier, White-Space Map, Scorecards & Sources
    end
```

---

## 7. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    IdeaSubmission ||--|| ValidationResponse : generates
    ValidationResponse ||--|| ExtractedData : contains
    ValidationResponse ||--|{ SourceRecord : surfaces
    ValidationResponse ||--|| MarketAnalysisResult : includes
    ValidationResponse ||--|| CompetitorAnalysisResult : includes
    ValidationResponse ||--|| WhiteSpaceAnalysisResult : synthesizes

    MarketAnalysisResult ||--|{ MarketSizeEstimate : reports
    MarketAnalysisResult ||--|{ CustomerSegment : defines
    MarketAnalysisResult ||--|| MarketAttractiveness : evaluates

    CompetitorAnalysisResult ||--|{ CompetitorRecord : discovers
    CompetitorAnalysisResult ||--|{ ComparisonDimension : benchmarks

    WhiteSpaceAnalysisResult ||--|{ WhiteSpaceOpportunity : triangulates

    IdeaSubmission {
        string idea PK
        string product_name
        string industry
        string target_audience
    }

    ExtractedData {
        string product_name
        string industry
        string target_audience
        string core_problem
        string_list keywords
    }

    SourceRecord {
        string url PK
        string title
        string snippet
        string query
        string category
        float score
    }

    MarketSizeEstimate {
        string figure
        string market_type
        string cagr
        string forecast_year
        string source_url FK
    }

    CustomerSegment {
        string segment_name
        string who_they_are
        string end_users
        string decision_makers
        string_list pain_points
    }

    CompetitorRecord {
        string name PK
        string classification
        string core_offering
        string pricing
        string_list strengths
        string_list customer_complaints
    }

    ComparisonDimension {
        string feature_or_dimension PK
        string startup_approach
        dict competitor_approaches
    }

    WhiteSpaceOpportunity {
        string opportunity_name PK
        string segment
        string pain_point
        string competitor_coverage
        string differentiation_hypothesis
        string evidence_strength
        float confidence
        string_list evidence
    }
```

---

## 8. AI Evaluation Pipeline Diagram

```mermaid
flowchart TD
    RawIdea["Raw Pitch Text"] --> InputGate{"Coherence Check<br/>(wordfreq >= 0.45)"}
    
    InputGate -- Incoherent --> RejectNode["Deterministic Fast-Fail<br/>(0.00s Latency)"]
    InputGate -- Valid --> Extractor["IdeaExtractionAgent<br/>(Groq LPU Cascading Failover)"]
    
    Extractor --> SearchAgent["MarketResearchAgent (CrewAI)<br/>(Autonomous Planning & Tool Selection)"]
    
    SearchAgent --> ToolCap{"Tool Budget Cap<br/>(3 to 5 Queries)"}
    ToolCap --> RepFilter{"Repetition Filter<br/>(Deduplicate Intent)"}
    RepFilter --> TavilyEngine["Tavily Search Engine<br/>(Advanced Relevance Index)"]
    
    TavilyEngine --> Sanitizer["DataRetrievalAgent<br/>• Non-Commercial Blocklist Filter<br/>• Seeded langdetect Language Gate<br/>• Canonical URL Normalization"]
    
    Sanitizer --> SizingEngine["MarketOpportunityAgent<br/>• Honest Null Sizing Clamping<br/>• Persona Segregation (Users vs Buyers)"]
    Sanitizer --> CompEngine["CompetitorAnalysisAgent<br/>• Direct vs Substitute Rivals<br/>• Feature Benchmark Matrix"]
    
    SizingEngine & CompEngine --> WhiteSpaceCore["WhiteSpaceEngine (Core Novelty)<br/>Triangulate: Pain ∩ Void ∩ Capability"]
    
    WhiteSpaceCore --> OutputModel["ValidationResponse Model<br/>100% Traceable Citations"]
```

---

## 9. AI / Multi-Agent Architecture Diagram

```mermaid
graph TB
    subgraph AgentOrchestration["CrewAI Orchestration Context"]
        Orch["ValidationCrewOrchestrator"]
        Task1["Task 1: Domain Parameter Extraction"]
        Task2["Task 2: Autonomous Market Evidence Retrieval"]
        Task3["Task 3: Market Size & Persona Modeling"]
        Task4["Task 4: Competitive Mapping & Matrix"]
        Task5["Task 5: White-Space Triangulation"]
    end

    subgraph SpecializedAgents["Specialized Autonomous Agents"]
        A1["IdeaExtractionAgent"]
        A2["MarketResearchAgent (CrewAI)"]
        A3["DataRetrievalAgent (Deterministic)"]
        A4["MarketOpportunityAgent"]
        A5["CompetitorAnalysisAgent"]
        A6["WhiteSpaceEngine"]
    end

    subgraph FailoverStack["Groq LPU Multi-Model Failover Stack"]
        M1["Primary: qwen/qwen3.8-27b"]
        M2["Backup 1: allam-2-7b"]
        M3["Backup 2: groq/compound-mini"]
        M4["Fallback: Regex Heuristic Parser"]
    end

    subgraph ToolKit["MarketResearchToolKit"]
        T1["search_competitors"]
        T2["search_industry_news"]
        T3["search_customer_demand"]
        T4["search_market_size"]
    end

    Orch --> Task1 --> A1
    A1 --> M1
    M1 -.->|HTTP 429| M2
    M2 -.->|HTTP 429| M3
    M3 -.->|Exception| M4

    Orch --> Task2 --> A2
    A2 --> ToolKit
    ToolKit --> A3

    Orch --> Task3 --> A4
    Orch --> Task4 --> A5
    A4 & A5 --> Task5 --> A6
```

---

## 10. API Architecture Diagram

```mermaid
flowchart TD
    Client["Client HTTP Request"] --> CORS["CORSMiddleware (FastAPI)"]
    CORS --> Security["Security & Header Validation"]
    Security --> Router["FastAPI Router: /api/validate"]
    
    Router --> PydanticIn["Pydantic Ingestion: IdeaSubmission Model"]
    
    PydanticIn --> ValidatorCheck{"wordfreq English Ratio Check"}
    ValidatorCheck -- Ratio < 0.45 --> FastResponse["200 OK: Friendly Guidance Response"]
    
    ValidatorCheck -- Ratio >= 0.45 --> Controller["ValidationCrewOrchestrator.validate_idea()"]
    
    Controller --> AgentPipe["In-Process Agent Pipeline"]
    AgentPipe --> PydanticOut["ValidationResponse Pydantic Serialization"]
    
    PydanticOut --> ClientResponse["JSON Response (HTTP 200 OK)"]
```

---

## 11. Deployment Architecture Diagram

```mermaid
graph TB
    subgraph UserTier["End-User Device"]
        Browser["Desktop / Mobile Web Browser"]
    end

    subgraph VercelEdge["Vercel Cloud Edge CDN"]
        EdgeDNS["Vercel Global Edge Network"]
        StaticSPA["Static Assets (HTML / JS / CSS)<br/>React 18 + Vite Production Bundle"]
    end

    subgraph RenderPlatform["Render Cloud Platform"]
        LoadBalancer["Render Load Balancer (HTTPS / SSL)"]
        BackendContainer["FastAPI Dockerized Python 3.11 Container<br/>Uvicorn ASGI Process Manager"]
    end

    subgraph CloudAPIs["External SaaS & Inference Clouds"]
        GroqAPI["Groq Cloud LPU API<br/>(api.groq.com)"]
        TavilyAPI["Tavily Search API<br/>(api.tavily.com)"]
    end

    Browser -- "1. Request Web App" --> EdgeDNS
    EdgeDNS --> StaticSPA
    StaticSPA -- "2. Deliver HTML/Bundle" --> Browser
    
    Browser -- "3. HTTPS POST /api/validate" --> LoadBalancer
    LoadBalancer --> BackendContainer
    
    BackendContainer -- "4. LLM Chat Completions" --> GroqAPI
    BackendContainer -- "5. Parallel Search Queries" --> TavilyAPI
    
    BackendContainer -- "6. Return ValidationResponse" --> Browser
```

---

## 12. Component Diagram

```mermaid
graph TD
    subgraph FrontendComponents["Frontend Components (frontend/src/components)"]
        App["App.jsx (Main Orchestrator)"]
        Header["Header.jsx (Hero Masthead)"]
        Metadata["ExtractedMetadata.jsx (Dossier Card)"]
        WhiteSpace["WhiteSpaceAnalysis.jsx (White-Space Map)"]
        Market["MarketOpportunity.jsx (TAM/SAM Sizing)"]
        Personas["CustomerSegments.jsx (Persona Cards)"]
        Competitors["CompetitorAnalysis.jsx (Matrix)"]
        Summary["ResultsSummary.jsx (Count-up Stats)"]
        Category["CategorySection.jsx (Evidence Grid)"]
        Source["SourceCard.jsx (Snippet Sanitizer)"]
    end

    subgraph BackendModules["Backend Modules (backend/)"]
        Main["main.py (FastAPI App)"]
        Orchestrator["crew/orchestrator.py"]
        CrewAgents["crew/agents.py"]
        CrewTasks["crew/tasks.py"]
        CrewTools["crew/tools.py"]
        
        AgentExtraction["agents/idea_extraction_agent.py"]
        AgentSearch["agents/web_search_agent.py"]
        AgentRetrieval["agents/data_retrieval_agent.py"]
        AgentMarket["agents/market_analysis_agent.py"]
        AgentComp["agents/competitor_analysis_agent.py"]
        
        ServiceLLM["services/llm_service.py"]
        ServiceWhiteSpace["services/white_space_engine.py"]
        ServiceText["services/text_utils.py"]
        
        Schemas["schemas/validation_schemas.py"]
    end

    App --> Header & Metadata & WhiteSpace & Market & Personas & Competitors & Summary & Category
    Category --> Source

    App -.->|HTTP POST| Main
    Main --> Schemas
    Main --> Orchestrator
    Orchestrator --> CrewAgents & CrewTasks & CrewTools
    Orchestrator --> AgentExtraction & AgentRetrieval & AgentMarket & AgentComp & ServiceWhiteSpace
    
    AgentExtraction & AgentMarket & AgentComp & ServiceWhiteSpace --> ServiceLLM
    AgentMarket & ServiceWhiteSpace --> ServiceText
    CrewTools --> AgentSearch
```

---

## 13. Class Diagram (Python Backend)

```mermaid
classDiagram
    class IdeaSubmission {
        +str idea
        +Optional[str] product_name
        +Optional[str] industry
        +Optional[str] target_audience
    }

    class ValidationResponse {
        +str idea
        +ExtractedData extracted_data
        +List[SourceRecord] sources
        +MarketAnalysisResult market_analysis
        +CompetitorAnalysisResult competitor_analysis
        +WhiteSpaceAnalysisResult white_space_analysis
        +Dict summary
    }

    class IdeaExtractionAgent {
        -List[str] MODEL_CASCADE
        +extract(idea: str, product_name: Optional[str]) ExtractedData
        -_call_groq_with_failover(prompt: str) Dict
        -_fallback_extraction(idea: str) ExtractedData
    }

    class MarketResearchToolKit {
        +search_competitors(query: str) str
        +search_industry_news(query: str) str
        +search_customer_demand(query: str) str
        +search_market_size(query: str) str
        -record_search(category: str, query: str) bool
    }

    class DataRetrievalAgent {
        +List[str] BLOCKED_DOMAINS
        +structure(raw_batches: Dict) Tuple
        -_is_clean_url(url: str) bool
        -_is_english(text: str) bool
        -_canonical_url(url: str) str
    }

    class MarketOpportunityAgent {
        +analyze(sources: List, extracted_data: Dict) MarketAnalysisResult
        -_extract_market_sizing(sources: List) List[MarketSizeEstimate]
        -_extract_personas(sources: List) List[CustomerSegment]
        -_fallback_analysis(sources: List) MarketAnalysisResult
    }

    class CompetitorAnalysisAgent {
        +analyze(sources: List, extracted_data: Dict) CompetitorAnalysisResult
        -_classify_competitors(sources: List) List[CompetitorRecord]
        -_build_matrix(competitors: List) List[ComparisonDimension]
        -_fallback_analysis(sources: List) CompetitorAnalysisResult
    }

    class WhiteSpaceEngine {
        +triangulate(market_analysis: MarketAnalysisResult, competitor_analysis: CompetitorAnalysisResult) WhiteSpaceAnalysisResult
        -_correlate_intersections(pain_points: List, competitor_voids: List) List
        -_fallback_whitespace() WhiteSpaceAnalysisResult
    }

    class ValidationCrewOrchestrator {
        -IdeaExtractionAgent idea_agent
        -DataRetrievalAgent retrieval_agent
        -MarketOpportunityAgent market_agent
        -CompetitorAnalysisAgent competitor_agent
        -WhiteSpaceEngine white_space_engine
        +validate_idea(submission: IdeaSubmission) ValidationResponse
        -_run_crew_market_research(domain_data: Dict) Dict
    }

    ValidationCrewOrchestrator --> IdeaExtractionAgent
    ValidationCrewOrchestrator --> MarketResearchToolKit
    ValidationCrewOrchestrator --> DataRetrievalAgent
    ValidationCrewOrchestrator --> MarketOpportunityAgent
    ValidationCrewOrchestrator --> CompetitorAnalysisAgent
    ValidationCrewOrchestrator --> WhiteSpaceEngine
    ValidationCrewOrchestrator ..> IdeaSubmission
    ValidationCrewOrchestrator ..> ValidationResponse
```
