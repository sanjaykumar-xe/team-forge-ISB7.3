import { useState, useEffect } from "react";

const CATEGORY_ORDER = [
  "Competitors",
  "Industry News",
  "Customer Demand",
  "Market Size & Trends",
];

/**
 * ResultsSummary Component
 * Editorial warm ink panel displaying real executive metrics and high-contrast category distribution.
 */
export default function ResultsSummary({
  summary,
  sources = [],
  competitorCount = 0,
  segmentCount = 0,
  opportunityCount = 0,
}) {
  if (!summary) return null;

  const targetTotal = summary.total_sources ?? sources.length;
  const [displayCount, setDisplayCount] = useState(0);
  const categories = summary.sources_per_category || summary.sources_per_query || {};

  useEffect(() => {
    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDisplayCount(targetTotal);
      return;
    }

    let startTimestamp = null;
    const duration = 500; // ms

    function step(timestamp) {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(eased * targetTotal);
      setDisplayCount(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }, [targetTotal]);

  return (
    <div id="section-overview" className="results-summary-panel">
      {/* Top High-Level Metrics Bar */}
      <div className="summary-top-metrics">
        <div className="summary-stat-block highlight-stat">
          <span className="summary-stat-num">{displayCount}</span>
          <div className="summary-stat-meta">
            <span className="summary-stat-title">Empirical Sources</span>
            <span className="summary-stat-sub">Across 4 research vectors</span>
          </div>
        </div>

        {competitorCount > 0 && (
          <div className="summary-stat-block">
            <span className="summary-stat-num">{competitorCount}</span>
            <div className="summary-stat-meta">
              <span className="summary-stat-title">Competitors</span>
              <span className="summary-stat-sub">Direct & substitutes</span>
            </div>
          </div>
        )}

        {opportunityCount > 0 && (
          <div className="summary-stat-block">
            <span className="summary-stat-num">{opportunityCount}</span>
            <div className="summary-stat-meta">
              <span className="summary-stat-title">White-Space Gaps</span>
              <span className="summary-stat-sub">High-conviction fits</span>
            </div>
          </div>
        )}

        {segmentCount > 0 && (
          <div className="summary-stat-block">
            <span className="summary-stat-num">{segmentCount}</span>
            <div className="summary-stat-meta">
              <span className="summary-stat-title">User Personas</span>
              <span className="summary-stat-sub">Granular buying profiles</span>
            </div>
          </div>
        )}
      </div>

      {/* High-Contrast Category Breakdown Strip */}
      <div className="summary-breakdown-grid">
        {CATEGORY_ORDER.map((cat) => {
          const count = categories[cat] || (sources.filter((s) => s.category === cat).length) || 0;
          return (
            <div key={cat} className="summary-category-item">
              <span className="summary-cat-label">{cat}</span>
              <div className="summary-cat-metrics">
                <span className="summary-cat-count">{count} {count === 1 ? "source" : "sources"}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
