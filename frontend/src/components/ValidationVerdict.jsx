/**
 * ValidationVerdict Component
 * Editorial executive report presenting the idea validation score, verdict badge,
 * dimension breakdowns, market strengths, critical risks, and actionable recommendations.
 */
export default function ValidationVerdict({ validation }) {
  if (!validation || !validation.overall_score) return null;

  const {
    overall_score,
    verdict_badge,
    verdict_badge_class,
    verdict_title,
    executive_summary,
    dimensions = {},
    strengths = [],
    risks = [],
    recommendations = [],
  } = validation;

  return (
    <section className="validation-verdict-section">
      {/* 1. Main Executive Verdict Card */}
      <div className="verdict-card">
        <div className="verdict-header">
          <div className="verdict-score-block">
            <span className="verdict-score-num">{overall_score}</span>
            <span className="verdict-score-denom">/100</span>
            <span className="verdict-score-label">VIABILITY SCORE</span>
          </div>

          <div className="verdict-title-block">
            <span className={`verdict-badge ${verdict_badge_class}`}>
              {verdict_badge}
            </span>
            <h2 className="verdict-heading">{verdict_title}</h2>
            <p className="verdict-summary-text">{executive_summary}</p>
          </div>
        </div>

        {/* 2. Four Dimension Progress Bars */}
        {Object.keys(dimensions).length > 0 && (
          <div className="dimensions-grid">
            {Object.entries(dimensions).map(([key, dim]) => (
              <div key={key} className="dimension-item">
                <div className="dim-header">
                  <span className="dim-label">{dim.label}</span>
                  <span className="dim-status">{dim.status} ({dim.score}%)</span>
                </div>
                <div className="dim-bar-track">
                  <div
                    className="dim-bar-fill"
                    style={{ width: `${dim.score}%` }}
                  />
                </div>
                <p className="dim-detail">{dim.detail}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Strengths vs Risks Side-by-Side Grid */}
      <div className="strategic-grid">
        {strengths.length > 0 && (
          <div className="strategic-card card-strengths">
            <div className="strategic-header">
              <span className="strategic-icon">✓</span>
              <h3 className="strategic-title">MARKET STRENGTHS & TAILWINDS</h3>
            </div>
            <ul className="strategic-list">
              {strengths.map((item, idx) => (
                <li key={idx} className="strategic-item">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {risks.length > 0 && (
          <div className="strategic-card card-risks">
            <div className="strategic-header">
              <span className="strategic-icon">!</span>
              <h3 className="strategic-title">CRITICAL RISKS & HURDLES</h3>
            </div>
            <ul className="strategic-list">
              {risks.map((item, idx) => (
                <li key={idx} className="strategic-item">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 4. Actionable Founder Next Steps */}
      {recommendations.length > 0 && (
        <div className="recommendations-card">
          <div className="recommendations-header">
            <h3 className="recommendations-title">RECOMMENDED FOUNDER ACTION PLAN</h3>
            <span className="recommendations-sub">Prioritized next steps before building full product</span>
          </div>
          <div className="recommendations-grid">
            {recommendations.map((step, idx) => (
              <div key={idx} className="rec-step-item">
                <span className="rec-step-num">0{idx + 1}</span>
                <p className="rec-step-text">{step}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
