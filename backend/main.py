"""
Startup Idea Validator — Backend API
------------------------------------
FastAPI service exposing idea validation endpoints.
Orchestrates the 9-stage research pipeline via the CrewAI Orchestrator:
  1. Idea Extraction Agent
  2. Autonomous Market Research Agent (Tavily Tool-Calling)
  3. Market Analysis Agent (TAM/SAM/SOM, CAGR, Drivers, Barriers)
  4. Competitor Discovery & Comparison Agent (1,500 Char Snippet Budget)
  5. Evidence-Backed Market White-Space Engine
  6. Strategic SWOT & Risk Analysis Agent
  7. MVP Recommendation & Feature Scoping Agent
  8. Go-To-Market Strategy Agent
  9. Conversational Startup Advisor (Multi-Turn Interactive Chat)
  + Google OAuth 2.0 & Asynchronous Email Automation Engine
"""

import os
import sys
import uuid
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output encoding to avoid Windows charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from schemas.validation_schemas import (
    IdeaSubmission,
    ValidationResponse,
    AdvisorChatRequest,
    AdvisorChatResponse,
    GoogleAuthRequest,
    AuthResponse,
    AsyncValidationRequest,
    AsyncValidationResponse,
)
from services.advisor_service import store_validation_result, generate_advisor_reply
from services.auth_service import (
    verify_google_credential,
    create_access_token,
    verify_access_token,
)
from services.email_service import send_validation_email, test_smtp_connection
from db.database import (
    get_user_by_email,
    create_or_get_user,
    get_user_by_id,
    create_validation_job,
    update_job_status,
    get_job_by_id,
    get_jobs_by_user,
)
from crew.orchestrator import ValidationCrewOrchestrator

app = FastAPI(
    title="Startup Idea Validator API",
    description="Multi-agent market research, startup idea validation, and email automation platform.",
    version="3.0.0",
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


def run_async_validation_pipeline(job_id: str, idea_text: str, email: str, user_id: Optional[str] = None):
    """Background worker executing full 9-stage validation pipeline and dispatching email."""
    try:
        update_job_status(job_id, "processing")
        response = orchestrator.validate_idea(IdeaSubmission(idea=idea_text))
        response.idea_id = job_id
        result_dict = response.model_dump()
        store_validation_result(job_id, result_dict)
        update_job_status(job_id, "completed", result_dict=result_dict)
        send_validation_email(email, result_dict, job_id)
        print(f"[async_worker] Job {job_id} completed and email dispatched to {email}")
    except Exception as exc:
        print(f"[async_worker] Job {job_id} failed: {exc}")
        update_job_status(job_id, "failed", error=str(exc))


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok", "version": "3.0.0"}


@app.post("/api/validate", response_model=ValidationResponse)
def validate_idea(
    submission: IdeaSubmission,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
):
    """
    Synchronous multi-agent validation pipeline endpoint:
      1. Validates English coherence / gibberish check.
      2. Runs 9-stage sequential multi-agent research & analysis.
      3. Discovers high-conviction white-space opportunities.
      4. Synthesizes SWOT, MVP recommendation, and GTM strategy.
      5. Returns comprehensive intelligence and caches dossier by idea_id.
      6. Automatically emails executive dossier to user if authenticated.
    """
    try:
        response = orchestrator.validate_idea(submission)
        if not response.idea_id:
            response.idea_id = f"idea-{uuid.uuid4().hex[:8]}"
        res_dict = response.model_dump()
        store_validation_result(response.idea_id, res_dict)

        # If user is authenticated, save record to validation history
        user_id = None
        user_email = ""
        if authorization and authorization.startswith("Bearer "):
            payload = verify_access_token(authorization.split(" ")[1])
            if payload:
                user_id = payload.get("user_id")
                user_email = payload.get("email", "")

        if user_id:
            create_validation_job(response.idea_id, submission.idea, user_email, user_id)
            update_job_status(response.idea_id, "completed", result_dict=res_dict)

        # Automatically dispatch email dossier to authenticated user or recipient email
        target_email = user_email
        if target_email and "@" in target_email:
            background_tasks.add_task(send_validation_email, target_email, res_dict, response.idea_id)
            print(f"[main.py] Queued automatic validation email to {target_email} in background.", flush=True)

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


# =============================================================================
# AUTHENTICATION & ASYNCHRONOUS EMAIL AUTOMATION ENDPOINTS
# =============================================================================

@app.post("/api/auth/google", response_model=AuthResponse)
def auth_google(request: GoogleAuthRequest):
    """
    Verifies Google OAuth ID token, registers/retrieves user profile,
    and issues a 7-day signed session JWT.
    """
    try:
        profile = verify_google_credential(request.credential)
        user = create_or_get_user(
            email=profile["email"],
            name=profile.get("name"),
            avatar_url=profile.get("avatar_url"),
        )
        token = create_access_token(user)
        return AuthResponse(token=token, user=user)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(exc)}")


