import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import SourceCard from "./components/SourceCard";
import ResultsSummary from "./components/ResultsSummary";

const API_URL =
  import.meta.env.VITE_API_URL || "https://team-forge-backend-production.onrender.com";

export default function App() {
  const [idea, setIdea] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");



  async function handleSubmit(e) {
    e.preventDefault();
    if (idea.trim().length < 10) {
      setErrorMessage("Describe the idea in a bit more detail (10+ characters).");
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
        body: JSON.stringify({ idea }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const data = await res.json();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err.message || "Something went wrong. Try again.");
      setStatus("error");
    }
  }

  return (
    <div className="page">
      <Header />

      <main className="dossier">
        <form className="submission-form" onSubmit={handleSubmit}>
          <label htmlFor="idea" className="field-label">
            DESCRIBE THE IDEA
          </label>
          <textarea
            id="idea"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="e.g. A subscription box that delivers pre-portioned spices for weeknight recipes, sourced directly from small farms."
            rows={4}
          />
          <div className="form-row">
            <span className="char-count">{idea.length}/1000</span>
            <button type="submit" disabled={status === "loading"}>
              {status === "loading" ? "Surveying…" : "Validate idea →"}
            </button>
          </div>
        </form>

        {status === "error" && <p className="error-banner">{errorMessage}</p>}

        {status === "loading" && (
          <div className="loading-container">
            <p className="loading-eyebrow">SCOUTING CURRENT MARKET TERRITORY…</p>
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
            <ResultsSummary summary={result.summary} sources={result.sources} />

            {result.sources.length === 0 ? (
              <p className="empty-state">
                No sources came back for this idea. Try rephrasing with a more
                specific product category, market segment, or customer workflow.
              </p>
            ) : (
              <ul className="source-list">
                {result.sources.map((source) => (
                  <SourceCard key={source.url} source={source} />
                ))}
              </ul>
            )}
          </section>
        )}
      </main>

      <footer className="footer-note">
        <span>MILESTONE 1 — WEB SEARCH API INTEGRATED</span>
        <span className="footer-divider"></span>
        <span>MILESTONE 2 ADDS MARKET OPPORTUNITY, COMPETITORS, AND SWOT</span>
      </footer>
    </div>
  );
}

