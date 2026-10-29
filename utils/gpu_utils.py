import os
import sys

def setup_cuda_dlls():
    """Ensure all pip-installed NVIDIA CUDA / cuBLAS / cuDNN DLLs are discoverable on Windows."""
    if sys.platform != "win32":
        return
    
    # 1. Check Python virtualenv, global site-packages, or PyInstaller frozen bundle
    search_roots = []
    if hasattr(sys, "_MEIPASS"):
        search_roots.append(sys._MEIPASS)
        search_roots.append(os.path.join(sys._MEIPASS, "nvidia"))
        search_roots.append(os.path.join(sys._MEIPASS, "torch", "lib"))
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        search_roots.append(exe_dir)
        search_roots.append(os.path.join(exe_dir, "_internal"))
        search_roots.append(os.path.join(exe_dir, "_internal", "nvidia"))
        search_roots.append(os.path.join(exe_dir, "_internal", "torch", "lib"))

    search_roots.extend([
        os.path.join(sys.prefix, "Lib", "site-packages"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Lib", "site-packages")
    ])

    for site_dir in search_roots:
        nvidia_base = os.path.join(site_dir, "nvidia")
        if os.path.exists(nvidia_base):
            for sub in ["cublas", "cudnn", "cuda_nvrtc", "cuda_runtime"]:
                bin_dir = os.path.join(nvidia_base, sub, "bin")
                if os.path.exists(bin_dir):
                    if bin_dir not in os.environ["PATH"]:
                        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                    if hasattr(os, "add_dll_directory"):
                        try:
                            os.add_dll_directory(bin_dir)
                        except Exception:
                            pass

setup_cuda_dlls()
