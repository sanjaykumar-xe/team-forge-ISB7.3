import React from "react";

export default function MVPRecommendation({ data }) {
  if (!data) return null;
  const {
    mvp_name,
    mvp_thesis,
    core_features = [],
    nice_to_haves = [],
    technical_considerations = [],
    resource_estimate,
    success_metrics = [],
    analysis_status,
    message,
  } = data;

  if (analysis_status === "processing_error" && !mvp_thesis) {
    return (
      <div id="section-mvp" className="mvp-recommendation-section">
        <div className="section-masthead">
          <div className="section-eyebrow-row">
            <span className="section-badge badge-amber">§ PRODUCT SCOPING</span>
            <span className="section-meta-tag">[PROCESSING NOTICE]</span>
          </div>
          <h3 className="section-headline">MVP Feature Recommendation</h3>
          <p className="insufficient-data-text">⚠️ {message || "MVP recommendation could not be completed."}</p>
        </div>
      </div>
    );
  }

  return (
    <div id="section-mvp" className="mvp-recommendation-section">
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-amber">§ PRODUCT SCOPING</span>
          <span className="section-meta-tag">[MILESTONE 3 — MVP SPECIFICATION]</span>
        </div>
        <h3 className="section-headline">MVP Feature Scope & Recommendation</h3>
        <p className="section-summary-text">
          Ruthlessly prioritized initial product configuration where every feature recommendation is justified by specific upstream market evidence.
        </p>
      </div>

      {(mvp_name || mvp_thesis) && (
        <div className="mvp-thesis-card">
          <div className="thesis-header">
            <span className="thesis-badge">MVP CORE THESIS</span>
            {mvp_name && <span className="mvp-name-tag">{mvp_name}</span>}
          </div>
          <p className="thesis-text">{mvp_thesis}</p>
        </div>
      )}

      {core_features && core_features.length > 0 && (
        <div className="mvp-features-container">
          <h4 className="sub-section-title">CORE LAUNCH FEATURES (PRIORITIZED)</h4>
          <div className="features-grid">
            {core_features.map((feat, i) => {
              const name = typeof feat === "string" ? feat : feat.feature || feat.title || "Feature";
              const desc = typeof feat === "object" ? feat.description : null;
              const just = typeof feat === "object" ? feat.justification : null;
              const evidence = typeof feat === "object" ? feat.upstream_evidence : null;
              const priority = typeof feat === "object" ? (feat.priority || "P0").toUpperCase() : "P0";
              const complexity = typeof feat === "object" ? feat.complexity : null;

              return (
                <div key={i} className="feature-card">
                  <div className="feature-card-header">
                    <span className={`priority-badge priority-${priority.slice(0, 2).toLowerCase()}`}>{priority}</span>
                    {complexity && <span className="complexity-tag">COMPLEXITY: {complexity.toUpperCase()}</span>}
                  </div>
                  <h5 className="feature-title">{name}</h5>
                  {desc && <p className="feature-desc">{desc}</p>}
                  {just && (
                    <div className="feature-justification">
                      <span className="just-label">JUSTIFICATION:</span> {just}
                    </div>
                  )}
                  {evidence && (
                    <div className="feature-upstream-evidence">
                      <span className="evidence-cite-label">UPSTREAM GROUNDING:</span> {evidence}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="mvp-secondary-grid">
        {nice_to_haves && nice_to_haves.length > 0 && (
          <div className="secondary-card">
            <h4 className="secondary-title">NICE-TO-HAVES / DEFERRED FEATURES</h4>
            <ul className="secondary-list">
              {nice_to_haves.map((item, idx) => {
                const text = typeof item === "string" ? item : item.feature || item.description || JSON.stringify(item);
                const just = typeof item === "object" ? item.justification : null;
                return (
                  <li key={idx} className="secondary-item">
                    <span className="secondary-item-bullet">›</span>
                    <div>
                      <strong>{text}</strong>
                      {just && <span className="deferral-note"> — {just}</span>}
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {technical_considerations && technical_considerations.length > 0 && (
          <div className="secondary-card">
            <h4 className="secondary-title">TECHNICAL & ARCHITECTURE CONSIDERATIONS</h4>
            <ul className="secondary-list">
              {technical_considerations.map((tc, idx) => (
                <li key={idx} className="secondary-item">
                  <span className="secondary-item-bullet">›</span>
                  <span>{tc}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {(resource_estimate || (success_metrics && success_metrics.length > 0)) && (
        <div className="mvp-bottom-row">
          {resource_estimate && (
            <div className="resource-estimate-card">
              <h4 className="secondary-title">RESOURCE & TIMELINE ESTIMATE</h4>
              {typeof resource_estimate === "string" ? (
                <p className="resource-text">{resource_estimate}</p>
              ) : (
                <div className="resource-props-grid">
                  {resource_estimate.timeline && (
                    <div className="resource-prop">
                      <span className="prop-label">ESTIMATED TIMELINE</span>
                      <span className="prop-val">{resource_estimate.timeline}</span>
                    </div>
                  )}
                  {resource_estimate.team_size && (
                    <div className="resource-prop">
                      <span className="prop-label">TEAM COMPOSITION</span>
                      <span className="prop-val">{resource_estimate.team_size}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {success_metrics && success_metrics.length > 0 && (
            <div className="success-metrics-card">
              <h4 className="secondary-title">VALIDATION METRICS & KPIS</h4>
              <ul className="metrics-list">
                {success_metrics.map((m, idx) => (
                  <li key={idx} className="metric-item">
                    <span className="metric-check">✓</span>
                    <span>{m}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
