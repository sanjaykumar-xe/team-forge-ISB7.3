import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import ResultsSummary from "./components/ResultsSummary";
import CategorySection from "./components/CategorySection";
import ExtractedMetadata from "./components/ExtractedMetadata";
const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

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
    if (idea.trim().length < 20) {
      setErrorMessage("Please describe your startup idea in more detail (at least 20 characters) so we can extract accurate market signals.");
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
      setErrorMessage(err.message || "Something went wrong. Try again.");
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
        <form className="submission-form" onSubmit={handleSubmit}>
          <div className="form-field main-idea-field">
            <label htmlFor="idea" className="field-label">
              DESCRIBE THE IDEA <span className="label-required">*</span>
            </label>
            <textarea
              id="idea"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="e.g. A subscription box that delivers pre-portioned spices for weeknight recipes, sourced directly from small farms."
              rows={4}
              maxLength={1000}
            />
            <div className="form-meta-row">
              <span className="char-count">{idea.length} {idea.length === 1 ? "character" : "characters"}</span>
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
                placeholder="e.g. SpiceBox, StudyPilot"
              />
            </div>

            <div className="form-field">
              <label htmlFor="industry" className="field-label">
                INDUSTRY OR CATEGORY <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                type="text"
                id="industry"
                list="industry-options"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. EdTech / AI, Transportation"
              />
              <p className="field-hint">
                Adding a specific category like &quot;MusicTech&quot; or &quot;EdTech&quot; significantly improves search accuracy.
              </p>
              <datalist id="industry-options">
                <option value="EdTech / AI" />
                <option value="Food & Beverage" />
                <option value="Transportation & Mobility" />
                <option value="Healthcare & HealthTech" />
                <option value="Fintech & Financial Services" />
                <option value="Artificial Intelligence & SaaS" />
                <option value="E-Commerce & Retail" />
                <option value="CleanTech & Sustainability" />
                <option value="Real Estate & PropTech" />
                <option value="Logistics & Supply Chain" />
                <option value="Developer Tools & DevOps" />
                <option value="Media & Entertainment" />
              </datalist>
            </div>

            <div className="form-field form-field-full">
              <label htmlFor="targetAudience" className="field-label">
                TARGET AUDIENCE <span className="label-optional">(OPTIONAL)</span>
              </label>
              <input
                type="text"
                id="targetAudience"
                list="audience-options"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g. School and college students, Busy home cooks"
              />
              <datalist id="audience-options">
                <option value="School and college students" />
                <option value="Home cooks & busy families" />
                <option value="Urban commuters & transit riders" />
                <option value="Small business owners & founders" />
                <option value="Software developers & engineering teams" />
                <option value="Remote workers & freelancers" />
                <option value="Healthcare professionals & clinics" />
                <option value="E-commerce shoppers & consumers" />
              </datalist>
            </div>
          </div>

          <div className="form-action-row">
            <button type="submit" disabled={status === "loading"}>
              {status === "loading" ? "Analyzing & Validating…" : "Validate idea →"}
            </button>
          </div>
        </form>

        {status === "error" && <p className="error-banner">{errorMessage}</p>}

        {status === "loading" && (
          <div className="loading-container">
            <p className="loading-eyebrow">SYNTHESIZING MARKET INTELLIGENCE…</p>
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
            {/* Extracted LLM Understanding */}
            {result.extracted_data && <ExtractedMetadata data={result.extracted_data} />}

            {/* 1. Sources Summary Bar */}
            <div className="evidence-header-divider">
              <span className="evidence-divider-label">SUPPORTING MARKET EVIDENCE & SIGNALS</span>
            </div>

            <ResultsSummary summary={result.summary} sources={result.sources} />

            {result.sources.length === 0 ? (
              <p className="empty-state">
                {result.summary?.message ||
                  "No sources came back for this idea. Try rephrasing with a more specific product category, market segment, or customer workflow."}
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
