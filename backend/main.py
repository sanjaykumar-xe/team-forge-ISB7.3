"""
Startup Idea Validator — Backend API
------------------------------------
FastAPI service exposing idea validation endpoints.
Orchestrates the 5-agent research pipeline via the CrewAI Orchestrator:
  1. Idea Extraction Agent
  2. Web Search Agent (Tavily 4-Category Search)
  3. Data Retrieval Agent (Sanitization, Filtering, Deduplication)
  4. Market Opportunity & Customer Segmentation Agent
  5. Competitor Discovery & Comparison Agent
  + Evidence-Backed Market White-Space Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from schemas.validation_schemas import IdeaSubmission, ValidationResponse
from crew.orchestrator import ValidationCrewOrchestrator

app = FastAPI(
    title="Startup Idea Validator API",
    description="Multi-agent market research and startup idea validation platform.",
    version="2.0.0",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the CrewAI orchestrator
orchestrator = ValidationCrewOrchestrator()


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_idea(submission: IdeaSubmission):
    """
    Main multi-agent validation pipeline endpoint:
      1. Validates English coherence / gibberish check.
      2. Runs sequential multi-agent research & analysis via CrewAI Orchestrator.
      3. Discovers high-conviction white-space opportunities via the White-Space Engine.
      4. Returns comprehensive market, competitor, customer persona, and citation evidence.
    """
    try:
        response = orchestrator.validate_idea(submission)
        return response
    except Exception as exc:
        print(f"[main.py] Validation error: {exc}", flush=True)
        raise HTTPException(status_code=500, detail=f"Validation error: {str(exc)}")
