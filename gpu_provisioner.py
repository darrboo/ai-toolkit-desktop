from enum import Enum

class BackendStrategy(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    SYCL = "sycl"
    OPENCL = "opencl"

    class GPUProvisioner:

    def detect_best_backend(self, system_info) -> BackendStrategy

    def validate_backend(self, backend, system_info) -> dict

    def install_backend(self, backend) -> Generator[dict, None, None]

 def detect_best_backend(self, system_info):

    gpus = system_info.get("gpu", [])

    for gpu in gpus:
        vendor = gpu.get("vendor", "").lower()

        if "nvidia" in vendor:
            return BackendStrategy.CUDA

        if "amd" in vendor:
            return BackendStrategy.ROCM

        if "intel" in vendor:
            if "arc" in gpu.get("model", "").lower():
                return BackendStrategy.SYCL

    return BackendStrategy.CPU

 def _install_cuda(self):

    yield progress("cuda", "Installing CUDA toolkit")

    cmds = [
        ["pkexec", "apt", "install", "-y",
         "nvidia-cuda-toolkit"]
    ]

    for cmd in cmds:
        yield self._run_stream(cmd)

def _build_llama(self, backend):

    flags = []

    if backend == "cuda":
        flags.append("LLAMA_CUBLAS=1")

    elif backend == "rocm":
        flags.append("LLAMA_HIPBLAS=1")

    elif backend == "sycl":
        flags.append("LLAMA_SYCL=1")

    cmd = ["make"] + flags

    