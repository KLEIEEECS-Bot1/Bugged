import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings
from app.models import DetectRequest, DetectResponse
from app.inference import detect, ROBERTA_ID, DISTIL_ID, MIN_WORDS, ABSTAIN_LOW, ABSTAIN_HIGH, W_ROBERTA, W_DISTIL, W_COMP

app = FastAPI(title="Local AI Text Detector (Ensemble)")

origins = [
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://app.rohitmachigad.space:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/meta")
def meta():
    return {
        "models": {"roberta": ROBERTA_ID, "distil": DISTIL_ID},
        "offline": os.getenv("HF_HUB_OFFLINE", "false"),
        "weights": {"roberta": W_ROBERTA, "distil": W_DISTIL, "compress": W_COMP},
        "guards": {"min_words": MIN_WORDS, "abstain_band": [ABSTAIN_LOW, ABSTAIN_HIGH]},
    }

@app.post("/detect", response_model=DetectResponse)
def detect_endpoint(req: DetectRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    p_ai, info = detect(text)
    p_human = 1.0 - p_ai

    meta = info.get("meta", {}) or {}
    votes = {
        "roberta": meta.get("roberta", None),
        "distil": meta.get("distil", None),
        "compress": meta.get("compress", None),
        "borderline": bool(meta.get("borderline", False)),
    }
    abstain = bool(info.get("abstain", False))
    decision = "inconclusive" if abstain else ("ai" if p_ai >= 0.5 else "human")

    return DetectResponse(
        proba_ai=round(float(p_ai), 4),
        proba_human=round(float(p_human), 4),
        decision=decision,
        votes=votes,
        borderline=votes["borderline"],
        latency_ms=int(info.get("latency_ms", 0)),
        model_versions={"roberta": "roberta-base-openai-detector", "distil": DISTIL_ID},
    )
