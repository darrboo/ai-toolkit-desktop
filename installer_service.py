import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Generator


class InstallerService:

    def __init__(self):
        self.base_dir = Path.home() / ".local/share/ai-toolkit"
        self.cache_dir = Path.home() / ".cache/ai-toolkit"
        self.repo_dir = self.base_dir / "repos"
        self.model_dir = self.base_dir / "models"
        self.build_dir = self.base_dir / "build"

        self._ensure_directories()

def _ensure_directories(self):
        for d in [
            self.base_dir,
            self.cache_dir,
            self.repo_dir,
            self.model_dir,
            self.build_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

def run_installation(
        self,
        selection: Dict[str, Any],
        system_info: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:

        # 1. Dependencies
        yield from self._install_dependencies_phase()

        # 2. Clone repositories
        yield from self._clone_phase()

        # 3. Build components
        backend = selection.get("build_backend", "cpu")
        yield from self._build_phase(backend)

        # 4. Download models
        for model in selection.get("models", []):
            yield from self._download_model_phase(model)

        yield {
            "component": "installation",
            "step": "complete",
            "status": "success",
            "message": "Installation complete"
        }

def _install_dependencies_phase(self):
        packages = [
            "build-essential",
            "cmake",
            "git",
            "python3-venv"
        ]

        yield {
            "component": "system",
            "step": "dependencies",
            "status": "running",
            "message": "Installing required packages"
        }

        cmd = ["pkexec", "apt", "install", "-y"] + packages
        result = self._run(cmd)

        if result["success"]:
            yield {
                "component": "system",
                "step": "dependencies",
                "status": "success",
                "message": "Dependencies installed"
            }
        else:
            yield {
                "component": "system",
                "step": "dependencies",
                "status": "failed",
                "message": result["error"]
            }
            return

def _clone_phase(self):
        repos = {
            "llama.cpp": "https://github.com/ggerganov/llama.cpp",
            "memU": "https://github.com/NevaMind-AI/memU",
            "zeroclaw": "https://github.com/openagen/zeroclaw"
        }

        for name, url in repos.items():
            target = self.repo_dir / name

            yield {
                "component": name,
                "step": "clone",
                "status": "running",
                "message": f"Cloning {name}"
            }

            if target.exists():
                result = self._run(["git", "-C", str(target), "pull"])
            else:
                result = self._run(["git", "clone", url, str(target)])

            yield {
                "component": name,
                "step": "clone",
                "status": "success" if result["success"] else "failed",
                "message": result.get("error", "Repository ready")
            }                        

def _build_phase(self, backend: str):

        yield from self._build_llama(backend)
        yield from self._build_memu()
        yield from self._build_zeroclaw()

def _build_llama(self, backend: str):
        path = self.repo_dir / "llama.cpp"

        yield {
            "component": "llama.cpp",
            "step": "build",
            "status": "running",
            "message": f"Building with backend: {backend}"
        }

        env = os.environ.copy()

        if backend == "cuda":
            env["LLAMA_CUBLAS"] = "1"

        result = self._run(
            ["make"],
            cwd=path,
            env=env
        )

        yield {
            "component": "llama.cpp",
            "step": "build",
            "status": "success" if result["success"] else "failed",
            "message": result.get("error", "Build complete")
        } 

            def _download_model_phase(self, model_id: str):

        model_path = self.model_dir / model_id

        if model_path.exists():
            yield {
                "component": model_id,
                "step": "download",
                "status": "success",
                "message": "Model already cached"
            }
            return

        yield {
            "component": model_id,
            "step": "download",
            "status": "running",
            "message": "Downloading model"
        }

        # Placeholder URL logic
        url = f"https://example.com/models/{model_id}.gguf"
        result = self._run(["wget", "-O", str(model_path), url])

        yield {
            "component": model_id,
            "step": "download",
            "status": "success" if result["success"] else "failed",
            "message": result.get("error", "Download complete")
        }

     def _run(self, cmd, cwd=None, env=None):
        try:
            subprocess.check_output(
                cmd,
                cwd=cwd,
                env=env,
                stderr=subprocess.STDOUT,
                text=True
            )
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.output
            }
                   