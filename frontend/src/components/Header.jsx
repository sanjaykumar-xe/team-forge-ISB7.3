/**
 * Header Component
 * Editorial masthead with serif question headline and concise research proposition.
 */
export default function Header() {
  return (
    <header className="masthead">
      <div className="masthead-eyebrow">
        <span className="masthead-badge">RESEARCH DOSSIER & INTELLIGENCE</span>
        <span className="masthead-date">EDITION 2026</span>
      </div>
      <h1 className="masthead-title">
        Does your startup idea <em className="accent-word">actually</em> hold up?
      </h1>
      <p className="masthead-sub">
        Validate your concept with real-time empirical market research. Discover live competitor voids,
        unaddressed customer demand, and defensible white-space opportunities before allocating capital or engineering time.
      </p>
    </header>
  );
}
