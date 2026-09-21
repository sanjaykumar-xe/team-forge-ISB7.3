# Team Forge — Data Contracts & Validation Schemas

This directory defines the strict Pydantic data models enforcing type safety, serialization, and frontend contract compliance across the validation pipeline.

---

## Key Schemas (`validation_schemas.py`)

- `IdeaSubmission`: Input request payload (`idea`, `product_name`, `industry`, `target_audience`).
- `SourceRecord`: Structured web source (`title`, `url`, `snippet`, `category`, `score`, `provider`).
- `MarketSizeEstimate`: Structured market figure with explicit citation URL, CAGR, and grounding level (`strong` vs `tentative`).
- `CustomerSegment`: Granular persona profile (End User vs Decision Maker, acute pain points, buying dynamics).
- `CompetitorRecord`: Competitor intelligence profile (core offering, strengths, weaknesses, source URL).
- `WhiteSpaceOpportunity`: Triangulated opportunity hypothesis with confidence scoring and evidence chains.
- `SWOTAnalysisResult`: 4-quadrant strategic matrix (S, W, O, T) and prioritized risks with mitigations.
- `MVPRecommendation`: Prioritized features (P0/P1/P2) with upstream grounding and resource estimates.
- `GTMStrategy`: Core positioning statement, channel fit rankings, launch phases, and traction targets.
- `ValidationResponse`: Complete composite response model returned by `POST /api/validate`.
