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
import SWOTAnalysis from "./components/SWOTAnalysis";
import MVPRecommendation from "./components/MVPRecommendation";
import GTMStrategy from "./components/GTMStrategy";
import StartupAdvisorChat from "./components/StartupAdvisorChat";

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
  { id: 5, label: "Synthesizing SWOT matrix & strategic risk roadmap" },
  { id: 6, label: "Scoping evidence-grounded MVP & go-to-market blueprint" },
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
  const [activeSection, setActiveSection] = useState("section-overview");

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

  useEffect(() => {
    if (status !== "done") return;

    const sectionIds = [
      "section-overview",
      "section-context",
      "section-whitespace",
      "section-market",
      "section-personas",
      "section-competitors",
      "section-swot",
      "section-mvp",
      "section-gtm",
      "section-sources",
      "section-advisor",
    ];

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const offset = 180;

      for (let i = sectionIds.length - 1; i >= 0; i--) {
        const el = document.getElementById(sectionIds[i]);
        if (el && el.offsetTop - offset <= scrollY) {
          setActiveSection(sectionIds[i]);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [status]);

  const handleJumpTo = (e, targetId) => {
    e.preventDefault();
    const el = document.getElementById(targetId);
    if (el) {
      const navOffset = 70;
      const elPosition = el.getBoundingClientRect().top + window.pageYOffset;
      window.scrollTo({
        top: elPosition - navOffset,
        behavior: "smooth",
      });
      setActiveSection(targetId);
      if (window.history?.replaceState) {
        window.history.replaceState(null, "", `#${targetId}`);
      }
    }
  };

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

    let cleanIdea = idea.trim().replace(/^(?:describe the startup concept|startup concept|idea|concept)\s*:\s*/i, "");
    let cleanProductName = productName.trim().replace(/^(?:startup\s*\/?\s*product name|product name|name)\s*:\s*/i, "");
    let cleanIndustry = industry.trim().replace(/^(?:industry or vertical|industry|vertical)\s*:\s*/i, "");
    let cleanTargetAudience = targetAudience.trim().replace(/^(?:target customer profile|target audience|target customer)\s*:\s*/i, "");

    setStatus("loading");
    setErrorMessage("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/api/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea: cleanIdea,
          product_name: cleanProductName || undefined,
          industry: cleanIndustry || undefined,
          target_audience: cleanTargetAudience || undefined,
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
                id="productName"
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="e.g. LegalMind AI"
              />
            </div>

            <div className="form-field">
              <label htmlFor="industry" className="field-label">
                INDUSTRY OR VERTICAL <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                id="industry"
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. LegalTech / Contract Automation"
              />
            </div>

            <div className="form-field">
              <label htmlFor="targetAudience" className="field-label">
                TARGET CUSTOMER PROFILE <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                id="targetAudience"
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g. In-house General Counsels at mid-market SaaS"
              />
            </div>
          </div>

          <div className="form-actions">
            {hasFormContent && (
              <button
                type="button"
                className="btn btn-secondary btn-clear"
                onClick={handleClearForm}
                disabled={status === "loading"}
              >
                Clear Form
              </button>
            )}
            <button
              type="submit"
              className="btn btn-primary"
              disabled={status === "loading" || idea.trim().length === 0}
            >
              {status === "loading" ? "Analyzing market signals…" : "Validate startup idea →"}
            </button>
          </div>
        </form>

        {status === "error" && (
          <div className="error-banner" role="alert">
            <span className="error-prefix">VALIDATION NOTICE:</span> {errorMessage}
          </div>
        )}

        {status === "loading" && (
          <div className="loading-container">
            <div className="loading-status-badge">
              <span className="pulsing-dot" />
              <span className="loading-eyebrow">
                VALIDATING STARTUP CONCEPT ACROSS 9 INTELLIGENCE STAGES…
              </span>
            </div>

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

        {status === "done" && result && (
          <section className="results">
            <nav className="quick-jump-nav" aria-label="Report sections">
              <span className="quick-jump-label">§ JUMP TO:</span>
              <div className="quick-jump-links">
                {[
                  { id: "section-overview", label: "Overview", show: true },
                  { id: "section-context", label: "Idea Context", show: Boolean(result.extracted_data) },
                  { id: "section-whitespace", label: "White-Space Map", show: Boolean(result.white_space_analysis) },
                  { id: "section-market", label: "Market Sizing", show: Boolean(result.market_analysis) },
                  { id: "section-personas", label: "Personas", show: Boolean(result.market_analysis?.customer_segments?.length) },
                  { id: "section-competitors", label: "Competitors", show: Boolean(result.competitor_analysis) },
                  { id: "section-swot", label: "SWOT & Risks", show: Boolean(result.swot_analysis) },
                  { id: "section-mvp", label: "MVP Scope", show: Boolean(result.mvp_recommendation) },
                  { id: "section-gtm", label: "GTM Strategy", show: Boolean(result.gtm_strategy) },
                  { id: "section-sources", label: "Sources", show: Boolean(result.sources && result.sources.length > 0) },
                { id: "section-advisor", label: "Advisor Chat", show: true },
                ]
                  .filter((sec) => sec.show)
                  .map((sec) => (
                    <a
                      key={sec.id}
                      href={`#${sec.id}`}
                      onClick={(e) => handleJumpTo(e, sec.id)}
                      className={`jump-link ${activeSection === sec.id ? "active-jump" : ""}`}
                    >
                      {sec.label}
                    </a>
                  ))}
              </div>
            </nav>

            <ResultsSummary
              summary={result.summary}
              sources={result.sources}
              competitorCount={competitorCount}
              segmentCount={segmentCount}
              opportunityCount={opportunityCount}
            />

            {result.extracted_data && <ExtractedMetadata data={result.extracted_data} />}

            {result.white_space_analysis && (
              <WhiteSpaceAnalysis data={result.white_space_analysis} />
            )}

            {result.market_analysis && (
              <MarketOpportunity data={result.market_analysis} />
            )}

            {result.market_analysis?.customer_segments && (
              <CustomerSegments segments={result.market_analysis.customer_segments} demandSourceCount={result.summary?.counts?.["Customer Demand"] ?? 0} />
            )}

            {result.competitor_analysis && (
              <CompetitorAnalysis data={result.competitor_analysis} />
            )}

            {result.swot_analysis && (
              <SWOTAnalysis data={result.swot_analysis} />
            )}

            {result.mvp_recommendation && (
              <MVPRecommendation data={result.mvp_recommendation} />
            )}

            {result.gtm_strategy && (
              <GTMStrategy data={result.gtm_strategy} />
            )}

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

            <StartupAdvisorChat
              ideaId={result.idea_id}
              currentView={activeSection}
              apiUrl={API_URL}
            />
          </section>
        )}
      </main>
    </div>
  );
}
