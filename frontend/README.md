# Frontend Application — Startup Idea Validator

The frontend is a responsive Single Page Application built with **React** and **Vite**, designed with an editorial aesthetic for startup research and validation.

---

## 📁 Component Hierarchy & Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # Masthead headline & value proposition
│   │   ├── ExtractedMetadata.jsx # Stamped AI Dossier metadata card
│   │   ├── ExtractedMetadata.css # Dossier styling & case-file badge
│   │   ├── ResultsSummary.jsx   # Summary panel with animated count-up counter
│   │   ├── CategorySection.jsx  # 3-column responsive category evidence grid
│   │   └── SourceCard.jsx       # Source card with snippet cleaner & pinned footer
│   ├── App.jsx                  # Main state controller (idea input, loading, results)
│   ├── App.css                  # Editorial layout, typography, & responsive styling
│   ├── index.css                # Design tokens, color palette, & base reset
│   └── main.jsx                 # React root DOM mounting
├── index.html                   # HTML template with Google Fonts (Instrument Serif, Space Mono, Inter)
├── vercel.json                  # Vercel SPA rewrite rules
└── vite.config.js               # Vite configuration
```

---

## ⚡ Key Features

- **Editorial Design System**: Clean typography pairing (Instrument Serif, Space Mono, Inter) on a warm neutral canvas.
- **AI Domain Dossier**: Stamped metadata card showing product name, industry vertical, target audience, and keyword tags.
- **Dynamic Research Summary**: High-contrast summary panel displaying total sources surfaced with animated count-up.
- **4-Category Evidence Grid**: 3-column responsive grid grouping sources into *Competitors*, *Industry News*, *Customer Demand*, and *Market Size*.
- **Snippet Sanitizer & Sentence Truncation**: Strips markdown artifacts and pipe tables, cleanly truncating text at sentence boundaries (~180–220 chars) with inline *"Read more"* toggles.
- **Pinned Card Footers**: Enforces equal card height across rows with hostname and relevance score pinned to the bottom.
- **Skeleton Pulse Loading**: Visual feedback while multi-angle search queries execute on the backend.
- **Environment Configuration**: Uses Vite environment variables (`import.meta.env.VITE_API_URL`) to seamlessly switch between local development and production.

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
