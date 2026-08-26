/**
 * Header Component
 * Editorial masthead banner with large serif question headline.
 */
export default function Header() {
  return (
    <header className="masthead">
      <p className="masthead-label">TEAM FORGE · MILESTONE 01</p>
      <h1 className="masthead-title">
        Does your idea <em className="accent-word">actually</em> hold up?
      </h1>
      <p className="masthead-sub">
        Turn an early startup idea into evidence — the Web Search Agent scouts
        current market signal, the Data Retrieval Agent structures what it finds,
        before you spend a weekend building the wrong thing.
      </p>
    </header>
  );
}

