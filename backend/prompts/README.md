# Team Forge — Externalized Prompt Engine

This directory externalizes all agent system instructions, prompt templates, and output contracts into modular Markdown files. This cleanly separates prompt engineering and domain guidance from Python logic.

---

## Prompt Structure & Organization

Each reasoning stage has dedicated pair files:
- `*_system.md`: Defines the agent persona, role, anti-hallucination constraints, and JSON response schema.
- `*_task.md`: Injects runtime startup variables (`{idea}`, `{product_name}`, `{industry}`, `{sources_str}`) and defines specific analytical goals.

| Prompt Pair | Agent / Component |
|---|---|
| `idea_extraction_system.md` | Idea Extraction Agent |
| `web_search_system.md` / `web_search_task.md` | Autonomous Market Research Agent (CrewAI) |
| `market_analysis_system.md` / `market_analysis_task.md` | Market Opportunity & Customer Segmentation Agent |
| `competitor_analysis_system.md` / `competitor_analysis_task.md` | Competitor Discovery & Positioning Agent |
| `white_space_system.md` / `white_space_task.md` | Evidence-Backed White-Space Engine |
| `swot_system.md` / `swot_task.md` | SWOT Analysis & Risk Assessment Agent |
| `mvp_system.md` / `mvp_task.md` | MVP Recommendation & Feature Scoping Agent |
| `gtm_system.md` / `gtm_task.md` | Go-To-Market Strategy Agent |

---

## Prompt Loader
The utility `loader.py` exposes:
```python
load_prompt(prompt_name: str, **kwargs) -> str
```
It reads the `.md` template from disk and safely performs variable interpolation.
