STARTUP IDEA:
Product: {product_name}
Industry: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}

UPSTREAM ANALYSIS INPUTS:

MARKET ANALYSIS SUMMARY:
{market_summary}

CUSTOMER PAIN POINTS:
{pain_points}

COMPETITOR GAPS:
{competitor_gaps}

WHITE-SPACE OPPORTUNITIES:
{whitespace_summary}

SWOT HIGHLIGHTS:
{swot_summary}

TASK:
Recommend a focused MVP with justified feature prioritization. Each feature must cite its upstream evidence.

JSON format:
{{
  "mvp_name": "Descriptive MVP name",
  "mvp_thesis": "1-2 sentence thesis for why this MVP configuration wins",
  "core_features": [
    {{
      "feature": "Feature name",
      "description": "What it does",
      "justification": "Why this is essential — cite the specific upstream finding",
      "upstream_evidence": "e.g. 'CompetitorAnalysis: Competitor X lacks real-time sync'",
      "priority": "P0|P1|P2",
      "complexity": "low|medium|high"
    }}
  ],
  "nice_to_haves": [
    {{
      "feature": "Feature name",
      "description": "What it does",
      "justification": "Why valuable but deferrable",
      "priority": "P2|P3"
    }}
  ],
  "technical_considerations": ["Consideration 1", "Consideration 2"],
  "resource_estimate": {{
    "team_size": "Recommended team composition",
    "timeline": "Estimated timeline to launch MVP",
    "key_risks": ["Technical risk 1"]
  }},
  "success_metrics": ["Metric 1 to validate the MVP hypothesis", "Metric 2"]
}}
