/**
 * Helper to extract clean uppercase hostname from a URL.
 */
function getCleanHostname(rawUrl) {
  try {
    const url = new URL(rawUrl);
    return url.hostname.replace(/^www\./i, "").toUpperCase();
  } catch {
    return "WEB SOURCE";
  }
}

/**
 * Determine a concise category label and tag style class based on query text.
 */
function getCategoryMeta(query = "") {
  const q = query.toLowerCase();
  if (q.includes("market size") || q.includes("industry")) {
    return { label: "MARKET SIZE & TRENDS", className: "tag-blue" };
  }
  if (q.includes("competitor") || q.includes("alternative")) {
    return { label: "COMPETITORS & ALTERNATIVES", className: "tag-green" };
  }
  if (q.includes("customer") || q.includes("demand") || q.includes("target")) {
    return { label: "TARGET DEMAND", className: "tag-rose" };
  }
  return { label: "MARKET INTELLIGENCE", className: "tag-default" };
}

/**
 * SourceCard Component
 * Sharp rectangular editorial card displaying research evidence, clean hostname, and relevance.
 */
export default function SourceCard({ source }) {
  const hostname = getCleanHostname(source.url);
  const relevancePct = Math.round((source.score || 0) * 100);
  const category = getCategoryMeta(source.query);

  return (
    <li className="source-card">
      <div className="source-header">
        <span className={`source-tag ${category.className}`}>
          {category.label}
        </span>
      </div>

      <a
        className="source-title"
        href={source.url}
        target="_blank"
        rel="noreferrer noopener"
      >
        {source.title}
      </a>

      <p className="source-snippet">{source.snippet}</p>

      <div className="source-footer">
        <span className="source-hostname">{hostname}</span>
        <span className="source-relevance">{relevancePct}% relevance &rarr;</span>
      </div>
    </li>
  );
}

