"""
Synthetic dataset generator for LLM Bench ML models.

Each row = one (hardware_config, llm_model) pair with:
  - Features: ram_gb, vram_gb, cpu_cores, cpu_freq_mhz, has_cuda, model_size_gb,
               model_min_ram_gb, model_min_vram_gb, requires_gpu
  - Target 1: tokens_per_sec  (regression)
  - Target 2: quality_tier    (classification: 0=Won't Run, 1=Slow, 2=Okay, 3=Good, 4=Great)

Physics-based rules with realistic noise to simulate real variance.
"""

import numpy as np
import pandas as pd
import json
import os
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

MODELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "models_db.json")


def load_models():
    with open(MODELS_PATH) as f:
        return json.load(f)


def generate_hardware_configs(n=800):
    """
    Generate realistic PC/laptop hardware configurations.
    Weighted toward common student/budget configs.
    """
    configs = []

    tiers = [
        # (weight, ram_range, vram_range, cores_range, freq_range, has_cuda)
        (0.20, (2, 4),   (0, 0),   (2, 4),  (1800, 2400), False),   # Ultra low-end (old laptops)
        (0.25, (4, 8),   (0, 0),   (4, 6),  (2000, 2800), False),   # Low-end (budget laptops)
        (0.20, (8, 8),   (0, 4),   (6, 8),  (2400, 3200), False),   # Mid laptop, no GPU
        (0.10, (8, 16),  (4, 6),   (6, 8),  (2800, 3500), True),    # Mid laptop + GPU
        (0.10, (16, 16), (6, 8),   (8, 12), (3000, 3800), True),    # Mid desktop
        (0.07, (16, 32), (8, 12),  (8, 16), (3200, 4200), True),    # High-end desktop
        (0.05, (32, 64), (12, 16), (12, 16),(3500, 4800), True),    # Workstation
        (0.03, (64, 96), (16, 24), (16, 32),(4000, 5000), True),    # Server-class
    ]

    weights = [t[0] for t in tiers]
    for _ in range(n):
        tier = random.choices(tiers, weights=weights)[0]
        _, ram_r, vram_r, cores_r, freq_r, has_cuda = tier

        ram = random.choice([2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96])
        ram = max(ram_r[0], min(ram_r[1], ram))
        ram = random.choice([r for r in [2,4,6,8,12,16,24,32,48,64,96]
                             if ram_r[0] <= r <= ram_r[1]] or [ram_r[0]])

        vram = 0
        if has_cuda:
            vram = random.choice([r for r in [2,4,6,8,10,12,16,24]
                                  if vram_r[0] <= r <= vram_r[1]] or [vram_r[0]])

        cores = int(np.clip(np.random.randint(cores_r[0], cores_r[1]+1), cores_r[0], cores_r[1]))
        freq  = int(np.random.uniform(freq_r[0], freq_r[1]))

        configs.append({
            "ram_gb":       ram,
            "vram_gb":      vram,
            "cpu_cores":    cores,
            "cpu_freq_mhz": freq,
            "has_cuda":     int(has_cuda),
        })
    return configs


def predict_tokens_per_sec(hw, model):
    """
    Physics-inspired formula for tokens/sec prediction.
    Based on:
    - Memory bandwidth (RAM speed proxy via freq * cores)
    - Whether model fits in VRAM (GPU path) vs RAM (CPU path)
    - Model size (larger = slower)
    - Quantization assumption (4-bit for Ollama models)
    """
    ram        = hw["ram_gb"]
    vram       = hw["vram_gb"]
    cores      = hw["cpu_cores"]
    freq       = hw["cpu_freq_mhz"]
    has_cuda   = hw["has_cuda"]
    model_size = model["size_gb"]
    min_ram    = model["min_ram_gb"]
    min_vram   = model["min_vram_gb"]
    req_gpu    = model["requires_gpu"]

    # Can't run at all
    if ram < min_ram:
        return 0.0
    if req_gpu and (not has_cuda or vram < min_vram):
        return 0.0

    # GPU path: model fits in VRAM
    if has_cuda and vram >= model_size * 0.9:
        base = 80.0
        # Scale by VRAM headroom
        vram_ratio = vram / (model_size + 1e-6)
        speed = base * np.log1p(vram_ratio) * (freq / 3000) * 0.8
        # Larger models are slower even on GPU
        size_penalty = 1.0 / (1.0 + model_size / 20.0)
        tps = speed * size_penalty

    # Partial GPU offload
    elif has_cuda and vram > 2:
        offload_ratio = min(vram / model_size, 0.8)
        cpu_speed = (cores * freq / 1000) * 0.4 / (model_size + 1)
        gpu_boost = offload_ratio * 30
        tps = cpu_speed + gpu_boost

    # Pure CPU path
    else:
        # Memory bandwidth proxy
        mem_bandwidth = cores * (freq / 1000) * 1.2
        # Tokens/sec drops fast with model size on CPU
        tps = mem_bandwidth / (model_size * 1.8 + 2)
        # RAM headroom helps (prevents swapping)
        ram_ratio = ram / (min_ram + 1e-6)
        if ram_ratio < 1.2:
            tps *= 0.5   # tight RAM penalty
        elif ram_ratio > 2.0:
            tps *= 1.15  # comfortable RAM bonus

    # Add realistic noise (±20%)
    noise = np.random.normal(1.0, 0.15)
    tps = max(0.1, tps * noise)
    return round(tps, 2)


def tps_to_tier(tps, can_run):
    """Convert tokens/sec to quality tier label."""
    if not can_run or tps < 0.5:
        return 0  # Won't Run
    elif tps < 3:
        return 1  # Slow
    elif tps < 8:
        return 2  # Okay
    elif tps < 20:
        return 3  # Good
    else:
        return 4  # Great


TIER_NAMES = {0: "Won't Run", 1: "Slow", 2: "Okay", 3: "Good", 4: "Great"}


def generate_dataset(n_hw=800):
    models = load_models()
    hw_configs = generate_hardware_configs(n_hw)

    rows = []
    for hw in hw_configs:
        # Sample a random subset of models per hardware config
        sampled = random.sample(models, min(len(models), random.randint(8, 20)))
        for model in sampled:
            tps = predict_tokens_per_sec(hw, model)
            can_run = tps > 0
            tier = tps_to_tier(tps, can_run)

            rows.append({
                # Hardware features
                "ram_gb":           hw["ram_gb"],
                "vram_gb":          hw["vram_gb"],
                "cpu_cores":        hw["cpu_cores"],
                "cpu_freq_mhz":     hw["cpu_freq_mhz"],
                "has_cuda":         hw["has_cuda"],
                # Model features
                "model_size_gb":    model["size_gb"],
                "model_min_ram_gb": model["min_ram_gb"],
                "model_min_vram_gb":model["min_vram_gb"],
                "requires_gpu":     int(model["requires_gpu"]),
                # Targets
                "tokens_per_sec":   tps,
                "quality_tier":     tier,
                "tier_name":        TIER_NAMES[tier],
            })

    df = pd.DataFrame(rows)
    out = os.path.join(os.path.dirname(__file__), "dataset.csv")
    df.to_csv(out, index=False)
    print(f"Generated {len(df)} samples → {out}")
    print(f"\nTier distribution:\n{df['tier_name'].value_counts()}")
    print(f"\nTokens/sec stats (runnable only):")
    runnable = df[df["tokens_per_sec"] > 0]
    print(runnable["tokens_per_sec"].describe().round(2))
    return df


if __name__ == "__main__":
    generate_dataset()
