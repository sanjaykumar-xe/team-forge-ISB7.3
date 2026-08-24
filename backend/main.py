"""
Team Forge — AI-Based Startup Idea Validator
Milestone 1 backend: idea submission -> Web Search Agent -> Data Retrieval Agent.

Web Search Agent uses the free, keyless `ddgs` (DuckDuckGo) library — no
API key or billing setup required to run this.

Later milestones plug in downstream agents (Market Opportunity, Competitor
Discovery, SWOT/Risk, MVP Recommendation, Go-To-Market, Report Generation,
Conversational Advisor) after the `structured_sources` step below — the
shape produced by DataRetrievalAgent is the stable contract they'll consume.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import ALLOWED_ORIGINS
from agents.web_search_agent import WebSearchAgent
from agents.data_retrieval_agent import DataRetrievalAgent

app = FastAPI(title="Startup Idea Validator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_search_agent = WebSearchAgent()
data_retrieval_agent = DataRetrievalAgent()


class IdeaSubmission(BaseModel):
    idea: str = Field(..., min_length=10, max_length=1000)


class SourceRecord(BaseModel):
    title: str
    url: str
    snippet: str
    query: str
    score: float


class ValidationResponse(BaseModel):
    idea: str
    sources: list[SourceRecord]
    summary: dict


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_idea(submission: IdeaSubmission):
    """
    Milestone 1 pipeline:
      1. Web Search Agent expands the idea into search queries and fetches
         live results from DuckDuckGo (free, no API key required).
      2. Data Retrieval Agent cleans, de-duplicates, and structures those
         results into a consistent source list.

    The response here is deliberately just structured source data —
    analysis (market opportunity, competitors, SWOT, etc.) is Milestone 2+.
    """
    try:
        raw_batches = web_search_agent.search(submission.idea)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    structured_sources = data_retrieval_agent.structure(raw_batches)
    summary = data_retrieval_agent.summarize_counts(structured_sources)

    return ValidationResponse(
        idea=submission.idea,
        sources=structured_sources,
        summary=summary,
    )
