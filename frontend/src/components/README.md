# Team Forge — Frontend UI Components

This directory contains the modular React presentation components for the Startup Idea Validator single-page application.

---

## Component Inventory

| Component File | Role / UI Section | Description |
|---|---|---|
| `Header.jsx` | Masthead & Branding | Displays project title, branding, and status indicators. |
| `ExtractedMetadata.jsx` | Domain Dossier | Displays extracted idea attributes (product name, industry, problem, keywords, and extraction confidence). |
| `ResultsSummary.jsx` | KPI Metrics Strip | Visual summary showing Total Addressable Market, Customer Density, and Evidence Counts. |
| `CustomerSegments.jsx` | Customer Personas | Interactive persona cards displaying Daily End Users vs Economic Decision Makers, acute pains, and the **Honest Grounding Notice**. |
| `MarketOpportunity.jsx` | Market Sizing | Displays TAM / SAM / SOM estimates with source links and tentative/strong grounding flags. |
| `CompetitorAnalysis.jsx` | Competitive Landscape | Side-by-side competitor profiles, capability comparison matrix, and market void callouts. |
| `WhiteSpaceAnalysis.jsx` | Market White-Space Map | Centerpiece module illustrating triangulated market gaps, solution fit, and demand signal quotes. |
| `SWOTAnalysis.jsx` | Strategic SWOT & Risks | High-contrast 4-quadrant SWOT matrix (S, W, O, T) and strategic risks grid with mitigations. |
| `MVPRecommendation.jsx` | MVP Feature Roadmap | Prioritized P0/P1/P2 feature cards with upstream grounding tags, deferred v2 list, and resource estimates. |
| `GTMStrategy.jsx` | Go-To-Market Plan | Idea-specific positioning statement, customer acquisition channels with fit scores, and launch timeline. |
| `CategorySection.jsx` | Sources Section | Grouped accordion view of all collected research evidence across categories. |
| `SourceCard.jsx` | Individual Citation Card | Displays verified article title, URL, snippet, and category badge. |

---

## Styling & Design System
- **Theme**: Light Editorial Cream (`#FAF8F5`) with crisp borders (`#222222`), deep black headings (`#111111`), and high-contrast WCAG AA accessible tags.
- **Responsiveness**: Fluid CSS grid layouts expanding seamlessly from single-column mobile viewports up to 4-column desktop layouts.
