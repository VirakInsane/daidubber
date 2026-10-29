import os
import sys
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import subprocess
import webview

from core.config_manager import ConfigManager
from core.pipeline import DubbingPipeline
from core.translator import GeminiTranslator
from utils.logger import logger
from utils.file_utils import get_video_files, check_video_status

_current_window = None

def _evaluate_js(script: str):
    global _current_window
    if _current_window:
        try:
            _current_window.evaluate_js(script)
        except Exception:
            pass

def _pick_directory(title: str = "ជ្រើសរើស Folder") -> str:
    global _current_window
    if _current_window:
        try:
            result = _current_window.create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                return result[0]
            return ""
        except Exception as e:
            logger.warning(f"Native file dialog fallback: {e}")
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title=title)
        root.destroy()
        return folder or ""
    except Exception:
        pass
    # PowerShell native FolderBrowserDialog fallback (works on all Windows machines without Tkinter)
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "[System.Reflection.Assembly]::LoadWithPartialName('System.windows.forms') | Out-Null; "
            "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
            f"$f.Description = '{title}'; "
            "$f.ShowNewFolderButton = $true; "
            "if ($f.ShowDialog() -eq 'OK') { Write-Output $f.SelectedPath }"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
        return res.stdout.strip()
    except Exception:
        return ""

