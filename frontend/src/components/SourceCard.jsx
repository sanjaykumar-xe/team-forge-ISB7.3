/**
 * Helper to extract clean uppercase hostname from a URL.
 */
function getCleanHostname(rawUrl) {
  try {
    if (!rawUrl) return "WEB SOURCE";
    const url = new URL(rawUrl);
    return url.hostname.replace(/^www\./i, "").toUpperCase();
  } catch {
    return "WEB SOURCE";
  }
}

/**
 * Determine a concise category label and tag style class.
 */
function getCategoryMeta(categoryName = "", query = "") {
  const cat = (categoryName || "").toLowerCase();
  const q = (query || "").toLowerCase();

  if (cat.includes("competitor") || q.includes("competitor") || q.includes("alternative")) {
    return { label: "COMPETITORS", className: "tag-green" };
  }
  if (cat.includes("news") || q.includes("news") || q.includes("trend")) {
    return { label: "INDUSTRY NEWS", className: "tag-blue" };
  }
  if (cat.includes("demand") || cat.includes("customer") || q.includes("customer") || q.includes("demand")) {
    return { label: "CUSTOMER DEMAND", className: "tag-rose" };
  }
  if (cat.includes("size") || cat.includes("market") || q.includes("size") || q.includes("growth")) {
    return { label: "MARKET SIZE & TRENDS", className: "tag-amber" };
  }
  return { label: "MARKET INTELLIGENCE", className: "tag-default" };
}

/**
 * SourceCard Component
 * Sharp rectangular editorial card displaying research evidence, clean hostname, and relevance.
 */
export default function SourceCard({ source }) {
  if (!source) return null;

  const rawScore = Number(source.score);
  const relevancePct = isNaN(rawScore)
    ? 0
    : Math.min(100, Math.max(0, Math.round(rawScore * 100)));

  const hostname = getCleanHostname(source.url);
  const category = getCategoryMeta(source.category, source.query);
  const isValidUrl = source.url && (source.url.startsWith("http://") || source.url.startsWith("https://"));

  return (
    <li className="source-card">
      <div className="source-header">
        <span className={`source-tag ${category.className}`}>
          {category.label}
        </span>
      </div>

      {isValidUrl ? (
        <a
          className="source-title"
          href={source.url}
          target="_blank"
          rel="noreferrer noopener"
        >
          {source.title || "Untitled source"}
        </a>
      ) : (
        <span className="source-title">
          {source.title || "Untitled source"}
        </span>
      )}

      <p className="source-snippet">{source.snippet || "No preview snippet available."}</p>

      <div className="source-footer">
        <span className="source-hostname">{hostname}</span>
        <span className="source-relevance">{relevancePct}% relevance &rarr;</span>
      </div>
    </li>
  );
}
