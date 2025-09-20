import os, time, zlib
from typing import Dict, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Cache/offline
CACHE_DIR = os.getenv("TRANSFORMERS_CACHE")
LOCAL_ONLY = os.getenv("HF_HUB_OFFLINE", "false").lower() == "true"

# Models: RoBERTa OpenAI detector + DistilBERT detector (set to a fine-tuned ID via env for best results)
ROBERTA_ID = "openai-community/roberta-base-openai-detector"
DISTIL_ID = os.getenv("DISTIL_DETECTOR_ID", "distilbert-base-uncased")  # replace with a fine-tuned 2-class checkpoint for accuracy

# Load once
roberta_tok = AutoTokenizer.from_pretrained(ROBERTA_ID, cache_dir=CACHE_DIR, local_files_only=LOCAL_ONLY)
roberta = AutoModelForSequenceClassification.from_pretrained(ROBERTA_ID, cache_dir=CACHE_DIR, local_files_only=LOCAL_ONLY)
roberta.eval()

distil_tok = AutoTokenizer.from_pretrained(DISTIL_ID, cache_dir=CACHE_DIR, local_files_only=LOCAL_ONLY)
# If using a base checkpoint (not fine-tuned), we force a 2-class head (random). Prefer a fine-tuned model to avoid noise.
distil = AutoModelForSequenceClassification.from_pretrained(
    DISTIL_ID, cache_dir=CACHE_DIR, local_files_only=LOCAL_ONLY, num_labels=2
)
distil.eval()

# Guards and weights
MIN_WORDS = int(os.getenv("MIN_WORDS", "30"))
ABSTAIN_LOW = float(os.getenv("ABSTAIN_LOW", "0.48"))
ABSTAIN_HIGH = float(os.getenv("ABSTAIN_HIGH", "0.52"))
W_ROBERTA = float(os.getenv("W_ROBERTA", "0.6"))
W_DISTIL = float(os.getenv("W_DISTIL", "0.3"))
W_COMP = float(os.getenv("W_COMP", "0.1"))

# Calibration placeholders (replace with fitted params for your domain)
CAL_A_R, CAL_B_R = float(os.getenv("CAL_A_R", "1.0")), float(os.getenv("CAL_B_R", "0.0"))
CAL_A_D, CAL_B_D = float(os.getenv("CAL_A_D", "1.0")), float(os.getenv("CAL_B_D", "0.0"))

def calibrate(p: float, a: float, b: float) -> float:
    x = a * p + b
    return 0.0 if x < 0 else 1.0 if x > 1 else float(x)

def compress_heuristic(text: str) -> float:
    if not text.strip():
        return 0.5
    raw = text.encode("utf-8", errors="ignore")
    c1 = len(zlib.compress(raw, level=1))
    c9 = len(zlib.compress(raw, level=9))
    ratio = c9 / max(1, c1)
    # Monotonic mapping: more compressible -> slightly more AI-like
    p = (1.15 - ratio) * 3.0 + 0.5
    if p < 0: p = 0.0
    if p > 1: p = 1.0
    return float(p)

@torch.inference_mode()
def score_models(text: str) -> Tuple[float, float, float]:
    # RoBERTa
    enc_r = roberta_tok(text, truncation=True, max_length=512, return_tensors="pt")
    out_r = roberta(**enc_r)
    p_r_raw = torch.softmax(out_r.logits, dim=-1)[0, 1].item()
    p_r = calibrate(p_r_raw, CAL_A_R, CAL_B_R)

    # DistilBERT
    enc_d = distil_tok(text, truncation=True, max_length=512, return_tensors="pt")
    out_d = distil(**enc_d)
    p_d_raw = torch.softmax(out_d.logits, dim=-1)[0, 1].item()
    p_d = calibrate(p_d_raw, CAL_A_D, CAL_B_D)

    # Compression
    p_c = compress_heuristic(text)

    return float(p_r), float(p_d), float(p_c)

def detect(text: str) -> Tuple[float, Dict]:
    t0 = time.time()
    words = text.strip().split()
    if len(words) < MIN_WORDS:
        meta = {"roberta": None, "distil": None, "compress": None, "borderline": False, "reason": "too_short"}
        return 0.5, {"meta": meta, "latency_ms": int((time.time() - t0) * 1000), "abstain": True}

    p_r, p_d, p_c = score_models(text)
    p_final = W_ROBERTA * p_r + W_DISTIL * p_d + W_COMP * p_c

    borderline = ABSTAIN_LOW <= p_final <= ABSTAIN_HIGH
    meta = {"roberta": round(p_r, 4), "distil": round(p_d, 4), "compress": round(p_c, 4), "borderline": borderline}
    info = {"meta": meta, "latency_ms": int((time.time() - t0) * 1000), "abstain": borderline}
    return float(p_final), info
