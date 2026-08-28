import { useState } from "react";

/**
 * Clean markdown symbols, table artifacts, and format raw snippet text.
 */
function cleanSnippetText(raw = "") {
  if (!raw || typeof raw !== "string") return "";

  let text = raw;

  // 1. Remove markdown links [text](url) -> text
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

  // 2. Remove markdown images and bracket placeholders [...], [1], [2], etc.
  text = text.replace(/!\[[^\]]*\]\([^)]*\)/g, "");
  text = text.replace(/\[\s*\.{2,}\s*\]/g, "");
  text = text.replace(/\[\d+\]/g, "");

  // 3. Remove table artifacts and repeated pipes (| | | or |---|---|)
  text = text.replace(/\|[-:\s|]+\|/g, " ");
  text = text.replace(/\|/g, " ");

  // 4. Strip markdown formatting headers (#, ##, ###), bold/italic (*, **, _, __)
  text = text.replace(/#{1,6}\s+/g, "");
  text = text.replace(/[*_]{1,3}([^*_]+)[*_]{1,3}/g, "$1");
  text = text.replace(/[*_]/g, "");

  // 5. Collapse consecutive whitespace, newlines, and tabs into single space
  text = text.replace(/\s+/g, " ").trim();

  // 6. Clean leading/trailing artifacts
  text = text.replace(/^[-:;,|•]+\s*/, "").replace(/[-:;,|•]+\s*$/, "");

  return text;
}

/**
 * Truncate clean text to ~180-220 characters ending at a sentence boundary if possible.
 */
function formatSnippetWithSentenceBreak(cleanText, targetMin = 160, targetMax = 220) {
  if (!cleanText || cleanText.length <= targetMax) {
    return {
      truncatedText: cleanText,
      fullText: cleanText,
      canExpand: false,
    };
  }

  // Look for a sentence boundary (., !, ?) between targetMin and targetMax
  const windowSub = cleanText.slice(0, targetMax + 20);
  const sentenceEndMatches = [...windowSub.matchAll(/([.!?])(\s+|$)/g)];

  let cutIdx = -1;
  for (const match of sentenceEndMatches) {
    const endPos = match.index + 1;
    if (endPos >= targetMin && endPos <= targetMax + 15) {
      cutIdx = endPos;
      break;
    }
  }

  // If no sentence boundary found in ideal window, look for word boundary
  if (cutIdx === -1) {
    const wordBoundary = cleanText.slice(0, targetMax).lastIndexOf(" ");
    if (wordBoundary > targetMin) {
      cutIdx = wordBoundary;
    } else {
      cutIdx = targetMax;
    }
    const truncated = cleanText.slice(0, cutIdx).trim().replace(/[.,;:!?]+$/, "") + "…";
    return {
      truncatedText: truncated,
      fullText: cleanText,
      canExpand: cleanText.length - truncated.length > 25,
    };
  }

  const truncated = cleanText.slice(0, cutIdx).trim();
  return {
    truncatedText: truncated,
    fullText: cleanText,
    canExpand: cleanText.length - truncated.length > 25,
  };
}

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
 * Balanced editorial card with cleaned snippets, expandable toggle, and anchored footers.
 */
export default function SourceCard({ source }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!source) return null;

  const rawScore = Number(source.score);
  const relevancePct = isNaN(rawScore)
    ? 0
    : Math.min(100, Math.max(0, Math.round(rawScore * 100)));

  const hostname = getCleanHostname(source.url);
  const category = getCategoryMeta(source.category, source.query);
  const isValidUrl = source.url && (source.url.startsWith("http://") || source.url.startsWith("https://"));

  const rawContent = source.snippet || source.content || "";
  const cleaned = cleanSnippetText(rawContent);
  const { truncatedText, fullText, canExpand } = formatSnippetWithSentenceBreak(cleaned);

  const displayText = isExpanded ? fullText : (truncatedText || "No preview snippet available.");

  return (
    <li className="source-card">
      <div className="source-header">
        <span className={`source-tag ${category.className}`}>
          {category.label}
        </span>
      </div>

      <div className="source-body">
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

        <p className="source-snippet">{displayText}</p>

        {canExpand && (
          <button
            type="button"
            className="snippet-toggle-btn"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? "Read less ↑" : "Read more ↓"}
          </button>
        )}
      </div>

      <div className="source-footer">
        <span className="source-hostname">{hostname}</span>
        <span className="source-relevance">{relevancePct}% relevance &rarr;</span>
      </div>
    </li>
  );
}
