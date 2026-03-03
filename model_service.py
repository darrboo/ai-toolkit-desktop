from typing import Dict, Any, List


class ModelService:

    def recommend_models(self, system_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        ram = self._get_ram(system_info)
        vram = self._get_max_vram(system_info)
        gpu_backend = self._select_gpu_backend(system_info)
        cpu_flags = system_info.get("cpu", {}).get("flags", {})

        candidates = self._build_candidate_models()

        recommendations = []
        for model in candidates:
            score = self._score_model(model, ram, vram, cpu_flags)
            if score["viable"]:
                recommendations.append(
                    self._format_recommendation(
                        model, score, gpu_backend
                    )
                )

        return sorted(
            recommendations,
            key=lambda x: (x["recommended"], x["confidence"]),
            reverse=True
        )

    # -------------------------------------------------
    # Candidate Definitions
    # -------------------------------------------------

    def _build_candidate_models(self):
        return [
            {"id": "mistral-7b", "size": 7},
            {"id": "llama-13b", "size": 13},
            {"id": "llama-34b", "size": 34},
            {"id": "llama-70b", "size": 70},
        ]

    # -------------------------------------------------
    # Scoring Logic
    # -------------------------------------------------

    def _score_model(self, model, ram, vram, cpu_flags):
        size = model["size"]

        ram_required = size * 0.9
        vram_required = size * 0.6

        viable = ram >= ram_required

        confidence = 0.5

        if ram > ram_required * 1.5:
            confidence += 0.2

        if vram and vram > vram_required:
            confidence += 0.2

        if cpu_flags.get("avx2"):
            confidence += 0.1
        else:
            confidence -= 0.1

        recommended = confidence > 0.75

        return {
            "viable": viable,
            "ram_required": round(ram_required, 2),
            "vram_required": round(vram_required, 2),
            "confidence": round(max(0, min(confidence, 1)), 2),
            "recommended": recommended
        }

    # -------------------------------------------------
    # Formatting
    # -------------------------------------------------

    def _format_recommendation(self, model, score, backend):
        return {
            "id": model["id"],
            "name": f"{model['size']}B Model",
            "size_billions": model["size"],
            "quantization": "Q4_K_M",
            "ram_required_gb": score["ram_required"],
            "vram_required_gb": score["vram_required"],
            "disk_required_gb": round(model["size"] * 0.6, 2),
            "backend": backend,
            "estimated_tokens_per_sec": self._estimate_speed(
                model["size"], backend
            ),
            "recommended": score["recommended"],
            "confidence": score["confidence"],
            "reason": self._build_reason(score)
        }

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _get_ram(self, system_info):
        return system_info.get("memory", {}).get("total_gb", 0)

    def _get_max_vram(self, system_info):
        gpus = system_info.get("gpu", [])
        vram_values = [g.get("vram_gb") for g in gpus if g.get("vram_gb")]
        return max(vram_values) if vram_values else 0

    def _select_gpu_backend(self, system_info):
        gpus = system_info.get("gpu", [])

        for gpu in gpus:
            if gpu.get("vendor") == "nvidia":
                return "cuda"
            if gpu.get("vendor") == "amd":
                return "rocm"
            if gpu.get("vendor") == "intel":
                return "opencl"

        return "cpu"

    def _estimate_speed(self, size, backend):
        base = 40 / size
        if backend == "cuda":
            base *= 2
        elif backend == "cpu":
            base *= 0.8
        return round(base, 1)

    def _build_reason(self, score):
        if score["recommended"]:
            return "Fits comfortably within detected hardware."
        if score["confidence"] > 0.5:
            return "Usable but may approach system limits."
        return "Low confidence due to hardware constraints."