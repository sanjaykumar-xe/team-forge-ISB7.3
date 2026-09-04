import React from "react";

/**
 * MarketOpportunity Component
 * Displays quantitative & qualitative market opportunity sizing, CAGR growth trends,
 * and market attractiveness scorecard with traceable source citations.
 */
export default function MarketOpportunity({ data }) {
  if (!data) return null;

  const {
    summary,
    market_size = [],
    growth_trends = [],
    demand_signals = [],
    attractiveness,
    confidence,
  } = data;

  const confidencePct = Math.round((confidence || 0.85) * 100);

  return (
    <div className="market-opportunity-section">
      {/* Header */}
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-amber">§ MARKET OPPORTUNITY & SIZING</span>
          <span className="section-confidence">Confidence: {confidencePct}%</span>
        </div>
        <h3 className="section-headline">Market Potential & Economic Dynamics</h3>
        {summary && <p className="section-summary-text">{summary}</p>}
      </div>

      {/* Market Sizing Cards */}
      {market_size.length > 0 && (
        <div className="market-size-grid">
          {market_size.map((item, idx) => (
            <div key={idx} className="market-size-card">
              <div className="market-size-header">
                <span className="market-type-pill">{item.market_type || "Market Size"}</span>
                {item.forecast_year && (
                  <span className="forecast-pill">Target {item.forecast_year}</span>
                )}
              </div>

              <div className="market-size-figure">{item.figure}</div>

              {item.cagr && (
                <div className="market-cagr-row">
                  <span className="cagr-label">GROWTH RATE (CAGR)</span>
                  <span className="cagr-value">{item.cagr}</span>
                </div>
              )}

              {item.evidence_snippet && (
                <p className="market-evidence-quote">
                  &ldquo;{item.evidence_snippet}&rdquo;
                </p>
              )}

              {item.source_url && (
                <div className="market-source-footer">
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer noopener"
                    className="market-source-link"
                  >
                    View Cited Source &rarr;
                  </a>
                </div>
              )}

              {item.notes && !item.source_url && (
                <div className="market-notes-footer">{item.notes}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Attractiveness & Strategic Trends Grid */}
      <div className="opportunity-dual-grid">
        {/* Market Attractiveness Scorecard */}
        {attractiveness && (
          <div className="attractiveness-panel">
            <h4 className="subpanel-title">Market Attractiveness Scorecard</h4>
            <div className="scorecard-metric-grid">
              <div className="scorecard-metric">
                <span className="metric-label">DEMAND STRENGTH</span>
                <span className={`metric-badge badge-${(attractiveness.demand_strength || "medium").toLowerCase()}`}>
                  {attractiveness.demand_strength || "Medium"}
                </span>
              </div>

              <div className="scorecard-metric">
                <span className="metric-label">GROWTH STRENGTH</span>
                <span className={`metric-badge badge-${(attractiveness.growth_strength || "medium").toLowerCase()}`}>
                  {attractiveness.growth_strength || "Medium"}
                </span>
              </div>

              <div className="scorecard-metric">
                <span className="metric-label">CUSTOMER URGENCY</span>
                <span className={`metric-badge badge-${(attractiveness.customer_urgency || "medium").toLowerCase()}`}>
                  {attractiveness.customer_urgency || "Medium"}
                </span>
              </div>

              <div className="scorecard-metric">
                <span className="metric-label">ACCESSIBILITY</span>
                <span className={`metric-badge badge-${(attractiveness.market_accessibility || "medium").toLowerCase()}`}>
                  {attractiveness.market_accessibility || "Medium"}
                </span>
              </div>
            </div>

            {Array.isArray(attractiveness.major_barriers) && attractiveness.major_barriers.length > 0 && (
              <div className="scorecard-list-group">
                <span className="scorecard-subhead">ENTRY BARRIERS</span>
                <ul className="editorial-bullet-list">
                  {attractiveness.major_barriers.map((barrier, i) => (
                    <li key={i}>{barrier}</li>
                  ))}
                </ul>
              </div>
            )}

            {Array.isArray(attractiveness.important_assumptions) && attractiveness.important_assumptions.length > 0 && (
              <div className="scorecard-list-group">
                <span className="scorecard-subhead">KEY ASSUMPTIONS</span>
                <ul className="editorial-bullet-list">
                  {attractiveness.important_assumptions.map((assumption, i) => (
                    <li key={i}>{assumption}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Growth Trends & Demand Signals */}
        <div className="trends-panel">
          {growth_trends.length > 0 && (
            <div className="trend-block">
              <h4 className="subpanel-title">Macro Growth Drivers</h4>
              <ul className="editorial-bullet-list">
                {growth_trends.map((trend, i) => (
                  <li key={i}>{trend}</li>
                ))}
              </ul>
            </div>
          )}

          {demand_signals.length > 0 && (
            <div className="trend-block">
              <h4 className="subpanel-title">Empirical Demand Signals</h4>
              <ul className="editorial-bullet-list">
                {demand_signals.map((signal, i) => (
                  <li key={i}>{signal}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
