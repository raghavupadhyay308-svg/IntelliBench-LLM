import platform
import subprocess
import json
import psutil
import shutil


def get_cpu_info():
    cpu = {
        "name": platform.processor() or "Unknown CPU",
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "freq_mhz": None,
        "arch": platform.machine(),
    }
    try:
        freq = psutil.cpu_freq()
        if freq:
            cpu["freq_mhz"] = round(freq.max, 0)
    except Exception:
        pass

    # Try to get a better CPU name on Windows/Linux
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output(
                "wmic cpu get Name", shell=True, text=True
            )
            lines = [l.strip() for l in result.strip().splitlines() if l.strip() and l.strip() != "Name"]
            if lines:
                cpu["name"] = lines[0]
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        cpu["name"] = line.split(":")[1].strip()
                        break
        elif platform.system() == "Darwin":
            result = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            )
            cpu["name"] = result.strip()
    except Exception:
        pass

    return cpu


def get_ram_info():
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 1),
        "available_gb": round(mem.available / (1024 ** 3), 1),
        "used_percent": mem.percent,
    }


def get_storage_info():
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024 ** 3), 1),
                "free_gb": round(usage.free / (1024 ** 3), 1),
                "fstype": part.fstype,
            })
        except Exception:
            pass
    return partitions


def get_gpu_info():
    gpus = []

    # Try NVIDIA via nvidia-smi
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        )
        for line in result.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                gpus.append({
                    "name": parts[0],
                    "vendor": "NVIDIA",
                    "vram_total_mb": int(parts[1]),
                    "vram_free_mb": int(parts[2]),
                    "vram_total_gb": round(int(parts[1]) / 1024, 1),
                    "driver_version": parts[3],
                    "cuda": True,
                })
    except Exception:
        pass

    # Try AMD via rocm-smi
    if not gpus:
        try:
            result = subprocess.check_output(
                ["rocm-smi", "--showmeminfo", "vram", "--json"],
                text=True,
                timeout=5,
            )
            data = json.loads(result)
            for card, info in data.items():
                if card.startswith("card"):
                    total = int(info.get("VRAM Total Memory (B)", 0))
                    used = int(info.get("VRAM Total Used Memory (B)", 0))
                    gpus.append({
                        "name": f"AMD GPU ({card})",
                        "vendor": "AMD",
                        "vram_total_mb": total // (1024 * 1024),
                        "vram_free_mb": (total - used) // (1024 * 1024),
                        "vram_total_gb": round(total / (1024 ** 3), 1),
                        "driver_version": "N/A",
                        "cuda": False,
                    })
        except Exception:
            pass

    # Fallback: check system GPU via platform tools
    if not gpus:
        try:
            if platform.system() == "Darwin":
                result = subprocess.check_output(
                    ["system_profiler", "SPDisplaysDataType"], text=True, timeout=5
                )
                for line in result.splitlines():
                    if "Chipset Model" in line:
                        name = line.split(":")[1].strip()
                        gpus.append({
                            "name": name,
                            "vendor": "Apple" if "Apple" in name else "Unknown",
                            "vram_total_mb": None,
                            "vram_free_mb": None,
                            "vram_total_gb": None,
                            "driver_version": "N/A",
                            "cuda": False,
                        })
                        break
            elif platform.system() == "Linux":
                result = subprocess.check_output(
                    ["lspci"], text=True, timeout=5
                )
                for line in result.splitlines():
                    if "VGA" in line or "3D" in line or "Display" in line:
                        name = line.split(":")[-1].strip()
                        gpus.append({
                            "name": name,
                            "vendor": "Unknown",
                            "vram_total_mb": None,
                            "vram_free_mb": None,
                            "vram_total_gb": None,
                            "driver_version": "N/A",
                            "cuda": False,
                        })
                        break
        except Exception:
            pass

    return gpus


def get_ollama_status():
    """Check if Ollama is installed and get list of installed models."""
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        return {"installed": False, "models": []}

    try:
        result = subprocess.check_output(
            ["ollama", "list"], text=True, timeout=5
        )
        models = []
        lines = result.strip().splitlines()
        for line in lines[1:]:  # skip header
            parts = line.split()
            if parts:
                models.append(parts[0])
        return {"installed": True, "models": models, "path": ollama_path}
    except Exception:
        return {"installed": True, "models": [], "path": ollama_path}


def scan_system():
    return {
        "os": {
            "system": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
        },
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "storage": get_storage_info(),
        "gpu": get_gpu_info(),
        "ollama": get_ollama_status(),
    }
