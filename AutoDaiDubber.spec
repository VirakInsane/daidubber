# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path(r"d:\project\AutoDaiDubber")

# 1. Collect Datas
datas = [
    (str(project_root / "ui" / "web" / "index.html"), "ui/web"),
    (str(project_root / "config.json"), "."),
    (str(project_root / "bin" / "ffmpeg.exe"), "bin"),
    (str(project_root / "bin" / "ffprobe.exe"), "bin"),
]

for pkg in ["webview", "faster_whisper", "customtkinter", "demucs"]:
    try:
        datas += collect_data_files(pkg)
    except Exception as e:
        print(f"Warning collecting data for {pkg}: {e}")

# 2. Collect Binaries (CUDA DLLs)
binaries = []
site_packages = Path(r"C:\Users\ko\AppData\Local\Programs\Python\Python312\Lib\site-packages")
nvidia_dir = site_packages / "nvidia"
if nvidia_dir.exists():
    for dll in nvidia_dir.glob("*/*/bin/*.dll"):
        binaries.append((str(dll), "."))

torch_lib = site_packages / "torch" / "lib"
if torch_lib.exists():
    for dll in torch_lib.glob("*.dll"):
        binaries.append((str(dll), "."))

# 3. Collect Hidden Imports
hiddenimports = [
    "webview",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
    "clr",
    "customtkinter",
    "darkdetect",
    "torch",
    "torchaudio",
    "demucs",
    "demucs.api",
    "demucs.separate",
    "demucs.apply",
    "demucs.pretrained",
    "faster_whisper",
    "ctranslate2",
    "edge_tts",
    "google.generativeai",
    "pydub",
    "soundfile",
    "numpy",
    "scipy",
    "scipy.signal",
    "nest_asyncio",
    "core",
    "core.audio_sync",
    "core.config_manager",
    "core.gender_detector",
    "core.pipeline",
    "core.transcriber",
    "core.translator",
    "core.tts_engine",
    "core.video_renderer",
    "core.vocal_separator",
    "ui",
    "ui.components",
    "ui.main_window",
    "ui.settings_dialog",
    "ui.styles",
    "ui.web_app",
    "utils",
    "utils.file_utils",
    "utils.gpu_utils",
    "utils.logger",
    "unittest",
    "unittest.mock"
]

try:
    hiddenimports += collect_submodules("demucs")
except Exception:
    pass

try:
    hiddenimports += collect_submodules("faster_whisper")
except Exception:
    pass

a = Analysis(
    [str(project_root / "app.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoDaiDubber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True, # Console enabled so user/logs can be seen or piped
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AutoDaiDubber',
)
