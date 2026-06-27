import json
import os


MODELS_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "models_db.json")


def load_models():
    with open(MODELS_DB_PATH, "r") as f:
        return json.load(f)


def recommend_models(system_info, use_case_filter=None):
    models = load_models()
    ram_gb = system_info["ram"]["total_gb"]
    gpus = system_info["gpu"]

    # Get best GPU VRAM
    vram_gb = 0
    has_cuda = False
    if gpus:
        for gpu in gpus:
            if gpu.get("vram_total_gb"):
                vram_gb = max(vram_gb, gpu["vram_total_gb"])
            if gpu.get("cuda"):
                has_cuda = True

    results = []
    for model in models:
        # Filter by use case if specified
        if use_case_filter and use_case_filter != "All":
            if use_case_filter not in model["use_cases"]:
                continue

        min_ram = model["min_ram_gb"]
        min_vram = model["min_vram_gb"]
        requires_gpu = model["requires_gpu"]

        # Determine compatibility
        ram_ok = ram_gb >= min_ram
        gpu_ok = True

        if requires_gpu:
            gpu_ok = has_cuda and vram_gb >= min_vram
        elif min_vram > 0:
            # Can run on CPU but GPU would help
            pass

        can_run = ram_ok and gpu_ok

        # Performance rating
        if can_run:
            if has_cuda and vram_gb >= min_vram:
                perf = "GPU Accelerated 🚀"
            elif ram_gb >= min_ram * 1.5:
                perf = "CPU (Comfortable)"
            else:
                perf = "CPU (Tight on RAM)"
        else:
            if not ram_ok:
                perf = f"Need {min_ram}GB RAM"
            else:
                perf = f"Need {min_vram}GB VRAM + CUDA GPU"

        results.append({
            **model,
            "can_run": can_run,
            "performance_note": perf,
            "ram_ok": ram_ok,
            "gpu_ok": gpu_ok,
        })

    # Sort: runnable first, then by size
    results.sort(key=lambda x: (not x["can_run"], x["size_gb"]))
    return results


def get_top_picks(system_info):
    """Return the single best recommendation per use case."""
    use_cases = ["Coding", "General Chat", "RAG", "Summarization"]
    picks = {}
    for uc in use_cases:
        recs = recommend_models(system_info, use_case_filter=uc)
        runnable = [r for r in recs if r["can_run"]]
        if runnable:
            picks[uc] = runnable[0]
    return picks
