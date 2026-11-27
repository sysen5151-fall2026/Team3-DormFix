"""Start the original DormFix model in LM Studio and verify its loaded identity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen

MODEL_REPO = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
MODEL_FILE = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
MODEL_SHA = "f2be3e1a239c12c9f3f01a962b11fb2807f8032fdb63b0a5502ea42ddef55e44"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}"
DEFAULT_MODEL = "dormfix-llama31-8b-instruct"
BASE = "http://127.0.0.1:1234"


def models(base=BASE):
    headers = {}
    if token := os.getenv("DORMFIX_LLM_API_KEY"):
        headers["Authorization"] = "Bearer " + token
    req = Request(base.rstrip("/") + "/api/v1/models", headers=headers)
    with urlopen(req, timeout=8) as reply:
        return json.load(reply)["models"]


def original(model):
    if model.get("type") != "llm":
        return False
    slug = re.compile(r"^(?:meta-)?llama-3[.-]1-8b-instruct(?:-gguf)?(?:[-@.]q[0-9a-z_.-]*)?(?:\.gguf)?$", re.I)
    for field in ("key", "display_name"):
        name = (model.get(field) or "").split("/")[-1].replace(" ", "-").replace("_", "-")
        if slug.fullmatch(name):
            return True
    return False


def loaded(base=BASE, requested=None):
    options = []
    for model in models(base):
        if original(model):
            for obj in model.get("loaded_instances", []):
                if obj.get("id"):
                    options.append((model, obj["id"]))
    if requested:
        options = [v for v in options if requested == v[1]]
    else:
        selected = [v for v in options if v[1] == DEFAULT_MODEL]
        options = selected or options
    if len(options) != 1:
        raise RuntimeError("Expected one loaded Meta Llama 3.1 8B Instruct instance. Run scripts/start_model.py or pass its exact --model ID.")
    return options[0]


def cli_path():
    exe = "lms.exe" if os.name == "nt" else "lms"
    found = shutil.which(exe)
    fallback = Path.home()/".lmstudio"/"bin"/exe
    if found or fallback.is_file():
        return found or str(fallback)
    raise RuntimeError("LM Studio CLI missing. Install LM Studio desktop or the official llmster headless package. See CHAPTER13.md.")


def stage_gguf(models_dir):
    target = models_dir / MODEL_REPO / MODEL_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            partial = Path(temp) / "weights.part"
            print("Downloading the original GGUF to the LM Studio model directory.", flush=True)
            total = 0
            with urlopen(MODEL_URL, timeout=180) as src, partial.open("wb") as dst:
                while chunk := src.read(4*1024*1024):
                    dst.write(chunk)
                    total += len(chunk)
                    if total // (256*1024*1024) != (total-len(chunk)) // (256*1024*1024):
                        print(f"Downloaded {total//(1024*1024)} MiB",flush=True)
            with partial.open("rb") as stream:
                if hashlib.file_digest(stream,"sha256").hexdigest() != MODEL_SHA:
                    raise RuntimeError("GGUF checksum mismatch. The unverified file was not installed.")
            partial.replace(target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != MODEL_SHA:
        raise RuntimeError(f"The existing file at {target} has a different digest. Choose the intended model directory.")
    print("Verified original GGUF: " + digest, flush=True)
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", action="store_true", help="disable GPU offload for the clean CPU run")
    parser.add_argument("--models-dir",type=Path,default=Path.home()/".lmstudio"/"models",
                        help="use the directory selected in LM Studio if it differs from the default")
    args = parser.parse_args()
    cli = cli_path()
    def cmd(*argv):
        subprocess.run([cli, *argv], check=True, stdin=subprocess.DEVNULL, timeout=900)
    cmd("daemon", "up")
    try:
        catalog = models()
    except OSError:
        cmd("server", "start", "--bind", "127.0.0.1", "--port", "1234")
        for attempt in range(30):
            try:
                catalog = models()
                break
            except OSError:
                if attempt == 29:
                    raise
                time.sleep(1)
    matches = [item for item in catalog if original(item)]
    sha = None
    if not matches or (args.models_dir / MODEL_REPO / MODEL_FILE).is_file():
        sha = stage_gguf(args.models_dir)
        for attempt in range(30):
            matches = [item for item in models() if original(item)]
            if matches:
                break
            time.sleep(1)
    if not matches:
        raise RuntimeError("Original weights not identified in LM Studio: " + json.dumps(
            [(m.get("key"),m.get("display_name")) for m in models()]))
    try:
        model, instance = loaded()
    except RuntimeError:
        exact = [m for m in matches if (m.get("quantization") or {}).get("name","").upper()=="Q4_K_M"]
        candidates = exact or matches
        if len(candidates) != 1:
            raise RuntimeError("Multiple Llama variants found. Load one in LM Studio and choose its ID.")
        flags = ["--gpu","off"] if args.cpu else []
        cmd("load", candidates[0]["key"], "--identifier", DEFAULT_MODEL, "--context-length", "2048", *flags)
        model, instance = loaded(requested=DEFAULT_MODEL)
    print(json.dumps({"server":BASE,"key":model["key"],"loaded_instance":instance,
                      "quantization":model.get("quantization"),"downloaded_sha256":sha}, indent=2))
    print("LM Studio is serving the original model. For the web app use: python chapter13.py --model " + json.dumps(instance))

if __name__ == "__main__":
    main()
