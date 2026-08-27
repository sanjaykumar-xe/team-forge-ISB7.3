const CATEGORY_ORDER = [
  "Competitors",
  "Industry News",
  "Customer Demand",
  "Market Size & Trends",
];

/**
 * ResultsSummary Component
 * High-contrast near-black panel showing total sources surfaced and the 4 category counts.
 */
export default function ResultsSummary({ summary, sources = [] }) {
  if (!summary) return null;

  const total = summary.total_sources ?? sources.length;
  const categories = summary.sources_per_category || summary.sources_per_query || {};

  return (
    <div className="results-summary-panel">
      <div className="summary-main-stat">
        <span className="summary-number">{total}</span>
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
