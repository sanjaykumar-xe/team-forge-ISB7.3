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
            Startup idea
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
              {status === "loading" ? "Searching…" : "Validate idea"}
            </button>
          </div>
        </form>

        {status === "error" && <p className="error-banner">{errorMessage}</p>}

        {status === "loading" && (
          <p className="loading-note">
            Running search queries across current market data — this can take
            a few seconds.
          </p>
        )}

        {status === "done" && result && (
          <section className="results">
            <ResultsSummary summary={result.summary} />


            {result.sources.length === 0 ? (
              <p className="empty-state">
                No sources came back for this idea. Try rephrasing it with a
                more specific market or product category.
              </p>
            ) : (
              <ul className="source-list">
                {result.sources.map((source, i) => (
                  <SourceCard key={source.url} source={source} index={i} />
                ))}
              </ul>
            )}
          </section>
        )}
      </main>

      <footer className="footer-note">
        Milestone 1 — Web Search API integrated · Milestone 2 adds market
        opportunity, competitor, and SWOT analysis.
      </footer>
    </div>
  );
}
