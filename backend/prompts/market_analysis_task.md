STARTUP IDEA TO ANALYZE:
Pitch: {idea}
Product Name: {product_name}
Industry Vertical: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}
Extracted Keywords: {keywords}

VERIFIED SEARCH SOURCES FROM RESEARCH:
{context_str}

TASK:
Produce a concise, grounded Market Opportunity & Customer Segmentation analysis.
CONSTRAINTS:
- Keep evidence snippets concise (1-2 sentences).
- Limit customer_segments to top 2 segments max.
- Maintain valid JSON syntax.
- If VERIFIED SEARCH SOURCES contain no quantitative market size figures, return "market_size": [], "attractiveness": null, and "confidence": null.

JSON structure must match this format:
{{
  "summary": "2-3 sentence executive synthesis.",
  "market_size": [
    {{
      "figure": "$X.X Billion",
      "market_type": "global|regional|niche",
      "cagr": "X.X%",
      "forecast_year": "2030",
      "source_url": "URL",
      "evidence_snippet": "Direct quote",
      "notes": "Caveats",
      "grounding": "strong|tentative"
    }}
  ],
  "growth_trends": ["Trend 1", "Trend 2"],
  "demand_signals": ["Signal 1", "Signal 2"],
  "customer_segments": [
    {{
      "segment_name": "Name",
      "who_they_are": "Profile",
      "end_users": "Daily users",
      "decision_makers": "Buyers",
      "primary_needs": ["Need 1"],
      "pain_points": ["Pain 1"],
      "motivations": ["Motivation 1"],
      "buying_behavior": "Procurement cycle",
      "industry_terminology": ["term1"]
    }}
  ],
  "pain_points": ["Pain 1", "Pain 2"],
  "buying_behavior": ["Characteristic 1"],
  "market_risks": ["Risk 1"],
  "attractiveness": {{
    "demand_strength": "High|Medium|Low",
    "growth_strength": "High|Medium|Low",
    "customer_urgency": "High|Medium|Low",
    "market_accessibility": "High|Medium|Low",
    "major_barriers": ["Barrier 1"],
    "important_assumptions": ["Assumption 1"]
  }},
  "confidence": 0.85,
  "additional_search_used": false,
  "additional_search_query": null
}}
