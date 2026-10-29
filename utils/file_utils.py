import os
import re
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".ts"}

def natural_sort_key(s: str):
    """Sort strings containing numbers naturally (e.g. EP1, EP2, ... EP10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def get_video_files(folder_path: str) -> List[Path]:
    """Scan folder for supported video files and sort them naturally."""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    
    files = []
    p = Path(folder_path)
    for f in p.iterdir():
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
            files.append(f)
            
    files.sort(key=lambda x: natural_sort_key(x.name))
    return files

def get_output_filename(video_file: Path, index: int, pattern: str = "prefix_index", prefix: str = "EP") -> str:
    """Generate output video filename based on pattern."""
    if pattern == "prefix_index":
        return f"{prefix}{index:03d}_KH.mp4"
    else:
        # Keep original stem + _KH
        return f"{video_file.stem}_KH.mp4"

def check_video_status(input_files: List[Path], output_folder: str, pattern: str = "prefix_index", prefix: str = "EP") -> Tuple[int, int, List[Dict[str, Any]]]:
    """Check which videos are already dubbed and which are remaining."""
    if not output_folder or not os.path.isdir(output_folder):
        items = [{"file": f, "status": "pending", "out_name": get_output_filename(f, i+1, pattern, prefix)} for i, f in enumerate(input_files)]
        return 0, len(input_files), items

    out_path = Path(output_folder)
    out_files = {f.name.lower() for f in out_path.iterdir() if f.is_file()}
    
    dubbed_count = 0
    items = []
    
    for i, f in enumerate(input_files):
        out_name = get_output_filename(f, i+1, pattern, prefix)
        is_done = out_name.lower() in out_files
        if is_done:
            dubbed_count += 1
            status = "done"
        else:
            status = "pending"
            
        items.append({
            "file": f,
            "status": status,
            "out_name": out_name,
            "index": i + 1
        })
        
    remaining_count = len(input_files) - dubbed_count
    return dubbed_count, remaining_count, items

def get_media_duration(file_path: str) -> float:
    """Get accurate duration of audio/video file using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        return float(res.stdout.strip())
    except Exception:
        return 0.0

def has_audio_stream(file_path: str) -> bool:
    """Check if media file has at least one audio stream using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            str(file_path)
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return "audio" in res.stdout.lower()
    except Exception:
        return False

def create_temp_dir(base_dir: str = None) -> Path:
    """Create a temporary workspace directory."""
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent / "temp"
    else:
        base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
