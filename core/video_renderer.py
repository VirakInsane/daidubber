import os
import subprocess
from pathlib import Path
from utils.logger import logger

class VideoRenderer:
    """Handles ultra-fast video rendering and audio-video muxing using FFmpeg and GPU acceleration."""

    def __init__(self, mode: str = "fast_copy"):
        # 'fast_copy' (-c:v copy: 3-second lossless render) or 'nvenc' (GPU accelerated re-encode)
        self.mode = mode

    def render(self, input_video: str, final_audio: str, output_video: str) -> bool:
        """
        Muxes the final dubbed audio with the original video stream.
        Utilizes direct stream copy for blazing fast rendering.
        """
        output_path = Path(output_video)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"⚡ កំពុង Render វីដេអូចុងក្រោយ (Mode: {self.mode})...")

        if self.mode == "fast_copy":
            # Blazing fast: No video re-encoding (takes ~3 seconds)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(input_video),
                "-i", str(final_audio),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_video)
            ]
        elif self.mode == "nvenc":
            # NVIDIA NVENC Hardware Accelerated encode
            cmd = [
                "ffmpeg", "-y",
                "-i", str(input_video),
                "-i", str(final_audio),
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-cq", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_video)
            ]
        else:
            # Fast CPU fallback
            cmd = [
                "ffmpeg", "-y",
                "-i", str(input_video),
                "-i", str(final_audio),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_video)
            ]

        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            if res.returncode == 0 and os.path.exists(output_video):
                file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
                logger.success(f"Render វីដេអូបានជោគជ័យល្បឿនលឿន! ទំហំ: {file_size_mb:.2f} MB")
                return True
            else:
                logger.warning(f"Fast render failed, falling back to standard copy: {res.stderr}")
                # Fallback to standard copy
                fallback_cmd = [
                    "ffmpeg", "-y",
                    "-i", str(input_video),
                    "-i", str(final_audio),
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    str(output_video)
                ]
                f_res = subprocess.run(
                    fallback_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                return f_res.returncode == 0
        except Exception as e:
            logger.error(f"Render error: {e}")
            return False
