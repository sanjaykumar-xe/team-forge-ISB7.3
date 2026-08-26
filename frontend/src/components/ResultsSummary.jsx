/**
 * Format raw query string into a clean editorial label.
 */
function getShortCategoryLabel(query = "") {
  const q = query.toLowerCase();
  if (q.includes("market size") || q.includes("industry")) {
    return "Market Size & Trends";
  }
  if (q.includes("competitor") || q.includes("alternative")) {
    return "Competitors & Alternatives";
  }
  if (q.includes("customer") || q.includes("demand") || q.includes("target")) {
    return "Target Customers & Demand";
  }
  return "Market Intelligence";
}

/**
 * ResultsSummary Component
 * High-contrast near-black panel showing total sources surfaced and category breakdowns.
 */
export default function ResultsSummary({ summary, sources = [] }) {
  if (!summary) return null;

  // Calculate average relevance per query angle
  const statsByQuery = {};
  for (const s of sources) {
    const q = s.query || "general";
    if (!statsByQuery[q]) {
      statsByQuery[q] = { count: 0, totalScore: 0 };
    }
    statsByQuery[q].count += 1;
    statsByQuery[q].totalScore += s.score || 0;
  }

  const queryEntries = Object.entries(summary.sources_per_query || {}).map(
    ([query, count]) => {
      const stats = statsByQuery[query];
      const avgScore = stats && stats.count > 0 ? Math.round((stats.totalScore / stats.count) * 100) : null;
      return {
        query,
        count,
        label: getShortCategoryLabel(query),
        avgScore,
      };
    }
  );

  return (
    <div className="results-summary-panel">
      <div className="summary-main-stat">
        <span className="summary-number">{summary.total_sources}</span>
        <div className="summary-label-group">
          <span className="summary-heading">Sources Surfaced</span>
          <span className="summary-caption">Live market intelligence across 3 research angles</span>
        </div>
      </div>

      <div className="summary-breakdown-grid">
        {queryEntries.map((item) => (
          <div key={item.query} className="summary-category-item">
            <span className="summary-cat-label">{item.label}</span>
            <div className="summary-cat-metrics">
              <span className="summary-cat-count">{item.count} sources</span>
              {item.avgScore !== null && (
                <span className="summary-cat-score">~{item.avgScore}% avg rel</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

