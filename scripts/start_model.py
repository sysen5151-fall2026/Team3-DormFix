"""Fetch the pinned classroom model and start a loopback-only inference endpoint."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import urlopen
import zipfile

MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/" + MODEL_NAME
MODEL_SHA = "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"
ENGINES = {
    "Windows": ("llama-b12801-bin-win-cpu-x64.zip", "8d11f256ff7a3cc474d4e82a81fcb01dfefd37fee97434220187e20a1674bf16"),
    "Linux": ("llama-b12801-bin-ubuntu-x64.tar.gz", "ef3277092c1f71523f4f7c88857111af710ef7e2b4af800e8712c06a7b4db984"),
}


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def obtain(directory, name, url, expected):
    path = directory / name
    if path.exists() and digest(path) == expected:
        return path
    print("Fetching " + name, flush=True)
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as output:
        partial = Path(output.name)
        try:
            with urlopen(url, timeout=120) as response:
                shutil.copyfileobj(response, output)
        except BaseException:
            output.close()
            partial.unlink(missing_ok=True)
            raise
    try:
        if digest(partial) != expected:
            raise ValueError("SHA-256 mismatch for " + name)
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)
    return path


def main():
    system = platform.system()
    if system not in ENGINES or platform.machine().lower() not in {"amd64", "x86_64"}:
        sys.exit("Use the external local endpoint instructions for this platform.")
    cache = Path(os.environ.get("DORMFIX_MODEL_CACHE", Path.home() / ".cache" / "dormfix-ch13"))
    cache.mkdir(parents=True, exist_ok=True)
    name, expected = ENGINES[system]
    archive = obtain(cache, name, "https://github.com/ggml-org/llama.cpp/releases/download/b12801/" + name, expected)
    model = obtain(cache, MODEL_NAME, MODEL_URL, MODEL_SHA)
    # Extract into a private directory so a partially expanded archive cannot become a later run's runtime.
    with tempfile.TemporaryDirectory(dir=cache) as temp:
        if name.endswith(".zip"):
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(temp)
        else:
            with tarfile.open(archive) as bundle:
                bundle.extractall(temp, filter="data")
        executable = next(Path(temp).rglob("llama-server.exe" if system == "Windows" else "llama-server"))
        env = os.environ.copy()
        if system == "Linux":
            env["LD_LIBRARY_PATH"] = str(executable.parent) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        subprocess.run([str(executable), "-m", str(model), "--alias", "dormfix-qwen", "--host", "127.0.0.1",
                        "--port", "8081", "-c", "2048", "-t", "4", "-ngl", "0"], env=env, check=True)


if __name__ == "__main__":
    main()
