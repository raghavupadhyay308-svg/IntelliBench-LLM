"""
Predictor: loads trained models and runs inference for a given
(hardware_config, llm_model) pair.
"""

import os
import numpy as np
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

FEATURES = [
    "ram_gb", "vram_gb", "cpu_cores", "cpu_freq_mhz", "has_cuda",
    "model_size_gb", "model_min_ram_gb", "model_min_vram_gb", "requires_gpu"
]

TIER_NAMES  = {0: "Won't Run", 1: "Slow", 2: "Okay", 3: "Good", 4: "Great"}
TIER_COLORS = {
    0: "#ef4444",   # red
    1: "#f97316",   # orange
    2: "#f59e0b",   # amber
    3: "#10b981",   # green
    4: "#6366f1",   # indigo
}
TIER_EMOJI  = {0: "✗", 1: "▲", 2: "◆", 3: "●", 4: "★"}

_regressor  = None
_classifier = None
_meta       = None


def _load():
    global _regressor, _classifier, _meta
    if _regressor is None:
        _regressor  = joblib.load(os.path.join(MODELS_DIR, "regressor.pkl"))
        _classifier = joblib.load(os.path.join(MODELS_DIR, "classifier.pkl"))
        _meta       = joblib.load(os.path.join(MODELS_DIR, "meta.pkl"))


def _build_feature_vector(system_info, model):
    """Extract feature vector from system_info dict + model dict."""
    gpus = system_info.get("gpu", [])
    vram_gb  = 0.0
    has_cuda = 0
    if gpus:
        for g in gpus:
            if g.get("vram_total_gb"):
                vram_gb = max(vram_gb, float(g["vram_total_gb"]))
            if g.get("cuda"):
                has_cuda = 1

    cpu   = system_info.get("cpu", {})
    ram   = system_info.get("ram", {})
    cores = cpu.get("cores_logical") or cpu.get("cores_physical") or 4
    freq  = cpu.get("freq_mhz") or 2800

    return np.array([[
        float(ram.get("total_gb", 8)),
        float(vram_gb),
        float(cores),
        float(freq),
        float(has_cuda),
        float(model["size_gb"]),
        float(model["min_ram_gb"]),
        float(model["min_vram_gb"]),
        float(int(model["requires_gpu"])),
    ]])


def predict(system_info, model):
    """
    Returns a dict with:
      - tokens_per_sec   (float)
      - quality_tier     (int 0-4)
      - tier_name        (str)
      - tier_color       (hex str)
      - tier_emoji       (str)
      - tier_probs       (dict tier_name → probability)
      - score            (int 0-100, overall performance score)
      - can_run          (bool)
      - model_r2         (float, regressor confidence)
      - model_acc        (float, classifier accuracy)
    """
    _load()

    X = _build_feature_vector(system_info, model)

    tps   = float(np.clip(_regressor.predict(X)[0], 0, None))
    tier  = int(_classifier.predict(X)[0])
    probs = _classifier.predict_proba(X)[0]

    tier_probs = {
        TIER_NAMES[i]: round(float(p) * 100, 1)
        for i, p in enumerate(probs)
    }

    # Overall score 0-100
    # Weights: tier (60%) + normalized tps (40%)
    tier_score = (tier / 4) * 60
    tps_score  = min(tps / 60, 1.0) * 40
    score = int(round(tier_score + tps_score))

    return {
        "tokens_per_sec": round(tps, 1),
        "quality_tier":   tier,
        "tier_name":      TIER_NAMES[tier],
        "tier_color":     TIER_COLORS[tier],
        "tier_emoji":     TIER_EMOJI[tier],
        "tier_probs":     tier_probs,
        "score":          score,
        "can_run":        tier > 0,
        "model_r2":       _meta["reg_r2"],
        "model_acc":      _meta["cls_acc"],
    }


def predict_all(system_info, models):
    """Predict for all models, return sorted by score desc."""
    _load()
    results = []
    for model in models:
        p = predict(system_info, model)
        results.append({**model, **p})
    results.sort(key=lambda x: -x["score"])
    return results
