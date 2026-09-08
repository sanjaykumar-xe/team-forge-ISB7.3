# 09. Deployment & Operations Documentation

## 1. Cloud Infrastructure Architecture
The platform is deployed using a modern cloud-native decoupled topology:
- **Frontend SPA**: Hosted on **Vercel Cloud** (Edge CDN distribution, automated HTTPS, zero-config rewrites).
- **Backend API**: Hosted on **Render Cloud** (Python 3.11 web service, managed environment, Uvicorn ASGI server).
- **Inference Cloud**: **Groq Cloud** (High-throughput LPU inference nodes).
- **Search Cloud**: **Tavily AI Search Engine** (API access with semantic index).

```
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│   Vercel Cloud   │ ──HTTPS──►│   Render Cloud   │ ──HTTPS──►│ Groq / Tavily    │
│  (React 18 SPA)  │           │   (FastAPI API)  │           │ (Inference/Web)  │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

---

## 2. Environment Configuration

### Backend Environment Variables (`backend/.env`)
Create a `.env` file in the `backend/` directory:

```env
# Groq Cloud API Key (LLM Inference)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Tavily Search API Key (Live Web Querying)
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# Environment and Port
ENVIRONMENT=production
PORT=8000
```

### Frontend Environment Variables (`frontend/.env`)
Create a `.env` file in the `frontend/` directory:

```env
# Points to deployed backend or local server
VITE_API_URL=http://127.0.0.1:8000
```

---

## 3. Local Development Setup

### 3.1 Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch FastAPI development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- API Health Check: `http://127.0.0.1:8000/api/health`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

### 3.2 Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite local development server
npm run dev
```
- Client Application: `http://localhost:5173`

---

## 4. Production Deployment

### 4.1 Backend on Render Cloud (`render.yaml`)
Configured via `render.yaml` in the repository root:
```yaml
services:
  - type: web
    name: team-forge-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: GROQ_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
```

### 4.2 Frontend on Vercel Cloud (`frontend/vercel.json`)
Configured via `frontend/vercel.json` for client-side routing:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
Deploy steps:
1. Import repository into Vercel.
2. Set Root Directory to `frontend`.
3. Add Environment Variable: `VITE_API_URL=https://team-forge-backend.onrender.com`.
4. Deploy.
