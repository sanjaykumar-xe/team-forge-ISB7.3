# Frontend Application — Startup Idea Validator

The frontend is a responsive Single Page Application built with **React** and **Vite**, designed with an editorial aesthetic for startup research and validation.

---

## 📁 Component Hierarchy & Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx                 # Masthead headline & value proposition
│   │   ├── ExtractedMetadata.jsx       # Stamped AI Dossier metadata card
│   │   ├── ExtractedMetadata.css       # Dossier styling & case-file badge
│   │   ├── WhiteSpaceAnalysis.jsx     # Centerpiece: Evidence-Backed Market White-Space Map
│   │   ├── MarketOpportunity.jsx      # Market sizing, CAGR, and attractiveness scorecard
│   │   ├── CustomerSegments.jsx       # Customer persona cards (End Users vs Decision Makers)
│   │   ├── CompetitorAnalysis.jsx     # Competitor cards & comparison matrix
│   │   ├── ResultsSummary.jsx         # Summary panel with animated count-up counter
│   │   ├── CategorySection.jsx        # Responsive category evidence grid
│   │   └── SourceCard.jsx             # Source card with snippet cleaner & pinned footer
│   ├── App.jsx                        # Main state controller (idea input, loading, results)
│   ├── App.css                        # Editorial layout, typography, & responsive styling
│   ├── index.css                      # Design tokens, color palette, & base reset
│   └── main.jsx                       # React root DOM mounting
├── index.html                         # HTML template with Google Fonts (Instrument Serif, Space Mono, Inter)
├── vercel.json                        # Vercel SPA rewrite rules
└── vite.config.js                     # Vite configuration
```

---

## ⚡ Key Features

- **Editorial Design System**: Clean typography pairing (Instrument Serif, Space Mono, Inter) on a warm neutral canvas.
- **AI Domain Dossier**: Stamped metadata card showing product name, industry vertical, target audience, and keyword tags.
- **Evidence-Backed Market White-Space Map**: Centerpiece view rendering high-conviction opportunity gaps triangulating customer pain, competitor voids, and startup capability with confidence scores and citations.
- **Market Opportunity & Sizing Panel**: Quantifiable TAM/SAM metrics, CAGR projections, forecast years, and honest null states when data is sparse.
- **Customer Segmentation**: Granular personas contrasting daily end users vs economic decision makers with acute friction points.
- **Competitor Comparison Matrix**: Direct vs indirect rival analysis with side-by-side capability benchmarking.
- **Dynamic Research Summary**: High-contrast summary panel displaying total sources surfaced with animated count-up.
- **4-Category Evidence Grid**: Responsive grid grouping sources into *Competitors*, *Industry News*, *Customer Demand*, and *Market Size*.
- **Snippet Sanitizer & Sentence Truncation**: Strips markdown artifacts and pipe tables, cleanly truncating text at sentence boundaries with inline *"Read more"* toggles.

---

## 🚀 Local Development

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## 📦 Production Build

```bash
npm run build
```

Generates production-optimized static assets in the `dist/` directory.
