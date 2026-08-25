# 🚀 Production Deployment Guide — Team Forge

This document provides complete, step-by-step instructions for deploying the **Backend to Render** and the **Frontend to Vercel**.

---

## 📋 Overview of Deployment Architecture

| Tier | Platform | Build Command | Start / Output | Env Variables |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | **Render** (Web Service) | `pip install -r requirements.txt` | `uvicorn main:app --host 0.0.0.0 --port $PORT` | `ALLOWED_ORIGINS` *(optional)* |
| **Frontend** | **Vercel** (Static / SPA) | `npm run build` | `dist/` (Output Directory) | `VITE_API_URL` *(Render URL)* |

---

## 1️⃣ Part 1: Deploy Backend to Render

### Option A: Standard Web Service (Recommended & Simplest)

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** in the top right corner and choose **Web Service**.
3. Under **Connect a repository**, select your GitHub repository (`team-forge-ISB7.3`).
4. Fill in the service configuration:
   - **Name**: `team-forge-backend` *(or a name of your choice)*
   - **Region**: Choose the region closest to you (e.g., *Singapore*, *Oregon*, *Frankfurt*)
   - **Branch**: `staging` *(or `main` for production)*
   - **Root Directory**: `backend` *(⚠️ Critical: Do not leave this empty)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Click **Create Web Service** at the bottom of the page.
6. Wait for the build logs to display `Application startup complete` and status to turn **Live**.
7. **Copy your backend URL** (e.g., `https://team-forge-backend.onrender.com`).

### Verify Backend Health
Open your backend URL with `/api/health` in your browser:
```
https://<your-backend-name>.onrender.com/api/health
```
Expected Response:
```json
{"status": "ok"}
```

---

## 2️⃣ Part 2: Deploy Frontend to Vercel

1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** → **Project**.
3. Under **Import Git Repository**, click **Import** next to your GitHub repository (`team-forge-ISB7.3`).
4. In the **Configure Project** page:
   - **Project Name**: `team-forge-frontend` *(or preferred name)*
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and select the `frontend` folder.
   - **Build and Output Settings**:
     - *Build Command*: `npm run build` (default)
     - *Output Directory*: `dist` (default)
5. **Set Environment Variables**:
   - Expand the **Environment Variables** accordion.
   - Add:
     - **Key**: `VITE_API_URL`
     - **Value**: `https://<your-backend-name>.onrender.com` *(⚠️ Do not add a trailing slash)*
6. Click **Deploy**.
7. Vercel will build the frontend and provide your live URL (e.g., `https://team-forge-frontend.vercel.app`).

---

## 3️⃣ Part 3: End-to-End Verification

1. Open your live Vercel URL in your browser.
2. In the textarea, submit a test startup concept:
   > *"A mobile app that matches freelance dog walkers with verified owners using real-time GPS tracking and automated scheduling."*
3. Click **Validate idea**.
4. Confirm that:
   - The button shows *"Searching…"*.
   - Within a few seconds, the source count summary and interactive source cards populate.

---

## 🔧 Troubleshooting & Tips

### Free Tier Render Spin-Down ("Cold Starts")
Render free tier web services spin down after 15 minutes of inactivity. When a new request arrives, it may take 30–50 seconds to wake up on the first hit. If the frontend times out during the initial wakeup, simply refresh or re-submit.

### CORS Errors
If you see a CORS error in your browser console:
1. Verify that `ALLOWED_ORIGINS` in Render environment variables includes your Vercel domain or is unset (backend defaults to allowing all origins with `allow_origins=["*"]`).
2. Ensure `VITE_API_URL` in Vercel is set correctly without a trailing slash (`/`).
