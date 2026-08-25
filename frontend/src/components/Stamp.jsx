/**
 * Stamp Component
 * Visual circular badge displaying the source match score percentage.
 */
export default function Stamp({ score }) {
  const pct = Math.round((score || 0) * 100);
  return (
    <div className="stamp" aria-hidden="true">
      <svg viewBox="0 0 64 64" width="52" height="52">
        <circle cx="32" cy="32" r="29" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="32" cy="32" r="24" fill="none" stroke="currentColor" strokeWidth="0.75" strokeDasharray="2 3" />
        <text x="32" y="29" textAnchor="middle" fontSize="14" fontFamily="IBM Plex Mono" fill="currentColor">
          {pct}
        </text>
        <text x="32" y="41" textAnchor="middle" fontSize="6" letterSpacing="1" fontFamily="IBM Plex Mono" fill="currentColor">
          MATCH
        </text>
      </svg>
    </div>
  );
}
