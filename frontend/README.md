# 🎨 Team Forge — Frontend Application

The frontend is a modern, responsive React + Vite application engineered for high clarity and rapid feedback during startup validation.

---

## 📁 Component Hierarchy & Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # Editorial masthead and milestone indicator
│   │   ├── ResultsSummary.jsx   # Coverage stats and search query breakdown chips
│   │   ├── SourceCard.jsx       # Individual research source item
│   │   └── Stamp.jsx            # SVG circular badge with percentage match score
│   ├── App.jsx                  # Main state orchestrator (Form submission, loading, & errors)
│   ├── App.css                  # Dossier/editorial layout styles
│   ├── index.css                # Typography, CSS variables, & reset styles
│   └── main.jsx                 # React root DOM mounting
├── public/                      # Static assets
├── index.html                   # HTML template with Google Fonts (Fraunces, IBM Plex Mono, Inter)
├── vercel.json                  # Vercel SPA routing rewrite rules
└── vite.config.js               # Vite configuration
```

---

## ⚡ Key Features

- **Match Score Stamp**: Interactive circular SVG stamp that renders dynamically calculated relevance scores.
- **Query Angle Breakdown**: Visual categorization chips indicating which market angle (market size, competitors, customer demand) generated each source.
- **Graceful Error Handling & Fallbacks**: Live feedback during long multi-query network requests, validation banners, and empty states.
- **Clean Configuration**: Uses Vite environment variables (`import.meta.env.VITE_API_URL`) to seamlessly toggle between local development and production.

---

## 🚀 Local Development

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env file
# (VITE_API_URL=http://localhost:8000)

# 4. Start local development server
npm run dev
```

App runs on `http://localhost:5173` (or `http://127.0.0.1:5173`).

---

## 📦 Production Build

```bash
npm run build
```
Generates production-optimized static files in `dist/` ready for Vercel deployment.
