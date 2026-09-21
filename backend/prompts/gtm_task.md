STARTUP IDEA:
Product: {product_name}
Industry: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}

UPSTREAM ANALYSIS INPUTS:

MARKET OPPORTUNITY:
{market_summary}

CUSTOMER SEGMENTS:
{segments_summary}

COMPETITOR LANDSCAPE:
{competitor_summary}

WHITE-SPACE POSITIONING:
{whitespace_summary}

SWOT ASSESSMENT:
{swot_summary}

MVP SCOPE:
{mvp_summary}

TASK:
Produce an actionable, idea-specific go-to-market strategy. Channels and positioning must be justified against THIS idea's specific landscape — not generic startup advice.

JSON format:
{{
  "positioning_statement": "For [target customer] who [pain point], [product] is a [category] that [key benefit]. Unlike [competitors], we [key differentiator].",
  "target_channels": [
    {{
      "channel": "Specific channel name",
      "rationale": "Why this channel fits THIS specific idea and audience",
      "fit_score": "high|medium|low",
      "tactics": ["Specific tactic 1", "Tactic 2"]
    }}
  ],
  "acquisition_strategy": {{
    "primary_method": "Core acquisition approach",
    "secondary_methods": ["Method 2"],
    "estimated_cac": "Estimated customer acquisition cost range",
    "rationale": "Why this approach fits the target segment"
  }},
  "pricing_approach": {{
    "model": "Pricing model (e.g., freemium, subscription, transaction)",
    "rationale": "Why this model fits based on competitor pricing and customer buying behavior",
    "price_range": "Estimated price point or range"
  }},
  "launch_phases": [
    {{
      "phase": "Phase name (e.g., Private Beta)",
      "duration": "Timeline",
      "objectives": ["Objective 1"],
      "milestones": ["Measurable milestone 1"]
    }}
  ],
  "key_metrics": [
    {{
      "metric": "Specific measurable metric",
      "target": "Concrete target value",
      "timeframe": "When to measure"
    }}
  ],
  "competitive_positioning": "How to position against the specific competitors identified in the analysis"
}}
