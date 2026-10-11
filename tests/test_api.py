from fastapi.testclient import TestClient
import backend.main as api

client = TestClient(api.app)
PNG = b"\x89PNG\r\n\x1a\n" + b"demo-bytes"

def test_health_is_explicit_demo_mode():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"
    assert response.json()["model"] is None

def test_image_upload_returns_no_model_claim():
    response = client.post("/api/analyze", files={"image": ("leaf.png", PNG, "image/png")}, data={"crop": "Tomato", "growth_stage": "Flowering", "variety": "Local", "symptoms": "Yellow lower leaves"})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "demo"
    assert body["score"] is None
    assert "no model configured" in body["diagnosis"]
    assert body["growth_stage"] == "Flowering"
    assert body["symptoms_received"] is True

def test_rejects_unsupported_mime_and_mismatched_content():
    unsupported = client.post("/api/analyze", files={"image": ("leaf.gif", b"GIF89a", "image/gif")})
    mismatch = client.post("/api/analyze", files={"image": ("leaf.png", b"not a png", "image/png")})
    assert unsupported.status_code == 415
    assert mismatch.status_code == 415

def test_rejects_oversized_image():
    response = client.post("/api/analyze", files={"image": ("large.png", b"\x89PNG\r\n\x1a\n" + b"0" * (api.MAX_BYTES + 1), "image/png")})
    assert response.status_code == 413

def test_weather_validates_coordinates():
    assert client.get("/api/weather?latitude=91&longitude=20").status_code == 422
    assert client.get("/api/weather?latitude=20&longitude=-181").status_code == 422

def test_weather_failure_returns_error_without_substitute(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("offline")
    monkeypatch.setattr(api, "urlopen", fail)
    response = client.get("/api/weather?latitude=19.07&longitude=72.87")
    assert response.status_code == 502
    assert "substituted" in response.json()["detail"]

def test_risk_endpoint_does_not_claim_unvalidated_risk():
    response = client.post("/api/risk", json={"crop": "Tomato", "disease": "early blight", "hourly": []})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unsupported_model"
    assert body["outbreak_probability"] is None