@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(None)):
    """Returns current authenticated user profile decoded from session JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@app.post("/api/validate/async", response_model=AsyncValidationResponse, status_code=202)
def validate_idea_async(request: AsyncValidationRequest, background_tasks: BackgroundTasks, authorization: Optional[str] = Header(None)):
    """
    Asynchronous validation endpoint:
    Queues validation pipeline in background and emails results directly to founder's Gmail.
    """
    user_id = request.user_id
    if not user_id and authorization and authorization.startswith("Bearer "):
        payload = verify_access_token(authorization.split(" ")[1])
        if payload:
            user_id = payload.get("user_id")
    if not user_id and request.email:
        u = get_user_by_email(request.email)
        if u:
            user_id = u["id"]

    job_id = f"val_{uuid.uuid4().hex[:10]}"
    create_validation_job(job_id, request.idea, request.email, user_id)
    background_tasks.add_task(run_async_validation_pipeline, job_id, request.idea, request.email, user_id)
    return AsyncValidationResponse(
        job_id=job_id,
        status="processing",
        message="Validation started in the background. You can safely close this page; your report will be emailed to you.",
        eta="45-60s",
    )


@app.get("/api/jobs/{job_id}")
def get_validation_job_status(job_id: str):
    """Checks progress and retrieves completed result for an asynchronous validation job."""
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/user/jobs")
def get_user_validation_history(authorization: Optional[str] = Header(None)):
    """Retrieves all past validation jobs for the authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session token")
    jobs = get_jobs_by_user(payload["user_id"], payload.get("email"))
    return {"jobs": jobs}

@app.get("/api/email/status")
def get_email_status():
    """Checks whether live SMTP credentials are configured in backend/.env."""
    from services.email_service import SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT
    is_configured = bool(SMTP_USER and SMTP_PASSWORD)
    return {
        "smtp_configured": is_configured,
        "smtp_server": SMTP_SERVER if is_configured else None,
        "smtp_user": SMTP_USER if is_configured else None,
        "message": "Live Gmail SMTP active" if is_configured else "Live SMTP credentials not set; emails saved locally as HTML previews in backend/data/emails/"
    }


@app.get("/api/jobs/{job_id}/email-preview", response_class=HTMLResponse)
def get_job_email_preview(job_id: str):
    """Returns the rendered responsive HTML email preview for a validation job."""
    from services.email_service import build_email_html
    email_path = os.path.join(os.path.dirname(__file__), "data", "emails", f"{job_id}.html")
    if os.path.exists(email_path):
        with open(email_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    job = get_job_by_id(job_id)
    if job and job.get("result"):
        html = build_email_html(job["result"], job_id)
        return HTMLResponse(content=html)
    raise HTTPException(status_code=404, detail="Email preview not found for this job ID")

@app.post("/api/jobs/{job_id}/send-email")
def send_job_email_endpoint(
    job_id: str,
    payload: Dict[str, Any] = Body(default={}),
    authorization: Optional[str] = Header(None),
):
    """
    Direct endpoint to dispatch or re-send the validation dossier to an email address.
    """
    job = get_job_by_id(job_id)
    report_dict = None
    email = payload.get("email", "").strip()

    if job and job.get("result"):
        report_dict = job["result"]
        if not email:
            email = job.get("email", "")

    if not report_dict:
        cached = get_validation_result(job_id)
        if cached:
            report_dict = cached

    if not report_dict:
        raise HTTPException(status_code=404, detail="Validation dossier not found for this ID")

    if not email and authorization and authorization.startswith("Bearer "):
        token_payload = verify_access_token(authorization.split(" ")[1])
        if token_payload:
            email = token_payload.get("email", "")

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid recipient email address is required.")

    success = send_validation_email(email, report_dict, job_id)
    return {
        "success": success,
        "email": email,
        "job_id": job_id,
        "message": f"Validation dossier dispatched to {email}" if success else "Email saved locally as preview.",
    }


@app.get("/api/email/test")
def test_email_endpoint(to_email: str = "sanjaykumar.mxe@gmail.com"):
    """Tests live SMTP connectivity and dispatches a test email."""
    return test_smtp_connection(to_email)
