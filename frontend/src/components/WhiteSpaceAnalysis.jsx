import React from "react";

/**
 * WhiteSpaceAnalysis Component
 * Centerpiece: "Evidence-Backed Market White-Space Map"
 * Triangulates: Customer Pain → Competitor Void → Market Gap → Startup Advantage
 */
export default function WhiteSpaceAnalysis({ data }) {
  if (!data || !Array.isArray(data.opportunities) || data.opportunities.length === 0) {
    if (data && data.analysis_status === "processing_error") {
      return (
        <div id="section-whitespace" className="whitespace-engine-section">
          <div className="section-masthead whitespace-masthead">
            <div className="section-eyebrow-row">
              <span className="section-badge badge-amber">§ MARKET WHITE-SPACE</span>
              <span className="section-meta-tag">[PROCESSING ERROR]</span>
            </div>
            <h3 className="section-headline whitespace-headline">
              Evidence-Backed Market White-Space Map
            </h3>
            <div className="empty-category-notice" style={{ marginTop: "1rem" }}>
              <p className="insufficient-data-text">
                ⚠️ {data.message || "White-space opportunity synthesis could not be completed due to a temporary processing error. Please retry your validation request."}
              </p>
            </div>
          </div>
        </div>
      );
    }
    return null;
  }

  const { opportunities } = data;

  return (
    <div id="section-whitespace" className="whitespace-engine-section">
      {/* Editorial Header */}
      <div className="section-masthead whitespace-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-amber">§ MARKET WHITE-SPACE</span>
          <span className="section-meta-tag">[EMPIRICAL TRIANGULATION MAP]</span>
        </div>
        <h3 className="section-headline whitespace-headline">
          Evidence-Backed Market White-Space Map
        </h3>
        <p className="section-summary-text">
          High-conviction market gaps triangulated by cross-referencing verified customer pain points,
          competitor omissions, and defensible startup capabilities.
        </p>

        {/* Visual Strategy Flow Diagram */}
        <div className="whitespace-pipeline-flow">
          <div className="flow-step">
            <span className="flow-num">01</span>
            <span className="flow-label">CUSTOMER PAIN</span>
            <span className="flow-desc">Verified Demand</span>
          </div>
          <div className="flow-arrow">&rarr;</div>

          <div className="flow-step">
            <span className="flow-num">02</span>
            <span className="flow-label">COMPETITOR VOID</span>
            <span className="flow-desc">Incumbent Omissions</span>
          </div>
          <div className="flow-arrow">&rarr;</div>

          <div className="flow-step">
            <span className="flow-num">03</span>
            <span className="flow-label">MARKET GAP</span>
            <span className="flow-desc">Unaddressed Need</span>
          </div>
          <div className="flow-arrow">&rarr;</div>

          <div className="flow-step highlight-step">
            <span className="flow-num">04</span>
            <span className="flow-label">STARTUP ADVANTAGE</span>
            <span className="flow-desc">Defensible Solution</span>
          </div>
        </div>
      </div>

      {/* Opportunity Cards List */}
      <div className="whitespace-cards-list">
        {opportunities.map((opp, idx) => {
          const hasConfidence = typeof opp.confidence === "number" && !isNaN(opp.confidence);
          const confidencePct = hasConfidence ? Math.round(opp.confidence * 100) : null;
          const strengthLower = (opp.evidence_strength || "low").toLowerCase();

          return (
            <div key={idx} className="whitespace-card">
              {/* Card Header Bar */}
              <div className="whitespace-card-header">
                <div className="opp-title-group">
                  <span className="opp-index">OPPORTUNITY 0{idx + 1}</span>
                  <h4 className="opp-title">{opp.opportunity_name}</h4>
                </div>
                <div className="opp-meta-badges">
                  <span className={`strength-badge strength-${strengthLower}`}>
                    Evidence: {opp.evidence_strength || "Low"}
                  </span>
                  <span className="confidence-meter-badge">
                    {hasConfidence ? `${confidencePct}% Conviction` : "Preliminary Hypothesis"}
                  </span>
                </div>
              </div>

              {/* Target Segment Tag */}
              {opp.segment && (
                <div className="opp-segment-banner">
                  <span className="segment-banner-label">TARGET SEGMENT:</span>
                  <span className="segment-banner-name">{opp.segment}</span>
                </div>
              )}

              {/* 4-Vector Evidence Flow Grid */}
              <div className="opp-flow-chain-grid">
                {/* 1. Customer Pain */}
                <div className="flow-chain-node node-pain">
                  <div className="node-header">
                    <span className="node-step-tag">VECTOR 1</span>
                    <span className="node-title">CUSTOMER PAIN</span>
                  </div>
                  <p className="node-body">{opp.pain_point}</p>
                  {Array.isArray(opp.demand_evidence) && opp.demand_evidence.length > 0 && (
                    <div className="node-evidence-sub">
                      <span className="evidence-sub-label">Demand Signals:</span>
                      <ul className="node-bullet-list">
                        {opp.demand_evidence.map((sig, sIdx) => (
                          <li key={sIdx}>&ldquo;{sig}&rdquo;</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* 2. Competitor Omissions */}
                <div className="flow-chain-node node-competitor">
                  <div className="node-header">
                    <span className="node-step-tag">VECTOR 2</span>
                    <span className="node-title">COMPETITOR OMISSIONS</span>
                  </div>
                  {Array.isArray(opp.competitor_coverage) && opp.competitor_coverage.length > 0 && (
                    <ul className="node-bullet-list comp-bullets">
                      {opp.competitor_coverage.map((comp, cIdx) => (
                        <li key={cIdx}>{comp}</li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* 3. Structural Market Gap */}
                <div className="flow-chain-node node-gap">
                  <div className="node-header">
                    <span className="node-step-tag">VECTOR 3</span>
                    <span className="node-title">DISCOVERED MARKET GAP</span>
                  </div>
                  <p className="node-body gap-text">{opp.gap}</p>
                </div>

                {/* 4. Startup Advantage */}
                <div className="flow-chain-node node-fit">
                  <div className="node-header">
                    <span className="node-step-tag">VECTOR 4</span>
                    <span className="node-title">STARTUP FIT & SOLUTION</span>
                  </div>
                  <p className="node-body fit-text">{opp.startup_fit}</p>
                </div>
              </div>

              {/* Differentiation Hypothesis Callout Box */}
              {opp.differentiation_hypothesis && (
                <div className="hypothesis-box">
                  <div className="hypothesis-header">
                    <span className="hypothesis-icon">◆</span>
                    <span className="hypothesis-label">DIFFERENTIATION & MOAT HYPOTHESIS</span>
                  </div>
                  <p className="hypothesis-body">{opp.differentiation_hypothesis}</p>
                </div>
              )}

              {/* Card Footer: Evidence Traceability & Risk */}
              {(opp.potential_risk || (Array.isArray(opp.evidence) && opp.evidence.length > 0)) && (
                <div className="whitespace-card-footer">
                  {opp.potential_risk && (
                    <div className="risk-callout">
                      <span className="risk-label">KEY RISK FACTOR:</span>
                      <span className="risk-text">{opp.potential_risk}</span>
                    </div>
                  )}

                  {Array.isArray(opp.evidence) && opp.evidence.length > 0 && (
                    <div className="citations-row">
                      <span className="citations-label">SUPPORTING SOURCES:</span>
                      <div className="citations-links">
                        {opp.evidence.map((url, uIdx) => (
                          <a
                            key={uIdx}
                            href={url}
                            target="_blank"
                            rel="noreferrer noopener"
                            className="citation-chip-link"
                          >
                            Source [{uIdx + 1}] &rarr;
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
