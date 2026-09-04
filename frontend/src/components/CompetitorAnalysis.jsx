import React from "react";

/**
 * CompetitorAnalysis Component
 * Displays direct, indirect, and emerging competitor profiles, pricing transparency,
 * customer complaints, multidimensional comparison matrix, and market gap vectors.
 */
export default function CompetitorAnalysis({ data }) {
  if (!data) return null;

  const {
    competitors = [],
    comparison_matrix = [],
    market_gaps = [],
    pricing_insights = [],
    business_models = [],
  } = data;

  const getClassificationBadge = (cls = "") => {
    const lower = cls.toLowerCase();
    if (lower === "direct") return { label: "DIRECT RIVAL", className: "tag-rose" };
    if (lower === "indirect") return { label: "INDIRECT ALTERNATIVE", className: "tag-blue" };
    if (lower === "emerging") return { label: "EMERGING ENTRANT", className: "tag-green" };
    return { label: cls.toUpperCase() || "COMPETITOR", className: "tag-default" };
  };

  return (
    <div className="competitor-analysis-section">
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-green">§ COMPETITIVE LANDSCAPE & MATRIX</span>
          <span className="section-count">{competitors.length} Competitors Surfaced</span>
        </div>
        <h3 className="section-headline">Direct Rivals, Substitute Alternatives & Market Gaps</h3>
      </div>

      {/* Competitor Profile Cards */}
      <div className="competitors-grid">
        {competitors.map((comp, idx) => {
          const badge = getClassificationBadge(comp.classification);
          return (
            <div key={idx} className="competitor-card">
              <div className="competitor-card-top">
                <span className={`source-tag ${badge.className}`}>{badge.label}</span>
                <h4 className="competitor-name">{comp.name}</h4>
                <p className="competitor-offering">{comp.core_offering}</p>
              </div>

              <div className="competitor-meta-grid">
                <div className="meta-item">
                  <span className="meta-label">TARGET AUDIENCE</span>
                  <span className="meta-val">{comp.target_customer || "General Market"}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">PRICING STRUCTURE</span>
                  <span className="meta-val">{comp.pricing || "Not disclosed in sources"}</span>
                </div>
                <div className="meta-item full-span">
                  <span className="meta-label">BUSINESS MODEL</span>
                  <span className="meta-val">{comp.business_model || "Not disclosed"}</span>
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="competitor-pro-con-grid">
                {Array.isArray(comp.strengths) && comp.strengths.length > 0 && (
                  <div className="pro-con-block">
                    <span className="pro-label">KEY STRENGTHS</span>
                    <ul className="pro-con-list">
                      {comp.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {Array.isArray(comp.weaknesses) && comp.weaknesses.length > 0 && (
                  <div className="pro-con-block">
                    <span className="con-label">WEAKNESSES & OMISSIONS</span>
                    <ul className="pro-con-list con-list">
                      {comp.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Customer Complaints */}
              {Array.isArray(comp.customer_complaints) && comp.customer_complaints.length > 0 && (
                <div className="complaints-block">
                  <span className="complaints-label">DOCUMENTED USER FRUSTRATIONS</span>
                  <ul className="complaints-list">
                    {comp.customer_complaints.map((c, i) => (
                      <li key={i}>&ldquo;{c}&rdquo;</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Multidimensional Comparison Matrix */}
      {comparison_matrix.length > 0 && (
        <div className="comparison-matrix-container">
          <div className="matrix-header-bar">
            <h4 className="matrix-title">Strategic Feature & Capability Comparison Matrix</h4>
            <span className="matrix-caption">Startup Approach vs Incumbent Solutions</span>
          </div>

          <div className="table-responsive-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th className="th-dimension">CAPABILITY / DIMENSION</th>
                  <th className="th-startup">PROPOSED STARTUP APPROACH</th>
                  {competitors.slice(0, 3).map((c, i) => (
                    <th key={i} className="th-competitor">{c.name.toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {comparison_matrix.map((row, rIdx) => (
                  <tr key={rIdx}>
                    <td className="td-dimension">{row.feature_or_dimension}</td>
                    <td className="td-startup">
                      <span className="startup-highlight-badge">INNOVATION</span>
                      {row.startup_approach}
                    </td>
                    {competitors.slice(0, 3).map((c, cIdx) => (
                      <td key={cIdx} className="td-competitor">
                        {row.competitor_approaches?.[c.name] ||
                          row.competitor_approaches?.[c.name.toLowerCase()] ||
                          "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Market Gaps & Business Models */}
      <div className="gaps-summary-grid">
        {market_gaps.length > 0 && (
          <div className="gap-panel">
            <h4 className="subpanel-title">Identified Market Gaps</h4>
            <ul className="editorial-bullet-list">
              {market_gaps.map((gap, i) => (
                <li key={i}>{gap}</li>
              ))}
            </ul>
          </div>
        )}

        {pricing_insights.length > 0 && (
          <div className="gap-panel">
            <h4 className="subpanel-title">Pricing & Monetization Voids</h4>
            <ul className="editorial-bullet-list">
              {pricing_insights.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
