# Frontend Application — Startup Idea Validator

The frontend is a responsive Single Page Application built with **React** and **Vite**, designed with an editorial aesthetic for startup research and validation.

---

## 📁 Component Hierarchy & Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # Masthead headline & value proposition
│   │   ├── ResultsSummary.jsx   # High-contrast dark summary panel & category stats
│   │   └── SourceCard.jsx       # Individual research source item with hostname & relevance
│   ├── App.jsx                  # Main state controller (idea input, skeleton loading, results)
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
- **Dynamic Research Summary**: High-contrast summary panel displaying total sources surfaced with per-angle breakdowns.
- **Structured Source Cards**: Attribution tags, clean domain hostnames, and relevance indicators for each search result.
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
