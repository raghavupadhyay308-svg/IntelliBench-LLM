import subprocess
import time
import threading


TEST_PROMPT = "Explain what a neural network is in exactly 3 sentences."


def run_benchmark(model_tag: str, progress_callback=None, result_callback=None):
    """
    Run a quick inference benchmark using ollama CLI.
    Calls result_callback(dict) when done.
    """
    def _run():
        try:
            if progress_callback:
                progress_callback("Starting Ollama...")

            start_time = time.time()
            process = subprocess.Popen(
                ["ollama", "run", model_tag, TEST_PROMPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            output_tokens = []
            first_token_time = None

            if progress_callback:
                progress_callback("Generating response...")

            for char in iter(lambda: process.stdout.read(1), ""):
                if first_token_time is None:
                    first_token_time = time.time()
                output_tokens.append(char)

            process.wait()
            end_time = time.time()

            output_text = "".join(output_tokens).strip()
            stderr_text = process.stderr.read() if process.stderr else ""

            if process.returncode != 0 or not output_text:
                if result_callback:
                    result_callback({
                        "success": False,
                        "error": stderr_text or "No output received from model.",
                        "model": model_tag,
                    })
                return

            total_time = end_time - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_time

            # Rough token count (approx 4 chars per token)
            approx_tokens = len(output_text) / 4
            tokens_per_sec = approx_tokens / total_time if total_time > 0 else 0

            if result_callback:
                result_callback({
                    "success": True,
                    "model": model_tag,
                    "output": output_text,
                    "total_time_sec": round(total_time, 2),
                    "time_to_first_token_sec": round(ttft, 2),
                    "approx_tokens": int(approx_tokens),
                    "tokens_per_sec": round(tokens_per_sec, 1),
                    "prompt": TEST_PROMPT,
                })

        except FileNotFoundError:
            if result_callback:
                result_callback({
                    "success": False,
                    "error": "Ollama not found. Please install Ollama first.",
                    "model": model_tag,
                })
        except Exception as e:
            if result_callback:
                result_callback({
                    "success": False,
                    "error": str(e),
                    "model": model_tag,
                })

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
