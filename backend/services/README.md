# Team Forge — Backend Services & Core Utilities

This directory contains standalone analytical engines, LLM client wrappers, and text sanitization helpers.

---

## Services Directory

| File | Purpose |
|---|---|
| `white_space_engine.py` | **Evidence-Backed Market White-Space Engine**: Analyzes the intersection between acute customer pain points, competitor coverage gaps, and startup capabilities to formulate defensible product hypotheses. |
| `llm_service.py` | Direct client wrapper for high-speed Groq API execution (`call_groq_json`, `call_groq_text`). Manages model fallbacks, temperature control, and JSON schema enforcement. |
| `text_utils.py` | Utility functions for string sanitization, token budgeting, word-boundary truncation (`truncate_at_word_boundary`), and markdown formatting. |
