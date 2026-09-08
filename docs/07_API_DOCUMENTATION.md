# 07. REST API Documentation & Endpoint Specification

## 1. API Architecture Overview
The backend exposes a high-performance **FastAPI** REST interface running on Python 3.11 with automatic Swagger UI and OpenAPI documentation generation.

- **Base URL (Local)**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **OpenAPI JSON Schema**: `http://127.0.0.1:8000/openapi.json`

---

## 2. Endpoints

### 2.1 Health Check
Checks service liveness and upstream readiness.

```http
GET /api/health
```

#### Response (200 OK)
```json
{
  "status": "ok"
}
```

---

### 2.2 Startup Idea Validation
Submits an unstructured natural-language idea description for end-to-end multi-agent validation.

```http
POST /api/validate
Content-Type: application/json
```

#### Request Headers
| Header | Value | Description |
| :--- | :--- | :--- |
| `Content-Type` | `application/json` | Required payload format |

#### Request Body (`IdeaSubmission`)
| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `idea` | `string` | **Yes** | Natural language description ($\ge 5$ characters, unlimited length). | `"A CI/CD tool that automatically checks for security vulnerabilities without slowing down builds"` |
| `product_name` | `string` | No | Explicit brand or product name override. | `"GuardrailCI"` |
| `industry` | `string` | No | Explicit vertical override. | `"DevSecOps"` |
| `target_audience` | `string` | No | Explicit audience override. | `"DevOps Engineers"` |

```json
{
  "idea": "A CI/CD tool that automatically checks for security vulnerabilities without slowing down builds",
  "product_name": "GuardrailCI",
  "industry": null,
  "target_audience": null
}
```

---

#### Response Case 1: Successful Validation (200 OK — `ValidationResponse`)