class BridgeAPI:
    """
    Bi-directional bridge between JavaScript Web UI and Python Backend.
    NOTE: All internal variables and helper methods MUST start with '_'
    so that pywebview does not inspect or expose them, preventing COM/recursion errors.
    """

    def __init__(self, config_manager: ConfigManager):
        self._config_manager = config_manager
        self._pipeline = DubbingPipeline(config_manager)
        self._is_processing = False
        self._video_files = []
        self._lock = threading.Lock()
        self._active_workers = {}
        self._completed_videos = 0

    def get_initial_state(self) -> Dict[str, Any]:
        from core.version import __version__, __release_date__, __edition__, CHANGELOG
        cfg = self._config_manager.config
        in_folder = cfg.get("last_input_folder", "")
        out_folder = cfg.get("last_output_folder", "")
        stats = self._get_folder_stats(in_folder, out_folder)
        return {
            "config": cfg,
            "stats": stats,
            "version": __version__,
            "release_date": __release_date__,
            "edition": __edition__,
            "changelog": CHANGELOG
        }

    def _get_folder_stats(self, in_folder: str, out_folder: str) -> Dict[str, Any]:
        if not in_folder or not os.path.isdir(in_folder):
            return {"total": 0, "dubbed": 0, "remaining": 0}

        self._video_files = get_video_files(in_folder)
        pattern = self._config_manager.get("output_naming_pattern", "prefix_index")
        prefix = self._config_manager.get("naming_prefix", "EP")

        dubbed, remaining, _ = check_video_status(self._video_files, out_folder, pattern, prefix)
        return {
            "total": len(self._video_files),
            "dubbed": dubbed,
            "remaining": remaining
        }

    def browse_input_folder(self) -> Optional[Dict[str, Any]]:
        folder = _pick_directory("ជ្រើសរើស Folder ដែលមានវីដេអូចិន")
        if not folder:
            return None

        self._config_manager.set("last_input_folder", folder)
        out_folder = self._config_manager.get("last_output_folder", "")
        
        if not out_folder:
            out_folder = str(Path(folder).parent / f"{Path(folder).name}_Dubbed_KH")
            self._config_manager.set("last_output_folder", out_folder)

        stats = self._get_folder_stats(folder, out_folder)
        return {
            "input_folder": folder,
            "output_folder": out_folder,
            "stats": stats
        }

    def browse_output_folder(self) -> Optional[Dict[str, Any]]:
        folder = _pick_directory("ជ្រើសរើស Folder សម្រាប់ Export វីដេអូ")
        if not folder:
            return None

        self._config_manager.set("last_output_folder", folder)
        in_folder = self._config_manager.get("last_input_folder", "")
        stats = self._get_folder_stats(in_folder, folder)
        return {
            "output_folder": folder,
            "stats": stats
        }

    def update_config(self, partial_config: Dict[str, Any]):
        for k, v in partial_config.items():
            self._config_manager.set(k, v)

    def save_settings(self, settings_dict: Dict[str, Any]):
        for k, v in settings_dict.items():
            self._config_manager.set(k, v)
        logger.info("បានរក្សាទុកការកំណត់ប្រព័ន្ធដោយជោគជ័យ។")

    def test_gemini(self, api_key: str, model_name: str) -> Dict[str, Any]:
        translator = GeminiTranslator(api_key=api_key, model_name=model_name)
        success, msg = translator.test_connection()
        return {"success": success, "message": msg}

    def open_output_folder(self):
        out_folder = self._config_manager.get("last_output_folder", "")
        if out_folder and os.path.exists(out_folder):
            os.startfile(out_folder)
        elif out_folder:
            Path(out_folder).mkdir(parents=True, exist_ok=True)
            os.startfile(out_folder)

    def start_dubbing(self):
        if self._is_processing:
            return

        in_dir = self._config_manager.get("last_input_folder", "")
        out_dir = self._config_manager.get("last_output_folder", "")

        if not in_dir or not os.path.isdir(in_dir):
            logger.error("សូមជ្រើសរើស Input Folder ដែលមានវីដេអូចិនជាមុនសិន!")
            self._notify_finished(False, "ខ្វះ Input Folder")
            return

        if not out_dir:
            logger.error("សូមជ្រើសរើស Output Folder សម្រាប់រក្សាទុកវីដេអូ!")
            self._notify_finished(False, "ខ្វះ Output Folder")
            return

        self._video_files = get_video_files(in_dir)
        pattern = self._config_manager.get("output_naming_pattern", "prefix_index")
        prefix = self._config_manager.get("naming_prefix", "EP")

        _, _, items = check_video_status(self._video_files, out_dir, pattern, prefix)
        pending = [it for it in items if it["status"] == "pending"]

        if not pending:
            logger.info("វីដេអូទាំងអស់នៅក្នុង Folder នេះត្រូវបាន Dubbed រួចរាល់ហើយ!")
            stats = self._get_folder_stats(in_dir, out_dir)
            self._notify_finished(True, "All videos already dubbed", stats)
            return

        Path(out_dir).mkdir(parents=True, exist_ok=True)
        self._is_processing = True
        self._completed_videos = 0
        self._active_workers.clear()

        max_workers = int(self._config_manager.get("max_parallel_videos", 2))
        logger.info(f"⚡ ចាប់ផ្តើមដំណើរការ {max_workers} វីដេអូស្របគ្នា (Concurrent Parallel Processing)...")

        thread = threading.Thread(target=self._run_concurrent_batch, args=(pending, out_dir, max_workers), daemon=True)
        thread.start()

    def stop_dubbing(self):
        if self._is_processing:
            self._pipeline.cancel()
            logger.warning("បានស្នើសុំបញ្ឈប់ដំណើរការ Dubbing...")

    def _run_concurrent_batch(self, pending_items: list, out_dir: str, max_workers: int):
        total_videos = len(self._video_files)
        total_pending = len(pending_items)
        out_path = Path(out_dir)

        def process_item(item):
            if self._pipeline.is_cancelled:
                return False, item

            video_file = item["file"]
            out_name = item["out_name"]
            final_out_file = out_path / out_name
            current_video_num = item["index"]
            worker_id = threading.get_ident()

            def on_progress(v_idx, v_total, stage_idx, stage_name, pct, detail):
                with self._lock:
                    self._active_workers[worker_id] = {
                        "name": video_file.name,
                        "stage": stage_name,
                        "stage_idx": stage_idx,
                        "pct": pct,
                        "detail": detail
                    }
                    self._update_aggregate_progress(total_pending, total_videos, max_workers)

            success = self._pipeline.process_single_video(
                video_path=str(video_file),
                output_path=str(final_out_file),
                video_index=current_video_num,
                total_videos=total_videos,
                progress_callback=on_progress
            )

            with self._lock:
                if worker_id in self._active_workers:
                    del self._active_workers[worker_id]
                if success:
                    self._completed_videos += 1
                    logger.success(f"Dubbed សម្រេច [{self._completed_videos}/{total_pending}]: {out_name}")
                else:
                    logger.error(f"បរាជ័យក្នុងការ Dubbed: {video_file.name}")

                self._update_aggregate_progress(total_pending, total_videos, max_workers)

            return success, item

        # Execute with thread pool concurrency
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_item, it) for it in pending_items]
            for fut in as_completed(futures):
                if self._pipeline.is_cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

        self._is_processing = False
        in_dir = self._config_manager.get("last_input_folder", "")
        stats = self._get_folder_stats(in_dir, out_dir)
        self._notify_finished(not self._pipeline.is_cancelled, "Completed", stats)

    def _update_aggregate_progress(self, total_pending: int, total_videos: int, max_workers: int):
        active_list = list(self._active_workers.values())
        num_active = len(active_list)
        
        # Calculate overall weighted progress
        active_sum = sum(w["pct"] for w in active_list)
        overall_pct = (self._completed_videos + (active_sum / max(1, max_workers))) / max(1, total_pending)
        overall_pct = min(1.0, max(0.0, overall_pct))

        if active_list:
            top_worker = active_list[0]
            stage_idx = top_worker["stage_idx"]
            stage_name = f"{num_active} វីដេអូស្របគ្នា (Stage: {top_worker['stage']})"
            names_summary = ", ".join(w["name"][:16] for w in active_list[:2])
            detail = f"[{self._completed_videos}/{total_pending} រួចរាល់] កំពុងដំណើរការ: {names_summary}..."
        else:
            stage_idx = 7
            stage_name = "Export"
            detail = f"Dubbed រួច {self._completed_videos}/{total_pending} ភាគ"

        self._notify_progress(self._completed_videos, total_videos, stage_idx, stage_name, overall_pct, detail, max_workers)

    def _notify_progress(self, v_idx, v_total, stage_idx, stage_name, pct, detail, max_workers=1):
        js = f"window.uiOnProgress({v_idx}, {v_total}, {stage_idx}, {json.dumps(stage_name)}, {pct}, {json.dumps(detail)}, {max_workers});"
        _evaluate_js(js)

    def _notify_finished(self, success, message, stats=None):
        js = f"window.uiOnFinished({json.dumps(success)}, {json.dumps(message)}, {json.dumps(stats)});"
        _evaluate_js(js)


def launch_web_app(config_manager: ConfigManager):
    global _current_window
    html_path = Path(__file__).resolve().parent / "web" / "index.html"
    if not html_path.exists() and hasattr(sys, "_MEIPASS"):
        html_path = Path(sys._MEIPASS) / "ui" / "web" / "index.html"
    api = BridgeAPI(config_manager)

    def forward_log(msg: str, level: str):
        js = f"window.uiOnLog({json.dumps(msg)}, {json.dumps(level)});"
        _evaluate_js(js)

    logger.add_listener(forward_log)

    from core.version import get_full_title
    window = webview.create_window(
        title=get_full_title(),
        url=str(html_path.resolve()),
        js_api=api,
        width=1040,
        height=890,
        min_size=(900, 750),
        background_color="#080c14"
    )
    _current_window = window

    logger.info("កំពុងបើកដំណើរការផ្ទាំងកម្មវិធីទំនើប (WebView2 Hardware Accelerated UI)...")
    webview.start(gui="edgechromium")
