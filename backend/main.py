"""
Startup Idea Validator — Backend API
------------------------------------
FastAPI service exposing idea validation endpoints.
Orchestrates the IdeaExtractionAgent, WebSearchAgent, and DataRetrievalAgent pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import ALLOWED_ORIGINS
from agents import IdeaExtractionAgent, WebSearchAgent, DataRetrievalAgent

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
idea_extraction_agent = IdeaExtractionAgent()
web_search_agent = WebSearchAgent()
data_retrieval_agent = DataRetrievalAgent()


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
    extracted_data: dict | None = Field(default=None, description="Structured extraction output from LLM.")
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
      1. Validates English coherence to prevent gibberish from triggering search.
      2. IdeaExtractionAgent extracts structured product, industry, and keyword metadata.
      3. WebSearchAgent executes targeted Tavily searches across 4 market categories.
      4. DataRetrievalAgent filters blocked domains, language-checks, deduplicates, and structures sources.
      5. Returns categorized source evidence alongside extracted idea metadata.
    """
    # 1. Nonsense/Gibberish check
    if not web_search_agent.is_valid_idea(submission.idea):
        return ValidationResponse(
            idea=submission.idea,
            extracted_data=None,
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
            }
        )

    # 2. Extract structured metadata
    try:
        extracted = idea_extraction_agent.extract(
            idea=submission.idea,
            product_name=submission.product_name,
            industry=submission.industry,
            target_audience=submission.target_audience,
        )
    except Exception as exc:
        print(f"[main.py] IdeaExtractionAgent failed: {exc}")
        extracted = {
            "product_name": submission.product_name or "Startup",
            "industry": submission.industry or "Software",
            "target_audience": submission.target_audience or "Consumers",
            "core_problem": submission.idea,
            "keywords": submission.idea.split()[:4],
        }

    # 3. Search execution across 4 market categories via Tavily
    try:
        raw_batches = web_search_agent.search(structured_idea=extracted)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Search agent failure: {str(exc)}")

    # 4. Data structuring, language filtering & category grouping
    structured_sources = data_retrieval_agent.structure(raw_batches)
    summary = data_retrieval_agent.summarize_counts(structured_sources)

    return ValidationResponse(
        idea=submission.idea,
        extracted_data=extracted,
        sources=structured_sources,
        summary=summary,
    )
