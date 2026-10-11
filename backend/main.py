"""KrishiRakshak API. Demo inference is explicitly illustrative, never a diagnosis."""
from datetime import datetime, timezone
import os
from typing import Optional
from urllib.request import urlopen
from urllib.parse import urlencode
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="KrishiRakshak AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",") if origin.strip()],
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX") or None,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
MAX_BYTES = 10 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAGIC = {"image/jpeg": lambda b: b.startswith(b"\xff\xd8\xff"), "image/png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"), "image/webp": lambda b: len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP"}

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo", "model": None, "persistence": "browser-local"}

@app.post("/api/analyze")
async def analyze(image: UploadFile = File(...), crop: str = Form("Other / unsure"), field: str = Form(""), growth_stage: str = Form(""), variety: str = Form(""), symptoms: str = Form("")):
    if image.content_type not in IMAGE_TYPES:
        raise HTTPException(415, "Upload a JPEG, PNG, or WebP image.")
    data = await image.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(400, "The uploaded image is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image must be 10 MB or smaller.")
    if not MAGIC[image.content_type](data):
        raise HTTPException(415, "Image content does not match its declared file type.")
    # There is deliberately no trained image model configured. This response is a
    # clearly labeled fixture for verifying the end-to-end upload workflow.
    return {"mode": "demo", "model_version": None, "crop": crop, "field": field, "growth_stage": growth_stage, "variety": variety, "symptoms_received": bool(symptoms.strip()),
            "diagnosis": "Illustrative review only — no model configured", "score": None,
            "risk": "Not available", "advisory": "Inspect the plant and seek local extension advice if symptoms persist.",
            "limitations": ["No crop classifier is configured", "No live weather is attached", "No confirmed diagnosis"]}

@app.get("/api/weather")
def weather(latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180)):
    """Fetch hourly gridded forecasts from Open-Meteo; values are not field observations."""
    query = urlencode({"latitude": latitude, "longitude": longitude, "hourly": "temperature_2m,relative_humidity_2m,precipitation", "current": "temperature_2m,relative_humidity_2m,precipitation", "forecast_days": 3, "timezone": "auto"})
    try:
        with urlopen("https://api.open-meteo.com/v1/forecast?" + query, timeout=8) as response:
            import json
            data = json.loads(response.read())
        return {"source": "Open-Meteo", "retrieved_at": datetime.now(timezone.utc).isoformat(), "data_kind": "gridded forecast; not field observation", "current": data.get("current"), "hourly": data.get("hourly"), "missing_variables": [k for k in ("leaf_wetness",) if k not in data.get("hourly", {})]}
    except Exception as exc:
        raise HTTPException(502, "Weather provider unavailable. No weather values were substituted.") from exc

class RiskRequest(BaseModel):
    crop: str
    disease: str
    hourly: list[dict]

@app.post("/api/risk")
def risk(request: RiskRequest):
    # Do not fabricate a disease-specific risk without an evidence-backed model.
    return {"status": "unsupported_model", "category": "Not available", "label": "No validated disease model configured", "crop": request.crop, "disease": request.disease, "contributing_variables": [], "missing_variables": ["disease-specific validated parameters", "leaf wetness", "local disease observations"], "outbreak_probability": None, "message": "Environmental suitability cannot be estimated reliably for this combination."}
