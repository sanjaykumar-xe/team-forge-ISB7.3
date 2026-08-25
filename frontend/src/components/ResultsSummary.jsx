/**
 * ResultsSummary Component
 * Displays total sources found and category chips per search query.
 */
export default function ResultsSummary({ summary }) {
  if (!summary) return null;

  return (
    <div className="results-summary">
      <span>
        <strong>{summary.total_sources}</strong> sources found
      </span>
      <span className="divider">·</span>
      {Object.entries(summary.sources_per_query || {}).map(([query, count]) => (
        <span key={query} className="query-chip">
          {query} ({count})
        </span>
      ))}
    </div>
  );
}
