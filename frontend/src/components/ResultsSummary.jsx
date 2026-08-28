import { useState, useEffect } from "react";

const CATEGORY_ORDER = [
  "Competitors",
  "Industry News",
  "Customer Demand",
  "Market Size & Trends",
];

/**
 * ResultsSummary Component
 * Editorial warm ink panel showing total sources surfaced with count-up animation and category breakdown.
 */
export default function ResultsSummary({ summary, sources = [] }) {
  if (!summary) return null;

  const targetTotal = summary.total_sources ?? sources.length;
  const [displayCount, setDisplayCount] = useState(0);
  const categories = summary.sources_per_category || summary.sources_per_query || {};

  useEffect(() => {
    // Skip animation if user prefers reduced motion
    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDisplayCount(targetTotal);
      return;
    }

    let startTimestamp = null;
    const duration = 550; // ms

    function step(timestamp) {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // ease-out cubic curve
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
    <div className="results-summary-panel">
      <div className="summary-main-stat">
        <span className="summary-number">{displayCount}</span>
        <div className="summary-label-group">
          <span className="summary-heading">Sources Surfaced</span>
          <span className="summary-caption">Live market intelligence across 4 strategic categories</span>
        </div>
      </div>

      <div className="summary-breakdown-grid">
        {CATEGORY_ORDER.map((cat) => {
          const count = categories[cat] || 0;
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