```json
{
  "idea": "A CI/CD tool that automatically checks for security vulnerabilities without slowing down builds",
  "extracted_data": {
    "product_name": "GuardrailCI",
    "industry": "DevSecOps",
    "target_audience": "Software engineering teams and DevOps engineers",
    "core_problem": "Traditional security scanning introduces significant latency into build pipelines.",
    "keywords": [
      "continuous integration",
      "vulnerability scanning",
      "build optimization",
      "DevSecOps"
    ]
  },
  "sources": [
    {
      "title": "DevSecOps Market Size & Growth Forecast Report 2030",
      "url": "https://marketsandmarkets.com/report/devsecops-market",
      "snippet": "The global DevSecOps market is projected to reach $23.9 Billion by 2030 at a CAGR of 13.5%...",
      "query": "DevSecOps market size 2024",
      "category": "Market Size & Trends",
      "score": 0.925
    }
  ],
  "market_analysis": {
    "summary": "The DevSecOps security scanning vertical exhibits strong institutional expansion...",
    "market_size": [
      {
        "figure": "$10.5 Billion",
        "market_type": "global",
        "cagr": "13.5%",
        "forecast_year": "2030",
        "source_url": "https://marketsandmarkets.com/report/devsecops-market",
        "evidence_snippet": "Global DevSecOps valuation reached $10.5B in 2024.",
        "notes": null
      }
    ],
    "growth_trends": ["Shift-left security mandates", "Automated container vulnerability audits"],
    "demand_signals": ["Developers actively complain about 15-minute pipeline scan delays"],
    "customer_segments": [
      {
        "segment_name": "Enterprise DevOps Leads",
        "who_they_are": "DevSecOps directors at companies with 200+ engineers",
        "end_users": "Software developers pushing commits daily",
        "decision_makers": "VP of Engineering or Chief Information Security Officer (CISO)",
        "primary_needs": ["Near-zero scan latency", "Low false-positive rate"],
        "pain_points": ["Broken developer velocity", "Ignored security tickets"],
        "motivations": ["Pass SOC2 audits without stalling release cycles"],
        "buying_behavior": "Enterprise annual SaaS contracts ($20k-$80k/yr)",
        "industry_terminology": ["SAST", "DAST", "CVE triage", "Shift-left"]
      }
    ],
    "attractiveness": {
      "demand_strength": "High",
      "growth_strength": "High",
      "customer_urgency": "High",
      "market_accessibility": "Medium",
      "major_barriers": ["Legacy vendor inertia", "High switching costs"],
      "important_assumptions": ["Enterprise teams prioritize speed over exhaustive scanning"]
    },
    "confidence": 0.88
  },
  "competitor_analysis": {
    "competitors": [
      {
        "name": "Snyk",
        "classification": "direct",
        "core_offering": "Developer security platform for code and containers",
        "target_customer": "Enterprise engineering teams",
        "major_features": ["CLI scanning", "IDE integration", "PR decoration"],
        "pricing": "Freemium with Enterprise tiers starting at $15k/yr",
        "business_model": "SaaS per-developer seat",
        "positioning": "Comprehensive developer-first security",
        "strengths": ["Huge developer ecosystem", "Strong integrations"],
        "weaknesses": ["Deep scans slow down build pipelines by 2-5 minutes"],
        "customer_complaints": ["Heavy pipeline latency during large monorepo builds"]
      }
    ],
    "comparison_matrix": [
      {
        "feature_or_dimension": "Build Pipeline Scan Speed",
        "startup_approach": "Sub-10-second differential caching",
        "competitor_approaches": {
          "Snyk": "1-3 minutes per build step",
          "Checkmarx": "5-10 minutes full scan"
        }
      }
    ],
    "market_gaps": ["Absence of sub-second differential scanning in existing CI runners"]
  },
  "white_space_analysis": {
    "opportunities": [
      {
        "opportunity_name": "Enterprise Ultra-Low Latency Differential Scanning",
        "segment": "Enterprise DevOps Teams",
        "pain_point": "Security scanning latency breaks daily CI/CD velocity",
        "demand_evidence": ["Developer forums cite build latency as #1 reason for disabling SAST"],
        "competitor_coverage": ["Incumbents execute full scans or slow AST analysis"],
        "gap": "No incumbent guarantees sub-10 second execution on PRs",
        "startup_fit": "GuardrailCI differential analysis checks only modified AST nodes",
        "differentiation_hypothesis": "Maintain 100% test velocity while catching 95% of critical CVEs",
        "evidence_strength": "High",
        "confidence": 0.90,
        "potential_risk": "Deep AST coverage may miss inter-module taint flows",
        "evidence": ["https://marketsandmarkets.com/report/devsecops-market"]
      }
    ]
  },
  "summary": {
    "total_sources": 23,
    "sources_per_category": {
      "Competitors": 11,
      "Industry News": 6,
      "Customer Demand": 0,
      "Market Size & Trends": 6
    },
    "sources_by_category": { ... }
  }
}
```

---

#### Response Case 2: Coherence Fast-Fail Rejection (200 OK — Friendly Guidance)
When non-English gibberish (e.g. `"asdfkjhasdkjfh zxcvbnm qwertyuiop"`) is submitted:

```json
{
  "idea": "asdfkjhasdkjfh zxcvbnm qwertyuiop",
  "extracted_data": null,
  "sources": [],
  "market_analysis": null,
  "competitor_analysis": null,
  "white_space_analysis": null,
  "summary": {
    "total_sources": 0,
    "sources_per_category": {
      "Competitors": 0,
      "Industry News": 0,
      "Customer Demand": 0,
      "Market Size & Trends": 0
    },
    "sources_by_category": {
      "Competitors": [],
      "Industry News": [],
      "Customer Demand": [],
      "Market Size & Trends": []
    },
    "message": "This doesn't look like a real idea description — try describing it in plain English."
  }
}
```

---

#### Response Case 3: Validation Error (422 Unprocessable Entity)
When `idea` is shorter than 5 characters:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "idea"],
      "msg": "String should have at least 5 characters",
      "input": "abc"
    }
  ]
}
```
