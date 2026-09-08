import React from "react";
import "./ExtractedMetadata.css";

export default function ExtractedMetadata({ data }) {
  if (!data) return null;

  return (
    <div id="section-context" className="extracted-dossier-card">
      <div className="extracted-header">
        <div className="extracted-badge-row">
          <span className="extracted-badge">§ IDEA CONTEXT</span>
          <span className="extracted-dossier-id">SECTION 01 — DOMAIN PARAMETERS</span>
        </div>
        <h3 className="extracted-title">{data.product_name || "Synthesized Concept"}</h3>
      </div>

      <div className="extracted-grid">
        <div className="extracted-item">
          <span className="extracted-label">INDUSTRY VERTICAL</span>
          <span className="extracted-value">{data.industry || "Software & Technology"}</span>
        </div>

        <div className="extracted-item">
          <span className="extracted-label">TARGET AUDIENCE</span>
          <span className="extracted-value">{data.target_audience || "General Market"}</span>
        </div>

        <div className="extracted-item full-width">
          <span className="extracted-label">CORE PROBLEM STATEMENT</span>
          <p className="extracted-problem">{data.core_problem}</p>
        </div>

        {Array.isArray(data.keywords) && data.keywords.length > 0 && (
          <div className="extracted-item full-width">
            <span className="extracted-label">RESEARCH KEYWORDS & SIGNALS</span>
            <div className="extracted-tags">
              {data.keywords.map((kw, i) => (
                <span key={i} className="keyword-chip">
                  #{kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
