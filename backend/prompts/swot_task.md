STARTUP IDEA:
Product: {product_name}
Industry: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}

UPSTREAM ANALYSIS INPUTS:

MARKET OPPORTUNITY SUMMARY:
{market_summary}

KEY CUSTOMER SEGMENTS:
{segments_summary}

COMPETITOR LANDSCAPE:
{competitor_summary}

WHITE-SPACE OPPORTUNITIES:
{whitespace_summary}

TASK:
Synthesize a judgment-driven SWOT analysis. Only elevate findings that genuinely warrant strategic attention.

JSON format:
{{
  "strengths": [
    {{"item": "Strength description", "evidence": "Which upstream finding supports this", "confidence": "high|medium|low"}}
  ],
  "weaknesses": [
    {{"item": "Weakness description", "evidence": "Supporting evidence", "confidence": "high|medium|low"}}
  ],
  "opportunities": [
    {{"item": "Opportunity description", "evidence": "Supporting evidence", "confidence": "high|medium|low"}}
  ],
  "threats": [
    {{"item": "Threat description", "evidence": "Supporting evidence", "confidence": "high|medium|low"}}
  ],
  "risk_assessment": [
    {{"risk": "Risk description", "severity": "high|medium|low", "mitigation": "Recommended mitigation"}}
  ],
  "strategic_recommendation": "2-3 sentence executive verdict on whether to pursue this idea."
}}
