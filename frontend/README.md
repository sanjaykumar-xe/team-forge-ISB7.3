# Frontend — Team Forge Validation Dashboard

The frontend is a modern, high-performance **React 18 + Vite** single-page application built for deep interactive exploration of autonomous venture validation reports. It features an **Editorial Light Theme** with fluid responsive grids, jump-navigation, real-time pipeline status tracking, and 12 dedicated analytical modules.

---

## 🎨 Design Philosophy & UX Architecture

- **Editorial Theme**: Clean ivory-to-slate gradient background (`#fafafa` / `#ffffff`), crisp typography (system font stack with geometric headings), refined borders (`border-slate-200`), and semantic badge coloring.
- **Fluid Layout**: Replaced rigid container widths with full-bleed responsive layouts (`w-full px-4 md:px-8 xl:px-12`) expanding to 3 and 4 columns on wide monitors.
- **§ Jump Navigation**: Sticky sub-header allowing one-click smooth scrolling directly to any of the analytical sections.
- **Honest Grounding Notice**: Real-time contextual amber alert rendering directly above personas whenever customer demand evidence yields 0 web citations, ensuring transparent reporting of market data availability.

---

## 📁 Directory Structure

```
frontend/
├── public/                     # Static assets (favicons, manifest)
├── src/
│   ├── assets/                 # SVGs, icons, illustrations
│   ├── components/             # 12 Modular analytical presentation components
│   │   ├── CustomerSegments.jsx   # ICP personas & [HONEST GROUNDING NOTICE]
│   │   ├── CompetitorAnalysis.jsx # Competitor positioning & direct/indirect matrix
│   │   ├── ExportPDF.jsx          # Printable report generator
│   │   ├── ExtractedMetadata.jsx  # Structured idea decomposition card
│   │   ├── GTMStrategy.jsx        # Go-to-market acquisition channels & funnels
│   │   ├── MarketAnalysis.jsx     # TAM / SAM / SOM & growth trends
│   │   ├── MVPRecommendation.jsx  # 3-phase product roadmap & risk mitigation
│   │   ├── PipelineVisualizer.jsx # Real-time 9-stage execution tracker
│   │   ├── README.md              # Component-level reference documentation
│   │   ├── ReportHeader.jsx       # Validation score, executive badges & export
│   │   ├── SourcesList.jsx        # Grounded web citations explorer
│   │   ├── SWOTAnalysis.jsx       # 4-quadrant strategic synthesis matrix
│   │   └── WhiteSpaceMap.jsx      # Evidence-backed opportunity gap radar
│   ├── App.css                 # Global editorial layout rules & custom scrollbars
│   ├── App.jsx                 # Core application controller & validation state
│   ├── index.css               # Tailwind utility imports & base variables
│   └── main.jsx                # React root mount
├── index.html                  # HTML entry point with meta tags & SEO structure
├── package.json                # React 18, Tailwind CSS, Lucide icons, Vite
├── tailwind.config.js          # Tailwind theme configuration
└── vite.config.js              # Vite bundler configuration
```

---

## 🧩 Key Components Reference

| Component | Responsibility & Features |
| :--- | :--- |
| **`ExtractedMetadata.jsx`** | Displays structured idea cards: Problem, Proposed Solution, Target Audience, Revenue Model, and Industry Category. |
| **`PipelineVisualizer.jsx`** | Displays real-time progress across all 9 autonomous validation stages with animated step transitions. |
| **`MarketAnalysis.jsx`** | Visualizes Market Sizing (TAM/SAM/SOM), Market Growth CAGR, Growth Drivers, and Entry Barriers. |
| **`CompetitorAnalysis.jsx`** | Comprehensive grid of direct & indirect competitors, strengths, weaknesses, positioning, and source URLs. |
| **`CustomerSegments.jsx`** | Buyer personas (ICP, pain points, willingness to pay) + conditional **`[HONEST GROUNDING NOTICE]`** alert banner. |
| **`WhiteSpaceMap.jsx`** | 2x2 opportunity matrix highlighting unmet market needs, market gaps, and differentiation opportunities. |
| **`SWOTAnalysis.jsx`** | 4-quadrant strategic matrix (Strengths, Weaknesses, Opportunities, Threats) grounded in empirical findings. |
| **`MVPRecommendation.jsx`** | Phased execution roadmap (Phase 1 MVP, Phase 2, Phase 3), feature prioritization, and technical risk mitigation. |
| **`GTMStrategy.jsx`** | Go-To-Market strategy, distribution channels, customer acquisition cost strategies, and milestone timeline. |
| **`SourcesList.jsx`** | Interactive drawer listing all verified web research citations with credibility indicators and live links. |
| **`ReportHeader.jsx`** | High-level executive scorecard with composite viability score, category tags, and action buttons. |
| **`ExportPDF.jsx`** | Browser-native print styles generating an investor-ready multi-page validation dossier. |

---

## 🚀 Getting Started

### Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation & Run
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Launch Vite development server
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### Production Build
```bash
npm run build
npm run preview
```
Vite will compile production-optimized bundles into `frontend/dist/`.
