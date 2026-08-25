import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "https://team-forge-backend-production.onrender.com";


function Stamp({ score }) {
  const pct = Math.round((score || 0) * 100);
  return (
    <div className="stamp" aria-hidden="true">
      <svg viewBox="0 0 64 64" width="52" height="52">
        <circle cx="32" cy="32" r="29" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="32" cy="32" r="24" fill="none" stroke="currentColor" strokeWidth="0.75" strokeDasharray="2 3" />
        <text x="32" y="29" textAnchor="middle" fontSize="14" fontFamily="IBM Plex Mono" fill="currentColor">
          {pct}
        </text>
        <text x="32" y="41" textAnchor="middle" fontSize="6" letterSpacing="1" fontFamily="IBM Plex Mono" fill="currentColor">
          MATCH
        </text>
      </svg>
    </div>
  );
}

function SourceCard({ source, index }) {
  return (
    <li className="source-card">
      <Stamp score={source.score} />
      <div className="source-body">
        <p className="source-eyebrow">{source.query}</p>
        <a className="source-title" href={source.url} target="_blank" rel="noreferrer">
          {source.title}
        </a>
        <p className="source-snippet">{source.snippet}</p>
        <p className="source-url">{source.url}</p>
      </div>
    </li>
  );
}

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
      <header className="masthead">
        <p className="masthead-label">TEAM FORGE — MILESTONE 01</p>
        <h1 className="masthead-title">Startup Idea Validator</h1>
        <p className="masthead-sub">
          Submit a concept. The Web Search Agent and Data Retrieval Agent pull
          live market sources so you can see what's already out there before
          you build.
        </p>
      </header>

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
            <div className="results-summary">
              <span>
                <strong>{result.summary.total_sources}</strong> sources found
              </span>
              <span className="divider">·</span>
              {Object.entries(result.summary.sources_per_query).map(([q, count]) => (
                <span key={q} className="query-chip">
                  {q} ({count})
                </span>
              ))}
            </div>

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
