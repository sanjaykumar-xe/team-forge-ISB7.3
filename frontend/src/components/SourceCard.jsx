import Stamp from "./Stamp";

/**
 * SourceCard Component
 * Displays a structured research source with match score, title, snippet, and link.
 */
export default function SourceCard({ source }) {
  return (
    <li className="source-card">
      <Stamp score={source.score} />
      <div className="source-body">
        <p className="source-eyebrow">{source.query}</p>
        <a
          className="source-title"
          href={source.url}
          target="_blank"
          rel="noreferrer noopener"
        >
          {source.title}
        </a>
        <p className="source-snippet">{source.snippet}</p>
        <p className="source-url">{source.url}</p>
      </div>
    </li>
  );
}
