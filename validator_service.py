from typing import Dict, Any, List


class ValidatorService:

    def validate_preinstall(
        self,
        system_info: Dict[str, Any],
        selection: Dict[str, Any]
    ) -> Dict[str, Any]:

        issues = []
        warnings = []
        actions = []

        disk_required = self._estimate_disk_usage(selection)
        disk_available = system_info.get("disk", {}).get("free_gb", 0)

        # Disk validation
        if disk_available < disk_required:
            issues.append(self._disk_issue(disk_required, disk_available))

        # RAM validation
        ram_required = self._estimate_ram_usage(selection)
        ram_available = system_info.get("memory", {}).get("total_gb", 0)

        if ram_available < ram_required:
            issues.append(self._ram_issue(ram_required, ram_available))

        # CPU flags
        cpu_flags = system_info.get("cpu", {}).get("flags", {})
        if not cpu_flags.get("avx2"):
            warnings.append({
                "code": "NO_AVX2",
                "message": "CPU lacks AVX2 support. Performance may degrade."
            })

        # GPU backend validation
        backend = selection.get("build_backend")
        gpu_issues = self._validate_gpu_backend(system_info, backend)
        issues.extend(gpu_issues)

        # Toolchain validation
        toolchain_actions = self._validate_toolchain(system_info)
        actions.extend(toolchain_actions)

        ready = len(issues) == 0

        return {
            "ready": ready,
            "blocking_issues": issues,
            "warnings": warnings,
            "actions_required": actions,
            "estimated_total_disk_gb": disk_required
        }

        def _disk_issue(self, required, available):
    return {
        "code": "INSUFFICIENT_DISK",
        "message": "Not enough disk space for selected installation.",
        "required_gb": required,
        "available_gb": available,
        "fix_options": [
            "Clear cache",
            "Choose smaller model",
            "Select alternative installation path"
        ]
    }

    def _validate_gpu_backend(self, system_info, backend):
    issues = []
    gpus = system_info.get("gpu", [])

    if backend == "cuda":
        if not any(g.get("vendor") == "nvidia" for g in gpus):
            issues.append({
                "code": "CUDA_NO_NVIDIA",
                "message": "CUDA backend selected but no NVIDIA GPU detected.",
                "fix_options": ["Switch to CPU", "Install NVIDIA GPU"]
            })

    if backend == "rocm":
        if not any(g.get("vendor") == "amd" for g in gpus):
            issues.append({
                "code": "ROCM_NO_AMD",
                "message": "ROCm backend selected but no AMD GPU detected.",
                "fix_options": ["Switch to CPU"]
            })

    return issues

    def _validate_toolchain(self, system_info):
    toolchain = system_info.get("toolchain", {})
    required = ["gcc", "cmake", "make", "git"]

    actions = []

    for tool in required:
        if not toolchain.get(tool, {}).get("installed"):
            actions.append(f"Install {tool}")

    return actions

    def _estimate_disk_usage(self, selection):
    models = selection.get("models", [])
    total = 2  # base install footprint
    for model in models:
        if "13b" in model:
            total += 8
        elif "34b" in model:
            total += 20
        elif "70b" in model:
            total += 40
        else:
            total += 5
    return total


def _estimate_ram_usage(self, selection):
    models = selection.get("models", [])
    total = 0
    for model in models:
        if "13b" in model:
            total += 12
        elif "34b" in model:
            total += 28
        elif "70b" in model:
            total += 60
        else:
            total += 6
    return total

    