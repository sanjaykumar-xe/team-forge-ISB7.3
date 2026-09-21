STARTUP IDEA TO VALIDATE:
Pitch: {idea}
Product Name: {product_name}
Industry: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}
Domain Keywords: {keywords}
{market_summary}

VERIFIED SEARCH SOURCES (Competitor & Demand Research):
{sources_str}

TASK:
Identify direct competitors, indirect alternatives, and emerging entrants based strictly on the verified sources.
If NO direct or commercial competitors exist in the provided sources, return "competitors": [] and "comparison_matrix": [].
Keep descriptions concise (1-2 sentences per field).

JSON structure must match this format:
{{
  "competitors": [
    {{
      "name": "Competitor Name",
      "classification": "direct|indirect|emerging",
      "core_offering": "Core solution",
      "target_customer": "Primary target",
      "major_features": ["Feature 1", "Feature 2"],
      "pricing": "Pricing structure",
      "business_model": "Revenue model",
      "positioning": "Market positioning",
      "strengths": ["Strength 1"],
      "weaknesses": ["Weakness 1"],
      "customer_complaints": ["Complaint 1"]
    }}
  ],
  "comparison_matrix": [
    {{
      "feature_or_dimension": "Dimension",
      "startup_approach": "How the startup solves this",
      "competitor_approaches": {{"CompA": "Their approach"}}
    }}
  ],
  "market_gaps": ["Gap 1", "Gap 2"],
  "pricing_insights": ["Insight 1"],
  "business_models": ["Model 1"],
  "additional_search_used": false,
  "additional_search_query": null
}}
