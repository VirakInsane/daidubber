import os
import sys
import json
import time
import shutil
import zipfile
import threading
import subprocess
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Default installation directory in LocalAppData (no admin rights needed!)
DEFAULT_INSTALL_DIR = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "AutoDaiDubber"

# Cloud pre-built package URL (Can be replaced with your Google Drive / GitHub Release direct link)
# e.g. "https://github.com/your-repo/AutoDaiDubber/releases/download/v1.0/AutoDaiDubber_Bundle.zip"
DEFAULT_CLOUD_URL = "" 

# Official Python 3.12 Embeddable 64-bit package from python.org (~11 MB)
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.12.9/python-3.12.9-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

# FFmpeg 64-bit essentials build from gyan.dev (~35 MB)
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

class ModernInstallerUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            from core.version import __version__
            v_str = f" Setup v{__version__}"
        except Exception:
            v_str = " - Web Installer"
        self.root.title(f"JAI AUTO DUBBING{v_str} 🎬⚡")
        self.root.geometry("620x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#080c14")

        # Set window icon if available
        base_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
        ico_file = base_dir / "assets" / "icons" / "app.ico"
        if ico_file.exists():
            try:
                self.root.iconbitmap(str(ico_file))
            except Exception:
                pass

        # Center window on screen
        self.center_window()

        self.install_dir = DEFAULT_INSTALL_DIR
        self.is_cancelled = False
        self.is_installing = False

        self._build_ui()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2) - 30
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header banner frame
        header_frame = tk.Frame(self.root, bg="#0d1424", height=110)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Title icon and text
        title_label = tk.Label(
            header_frame,
            text="🎬 JAI AUTO DUBBING",
            font=("Segoe UI", 18, "bold"),
            fg="#60a5fa",
            bg="#0d1424"
        )
        title_label.pack(anchor="w", padx=25, pady=(16, 2))

        subtitle_label = tk.Label(
            header_frame,
            text="កម្មវិធីដំឡើងស្វ័យប្រវត្តិ (AI Chinese to Khmer Auto-Setup)",
            font=("Khmer OS Siemreap", 10),
            fg="#94a3b8",
            bg="#0d1424"
        )
        subtitle_label.pack(anchor="w", padx=25)

        # Main content area
        content_frame = tk.Frame(self.root, bg="#080c14")
        content_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Status header
        self.status_title = tk.Label(
            content_frame,
            text="ត្រៀមដំឡើងកម្មវិធី JAI AUTO DUBBING",
            font=("Khmer OS Siemreap", 12, "bold"),
            fg="#f8fafc",
            bg="#080c14"
        )
        self.status_title.pack(anchor="w", pady=(0, 6))

        # Description / Step label
        self.status_detail = tk.Label(
            content_frame,
            text="កម្មវិធីនឹងទាញយក និងដំឡើង Python Runtime, AI Models, និង FFmpeg ស្វ័យប្រវត្តិ។",
            font=("Khmer OS Siemreap", 9),
            fg="#94a3b8",
            bg="#080c14",
            wraplength=570,
            justify="left"
        )
        self.status_detail.pack(anchor="w", pady=(0, 15))

        # Destination path box
        dest_box = tk.Frame(content_frame, bg="#131d31", bd=1, relief="solid")
        dest_box.pack(fill="x", pady=(0, 15), ipady=6, ipadx=10)

        dest_title = tk.Label(
            dest_box,
            text="📁 ទីតាំងដំឡើង (Install Path):",
            font=("Khmer OS Siemreap", 8, "bold"),
            fg="#64748b",
            bg="#131d31"
        )
        dest_title.pack(anchor="w")

        self.dest_label = tk.Label(
            dest_box,
            text=str(self.install_dir),
            font=("Consolas", 9),
            fg="#38bdf8",
            bg="#131d31"
        )
        self.dest_label.pack(anchor="w", pady=(2, 0))

        # Progress bar container
        prog_container = tk.Frame(content_frame, bg="#080c14")
        prog_container.pack(fill="x", pady=(5, 5))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#1e293b",
            background="#3b82f6",
            bordercolor="#1e293b",
            lightcolor="#60a5fa",
            darkcolor="#2563eb"
        )

        self.progress_bar = ttk.Progressbar(
            prog_container,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            length=570
        )
        self.progress_bar.pack(fill="x", ipady=4)

        # Progress percentage and details
        info_frame = tk.Frame(content_frame, bg="#080c14")
        info_frame.pack(fill="x", pady=(4, 15))

        self.speed_label = tk.Label(
            info_frame,
            text="រង់ចាំការចាប់ផ្តើម...",
            font=("Segoe UI", 9),
            fg="#64748b",
            bg="#080c14"
        )
        self.speed_label.pack(side="left")

        self.percent_label = tk.Label(
            info_frame,
            text="0%",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#080c14"
        )
        self.percent_label.pack(side="right")

        # Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#080c14")
        btn_frame.pack(fill="x", side="bottom", padx=25, pady=(0, 20))

        self.cancel_btn = tk.Button(
            btn_frame,
            text="បោះបង់ (Cancel)",
            font=("Khmer OS Siemreap", 9),
            bg="#1e293b",
            fg="#cbd5e1",
            activebackground="#334155",
            activeforeground="#f8fafc",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.on_cancel
        )
        self.cancel_btn.pack(side="right", padx=(10, 0))

        self.start_btn = tk.Button(
            btn_frame,
            text="🚀 ចាប់ផ្តើមដំឡើង (Install Now)",
            font=("Khmer OS Siemreap", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.start_installation
        )
        self.start_btn.pack(side="right")

        # Check if already installed
        if (self.install_dir / "AutoDaiDubber.exe").exists() or (self.install_dir / "app.py").exists():
            self.status_title.config(text="កម្មវិធីត្រូវបានដំឡើងរួចរាល់ហើយ!")
            self.status_detail.config(text="បានរកឃើញកម្មវិធី JAI AUTO DUBBING ក្នុងកុំព្យូទ័ររបស់អ្នករួចជាស្រេច។")
            self.start_btn.config(text="⚡ បើកកម្មវិធី (Launch App)", bg="#10b981", activebackground="#059669")
            self.progress_bar["value"] = 100
            self.percent_label.config(text="100%")
            self.speed_label.config(text="រួចរាល់សម្រាប់ដំណើរការ")

    def update_status(self, title: str, detail: str, pct: float, speed_info: str = ""):
        def _update():
            self.status_title.config(text=title)
            self.status_detail.config(text=detail)
            self.progress_bar["value"] = pct
            self.percent_label.config(text=f"{int(pct)}%")
            if speed_info:
                self.speed_label.config(text=speed_info)
        self.root.after(0, _update)

    def on_cancel(self):
        if self.is_installing:
            if messagebox.askyesno("បញ្ជាក់", "តើអ្នកពិតជាចង់បោះបង់ការដំឡើងមែនទេ?"):
                self.is_cancelled = True
                self.root.destroy()
        else:
            self.root.destroy()

    def start_installation(self):
        # If already installed, launch directly!
        exe_path = self.install_dir / "AutoDaiDubber.exe"
        if exe_path.exists():
            subprocess.Popen([str(exe_path)], cwd=str(self.install_dir))
            self.root.destroy()
            return

        py_launcher = self.install_dir / "python" / "pythonw.exe"
        app_py = self.install_dir / "app.py"
        if py_launcher.exists() and app_py.exists():
            subprocess.Popen([str(py_launcher), str(app_py)], cwd=str(self.install_dir))
            self.root.destroy()
            return

        # Start background installation thread
        self.start_btn.config(state="disabled", bg="#475569")
        self.is_installing = True
        threading.Thread(target=self._run_install_worker, daemon=True).start()

    def _download_file(self, url: str, dest_path: Path, step_title: str):
        """Downloads a remote file with real-time speed and progress calculation."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "AutoDaiDubber-Installer/1.0"})
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            start_time = time.time()
            last_update = 0

            while not self.is_cancelled:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                now = time.time()

                if now - last_update > 0.2:
                    last_update = now
                    elapsed = max(now - start_time, 0.001)
                    speed_mb = (downloaded / (1024 * 1024)) / elapsed
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        speed_str = f"ល្បឿន: {speed_mb:.1f} MB/s ({mb_done:.1f} MB / {mb_total:.1f} MB)"
                        self.update_status(step_title, f"កំពុងទាញយក: {dest_path.name}", pct, speed_str)
                    else:
                        mb_done = downloaded / (1024 * 1024)
                        self.update_status(step_title, f"កំពុងទាញយក: {dest_path.name}", 50, f"{mb_done:.1f} MB ({speed_mb:.1f} MB/s)")

    def _create_desktop_shortcut(self, target_exe: Path, shortcut_name: str = "JAI AUTO DUBBING"):
        """Creates a desktop shortcut with custom icon without requiring external dependencies."""
        desktop = Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / "Desktop"
        shortcut_path = desktop / f"{shortcut_name}.lnk"
        icon_path = self.install_dir / "assets" / "icons" / "app.ico"
        icon_line = f'$Shortcut.IconLocation = "{icon_path},0"; ' if icon_path.exists() else ''
        ps_cmd = (
            f'$WshShell = New-Object -ComObject WScript.Shell; '
            f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
            f'$Shortcut.TargetPath = "{target_exe}"; '
            f'$Shortcut.WorkingDirectory = "{target_exe.parent}"; '
            f'$Shortcut.Description = "JAI AUTO DUBBING - AI Chinese to Khmer Suite"; '
            f'{icon_line}'
            f'$Shortcut.Save()'
        )
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
        except Exception:
            pass

    def _run_install_worker(self):
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            temp_dir = self.install_dir / "_temp"
            temp_dir.mkdir(exist_ok=True)

            # Check if local prebuilt bundle exists alongside installer
            current_dir = Path(__file__).resolve().parent
            local_bundle = current_dir / "dist" / "AutoDaiDubber"
            if not local_bundle.exists():
                local_bundle = current_dir / "AutoDaiDubber"

            if local_bundle.exists() and (local_bundle / "AutoDaiDubber.exe").exists():
                self.update_status("កំពុងចម្លងកម្មវិធី (Local Copy)...", "កំពុងចម្លងឯកសារកម្មវិធីពីប្រភពក្នុងស្រុក...", 30)
                shutil.copytree(local_bundle, self.install_dir, dirs_exist_ok=True)
                self.update_status("ដំឡើងរួចរាល់!", "កំពុងបង្កើត Shortcut លើ Desktop...", 90)
                self._create_desktop_shortcut(self.install_dir / "AutoDaiDubber.exe")
                self._finish_and_launch(self.install_dir / "AutoDaiDubber.exe")
                return

            # Check if cloud URL is configured
            if DEFAULT_CLOUD_URL and DEFAULT_CLOUD_URL.startswith("http"):
                zip_path = temp_dir / "app_package.zip"
                self._download_file(DEFAULT_CLOUD_URL, zip_path, "កំពុងទាញយកកញ្ចប់កម្មវិធីពី Cloud...")
                self.update_status("កំពុងពន្លាឯកសារ (Extracting)...", "កំពុងរៀបចំប្រព័ន្ធ...", 85)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.install_dir)
                try: os.remove(zip_path)
                except Exception: pass
                exe_target = self.install_dir / "AutoDaiDubber.exe"
                self._create_desktop_shortcut(exe_target)
                self._finish_and_launch(exe_target)
                return

            # Step 1: Download Python 3.12 Embeddable (~11 MB)
            python_zip = temp_dir / "python_embed.zip"
            python_dir = self.install_dir / "python"
            if not (python_dir / "python.exe").exists():
                self._download_file(PYTHON_EMBED_URL, python_zip, "ជំហាន 1/4: កំពុងទាញយក Python Runtime (~11 MB)...")
                self.update_status("កំពុងរៀបចំ Python Runtime...", "កំពុងពន្លា Python...", 25)
                python_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(python_zip, 'r') as zip_ref:
                    zip_ref.extractall(python_dir)
                try: os.remove(python_zip)
                except Exception: pass

                # Enable site-packages in python312._pth
                pth_file = list(python_dir.glob("*._pth"))
                if pth_file:
                    content = pth_file[0].read_text(encoding="utf-8")
                    content = content.replace("#import site", "import site")
                    if "import site" not in content:
                        content += "\nimport site\n"
                    pth_file[0].write_text(content, encoding="utf-8")

            # Step 2: Install PIP
            python_exe = python_dir / "python.exe"
            pip_exe = python_dir / "Scripts" / "pip.exe"
            if not pip_exe.exists():
                self.update_status("ជំហាន 2/4: កំពុងរៀបចំ PIP Package Manager...", "កំពុងទាញយក get-pip.py...", 35)
                get_pip_py = temp_dir / "get-pip.py"
                self._download_file(GET_PIP_URL, get_pip_py, "កំពុងទាញយក get-pip.py...")
                subprocess.run([str(python_exe), str(get_pip_py), "--no-warn-script-location"], check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
                try: os.remove(get_pip_py)
                except Exception: pass

            # Step 3: Copy AutoDaiDubber codebase
            self.update_status("ជំហាន 3/4: កំពុងរៀបចំកូដកម្មវិធី...", "កំពុងចម្លងឯកសារប្រព័ន្ធ...", 50)
            if hasattr(sys, '_MEIPASS'):
                proj_root = Path(sys._MEIPASS)
            else:
                proj_root = Path(__file__).resolve().parent
            for item in ["core", "ui", "utils", "assets", "app.py", "config.json", "requirements.txt"]:
                src = proj_root / item
                dst = self.install_dir / item
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                elif src.is_file():
                    shutil.copy2(src, dst)

            # Step 4: Install AI Dependencies via PIP
            self.update_status("ជំហាន 4/4: កំពុងដំឡើងបណ្ណាល័យ AI...", "កំពុងដំឡើង PyTorch, Whisper, Demucs, Webview (សូមរង់ចាំ)...", 65)
            req_file = self.install_dir / "requirements.txt"
            pip_cmd = [
                str(python_exe), "-m", "pip", "install",
                "--no-warn-script-location",
                "-r", str(req_file)
            ]
            subprocess.run(pip_cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)

            # Create Desktop Shortcut
            # Create Desktop Shortcut & Launchers
            self.update_status("ដំឡើងបានជោគជ័យ!", "កំពុងបង្កើត Shortcut លើ Desktop...", 95)
            py_w = python_dir / "pythonw.exe"
            app_p = self.install_dir / "app.py"

            # 1. Clean VBScript launcher with Chr(34) concatenation (zero syntax errors)
            launcher_vbs = self.install_dir / "Run_AutoDaiDubber.vbs"
            vbs_script = (
                'Set WshShell = CreateObject("WScript.Shell")\r\n'
                f'WshShell.CurrentDirectory = "{self.install_dir}"\r\n'
                f'cmd = Chr(34) & "{py_w}" & Chr(34) & " " & Chr(34) & "{app_p}" & Chr(34)\r\n'
                'WshShell.Run cmd, 0, False\r\n'
            )
            launcher_vbs.write_text(vbs_script, encoding="ascii")

            # 2. Native BAT launcher
            launcher_bat = self.install_dir / "AutoDaiDubber.bat"
            bat_script = (
                '@echo off\r\n'
                f'cd /d "{self.install_dir}"\r\n'
                f'start "" "{py_w}" "{app_p}"\r\n'
            )
            launcher_bat.write_text(bat_script, encoding="utf-8")

            # 3. Create Desktop shortcut pointing to launcher
            self._create_desktop_shortcut(launcher_vbs)

            self.update_status("រួចរាល់!", "ដំឡើងជោគជ័យ ១០០%! កំពុងបើកកម្មវិធី...", 100)
            time.sleep(1)
            self._finish_and_launch(launcher_vbs)

        except Exception as e:
            if not self.is_cancelled:
                self.root.after(0, lambda: messagebox.showerror("កំហុសដំឡើង (Install Error)", f"មានបញ្ហាក្នុងការដំឡើង:\n{e}"))
                self.root.after(0, lambda: self.start_btn.config(state="normal", bg="#2563eb"))

    def _finish_and_launch(self, target_to_run: Path):
        def _launch():
            try:
                os.startfile(str(target_to_run))
            except Exception:
                subprocess.Popen([str(target_to_run)], shell=True)
            self.root.destroy()
        self.root.after(1000, _launch)

def main():
    root = tk.Tk()
    app = ModernInstallerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
