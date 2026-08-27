"""
Startup Idea Validator — Backend API
------------------------------------
FastAPI service exposing idea validation endpoints.
Orchestrates the WebSearchAgent and DataRetrievalAgent pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import ALLOWED_ORIGINS
from agents import WebSearchAgent, DataRetrievalAgent

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


class IdeaSubmission(BaseModel):
    """Schema for incoming idea submission requests with optional structured fields."""
    idea: str = Field(..., min_length=10, max_length=1000, description="Startup description to validate.")
    product_name: str | None = Field(default=None, max_length=100, description="Optional product or startup name.")
    industry: str | None = Field(default=None, max_length=100, description="Optional industry or category.")
    target_audience: str | None = Field(default=None, max_length=150, description="Optional target audience.")


class SourceRecord(BaseModel):
    """Schema for individual structured source findings."""
    title: str
    url: str
    snippet: str
    query: str
    score: float


class ValidationResponse(BaseModel):
    """Schema for the full validation response returned to the client."""
    idea: str
    sources: list[SourceRecord]
    summary: dict


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_idea(submission: IdeaSubmission):
    """
    Main validation pipeline:
      1. Validates English coherence to prevent gibberish from triggering fallbacks.
      2. WebSearchAgent generates multi-angle queries and searches live web data.
      3. DataRetrievalAgent language-filters, cleans, de-duplicates, and structures the findings.
      4. Returns structured source records and coverage metrics.
    """
    # 1. Nonsense/Gibberish check (Issue 4)
    if not web_search_agent.is_valid_idea(submission.idea):
        return ValidationResponse(
            idea=submission.idea,
            sources=[],
            summary={
                "total_sources": 0,
                "sources_per_query": {},
                "message": "This doesn't look like a real idea description — try describing it in plain English."
            }
        )

    # 2. Search execution with query disambiguation (Issue 3 & 5)
    try:
        raw_batches = web_search_agent.search(
            idea=submission.idea,
            product_name=submission.product_name,
            industry=submission.industry,
            target_audience=submission.target_audience,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Search agent failure: {str(exc)}")

    # 3. Data structuring & language filtering (Issue 6)
    structured_sources = data_retrieval_agent.structure(raw_batches)
    summary = data_retrieval_agent.summarize_counts(structured_sources)

    return ValidationResponse(
        idea=submission.idea,
        sources=structured_sources,
        summary=summary,
    )
