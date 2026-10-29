import sys
import logging
from datetime import datetime
from pathlib import Path

class AppLogger:
    """Thread-safe logging utility that supports GUI log listeners and file logs."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._listeners = []
            cls._instance._log_file = None
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        # Ensure sys.stdout handles UTF-8 for Khmer text and emojis on Windows
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

        self.logger = logging.getLogger("AutoDaiDubber")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def add_listener(self, callback):
        """Add a callback function (takes text string, level) for GUI real-time logs."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        
        # Log to python logger
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

        # Notify GUI listeners
        for listener in self._listeners:
            try:
                listener(formatted, level)
            except Exception:
                pass

    def info(self, message: str):
        self.log(message, "INFO")

    def success(self, message: str):
        self.log(f"✅ {message}", "SUCCESS")

    def warning(self, message: str):
        self.log(f"⚠️ {message}", "WARNING")

    def error(self, message: str):
        self.log(f"❌ {message}", "ERROR")

    def step(self, step_num: int, total_steps: int, message: str):
        self.log(f"📌 [ជំហាន {step_num}/{total_steps}] {message}", "STEP")

logger = AppLogger()
