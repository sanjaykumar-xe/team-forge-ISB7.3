# 10. User Guide & Operations Manual

## 1. Getting Started
The **Startup Idea Validator** provides an intuitive, high-contrast editorial interface for researching startup ideas. 

---

## 2. Navigating the Interface

```
┌────────────────────────────────────────────────────────────────────────┐
│               TEAM FORGE — STARTUP IDEA VALIDATOR                      │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Pitch Your Idea:                                               │   │
│   │ [ Describe your startup concept in plain English...          ] │   │
│   │                                                                │   │
│   │ [Optional: Product Name] [Optional: Industry] [Audience]       │   │
│   │                                                                │   │
│   │ [  VALIDATE STARTUP IDEA  ]                                    │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Input Your Startup Idea
- In the primary textarea, describe your startup concept.
- **Tip for Best Results**: Include the problem you are solving, who experiences it, and your proposed solution.
- *Example*: `"A smart B2B platform that helps independent logistics carriers automate dispatching, route matching, and fuel compliance."`
- You can enter single-sentence elevator pitches or detailed 2,000-word business plans. The system supports **unlimited input length**.
- Optional: Specify your brand name (e.g. `CarrierSync`) or explicit target audience if you already have them defined.

### Step 2: Live Multi-Agent Execution
- Click **Validate Startup Idea**.
- The interface activates a pulsing loading state while the multi-agent pipeline executes across the live web.
- Typical analysis duration: **60 to 120 seconds**.

---

## 3. Interpreting Your Validation Intelligence

### A. The AI Domain Dossier Card
- Located at the top of the results page.
- Displays normalized domain metadata extracted by `IdeaExtractionAgent`:
  - **Product Name**: Official or inferred brand identifier.
  - **Industry Vertical**: Primary sector classification.
  - **Target Audience**: Who the product serves.
  - **Core Problem**: Refined acute pain statement.
  - **Domain Keywords**: Strategic keywords surfaced for research.

---

### B. The Evidence-Backed Market White-Space Map (Centerpiece)
- This view highlights **defensible market opportunity gaps** discovered by the `WhiteSpaceEngine`.
- Each opportunity card displays:
  - **Opportunity Title & Segment**: What the gap is and who needs it.
  - **Customer Pain Point**: The specific frustration reported by real users.
  - **Competitor Void**: Why incumbents (e.g. legacy software, market leaders) fail to address it.
  - **Differentiation Hypothesis**: How your startup can win this segment.
  - **Evidence Strength**: `High`, `Medium`, or `Low` with a quantitative confidence percentage.
  - **Traceable Citations**: Clickable source links proving the claim.

---

### C. Market Opportunity & Sizing Panel
- **TAM / SAM Estimates**: Empirical market valuations with CAGR growth projections and forecast horizons.
- **Honest Null Notification**: If institutional market sizing reports do not yet exist for a niche or nascent vertical, the system displays an honest informational notice rather than hallucinating speculative numbers.
- **Market Attractiveness Scorecard**: Rates Demand Strength, Growth Strength, Customer Urgency, and Accessibility.

---

### D. Customer Segmentation Persona Cards
- Persona profiles broken down into:
  - **Daily End Users**: Hands-on workflow challenges, daily tasks, and emotional friction.
  - **Economic Decision Makers**: Budget authority, ROI criteria, compliance mandates, and purchasing habits.
  - **Industry Terminology & Jargon**: Domain-specific vocabulary used by your prospective buyers.

---

### E. Competitor Comparison Matrix
- Visual side-by-side benchmarking table comparing your startup concept against primary direct competitors and indirect substitutes across key feature dimensions.
- Uncovers competitor pricing tiers, business models, documented strengths, and user complaints.

---

### F. 4-Category Evidence Grid & Source Cards
- Groups 20–35 verified research sources into:
  1. *Competitors & Alternatives*
  2. *Industry News & Venture Activity*
  3. *Customer Demand & User Reviews*
  4. *Market Size & Growth Trends*
- Each card includes the article title, publisher hostname, relevance score, and a clean snippet truncated at a sentence boundary with an inline *"Read more"* toggle.
