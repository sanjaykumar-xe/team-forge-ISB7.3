"""
Startup Idea Validator — Backend API
------------------------------------
FastAPI service exposing idea validation endpoints.
Orchestrates the WebSearchAgent, DataRetrievalAgent, and ValidationAgent pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import ALLOWED_ORIGINS
from agents import WebSearchAgent, DataRetrievalAgent, ValidationAgent

app = FastAPI(
    title="Startup Idea Validator API",
    description="Backend service powering market research and startup idea validation.",
    version="1.0.0",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate agents
web_search_agent = WebSearchAgent()
data_retrieval_agent = DataRetrievalAgent()
validation_agent = ValidationAgent()


class IdeaSubmission(BaseModel):
    """Schema for incoming idea submission requests with optional structured fields."""
    idea: str = Field(..., min_length=3, description="Startup description to validate.")
    product_name: str | None = Field(default=None, description="Optional product or startup name.")
    industry: str | None = Field(default=None, description="Optional industry or category.")
    target_audience: str | None = Field(default=None, description="Optional target audience.")


class SourceRecord(BaseModel):
    """Schema for individual structured source findings."""
    title: str
    url: str
    snippet: str
    query: str
    category: str
    score: float


class ValidationResponse(BaseModel):
    """Schema for the full validation response returned to the client."""
    idea: str
    sources: list[SourceRecord]
    summary: dict
    validation: dict


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_idea(submission: IdeaSubmission):
    """
    Main validation pipeline:
      1. Validates English coherence to prevent gibberish from triggering fallbacks.
      2. WebSearchAgent generates category-specific queries and searches live web data.
      3. DataRetrievalAgent language-filters, cleans, categorizes, and structures findings.
      4. ValidationAgent synthesizes the evidence into an idea viability verdict, score, & strategic insights.
      5. Returns full validation report backed by categorized source evidence.
    """
    # 1. Nonsense/Gibberish check
    if not web_search_agent.is_valid_idea(submission.idea):
        return ValidationResponse(
            idea=submission.idea,
            sources=[],
            summary={
                "total_sources": 0,
                "sources_per_category": {
                    "Competitors": 0,
                    "Industry News": 0,
                    "Customer Demand": 0,
                    "Market Size & Trends": 0,
                },
                "sources_by_category": {},
                "message": "This doesn't look like a real idea description — try describing it in plain English."
            },
            validation={
                "overall_score": 0,
                "verdict_badge": "INVALID INPUT",
                "verdict_badge_class": "verdict-risk",
                "verdict_title": "Please provide a descriptive startup idea in English",
                "executive_summary": "We couldn't evaluate this submission because the input text did not contain recognizable English words or a coherent product proposition.",
                "dimensions": {},
                "strengths": [],
                "risks": ["Input lacks clear product definition"],
                "recommendations": ["Describe the core customer problem and proposed solution in 1-2 complete sentences."]
            }
        )

    # 2. Search execution across 4 market categories
    try:
        raw_batches = web_search_agent.search(
            idea=submission.idea,
            product_name=submission.product_name,
            industry=submission.industry,
            target_audience=submission.target_audience,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Search agent failure: {str(exc)}")

    # 3. Data structuring, language filtering & category grouping
    meaningful_keywords = web_search_agent.get_meaningful_keywords(
        idea=submission.idea,
        industry=submission.industry,
        product_name=submission.product_name,
    )
    structured_sources = data_retrieval_agent.structure(raw_batches, core_keywords=meaningful_keywords)
    summary = data_retrieval_agent.summarize_counts(structured_sources)

    # 4. Validation Synthesis Engine
    validation_report = validation_agent.evaluate(
        idea=submission.idea,
        industry=submission.industry,
        product_name=submission.product_name,
        target_audience=submission.target_audience,
        sources_by_category=summary.get("sources_by_category", {}),
    )

    return ValidationResponse(
        idea=submission.idea,
        sources=structured_sources,
        summary=summary,
        validation=validation_report,
    )
