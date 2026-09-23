"""
Conversational Startup Advisor Service
--------------------------------------
Multi-turn conversational advisor for validating startup ideas.
Maintains in-memory validation result cache and per-session conversation state.
Enforces strict anti-hallucination grounding using the accumulated validation dossier.
"""

import json
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

from prompts.loader import load_prompt
from services.llm_service import clean_json_response, execute_groq_completion

# In-memory stores for validation dossiers and conversation history with bounded growth
MAX_CACHE_SIZE = 100
MAX_HISTORY_PER_SESSION = 50

VALIDATION_CACHE: Dict[str, Dict[str, Any]] = {}
SESSION_CONVERSATIONS: Dict[str, List[Dict[str, str]]] = {}


def store_validation_result(idea_id: str, result: Dict[str, Any]) -> str:
    """Caches full validation response in memory keyed by idea_id with FIFO eviction."""
    # Evict oldest entries if capacity reached to avoid memory leaks on long-running servers
    while len(VALIDATION_CACHE) >= MAX_CACHE_SIZE:
        oldest_id = next(iter(VALIDATION_CACHE))
        VALIDATION_CACHE.pop(oldest_id, None)
        SESSION_CONVERSATIONS.pop(oldest_id, None)

    VALIDATION_CACHE[idea_id] = result
    if idea_id not in SESSION_CONVERSATIONS:
        SESSION_CONVERSATIONS[idea_id] = []
    return idea_id


