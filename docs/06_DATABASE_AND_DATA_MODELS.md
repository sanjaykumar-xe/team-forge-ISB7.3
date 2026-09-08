# 06. Data Models, Schema Design & Stateless Architecture

## 1. Architectural Rationale: Stateless In-Memory Design
The **Startup Idea Validator** operates on an **in-memory, strictly stateless request-response model**:
1. **Intellectual Property Protection**: Founders submitting unpatented, proprietary startup concepts require zero-retention privacy guarantees. The platform stores zero pitches on persistent disk or databases.
2. **Real-Time Live Web Dynamism**: Market conditions, news, competitor pricing, and CAGR projections evolve daily. Persisting stale search cache would degrade the accuracy of validation results.
3. **High-Performance Pipeline Velocity**: In-process Python object passing avoids database serialization bottlenecks and disk I/O latency.

---

## 2. Core Entity-Relationship & Schema Hierarchy

All data structures are enforced via **Pydantic v2** models in [`backend/schemas/validation_schemas.py`](../backend/schemas/validation_schemas.py).

```
┌────────────────────────────────────────────────────────────────────────┐
│                          IdeaSubmission (Request)                      │
│   • idea: str (Mandatory, unlimited text)                              │
│   • product_name: Optional[str]                                        │
│   • industry: Optional[str]                                            │
│   • target_audience: Optional[str]                                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ triggers
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        ValidationResponse (Root Model)                 │
│   • idea: str                                                          │
│   • extracted_data: ExtractedData                                      │
│   • sources: List[SourceRecord]                                        │
│   • market_analysis: MarketAnalysisResult                              │
│   • competitor_analysis: CompetitorAnalysisResult                      │
│   • white_space_analysis: WhiteSpaceAnalysisResult                    │
│   • summary: Dict[str, Any]                                            │
└───────┬──────────────┬──────────────────┬───────────────────┬──────────┘
        │              │                  │                   │
        ▼              ▼                  ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────┐ ┌────────────────────┐
│ExtractedData │ │ SourceRecord │ │MarketAnalysis │ │ CompetitorAnalysis │
│•product_name │ │•title        │ │•market_size[] │ │ •competitors[]     │
│•industry     │ │•url          │ │•growth_trends │ │ •comparison_matrix │
│•audience     │ │•snippet      │ │•segments[]    │ │ •market_gaps       │
│•core_problem │ │•category     │ │•attractiveness│ │ •pricing_insights  │
│•keywords[]   │ │•score        │ │•confidence    │ └────────────────────┘
└──────────────┘ └──────────────┘ └───────┬───────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────┐
                         │    WhiteSpaceAnalysisResult     │
                         │    • opportunities[]            │
                         │      - opportunity_name         │
                         │      - segment                  │
                         │      - pain_point               │
                         │      - competitor_coverage      │
                         │      - differentiation          │
                         │      - evidence_strength        │
                         │      - confidence               │
                         │      - evidence[]               │
                         └─────────────────────────────────┘
```

---

## 3. Schema Definitions & Field Invariants

### 3.1 `ExtractedData`
```python
class ExtractedData(BaseModel):
    product_name: str
    industry: str
    target_audience: str
    core_problem: str
    keywords: List[str]
```

### 3.2 `SourceRecord`
```python
class SourceRecord(BaseModel):
    title: str
    url: str
    snippet: str
    query: str
    category: str  # Competitors | Industry News | Customer Demand | Market Size & Trends
    score: float   # Calibrated relevance score (0.0 to 1.0)
```

### 3.3 `MarketSizeEstimate` & `CustomerSegment`
```python
class MarketSizeEstimate(BaseModel):
    figure: str                  # e.g., "$10.5 Billion"
    market_type: str            # "global" | "regional" | "niche"
    cagr: Optional[str]         # e.g., "13.5%"
    forecast_year: Optional[str] # e.g., "2030"
    source_url: str             # Verified URL citation
    evidence_snippet: str
    notes: Optional[str]

class CustomerSegment(BaseModel):
    segment_name: str
    who_they_are: str
    end_users: str              # Daily hands-on user
    decision_makers: str        # Economic buyer / budget holder
    primary_needs: List[str]
    pain_points: List[str]
    motivations: List[str]
    buying_behavior: str
    industry_terminology: List[str]
```

### 3.4 `CompetitorRecord` & `ComparisonDimension`
```python
class CompetitorRecord(BaseModel):
    name: str
    classification: str          # "direct" | "indirect" | "substitute"
    core_offering: str
    target_customer: str
    major_features: List[str]
    pricing: str                 # Specific tier or "unavailable"
    business_model: str
    positioning: str
    strengths: List[str]
    weaknesses: List[str]
    customer_complaints: List[str]

class ComparisonDimension(BaseModel):
    feature_or_dimension: str
    startup_approach: str
    competitor_approaches: Dict[str, str]
```

### 3.5 `WhiteSpaceOpportunity`
```python
class WhiteSpaceOpportunity(BaseModel):
    opportunity_name: str
    segment: str
    pain_point: str
    demand_evidence: List[str]
    competitor_coverage: List[str]
    gap: str
    startup_fit: str
    differentiation_hypothesis: str
    evidence_strength: str       # "High" | "Medium" | "Low"
    confidence: float            # 0.0 to 1.0
    potential_risk: Optional[str]
    evidence: List[str]          # Traceable source URLs
```
