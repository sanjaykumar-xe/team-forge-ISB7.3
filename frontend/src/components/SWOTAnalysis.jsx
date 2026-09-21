import React from "react";

export default function SWOTAnalysis({ data }) {
  if (!data) return null;
  const {
    strengths = [],
    weaknesses = [],
    opportunities = [],
    threats = [],
    risk_assessment = [],
    strategic_recommendation = "",
    analysis_status,
    message,
  } = data;

  if (analysis_status === "processing_error" && !strategic_recommendation) {
    return (
      <div id="section-swot" className="swot-analysis-section">
        <div className="section-masthead">
          <div className="section-eyebrow-row">
            <span className="section-badge badge-amber">§ STRATEGIC SYNTHESIS</span>
            <span className="section-meta-tag">[PROCESSING NOTICE]</span>
          </div>
          <h3 className="section-headline">Strategic SWOT & Risk Analysis</h3>
          <p className="insufficient-data-text">⚠️ {message || "SWOT analysis could not be completed."}</p>
        </div>
      </div>
    );
  }

  const renderItems = (items, fallbackText) => {
    if (!items || items.length === 0) {
      return <p className="swot-empty">{fallbackText}</p>;
    }
    return (
      <ul className="swot-item-list">
        {items.map((item, idx) => {
          const text = typeof item === "string" ? item : item.item || item.description || JSON.stringify(item);
          const evidence = typeof item === "object" ? item.evidence : null;
          const conf = typeof item === "object" ? (item.confidence || "").toLowerCase() : null;
          return (
            <li key={idx} className="swot-item">
              <div className="swot-item-header">
                <span className="swot-item-text">{text}</span>
                {conf && <span className={`swot-conf-badge conf-${conf}`}>{conf.toUpperCase()}</span>}
              </div>
              {evidence && (
                <div className="swot-item-evidence">
                  <span className="evidence-cite-label">EVIDENCE:</span> {evidence}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <div id="section-swot" className="swot-analysis-section">
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-amber">§ STRATEGIC SYNTHESIS</span>
          <span className="section-meta-tag">[MILESTONE 3 — SWOT & RISKS]</span>
        </div>
        <h3 className="section-headline">Strategic SWOT & Risk Analysis</h3>
        <p className="section-summary-text">
          Judgment-driven synthesis elevating only high-conviction findings across market, competitor, and white-space evidence.
        </p>
      </div>

      {strategic_recommendation && (
        <div className="swot-verdict-card">
          <div className="verdict-badge-row">
            <span className="verdict-label">EXECUTIVE STRATEGIC VERDICT</span>
          </div>
          <p className="verdict-text">{strategic_recommendation}</p>
        </div>
      )}

      <div className="swot-matrix-grid">
        <div className="swot-quadrant quadrant-strengths">
          <div className="quadrant-header">
            <span className="quadrant-letter">S</span>
            <span className="quadrant-title">STRENGTHS & MOATS</span>
          </div>
          {renderItems(strengths, "No unique internal strengths verified from current evidence.")}
        </div>

        <div className="swot-quadrant quadrant-weaknesses">
          <div className="quadrant-header">
            <span className="quadrant-letter">W</span>
            <span className="quadrant-title">VULNERABILITIES & GAPS</span>
          </div>
          {renderItems(weaknesses, "No acute internal vulnerabilities identified.")}
        </div>

        <div className="swot-quadrant quadrant-opportunities">
          <div className="quadrant-header">
            <span className="quadrant-letter">O</span>
            <span className="quadrant-title">MARKET OPPORTUNITIES</span>
          </div>
          {renderItems(opportunities, "No verified expansion opportunities detected.")}
        </div>

        <div className="swot-quadrant quadrant-threats">
          <div className="quadrant-header">
            <span className="quadrant-letter">T</span>
            <span className="quadrant-title">EXTERNAL THREATS</span>
          </div>
          {renderItems(threats, "No critical external threats observed.")}
        </div>
      </div>

      {risk_assessment && risk_assessment.length > 0 && (
        <div className="swot-risks-container">
          <h4 className="sub-section-title">TOP STRATEGIC RISKS & MITIGATION ROADMAP</h4>
          <div className="risks-grid">
            {risk_assessment.map((r, i) => {
              const riskDesc = typeof r === "string" ? r : r.risk || JSON.stringify(r);
              const severity = typeof r === "object" ? (r.severity || "medium").toLowerCase() : "medium";
              const mitigation = typeof r === "object" ? r.mitigation : null;
              return (
                <div key={i} className="risk-card">
                  <div className="risk-header">
                    <span className={`risk-severity-badge severity-${severity}`}>{severity.toUpperCase()} SEVERITY</span>
                    <span className="risk-num">RISK 0{i + 1}</span>
                  </div>
                  <p className="risk-description">{riskDesc}</p>
                  {mitigation && (
                    <div className="risk-mitigation">
                      <span className="mitigation-label">MITIGATION:</span> {mitigation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
