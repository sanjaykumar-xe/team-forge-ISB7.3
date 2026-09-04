"""
Team Forge — Pydantic Schemas for Milestone 2 Validation Pipeline
----------------------------------------------------------------
Defines strict, typed contracts for:
- User Idea Submission (No artificial character limit)
- Idea Extraction Metadata
- Source Evidence Records
- Market Opportunity & Customer Segmentation Analysis
- Competitor Discovery & Comparison Matrix
- Evidence-Backed Market White-Space Engine
- Full Validation Response Object
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class IdeaSubmission(BaseModel):
    """Schema for incoming idea submission requests with arbitrary text length."""
    idea: str = Field(..., min_length=3, description="Startup description to validate.")
    product_name: Optional[str] = Field(default=None, description="Optional product or startup name.")
    industry: Optional[str] = Field(default=None, description="Optional industry or category.")
    target_audience: Optional[str] = Field(default=None, description="Optional target audience.")


class SourceRecord(BaseModel):
    """Schema for individual structured source findings from web research."""
    title: str
    url: str
    snippet: str
    query: str
    category: str
    score: float


class MarketSizeEstimate(BaseModel):
    """Quantitative or qualitative market size estimate tied directly to empirical sources."""
    figure: str = Field(..., description="Estimated market valuation, e.g. '$14.2 Billion'")
    market_type: str = Field(default="global", description="Scope: global, regional, or niche")
    cagr: Optional[str] = Field(default=None, description="Compound Annual Growth Rate if available, e.g. '18.4%'")
    forecast_year: Optional[str] = Field(default=None, description="Forecast target year, e.g. '2032'")
    source_url: Optional[str] = Field(default=None, description="Source URL where this figure was retrieved")
    evidence_snippet: Optional[str] = Field(default=None, description="Direct quote or snippet supporting this valuation")
    notes: Optional[str] = Field(default=None, description="Contextual notes or flags regarding source disagreement")


class CustomerSegment(BaseModel):
    """Granular customer persona profile derived from market demand signals."""
    segment_name: str = Field(..., description="Identifier name of the customer segment")
    who_they_are: str = Field(..., description="Profile description of this customer group")
    end_users: str = Field(..., description="Daily operational users of the solution")
    decision_makers: str = Field(..., description="Economic buyer or purchasing authority")
    primary_needs: List[str] = Field(default_factory=list, description="Core workflow requirements and priorities")
    pain_points: List[str] = Field(default_factory=list, description="Acute frustrations and friction points")
    motivations: List[str] = Field(default_factory=list, description="Key drivers for adopting a new platform")
    buying_behavior: str = Field(..., description="Procurement cycle, price sensitivity, and adoption criteria")
    industry_terminology: List[str] = Field(default_factory=list, description="Domain jargon and industry terminology")


class MarketAttractiveness(BaseModel):
    """Structured scorecard evaluating market entry conditions."""
    demand_strength: str = Field(..., description="Demand velocity: High, Medium, or Low")
    growth_strength: str = Field(..., description="Growth trajectory: High, Medium, or Low")
    customer_urgency: str = Field(..., description="Willingness to act: High, Medium, or Low")
    market_accessibility: str = Field(..., description="Go-to-market reachability: High, Medium, or Low")
    major_barriers: List[str] = Field(default_factory=list, description="Key structural or regulatory barriers")
    important_assumptions: List[str] = Field(default_factory=list, description="Critical assumptions underlying the evaluation")


class MarketAnalysisResult(BaseModel):
    """Comprehensive output from the Market Opportunity & Customer Segmentation Agent."""
    summary: str = Field(..., description="Executive market overview synthesis")
    market_size: List[MarketSizeEstimate] = Field(default_factory=list)
    growth_trends: List[str] = Field(default_factory=list)
    demand_signals: List[str] = Field(default_factory=list)
    customer_segments: List[CustomerSegment] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    buying_behavior: List[str] = Field(default_factory=list)
    market_risks: List[str] = Field(default_factory=list)
    attractiveness: Optional[MarketAttractiveness] = None
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class CompetitorRecord(BaseModel):
    """Detailed profile of an identified competitor or alternative."""
    name: str = Field(..., description="Company or product name")
    classification: str = Field(..., description="direct, indirect, or emerging")
    core_offering: str = Field(..., description="Summary of core value proposition")
    target_customer: str = Field(..., description="Primary customer vertical")
    major_features: List[str] = Field(default_factory=list)
    pricing: str = Field(default="unavailable", description="Pricing tier or structure if disclosed in research")
    business_model: str = Field(default="unavailable", description="Revenue model (e.g. B2B SaaS, Transactional)")
    positioning: str = Field(..., description="Market positioning stance")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    customer_complaints: List[str] = Field(default_factory=list, description="Empirical complaints or review frustrations")


class ComparisonMatrixRow(BaseModel):
    """Row in the multidimensional competitor comparison matrix."""
    feature_or_dimension: str = Field(..., description="Evaluation capability or parameter")
    startup_approach: str = Field(..., description="How the proposed startup addresses this dimension")
    competitor_approaches: Dict[str, str] = Field(default_factory=dict, description="Mapping of competitor name to their approach")


class CompetitorAnalysisResult(BaseModel):
    """Comprehensive output from the Competitor Discovery & Comparison Agent."""
    competitors: List[CompetitorRecord] = Field(default_factory=list)
    comparison_matrix: List[ComparisonMatrixRow] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)
    pricing_insights: List[str] = Field(default_factory=list)
    business_models: List[str] = Field(default_factory=list)


class WhiteSpaceOpportunity(BaseModel):
    """Traceable, evidence-backed market white space opportunity."""
    opportunity_name: str = Field(..., description="Actionable title of the identified opportunity gap")
    segment: str = Field(..., description="Underserved customer segment")
    pain_point: str = Field(..., description="Acute unaddressed customer pain point")
    demand_evidence: List[str] = Field(default_factory=list, description="Supporting empirical evidence quotes/signals")
    competitor_coverage: List[str] = Field(default_factory=list, description="Current competitor behavior and omissions")
    gap: str = Field(..., description="Clear structural gap left open in the market")
    startup_fit: str = Field(..., description="Why the startup concept is structurally suited to conquer this gap")
    differentiation_hypothesis: str = Field(..., description="Strategic hypothesis for sustainable differentiation")
    evidence_strength: str = Field(default="High", description="Evidence backing tier: High, Medium, or Low")
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)
    potential_risk: Optional[str] = Field(default=None, description="Key execution or market hazard to monitor")
    evidence: List[str] = Field(default_factory=list, description="Traceable source URLs and citations")


class WhiteSpaceAnalysisResult(BaseModel):
    """Aggregated output from the Evidence-Backed Market White-Space Engine."""
    opportunities: List[WhiteSpaceOpportunity] = Field(default_factory=list)


class ValidationResponse(BaseModel):
    """Full unified validation response combining Milestone 1 evidence and Milestone 2 intelligence."""
    idea: str
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Structured extraction output from LLM.")
    sources: List[SourceRecord] = Field(default_factory=list, description="Sanitized and verified search evidence.")
    market_analysis: Optional[MarketAnalysisResult] = Field(default=None, description="Market opportunity & segmentation.")
    competitor_analysis: Optional[CompetitorAnalysisResult] = Field(default=None, description="Competitor discovery & comparison.")
    white_space_analysis: Optional[WhiteSpaceAnalysisResult] = Field(default=None, description="Evidence-backed white-space map.")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Source counts and category summaries.")
