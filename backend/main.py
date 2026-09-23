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

import sys

# Ensure UTF-8 output encoding to avoid Windows charmap encoding errors with unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
import uuid
from schemas.validation_schemas import (
    IdeaSubmission,
    ValidationResponse,
    AdvisorChatRequest,
    AdvisorChatResponse,
)
from services.advisor_service import store_validation_result, generate_advisor_reply
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
        if not response.idea_id:
            response.idea_id = f"idea-{uuid.uuid4().hex[:8]}"
        store_validation_result(response.idea_id, response.model_dump())
        return response
    except Exception as exc:
        print(f"[main.py] Validation error: {exc}", flush=True)
        raise HTTPException(status_code=500, detail=f"Validation error: {str(exc)}")

@app.post("/api/advisor/chat", response_model=AdvisorChatResponse)
def advisor_chat(request: AdvisorChatRequest):
    """
    Conversational Startup Advisor Endpoint (Milestone 3):
    Provides multi-turn, context-aware interactive venture advice
    grounded strictly in the validated idea dossier.
    """
    try:
        client_history = (
            [m.model_dump() for m in request.conversation_history]
            if request.conversation_history
            else None
        )
        reply_data = generate_advisor_reply(
            idea_id=request.idea_id,
            message=request.message,
            current_view=request.current_view,
            client_history=client_history,
        )
        return AdvisorChatResponse(
            reply=reply_data["reply"],
            grounded_in=reply_data.get("grounded_in", []),
        )
    except Exception as exc:
        print(f"[main.py] Advisor chat error: {exc}", flush=True)
        raise HTTPException(status_code=500, detail=f"Advisor chat error: {str(exc)}")

