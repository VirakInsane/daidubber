"""
UI Styles, themes, and color definitions for AutoDaiDubber.
Modern Cyberpunk / Glassmorphic Dark Theme with Khmer font support.
"""

# Color Palette
BG_DARK = "#090d16"          # Deep midnight dark background
CARD_BG = "#111827"          # Dark container background
CARD_BORDER = "#1f293d"      # Subtle border
CARD_HOVER = "#182238"       # Hover background
CARD_GLOW = "#00d2ff"        # Glowing border accent

ACCENT_CYAN = "#00f0ff"      # Glowing electric cyan
ACCENT_BLUE = "#0066ff"      # Vibrant royal blue
ACCENT_PINK = "#ff007f"      # Neon magenta / cyberpunk pink
ACCENT_PURPLE = "#8a2be2"    # Cyberpunk violet
ACCENT_GREEN = "#00f59b"     # Neon emerald / success
ACCENT_ORANGE = "#ff9500"    # Alert orange
ACCENT_RED = "#ff3366"       # Error red

TEXT_PRIMARY = "#f8fafc"     # Crisp white
TEXT_SECONDARY = "#94a3b8"   # Slate gray
TEXT_MUTED = "#64748b"       # Muted gray

INPUT_BG = "#0b1120"         # Input field background
INPUT_BORDER = "#1e293b"     # Input border
INPUT_FOCUS = "#00f0ff"      # Input focus glow

PROGRESS_BG = "#0f172a"
PROGRESS_FILL = "#00f0ff"

# Neon Visualizer Palette
EQUALIZER_COLORS = [
    "#00f0ff", "#00d2ff", "#00b4d8", "#0096c7",
    "#0077b6", "#5e60ce", "#7928ca", "#9d4edd",
    "#c77dff", "#e0aaff", "#ff007f", "#ff0055",
    "#00f59b", "#10b981", "#059669", "#00f0ff"
]

# Fonts (Leelawadee UI provides first-class support for both Khmer & Latin)
FONT_FAMILY = "Leelawadee UI"

FONT_HEADER = (FONT_FAMILY, 15, "bold")
FONT_TITLE = (FONT_FAMILY, 13, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_CONSOLE = ("Consolas", 9)
