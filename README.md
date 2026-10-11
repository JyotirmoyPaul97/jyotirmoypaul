# KrishiRakshak AI

A responsive crop-health decision-support demo with a React/Vite dashboard and a FastAPI service. The interface separates image-model evidence from environmental suitability and confirmed disease. **Demo mode has no trained model, database, or configured weather provider by default; it does not make live crop or weather claims.**

[Your Link Here](https://jyotirmoypaul-e21w.vercel.app/)

## Project structure

```text
src/                 React application and responsive styles
backend/main.py      FastAPI upload validation, weather proxy, model status
backend/requirements.txt
public/images/       Supplied project imagery
```

## Run locally

Prerequisites: Node.js 20+ and Python 3.10+.

```powershell
npm install
npm run dev
```

If the Windows `npm` shim points at a missing global install, invoke the bundled CLI directly: `node "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" install` and use the same path with `run dev`.

In another terminal:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Open the Vite URL, normally `http://localhost:5173`. The image-analysis page validates JPEG/PNG/WebP and a 10 MB limit. Without the API, it returns a clearly labeled browser demo. With the API, it returns an explicit “no model configured” result. Analysis history is stored in browser local storage and can be cleared from Field history.

Run the backend API checks with `.\.venv\Scripts\python.exe -m pytest -q` on Windows (or `python -m pytest -q` after activating the virtual environment).

## Weather and risk

`GET /api/weather?latitude=..&longitude=..` retrieves timestamped gridded hourly weather from Open-Meteo. It requires network access when invoked; provider failure returns an error instead of substitute values. The UI will describe location/forecast limitations. Leaf wetness is not available from this integration. `POST /api/risk` explicitly returns unavailable until a disease-specific validated model is configured. The dashboard's plotted series is illustrative demo data, labelled as such; it is not an outbreak forecast.

## Deploy a judge-ready preview on Vercel

The frontend and API are intentionally deployed as two Vercel projects so Vercel can use its Vite static build and FastAPI Python runtime independently. The root `vercel.json` includes the SPA fallback for direct page refreshes. The FastAPI app is in `backend/main.py`; deploy it as a second Vercel project with the project **Root Directory** set to `backend` (its `requirements.txt` is already there). Vercel's FastAPI runtime discovers the `app` instance in `main.py`.

1. Push this project to a Git provider and import it into Vercel. Keep the frontend root directory at `.`; Vercel should detect Vite and run `npm run build` with output directory `dist`.
2. Import the same repository a second time as a backend project and set its root directory to `backend`. Deploy it and check `<backend-url>/api/health` for the demo API status.
3. In the backend project's environment variables, set `CORS_ORIGINS` to `http://localhost:5173,http://127.0.0.1:5173,https://YOUR-FRONTEND.vercel.app`. For preview deployments, optionally set `CORS_ORIGIN_REGEX` to `https://[a-z0-9-]+-[a-z0-9-]+\.vercel\.app`; narrow this to your team's preview domain if you use one.
4. In the frontend project's environment variables, set `VITE_API_BASE_URL` to the backend's public origin (for example, `https://your-api.vercel.app`, with no trailing slash), then redeploy the frontend. The value is embedded at build time.

The frontend also runs without a backend URL in explicitly labeled demo mode, so a judge can still explore the interface and upload flow. Live weather calls and API-backed upload validation require the backend project. The uploaded image still receives an illustrative “no model configured” response; there is no trained disease diagnosis model. Browser history is local to that browser and is not shared between users. Never put server secrets in `VITE_` variables.

For local development, keep the Vite frontend on port 5173 and FastAPI on port 8000 as described above. `VITE_API_BASE_URL` defaults to `http://localhost:8000` during development and can be overridden for a hosted backend.

## Model limitations and next steps

No plant disease model or calibrated confidence score ships with this project. Demo image review is not a prediction. Before production, choose and evaluate a model on field images for supported crops, calibrate scores, version it, and test uncertain/unsupported cases. Build disease-specific risk rules from credible local extension or research sources, validate against observed outcomes, and keep suitability distinct from outbreak probability. Add Supabase migrations, authentication, per-user authorization, image storage/deletion, audit controls, and deployment-specific CORS. Treatment recommendations remain conservative and never name a pesticide or dosage.
