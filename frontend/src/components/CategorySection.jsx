import { useState } from "react";
import SourceCard from "./SourceCard";

/**
 * CategorySection Component
 * Renders a categorized row/grid of sources with a monospace header and collapsible "SHOW MORE".
 */
export default function CategorySection({ title, sources = [], initialLimit = 3 }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const visibleSources = isExpanded ? sources : sources.slice(0, initialLimit);
  const remainingCount = sources.length - initialLimit;

  return (
    <section className="category-section">
      <div className="category-section-header">
        <h3 className="category-title">{title}</h3>
        <span className="category-count">{sources.length} sources</span>
      </div>

      <ul className="category-grid">
        {visibleSources.map((source) => (
          <SourceCard key={source.url} source={source} />
        ))}
      </ul>

      {remainingCount > 0 && (
        <div className="category-action-row">
          <button
            type="button"
            className="btn-show-more"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? "SHOW LESS ↑" : `SHOW ${remainingCount} MORE ↓`}
          </button>
        </div>
      )}
    </section>
  );
}
