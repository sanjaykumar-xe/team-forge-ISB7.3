"""
Team Forge — Pydantic Validation Schemas
----------------------------------------
Data contracts for startup validation requests, empirical search sources,
Milestone 2 analytical structures (Market, Competitor, White-Space),
and Milestone 3 strategic structures (SWOT, MVP, GTM).
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class IdeaSubmission(BaseModel):
    """Raw startup concept submitted by the user."""
    idea: str = Field(..., min_length=5, description="Unprocessed pitch text describing the startup concept")
    product_name: Optional[str] = Field(default=None, description="Explicit startup/product name, if provided")
    industry: Optional[str] = Field(default=None, description="Explicit industry or vertical, if provided")
    target_audience: Optional[str] = Field(default=None, description="Explicit target customer description, if provided")


class SourceRecord(BaseModel):
    """Single empirical search result retrieved from verified web sources."""
    url: str
    title: str
    snippet: str
    category: str = Field(..., description="Competitors | Market Size & Trends | Customer Demand | Industry News")
    relevance_score: Optional[float] = None
    published_date: Optional[str] = None
    query: Optional[str] = None


class MarketSizeEstimate(BaseModel):
    """Quantitative market sizing figure with direct empirical provenance."""
    figure: str = Field(..., description="Valuation amount, e.g. '$12.4 Billion'")
    market_type: str = Field(default="global", description="global | regional | niche")
    cagr: Optional[str] = Field(default=None, description="Compound Annual Growth Rate, e.g. '14.2%'")
    forecast_year: Optional[str] = Field(default=None, description="Year of forecast, e.g. '2030'")
    source_url: Optional[str] = Field(default=None, description="Traceable URL where the metric was found")
    evidence_snippet: Optional[str] = Field(default=None, description="Verbatim citation or context snippet from source")
    notes: Optional[str] = Field(default=None, description="Notes on variance or conflict between multiple sources")
    grounding: Optional[str] = Field(default="strong", description="Grounding conviction: 'strong' or 'tentative'")


class CustomerSegment(BaseModel):
    """Deep profile of a target customer cohort."""
    segment_name: str
    who_they_are: str
    end_users: str = Field(..., description="Who uses the product on a day-to-day basis")
    decision_makers: str = Field(..., description="Who approves or pays for the purchase")
    primary_needs: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    buying_behavior: str = Field(..., description="Procurement style, price sensitivity, purchase cycle")
    industry_terminology: List[str] = Field(default_factory=list)


class MarketAttractiveness(BaseModel):
    """Composite attractiveness scorecard based on empirical research."""
    demand_strength: str = Field(..., description="High | Medium | Low")
    growth_strength: str = Field(..., description="High | Medium | Low")
    customer_urgency: str = Field(..., description="High | Medium | Low")
    market_accessibility: str = Field(..., description="High | Medium | Low")
    major_barriers: List[str] = Field(default_factory=list)
    important_assumptions: List[str] = Field(default_factory=list)


class MarketAnalysisResult(BaseModel):
    """Aggregated output from the Market Opportunity & Customer Segmentation Agent."""
    summary: str
    market_size: List[MarketSizeEstimate] = Field(default_factory=list)
    growth_trends: List[str] = Field(default_factory=list)
    demand_signals: List[str] = Field(default_factory=list)
    customer_segments: List[CustomerSegment] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    buying_behavior: List[str] = Field(default_factory=list)
    market_risks: List[str] = Field(default_factory=list)
    attractiveness: Optional[MarketAttractiveness] = None
    confidence: Optional[float] = Field(default=None, description="Conviction score (null if preliminary/unverified)")
    analysis_status: Optional[str] = Field(default="completed", description="Analysis status: 'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None, description="Diagnostic notice or retry message if processing encountered an error")


class CompetitorRecord(BaseModel):
    """Structured profile of a discovered market rival."""
    name: str
    classification: str = Field(..., description="direct | indirect | emerging")
    core_offering: str
    target_customers: Optional[str] = Field(default="Target market", description="Target customer segment")
    key_features: List[str] = Field(default_factory=list)
    pricing: Optional[str] = Field(default="unavailable", description="Documented pricing tiers or 'unavailable'")
    business_model: Optional[str] = Field(default="unavailable", description="Observed revenue model or 'unavailable'")
    positioning: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    customer_complaints: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None


class ComparisonMatrixRow(BaseModel):
    """One capability dimension compared across competitors."""
    dimension: str = Field(default="Feature Dimension", description="Feature, pricing, speed, UX, compliance, etc.")

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict) and "feature_or_dimension" in obj and "dimension" not in obj:
            obj["dimension"] = obj["feature_or_dimension"]
        return super().model_validate(obj, *args, **kwargs)
    startup_approach: str = Field(..., description="How the evaluated startup solves this dimension")
    competitor_approaches: Dict[str, str] = Field(default_factory=dict, description="Map of {CompetitorName: approach_description}")


class CompetitorAnalysisResult(BaseModel):
    """Aggregated output from the Competitor Discovery & Comparison Agent."""
    summary: str = Field(default="Competitive landscape discovery completed.", description="Executive synthesis")
    competitors: List[CompetitorRecord] = Field(default_factory=list)
    comparison_matrix: List[ComparisonMatrixRow] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)
    pricing_gaps: List[str] = Field(default_factory=list)
    unmet_customer_needs: List[str] = Field(default_factory=list)
    confidence: Optional[float] = Field(default=None, description="Conviction score (null if preliminary/unverified)")
    analysis_status: Optional[str] = Field(default="completed", description="Analysis status: 'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None, description="Diagnostic notice or retry message if processing encountered an error")


class WhiteSpaceOpportunity(BaseModel):
    """A structural, evidence-backed intersection of pain, competitor absence, and capability."""
    opportunity_name: str = Field(..., description="Concise strategic title for the discovered white-space")
    customer_segment: str = Field(default="Target Customer Cohort", description="Exact customer cohort experiencing this unaddressed need")
    pain_point: str = Field(..., description="Acute friction, bottleneck, or unmet expectation")
    demand_evidence: List[str] = Field(default_factory=list, description="Supporting empirical evidence quotes/signals")
    competitor_coverage: List[str] = Field(default_factory=list, description="Current competitor behavior and omissions")
    gap: str = Field(default="", description="Clear structural gap left open in the market")
    startup_fit: str = Field(default="", description="Why the startup concept is structurally suited to conquer this gap")
    differentiation_hypothesis: str = Field(default="", description="Strategic hypothesis for sustainable differentiation")
    evidence_strength: str = Field(default="Low", description="Evidence backing tier: High, Medium, or Low")
    confidence: Optional[float] = Field(default=None, description="Conviction score (null if preliminary/unverified)")
    potential_risk: Optional[str] = Field(default=None, description="Key execution or market hazard to monitor")
    evidence: List[str] = Field(default_factory=list, description="Traceable source URLs and citations")

    @field_validator("demand_evidence", "competitor_coverage", "evidence", mode="before")
    @classmethod
    def coerce_string_list(cls, v):
        if not isinstance(v, list):
            return [str(v)] if v else []
        flattened = []
        for item in v:
            if isinstance(item, list):
                flattened.extend(cls.coerce_string_list(item))
            elif item is not None:
                flattened.append(str(item))
        return flattened


class WhiteSpaceAnalysisResult(BaseModel):
    """Aggregated output from the Evidence-Backed Market White-Space Engine."""
    opportunities: List[WhiteSpaceOpportunity] = Field(default_factory=list)
    analysis_status: Optional[str] = Field(default="completed", description="Analysis status: 'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None, description="Diagnostic notice or retry message if processing encountered an error")


# ══════════════════════════════════════════════════════════════════════
# Milestone 3 Schemas: SWOT, MVP, GTM
# ══════════════════════════════════════════════════════════════════════

class SWOTItem(BaseModel):
    """Single evidence-backed item in a SWOT quadrant."""
    item: str = Field(..., description="Description of the SWOT element")
    evidence: str = Field(default="", description="Upstream finding or source citation backing this item")
    confidence: str = Field(default="medium", description="Confidence tier: high, medium, or low")


class SWOTRiskItem(BaseModel):
    """Identified strategic risk with severity and mitigation."""
    risk: str = Field(..., description="Specific risk description")
    severity: str = Field(default="medium", description="Severity tier: high, medium, or low")
    mitigation: str = Field(default="", description="Concrete actionable mitigation strategy")


class SWOTAnalysisResult(BaseModel):
    """Aggregated output from the SWOT & Risk Analysis Agent (Milestone 3)."""
    strengths: List[Union[SWOTItem, Dict[str, Any], str]] = Field(default_factory=list)
    weaknesses: List[Union[SWOTItem, Dict[str, Any], str]] = Field(default_factory=list)
    opportunities: List[Union[SWOTItem, Dict[str, Any], str]] = Field(default_factory=list)
    threats: List[Union[SWOTItem, Dict[str, Any], str]] = Field(default_factory=list)
    risk_assessment: List[Union[SWOTRiskItem, Dict[str, Any], str]] = Field(default_factory=list)
    strategic_recommendation: str = Field(default="", description="2-3 sentence executive verdict on whether to pursue this idea")
    analysis_status: Optional[str] = Field(default="completed", description="'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None)


class MVPFeature(BaseModel):
    """A prioritized feature recommendation for the MVP."""
    feature: str = Field(..., description="Feature title")
    description: Optional[str] = Field(default="", description="Functional description")
    justification: str = Field(default="", description="Why this feature is critical for the MVP")
    upstream_evidence: str = Field(default="", description="Specific citation to upstream finding (pain point, competitor gap, white space)")
    priority: str = Field(default="P0", description="Priority: P0 (Must Have), P1 (High Value), P2 (Nice to Have)")
    complexity: Optional[str] = Field(default="medium", description="Estimated complexity: low, medium, or high")


class MVPRecommendation(BaseModel):
    """Aggregated output from the MVP Recommendation Agent (Milestone 3)."""
    mvp_name: str = Field(default="Startup MVP", description="Descriptive name of the MVP configuration")
    mvp_thesis: str = Field(default="", description="1-2 sentence core thesis for why this MVP configuration wins")
    core_features: List[Union[MVPFeature, Dict[str, Any], str]] = Field(default_factory=list)
    nice_to_haves: List[Union[Dict[str, Any], str]] = Field(default_factory=list)
    technical_considerations: List[str] = Field(default_factory=list)
    resource_estimate: Optional[Union[Dict[str, Any], str]] = Field(default=None)
    success_metrics: List[str] = Field(default_factory=list)
    analysis_status: Optional[str] = Field(default="completed", description="'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None)


class GTMChannel(BaseModel):
    """Target acquisition channel with fit rationale and tactics."""
    channel: str = Field(..., description="Channel name, e.g. 'Developer Communities / GitHub'")
    rationale: str = Field(default="", description="Why this channel fits this specific idea and audience")
    fit_score: str = Field(default="high", description="Channel fit tier: high, medium, or low")
    tactics: List[str] = Field(default_factory=list, description="Specific tactics for this channel")


class GTMStrategy(BaseModel):
    """Aggregated output from the Go-To-Market Strategy Agent (Milestone 3)."""
    positioning_statement: str = Field(default="", description="Idea-specific value positioning statement")
    target_channels: List[Union[GTMChannel, Dict[str, Any], str]] = Field(default_factory=list)
    acquisition_strategy: Optional[Union[Dict[str, Any], str]] = Field(default=None)
    pricing_approach: Optional[Union[Dict[str, Any], str]] = Field(default=None)
    launch_phases: List[Union[Dict[str, Any], str]] = Field(default_factory=list)
    key_metrics: List[Union[Dict[str, Any], str]] = Field(default_factory=list)
    competitive_positioning: Optional[str] = Field(default=None)
    analysis_status: Optional[str] = Field(default="completed", description="'completed' or 'processing_error'")
    message: Optional[str] = Field(default=None)


class ChatMessage(BaseModel):
    """Single turn in a conversational advisor session."""
    role: str = Field(..., description="'user' or 'advisor'")
    content: str = Field(..., description="Message text")


class AdvisorChatRequest(BaseModel):
    """Request schema for conversational advisor endpoint."""
    idea_id: str = Field(..., description="Identifies which validated idea this conversation is about")
    message: str = Field(..., description="The user's question")
    current_view: Optional[str] = Field(default=None, description="Current report section in view, e.g. 'competitors', 'market_sizing'")
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Prior turns in this session")


class AdvisorChatResponse(BaseModel):
    """Response schema for conversational advisor endpoint."""
    reply: str = Field(..., description="Advisor answer text")
    grounded_in: List[str] = Field(default_factory=list, description="List of report sections referenced for this answer")


class ValidationResponse(BaseModel):
    """Full unified validation response combining Milestone 1, 2, and 3 intelligence."""
    idea_id: Optional[str] = Field(default=None, description="Unique identifier for conversational advisor session.")
    idea: str
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Structured extraction output from LLM.")
    sources: List[SourceRecord] = Field(default_factory=list, description="Sanitized and verified search evidence.")
    market_analysis: Optional[MarketAnalysisResult] = Field(default=None, description="Market opportunity & segmentation.")
    competitor_analysis: Optional[CompetitorAnalysisResult] = Field(default=None, description="Competitor discovery & comparison.")
    white_space_analysis: Optional[WhiteSpaceAnalysisResult] = Field(default=None, description="Evidence-backed white-space map.")
    swot_analysis: Optional[SWOTAnalysisResult] = Field(default=None, description="SWOT & Risk analysis (Milestone 3).")
    mvp_recommendation: Optional[MVPRecommendation] = Field(default=None, description="MVP Recommendation (Milestone 3).")
    gtm_strategy: Optional[GTMStrategy] = Field(default=None, description="Go-To-Market Strategy (Milestone 3).")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Source counts and category summaries.")
