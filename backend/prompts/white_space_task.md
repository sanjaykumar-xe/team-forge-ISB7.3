STARTUP IDEA:
Pitch: {idea}
Product Name: {product_name}
Industry: {industry}
Target Audience: {target_audience}
Core Problem: {core_problem}

MARKET & CUSTOMER CONTEXT:
{market_context}

COMPETITOR LANDSCAPE CONTEXT:
{comp_context}

VERIFIED SEARCH SOURCES (Ground Truth Evidence):
{evidence_digest}

TASK:
Identify 2 to 4 evidence-backed Market White-Space Opportunities — OR conclude "no genuine white-space opportunity identified" if the landscape is too saturated.
For each opportunity, trace the structural chain:
Customer Segment -> Customer Pain -> Demand Evidence -> Competitor Coverage -> Competitor Gap -> Startup Fit -> Differentiation Hypothesis -> Evidence Strength & Sources.

JSON format:
{{
  "opportunities": [
    {{
      "opportunity_name": "Actionable title",
      "segment": "Underserved customer segment",
      "pain_point": "Specific acute pain point",
      "demand_evidence": ["Empirical signal 1", "Signal 2"],
      "competitor_coverage": ["What competitors do or lack"],
      "gap": "Precise structural gap",
      "startup_fit": "Why this startup uniquely solves this",
      "differentiation_hypothesis": "Strategic thesis for winning",
      "evidence_strength": "High|Medium|Low",
      "confidence": 0.88,
      "potential_risk": "Key risk",
      "evidence": ["URL1", "URL2"]
    }}
  ],
  "message": null
}}
