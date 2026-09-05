import { useState, useEffect } from "react";
import "./App.css";
import Header from "./components/Header";
import ExtractedMetadata from "./components/ExtractedMetadata";
import ResultsSummary from "./components/ResultsSummary";
import CategorySection from "./components/CategorySection";
import MarketOpportunity from "./components/MarketOpportunity";
import CustomerSegments from "./components/CustomerSegments";
import CompetitorAnalysis from "./components/CompetitorAnalysis";
import WhiteSpaceAnalysis from "./components/WhiteSpaceAnalysis";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const CATEGORIES = [
  { key: "Competitors", title: "COMPETITORS" },
  { key: "Industry News", title: "INDUSTRY NEWS" },
  { key: "Customer Demand", title: "CUSTOMER DEMAND" },
  { key: "Market Size & Trends", title: "MARKET SIZE & TRENDS" },
];

const RESEARCH_STAGES = [
  { id: 1, label: "Extracting idea parameters & domain keywords" },
  { id: 2, label: "Executing multi-vector live web research" },
  { id: 3, label: "Synthesizing customer demand & market sizing" },
  { id: 4, label: "Triangulating defensible market white-space" },
];

export default function App() {
  const [idea, setIdea] = useState("");
  const [productName, setProductName] = useState("");
  const [industry, setIndustry] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeStage, setActiveStage] = useState(1);

  // Animate research stages during loading state
  useEffect(() => {
    if (status !== "loading") {
      setActiveStage(1);
      return;
    }

    const stageInterval = setInterval(() => {
      setActiveStage((prev) => (prev < RESEARCH_STAGES.length ? prev + 1 : prev));
    }, 2800);

    return () => clearInterval(stageInterval);
  }, [status]);

  function handleClearForm() {
    setIdea("");
    setProductName("");
    setIndustry("");
    setTargetAudience("");
    setErrorMessage("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (idea.trim().length < 15) {
      setErrorMessage(
        "Please describe your startup idea in a bit more detail (at least 15 characters) so we can extract accurate domain context and market signals."
      );
      setStatus("error");
      return;
    }

    setStatus("loading");
    setErrorMessage("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/api/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea,
          product_name: productName.trim() || undefined,
          industry: industry.trim() || undefined,
          target_audience: targetAudience.trim() || undefined,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        let msg = "Request failed";
        if (typeof body.detail === "string") {
          msg = body.detail;
        } else if (Array.isArray(body.detail)) {
          msg = body.detail.map((err) => err.msg || JSON.stringify(err)).join(", ");
        } else if (body.detail && typeof body.detail === "object") {
          msg = body.detail.msg || JSON.stringify(body.detail);
        } else if (body.message) {
          msg = body.message;
        } else {
          msg = `Request failed (${res.status})`;
        }
        throw new Error(msg);
      }

      const data = await res.json();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err.message || "Something went wrong during market analysis. Please check your backend connection and try again.");
      setStatus("error");
    }
  }

  // Group sources by category for rendering
  const sourcesByCategory = result?.summary?.sources_by_category || {};
  if (result?.sources && Object.keys(sourcesByCategory).length === 0) {
    for (const cat of CATEGORIES) {
      sourcesByCategory[cat.key] = [];
    }
    for (const s of result.sources) {
      const catKey = s.category || "Industry News";
      if (!sourcesByCategory[catKey]) sourcesByCategory[catKey] = [];
      sourcesByCategory[catKey].push(s);
    }
  }

  const competitorCount = result?.competitor_analysis?.competitors?.length || 0;
  const segmentCount = result?.market_analysis?.customer_segments?.length || 0;
  const opportunityCount = result?.white_space_analysis?.opportunities?.length || 0;
  const hasFormContent = Boolean(idea || productName || industry || targetAudience);

  return (
    <div className="page">
      <Header />

      <main className="dossier">
        {/* Research Input Form */}
        <form className="submission-form" onSubmit={handleSubmit}>
          <div className="form-field main-idea-field">
            <label htmlFor="idea" className="field-label">
              DESCRIBE THE STARTUP CONCEPT <span className="label-required">*</span>
            </label>
            <textarea
              id="idea"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your startup concept, target customer pain, core workflow, monetization mechanism, or key assumptions in detail."
              rows={5}
            />
            <div className="form-meta-row">
              <span className="char-count">
                {idea.length.toLocaleString()} {idea.length === 1 ? "character" : "characters"}
              </span>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="productName" className="field-label">
                STARTUP / PRODUCT NAME <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                type="text"
                id="productName"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="e.g. StudyPilot, FarmOptima, ClinicGuard"
              />
            </div>

            <div className="form-field">
              <label htmlFor="industry" className="field-label">
                INDUSTRY OR VERTICAL <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                type="text"
                id="industry"
                list="industry-options"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. HealthTech, AgriTech, FinTech, DevTools"
              />
              <datalist id="industry-options">
                <option value="Healthcare & HealthTech" />
                <option value="Agriculture & AgriTech" />
                <option value="Fintech & Financial Services" />
                <option value="EdTech & Education" />
                <option value="DevSecOps & Developer Tools" />
                <option value="CleanTech & Sustainability" />
                <option value="Logistics & Supply Chain" />
                <option value="Enterprise SaaS & Automation" />
              </datalist>
            </div>

            <div className="form-field form-field-full">
              <label htmlFor="targetAudience" className="field-label">
                TARGET CUSTOMER PROFILE <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                type="text"
                id="targetAudience"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g. Small and mid-sized clinics, Independent agronomists, University researchers"
              />
            </div>
          </div>

          <div className="form-action-row">
            {hasFormContent && (
              <button
                type="button"
                className="btn-clear-form"
                onClick={handleClearForm}
                disabled={status === "loading"}
              >
                Clear
              </button>
            )}
            <button type="submit" disabled={status === "loading"}>
              {status === "loading" ? "Analyzing market signals…" : "Validate startup idea →"}
            </button>
          </div>
        </form>

        {status === "error" && (
          <div className="error-banner" role="alert">
            <span className="error-prefix">VALIDATION NOTICE:</span> {errorMessage}
          </div>
        )}

        {/* Structured Research Loading State */}
        {status === "loading" && (
          <div className="loading-container">
            <div className="loading-status-badge">
              <span className="pulsing-dot" />
              <span className="loading-eyebrow">
                VALIDATING STARTUP CONCEPT ACROSS MARKET VECTORS…
              </span>
            </div>

            {/* Research Progress Stages */}
            <div className="research-stepper">
              {RESEARCH_STAGES.map((stg) => {
                const isDone = activeStage > stg.id;
                const isActive = activeStage === stg.id;
                return (
                  <div
                    key={stg.id}
                    className={`stepper-item ${isDone ? "step-done" : ""} ${isActive ? "step-active" : ""}`}
                  >
                    <span className="step-indicator">
                      {isDone ? "✓" : `0${stg.id}`}
                    </span>
                    <span className="step-text">{stg.label}</span>
                  </div>
                );
              })}
            </div>

            {/* Shimmering Skeleton Cards */}
            <div className="skeleton-list">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton-card">
                  <div className="skeleton-bar bar-tag" />
                  <div className="skeleton-bar bar-title" />
                  <div className="skeleton-bar bar-snippet-1" />
                  <div className="skeleton-bar bar-snippet-2" />
                  <div className="skeleton-footer">
                    <div className="skeleton-bar bar-host" />
                    <div className="skeleton-bar bar-score" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Presentation Dashboard */}
        {status === "done" && result && (
          <section className="results">
            {/* Quick-Jump Section Navigation Bar */}
            <nav className="quick-jump-nav" aria-label="Report sections">
              <span className="quick-jump-label">§ JUMP TO:</span>
              <div className="quick-jump-links">
                <a href="#section-overview" className="jump-link">Overview</a>
                <a href="#section-context" className="jump-link">Idea Context</a>
                <a href="#section-whitespace" className="jump-link highlight-jump">White-Space Map</a>
                <a href="#section-market" className="jump-link">Market Sizing</a>
                <a href="#section-personas" className="jump-link">Personas</a>
                <a href="#section-competitors" className="jump-link">Competitors</a>
                <a href="#section-sources" className="jump-link">Sources</a>
              </div>
            </nav>

            {/* Top-Level Executive Summary & Real Metrics */}
            <ResultsSummary
              summary={result.summary}
              sources={result.sources}
              competitorCount={competitorCount}
              segmentCount={segmentCount}
              opportunityCount={opportunityCount}
            />

            {/* 1. Extracted Domain Context */}
            {result.extracted_data && <ExtractedMetadata data={result.extracted_data} />}

            {/* 2. Visual Centerpiece: Evidence-Backed Market White-Space Map */}
            {result.white_space_analysis && (
              <WhiteSpaceAnalysis data={result.white_space_analysis} />
            )}

            {/* 3. Market Opportunity Sizing & Attractiveness */}
            {result.market_analysis && (
              <MarketOpportunity data={result.market_analysis} />
            )}

            {/* 4. Target Customer Segmentation */}
            {result.market_analysis?.customer_segments && (
              <CustomerSegments segments={result.market_analysis.customer_segments} />
            )}

            {/* 5. Competitor Discovery & Capability Matrix */}
            {result.competitor_analysis && (
              <CompetitorAnalysis data={result.competitor_analysis} />
            )}

            {/* 6. Supporting Research Sources */}
            <div id="section-sources" className="evidence-header-divider">
              <span className="evidence-divider-label">
                § SUPPORTING RESEARCH EVIDENCE & SOURCE CITATIONS
              </span>
            </div>

            {result.sources.length === 0 ? (
              <p className="empty-state">
                {result.summary?.message ||
                  "No search sources returned. Try refining domain keywords or category terms."}
              </p>
            ) : (
              <div className="categorized-results-container">
                {CATEGORIES.map((cat) => {
                  const sources = sourcesByCategory[cat.key] || [];
                  return (
                    <CategorySection
                      key={cat.key}
                      title={cat.title}
                      sources={sources}
                      initialLimit={3}
                    />
                  );
                })}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
