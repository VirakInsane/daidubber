import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 output encoding for Khmer & Chinese characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Handle PyInstaller frozen environment
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
else:
    PROJECT_ROOT = Path(__file__).resolve().parent
    BUNDLE_DIR = PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BUNDLE_DIR) not in sys.path:
    sys.path.insert(0, str(BUNDLE_DIR))

# Ensure bundled ffmpeg/ffprobe in bin/ are in PATH
for cand_bin in [BUNDLE_DIR / "bin", PROJECT_ROOT / "bin"]:
    if (cand_bin / "ffmpeg.exe").exists():
        os.environ["PATH"] = str(cand_bin) + os.pathsep + os.environ.get("PATH", "")
        break

from utils.gpu_utils import setup_cuda_dlls
setup_cuda_dlls()

from core.config_manager import ConfigManager
from utils.logger import logger

def main():
    logger.info("🎬 កំពុងចាប់ផ្តើមកម្មវិធី JAI AUTO DUBBING...")
    config_mgr = ConfigManager(PROJECT_ROOT)

    # Try launching Modern Animated WebView2 UI first (Pixel-perfect matching preview)
    try:
        from ui.web_app import launch_web_app
        launch_web_app(config_mgr)
    except Exception as e:
        logger.warning(f"WebView2 initialization fallback ({e}), starting CustomTkinter interface...")
        from ui.main_window import MainWindow
        app = MainWindow(config_mgr)
        app.mainloop()

if __name__ == "__main__":
    main()