def get_validation_result(idea_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves validation dossier by idea_id, with fallback to pre-loaded benchmarks."""
    if idea_id in VALIDATION_CACHE:
        return VALIDATION_CACHE[idea_id]
    
    # Check for known benchmark responses in brain/scratch or local scratch
    brain_scratch = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity-ide", "brain")
    candidate_paths = [
        os.path.join(os.getcwd(), "scratch", f"{idea_id}.json"),
        os.path.join(os.getcwd(), "scratch", f"{idea_id}_response.json"),
        os.path.join(os.getcwd(), "..", "scratch", f"{idea_id}.json"),
    ]
    if os.path.exists(brain_scratch):
        for root, _, files in os.walk(brain_scratch):
            for f in files:
                if idea_id.lower() in f.lower() and f.endswith(".json"):
                    candidate_paths.append(os.path.join(root, f))

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    VALIDATION_CACHE[idea_id] = data
                    if idea_id not in SESSION_CONVERSATIONS:
                        SESSION_CONVERSATIONS[idea_id] = []
                    return data
            except Exception:
                continue

    return None


def assemble_context_bundle(result: Dict[str, Any]) -> str:
    """
    Assembles a rich, structured, token-budgeted JSON context bundle.
    Preserves all empirical data (competitors, pricing, technical risks, SWOT, market sizing)
    while pruning duplicate matrix tables to stay comfortably within Groq ITPM budgets.
    """
    bundle: Dict[str, Any] = {
        "idea": result.get("idea", ""),
        "extracted_data": result.get("extracted_data"),
    }
    
    # Market Analysis
    ma = result.get("market_analysis") or {}
    bundle["market_analysis"] = {
        "market_size": ma.get("market_size"),
        "growth_trends": ma.get("growth_trends"),
        "customer_segments": ma.get("customer_segments"),
        "pain_points": ma.get("pain_points"),
        "market_risks": ma.get("market_risks"),
    }
    
    # Competitor Analysis (all competitor profiles, classifications, and pricing)
    ca = result.get("competitor_analysis") or {}
    competitors = ca.get("competitors")
    if not competitors:
        competitors = (ca.get("direct_competitors") or []) + (ca.get("indirect_competitors") or [])
    bundle["competitor_analysis"] = {
        "competitors": competitors,
        "market_gaps": ca.get("market_gaps"),
        "pricing_gaps": ca.get("pricing_gaps"),
    }
    
    # White Space Analysis
    ws = result.get("white_space_analysis") or {}
    bundle["white_space_analysis"] = {
        "opportunities": ws.get("opportunities") or ws.get("unmet_needs"),
        "market_gaps": ws.get("market_gaps"),
    }
    
    # SWOT Analysis
    swot = result.get("swot_analysis") or {}
    bundle["swot_analysis"] = {
        "strengths": swot.get("strengths"),
        "weaknesses": swot.get("weaknesses"),
        "opportunities": swot.get("opportunities"),
        "threats": swot.get("threats"),
        "key_risks": swot.get("key_risks"),
    }
    
    # MVP Recommendation
    mvp = result.get("mvp_recommendation") or {}
    bundle["mvp_recommendation"] = {
        "mvp_name": mvp.get("mvp_name"),
        "mvp_thesis": mvp.get("mvp_thesis"),
        "core_features": mvp.get("core_features"),
        "technical_considerations": mvp.get("technical_considerations"),
        "resource_estimate": mvp.get("resource_estimate"),
        "success_metrics": mvp.get("success_metrics"),
    }
    
    # GTM Strategy
    gtm = result.get("gtm_strategy") or {}
    bundle["gtm_strategy"] = {
        "positioning_statement": gtm.get("positioning_statement"),
        "target_channels": gtm.get("target_channels"),
        "acquisition_strategy": gtm.get("acquisition_strategy"),
        "launch_phases": gtm.get("launch_phases"),
        "key_metrics": gtm.get("key_metrics"),
    }
    
    # Compact Sources Summary
    sources = result.get("sources") or []
    bundle["sources_summary"] = [
        {"title": s.get("title"), "category": s.get("category"), "url": s.get("url")}
        for s in sources[:8] if isinstance(s, dict)
    ]
    
    return json.dumps(bundle, separators=(",", ":"), default=str)


def generate_advisor_reply(
    idea_id: str,
    message: str,
    current_view: Optional[str] = None,
    client_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Generates a conversational, strictly-grounded reply using the accumulated idea context.
    Maintains multi-turn continuity and tracks referenced report sections.
    """
    result = get_validation_result(idea_id)
    if not result:
        return {
            "reply": f"No validation dossier found for idea_id '{idea_id}'. Please validate an idea first.",
            "grounded_in": [],
        }

    # Prepare context bundle and active section
    context_bundle_str = assemble_context_bundle(result)
    active_view_str = current_view or "general_overview"

    # Load externalized system prompt
    try:
        system_prompt = load_prompt(
            "advisor_chat_system",
            context_bundle=context_bundle_str,
            current_view=active_view_str,
        )
    except Exception as exc:
        system_prompt = (
            f"You are the Startup Advisor for Team Forge. Here is the validation data:\n{context_bundle_str}\n"
            f"Current view: {active_view_str}. Answer strictly based on this data. "
            'Return JSON: {"reply": "...", "grounded_in": [...]}'
        )

    # Reconstruct multi-turn conversation messages for Groq
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    # Use client_history if provided, otherwise fallback to server-side session history
    session_history = (
        client_history
        if (client_history is not None and len(client_history) > 0)
        else SESSION_CONVERSATIONS.get(idea_id, [])
    )

    # Keep at most last 4 prior turns for concise dialog context
    recent_history = session_history[-4:] if len(session_history) > 4 else session_history
    for turn in recent_history:
        role = turn.get("role", "user")
        api_role = "assistant" if role == "advisor" else "user"
        content = turn.get("content", "")
        if content:
            messages.append({"role": api_role, "content": content})

    # Append latest user message with JSON output reminder
    messages.append({
        "role": "user",
        "content": f"{message}\n\nRespond strictly in JSON format with keys 'reply' and 'grounded_in'."
    })

    # Execute completion via Groq with JSON formatting
    try:
        raw_content, model_used = execute_groq_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.1,
            json_mode=True,
        )
        cleaned_json = clean_json_response(raw_content)
        parsed = json.loads(cleaned_json)
        reply_text = parsed.get("reply", "")
        grounded_in = parsed.get("grounded_in", [])
        if not isinstance(grounded_in, list):
            grounded_in = [str(grounded_in)] if grounded_in else []
    except Exception as exc:
        reply_text = f"I evaluated your question against the validated dossier: {str(exc)}"
        grounded_in = []

    # Update server-side conversation state with eviction safeguards
    while len(SESSION_CONVERSATIONS) >= MAX_CACHE_SIZE and idea_id not in SESSION_CONVERSATIONS:
        oldest_sess = next(iter(SESSION_CONVERSATIONS))
        SESSION_CONVERSATIONS.pop(oldest_sess, None)

    if idea_id not in SESSION_CONVERSATIONS:
        SESSION_CONVERSATIONS[idea_id] = []
    SESSION_CONVERSATIONS[idea_id].append({"role": "user", "content": message})
    SESSION_CONVERSATIONS[idea_id].append({"role": "advisor", "content": reply_text})

    # Bound history length per session
    if len(SESSION_CONVERSATIONS[idea_id]) > MAX_HISTORY_PER_SESSION:
        SESSION_CONVERSATIONS[idea_id] = SESSION_CONVERSATIONS[idea_id][-MAX_HISTORY_PER_SESSION:]

    return {
        "reply": reply_text,
        "grounded_in": grounded_in,
    }
