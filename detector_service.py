import os
import platform
import subprocess
import shutil
import socket
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None


class DetectorService:
    """
    Collects normalized system information for Debian derivatives.
    All methods return structured dictionaries and never raise unhandled exceptions.
    """

    # ------------------------------
    # Public Entry Point
    # ------------------------------

    def scan(self) -> Dict[str, Any]:
        return {
            "os": self._safe(self.detect_os),
            "cpu": self._safe(self.detect_cpu),
            "memory": self._safe(self.detect_memory),
            "disk": self._safe(lambda: self.detect_disk("/")),
            "gpu": self._safe(self.detect_gpu, default=[]),
            "runtimes": self._safe(self.detect_runtimes),
            "toolchain": self._safe(self.detect_toolchain),
            "network": self._safe(self.detect_network),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ------------------------------
    # Core Detection Methods
    # ------------------------------

    def detect_os(self) -> Dict[str, Any]:
        os_release = self._parse_os_release()
        return {
            "name": os_release.get("NAME"),
            "version": os_release.get("VERSION_ID"),
            "codename": os_release.get("VERSION_CODENAME"),
            "kernel": platform.release(),
            "architecture": platform.machine(),
            "is_debian_derivative": "debian" in (os_release.get("ID", "") or "").lower()
        }

    def detect_cpu(self) -> Dict[str, Any]:
        cpuinfo = self._run(["lscpu"])
        flags = self._parse_cpu_flags()

        return {
            "model": self._extract_field(cpuinfo, "Model name"),
            "cores_physical": psutil.cpu_count(logical=False) if psutil else None,
            "cores_logical": psutil.cpu_count(logical=True) if psutil else os.cpu_count(),
            "frequency_mhz": psutil.cpu_freq().current if psutil and psutil.cpu_freq() else None,
            "flags": {
                "avx": "avx" in flags,
                "avx2": "avx2" in flags,
                "avx512": any(f.startswith("avx512") for f in flags),
                "fma": "fma" in flags
            }
        }

    def detect_memory(self) -> Dict[str, Any]:
        if psutil:
            vm = psutil.virtual_memory()
            sm = psutil.swap_memory()
            return {
                "total_gb": round(vm.total / 1e9, 2),
                "available_gb": round(vm.available / 1e9, 2),
                "swap_total_gb": round(sm.total / 1e9, 2),
                "swap_free_gb": round(sm.free / 1e9, 2)
            }

        # Fallback
        return {"error": "psutil not installed"}

    def detect_disk(self, path: str = "/") -> Dict[str, Any]:
        usage = shutil.disk_usage(path)
        return {
            "mount_point": path,
            "total_gb": round(usage.total / 1e9, 2),
            "free_gb": round(usage.free / 1e9, 2),
            "filesystem": self._get_filesystem_type(path)
        }

    def detect_gpu(self) -> List[Dict[str, Any]]:
        gpus = []
        gpus.extend(self._detect_nvidia())
        gpus.extend(self._detect_amd())
        gpus.extend(self._detect_intel())
        return gpus

    def detect_runtimes(self) -> Dict[str, Any]:
        return {
            "cuda": self._detect_cuda(),
            "rocm": self._detect_rocm(),
            "opencl": self._detect_opencl(),
            "vulkan": self._detect_vulkan()
        }

    def detect_toolchain(self) -> Dict[str, Any]:
        return {
            "gcc": self._detect_binary_version("gcc"),
            "cmake": self._detect_binary_version("cmake"),
            "make": self._detect_binary_version("make"),
            "git": self._detect_binary_version("git")
        }

    def detect_network(self) -> Dict[str, Any]:
        try:
            socket.create_connection(("github.com", 443), timeout=3)
            return {"online": True, "github_reachable": True}
        except Exception:
            return {"online": False, "github_reachable": False}

    # ------------------------------
    # GPU Vendor Detection
    # ------------------------------

    def _detect_nvidia(self) -> List[Dict[str, Any]]:
        if not shutil.which("nvidia-smi"):
            return []

        output = self._run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                            "--format=csv,noheader"])
        gpus = []

        for line in output.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                gpus.append({
                    "vendor": "nvidia",
                    "name": parts[0],
                    "vram_gb": round(float(parts[1].split()[0]) / 1024, 2),
                    "driver_version": parts[2],
                    "cuda_available": True,
                    "rocm_available": False,
                    "opencl_available": self._binary_exists("clinfo"),
                    "vulkan_available": self._binary_exists("vulkaninfo")
                })
        return gpus

    def _detect_amd(self) -> List[Dict[str, Any]]:
        if not shutil.which("rocminfo"):
            return []

        return [{
            "vendor": "amd",
            "name": "AMD GPU",
            "vram_gb": None,
            "driver_version": None,
            "cuda_available": False,
            "rocm_available": True,
            "opencl_available": self._binary_exists("clinfo"),
            "vulkan_available": self._binary_exists("vulkaninfo")
        }]

    def _detect_intel(self) -> List[Dict[str, Any]]:
        lspci = self._run(["lspci"])
        if "VGA compatible controller: Intel" not in lspci:
            return []

        return [{
            "vendor": "intel",
            "name": "Intel Integrated Graphics",
            "vram_gb": None,
            "driver_version": None,
            "cuda_available": False,
            "rocm_available": False,
            "opencl_available": self._binary_exists("clinfo"),
            "vulkan_available": self._binary_exists("vulkaninfo")
        }]

    # ------------------------------
    # Runtime Detection
    # ------------------------------

    def _detect_cuda(self) -> Dict[str, Any]:
        return {
            "installed": shutil.which("nvcc") is not None,
            "version": self._get_binary_version("nvcc")
        }

    def _detect_rocm(self) -> Dict[str, Any]:
        return {
            "installed": shutil.which("rocminfo") is not None,
            "version": self._get_binary_version("rocminfo")
        }

    def _detect_opencl(self) -> Dict[str, Any]:
        return {
            "installed": shutil.which("clinfo") is not None
        }

    def _detect_vulkan(self) -> Dict[str, Any]:
        return {
            "installed": shutil.which("vulkaninfo") is not None
        }

    # ------------------------------
    # Helpers
    # ------------------------------

    def _run(self, cmd: List[str]) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        except Exception:
            return ""

    def _safe(self, fn, default=None):
        try:
            return fn()
        except Exception as e:
            return default if default is not None else {"error": str(e)}

    def _binary_exists(self, name: str) -> bool:
        return shutil.which(name) is not None

    def _detect_binary_version(self, name: str) -> Dict[str, Any]:
        if not self._binary_exists(name):
            return {"installed": False, "version": None}
        return {
            "installed": True,
            "version": self._get_binary_version(name)
        }

    def _get_binary_version(self, name: str) -> Optional[str]:
        output = self._run([name, "--version"])
        return output.split("\n")[0] if output else None

    def _parse_os_release(self) -> Dict[str, str]:
        data = {}
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        data[k] = v.strip('"')
        return data

    def _parse_cpu_flags(self) -> List[str]:
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("flags"):
                        return line.split(":")[1].strip().split()
        except Exception:
            pass
        return []

    def _extract_field(self, text: str, field: str) -> Optional[str]:
        for line in text.splitlines():
            if field in line:
                return line.split(":")[1].strip()
        return None

    def _get_filesystem_type(self, path: str) -> Optional[str]:
        try:
            return self._run(["df", "-T", path]).splitlines()[1].split()[1]
        except Exception:
            return None