import { useState } from "react";
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

export default function App() {
  const [idea, setIdea] = useState("");
  const [productName, setProductName] = useState("");
  const [industry, setIndustry] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

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
      setErrorMessage(err.message || "Something went wrong during market analysis. Please try again.");
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

  return (
    <div className="page">
      <Header />

      <main className="dossier">
        {/* Natural Language Submission Form — Zero Upper Character Limit */}
        <form className="submission-form" onSubmit={handleSubmit}>
          <div className="form-field main-idea-field">
            <label htmlFor="idea" className="field-label">
              DESCRIBE THE STARTUP IDEA <span className="label-required">*</span>
            </label>
            <textarea
              id="idea"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Describe your startup concept in detail. You can include product workflows, target customers, data sources, or specific business mechanisms (no length limits)."
              rows={5}
            />
            <div className="form-meta-row">
              <span className="char-count">
                {idea.length.toLocaleString()} {idea.length === 1 ? "character" : "characters"} (No Limit)
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
                placeholder="e.g. HealthTech, AgriTech, FinTech / Education"
              />
              <datalist id="industry-options">
                <option value="Healthcare & HealthTech" />
                <option value="Agriculture & AgriTech" />
                <option value="Fintech & Financial Services" />
                <option value="EdTech & Education" />
                <option value="DevSecOps & Developer Tools" />
                <option value="CleanTech & Sustainability" />
                <option value="Logistics & Supply Chain" />
                <option value="Artificial Intelligence & SaaS" />
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
                placeholder="e.g. Small and mid-sized clinics, Smallholder farmers, University students"
              />
            </div>
          </div>

          <div className="form-action-row">
            <button type="submit" disabled={status === "loading"}>
              {status === "loading" ? "Orchestrating Multi-Agent Pipeline…" : "Validate startup idea →"}
            </button>
          </div>
        </form>

        {status === "error" && <p className="error-banner">{errorMessage}</p>}

        {/* Skeleton Loading State */}
        {status === "loading" && (
          <div className="loading-container">
            <div className="loading-status-badge">
              <span className="pulsing-dot" />
              <span className="loading-eyebrow">
                EXECUTING 5-AGENT CREWAI VALIDATION PIPELINE…
              </span>
            </div>
            <p className="loading-subcaption">
              Extracting domain parameters &bull; Querying 4 research vectors &bull; Sizing market &bull; Mapping competitors &bull; Triangulating white space
            </p>
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

        {/* Results Presentation */}
        {status === "done" && result && (
          <section className="results">
            {/* 1. AI Domain Extraction Dossier */}
            {result.extracted_data && <ExtractedMetadata data={result.extracted_data} />}

            {/* 2. CORE NOVELTY: Evidence-Backed Market White-Space Engine */}
            {result.white_space_analysis && (
              <WhiteSpaceAnalysis data={result.white_space_analysis} />
            )}

            {/* 3. Market Opportunity & Sizing */}
            {result.market_analysis && (
              <MarketOpportunity data={result.market_analysis} />
            )}

            {/* 4. Target Customer Segmentation */}
            {result.market_analysis?.customer_segments && (
              <CustomerSegments segments={result.market_analysis.customer_segments} />
            )}

            {/* 5. Competitor Discovery & Comparison Matrix */}
            {result.competitor_analysis && (
              <CompetitorAnalysis data={result.competitor_analysis} />
            )}

            {/* 6. Supporting Market Evidence & Source Records */}
            <div className="evidence-header-divider">
              <span className="evidence-divider-label">
                § SUPPORTING RESEARCH EVIDENCE & EMPIRICAL SOURCES
              </span>
            </div>

            <ResultsSummary summary={result.summary} sources={result.sources} />

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
