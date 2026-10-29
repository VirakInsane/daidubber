import math
import random
import tkinter as tk
import customtkinter as ctk
from typing import List, Optional
from ui.styles import (
    CARD_BG, CARD_BORDER, CARD_HOVER, ACCENT_CYAN, ACCENT_BLUE, ACCENT_PINK,
    ACCENT_PURPLE, ACCENT_GREEN, ACCENT_RED, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    INPUT_BG, FONT_CONSOLE, FONT_SMALL, FONT_BODY_BOLD, EQUALIZER_COLORS
)

class GlassCard(ctk.CTkFrame):
    """A sleek dark container card with rounded corners, subtle border, and optional glow."""
    def __init__(self, master, glowing=False, glow_color=ACCENT_CYAN, **kwargs):
        border_c = glow_color if glowing else kwargs.pop("border_color", CARD_BORDER)
        border_w = 2 if glowing else kwargs.pop("border_width", 1)
        super().__init__(
            master,
            fg_color=kwargs.pop("fg_color", CARD_BG),
            border_color=border_c,
            border_width=border_w,
            corner_radius=kwargs.pop("corner_radius", 12),
            **kwargs
        )
        self.glowing = glowing
        self.glow_color = glow_color

    def set_glow(self, active: bool, color: Optional[str] = None):
        c = color or self.glow_color
        if active:
            self.configure(border_color=c, border_width=2)
        else:
            self.configure(border_color=CARD_BORDER, border_width=1)


class AudioVisualizerWidget(tk.Canvas):
    """
    Animated Canvas widget displaying high-tech neon equalizer / soundwave bars.
    Animates at ~30 FPS with ambient wave when idle, and energetic audio dynamics when active.
    """
    def __init__(self, master, width=280, height=42, num_bars=24, **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=INPUT_BG,
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.num_bars = num_bars
        self.is_active = False
        self.is_running = True
        self.phase = 0.0

        # Bar state tracking
        self.bar_heights = [0.15] * num_bars
        self.peak_heights = [0.2] * num_bars
        self.peak_fall_speed = [0.02] * num_bars

        self.bind("<Destroy>", self._on_destroy)
        self._animate()

    def set_mode(self, active: bool):
        """Toggle between idle ambient wave and active processing beat."""
        self.is_active = active

    def _animate(self):
        if not self.is_running:
            return

        try:
            self.delete("all")
            bar_w = (self.width - (self.num_bars + 1) * 2) / self.num_bars
            self.phase += 0.08

            for i in range(self.num_bars):
                # Calculate bar height
                if self.is_active:
                    # Dynamic rhythmic audio visualization
                    base = 0.3 + 0.35 * math.sin(self.phase * 2.2 + i * 0.45)
                    random_burst = random.uniform(-0.15, 0.35)
                    target_h = max(0.1, min(0.95, base + random_burst))
                    self.bar_heights[i] += (target_h - self.bar_heights[i]) * 0.35
                else:
                    # Gentle ambient breathing wave
                    wave = 0.22 + 0.14 * math.sin(self.phase + i * 0.3)
                    self.bar_heights[i] += (wave - self.bar_heights[i]) * 0.15

                h_val = max(3, int(self.bar_heights[i] * (self.height - 8)))
                x0 = 2 + i * (bar_w + 2)
                y0 = self.height - 4 - h_val
                x1 = x0 + bar_w
                y1 = self.height - 4

                # Update peak hold dot
                if h_val > self.peak_heights[i]:
                    self.peak_heights[i] = h_val
                    self.peak_fall_speed[i] = 0.5
                else:
                    self.peak_heights[i] = max(3, self.peak_heights[i] - self.peak_fall_speed[i])
                    self.peak_fall_speed[i] += 0.15

                # Color from palette
                c_idx = i % len(EQUALIZER_COLORS)
                bar_color = EQUALIZER_COLORS[c_idx]

                # Draw main equalizer bar
                self.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="", width=0)

                # Draw peak cap (floating dot)
                peak_y = self.height - 4 - self.peak_heights[i] - 2
                self.create_rectangle(x0, peak_y, x1, peak_y + 1, fill="#ffffff", outline="", width=0)

            self.after(33, self._animate)
        except Exception:
            pass

    def _on_destroy(self, event=None):
        self.is_running = False


class PulsingStatusDot(tk.Canvas):
    """
    Animated glowing status dot with expanding pulsing halo.
    Indicates GPU/Ready/Dubbing state with smooth color breathing.
    """
    def __init__(self, master, size=24, **kwargs):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=CARD_BG,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.phase = 0.0
        self.state = "ready"  # 'ready', 'processing', 'completed', 'stopped'
        self.is_running = True
        self.bind("<Destroy>", self._on_destroy)
        self._animate()

    def set_state(self, state: str):
        self.state = state

    def _animate(self):
        if not self.is_running:
            return

        try:
            self.delete("all")
            cx, cy = self.size / 2, self.size / 2
            self.phase += 0.12

            if self.state == "processing":
                color_core = ACCENT_CYAN
                color_halo = "#005580"
                halo_pulse = 2.5 + 2.5 * math.sin(self.phase * 2)
            elif self.state == "ready":
                color_core = ACCENT_GREEN
                color_halo = "#0b3d2c"
                halo_pulse = 1.5 + 1.5 * math.sin(self.phase)
            elif self.state == "completed":
                color_core = ACCENT_GREEN
                color_halo = "#00f59b"
                halo_pulse = 2.0
            else:  # stopped / error
                color_core = ACCENT_RED
                color_halo = "#4d0014"
                halo_pulse = 1.5 + 1.5 * math.sin(self.phase)

            # Outer halo ring
            halo_r = 7 + halo_pulse
            self.create_oval(cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r, fill=color_halo, outline="")

            # Inner bright core
            core_r = 4.5
            self.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill=color_core, outline="")

            self.after(35, self._animate)
        except Exception:
            pass

    def _on_destroy(self, event=None):
        self.is_running = False


class SmoothProgressBar(ctk.CTkProgressBar):
    """
    Smoothly interpolated progress bar that eases towards target percentage
    instead of jerky instantaneous jumps.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_val = 0.0
        self.target_val = 0.0
        self.is_animating = False

    def set_target(self, target: float):
        self.target_val = max(0.0, min(1.0, float(target)))
        if not self.is_animating:
            self.is_animating = True
            self._step_interpolate()

    def _step_interpolate(self):
        diff = self.target_val - self.current_val
        if abs(diff) < 0.005:
            self.current_val = self.target_val
            self.set(self.current_val)
            self.is_animating = False
            return

        # Smooth easing
        self.current_val += diff * 0.18
        self.set(self.current_val)
        self.after(20, self._step_interpolate)


class PipelineProgressWidget(ctk.CTkFrame):
    """
    Visualizes dubbing pipeline stages horizontally with glowing active step
    and pulsing animation.
    """
    def __init__(self, master, stages: List[str], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.stages = stages
        self.pills = []
        self.active_index = -1
        self.pulse_phase = 0.0
        self.is_animating = True

        self._build_pills()
        self.bind("<Destroy>", self._on_destroy)
        self._pulse_loop()

    def _build_pills(self):
        for idx, stage in enumerate(self.stages):
            pill_frame = ctk.CTkFrame(self, fg_color="transparent")
            pill_frame.pack(side="left", padx=2, pady=2)

            btn = ctk.CTkLabel(
                pill_frame,
                text=f"{idx + 1}. {stage}",
                fg_color="#182238",
                text_color=TEXT_SECONDARY,
                corner_radius=6,
                font=(FONT_SMALL[0], 9),
                padx=7,
                pady=3
            )
            btn.pack(side="left")
            self.pills.append(btn)

            if idx < len(self.stages) - 1:
                arrow = ctk.CTkLabel(
                    pill_frame,
                    text="➔",
                    font=(FONT_SMALL[0], 8),
                    text_color=TEXT_MUTED
                )
                arrow.pack(side="left", padx=2)

    def set_active_stage(self, active_index: int):
        self.active_index = active_index
        for idx, pill in enumerate(self.pills):
            if idx < active_index:
                # Completed stage with green check
                pill.configure(
                    fg_color="#0e3a2f",
                    text_color=ACCENT_GREEN,
                    text=f"{idx + 1}. {self.stages[idx]} ✓"
                )
            elif idx == active_index:
                # In progress active stage
                pill.configure(
                    fg_color="#004d80",
                    text_color=ACCENT_CYAN,
                    text=f"⚡ {self.stages[idx]}"
                )
            else:
                # Pending stage
                pill.configure(
                    fg_color="#182238",
                    text_color=TEXT_SECONDARY,
                    text=f"{idx + 1}. {self.stages[idx]}"
                )

    def _pulse_loop(self):
        if not self.is_animating:
            return

        try:
            if 0 <= self.active_index < len(self.pills):
                self.pulse_phase += 0.2
                # Pulsing brightness between cyan and electric blue
                if math.sin(self.pulse_phase) > 0:
                    self.pills[self.active_index].configure(fg_color="#00558f", text_color="#ffffff")
                else:
                    self.pills[self.active_index].configure(fg_color="#003d66", text_color=ACCENT_CYAN)

            self.after(120, self._pulse_loop)
        except Exception:
            pass

    def reset(self):
        self.active_index = -1
        for idx, pill in enumerate(self.pills):
            pill.configure(
                fg_color="#182238",
                text_color=TEXT_SECONDARY,
                text=f"{idx + 1}. {self.stages[idx]}"
            )

    def _on_destroy(self, event=None):
        self.is_animating = False


class LogConsoleWidget(ctk.CTkFrame):
    """A high-tech terminal console widget displaying live colored logs."""
    def __init__(self, master, height=130, **kwargs):
        super().__init__(master, fg_color=INPUT_BG, border_color=CARD_BORDER, border_width=1, corner_radius=10, **kwargs)
        self.pack_propagate(False)
        self.configure(height=height)

        self.text_area = tk.Text(
            self,
            bg=INPUT_BG,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_CYAN,
            relief="flat",
            wrap="word",
            font=FONT_CONSOLE,
            padx=10,
            pady=8
        )
        self.scrollbar = ctk.CTkScrollbar(self, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y", padx=2, pady=2)
        self.text_area.pack(side="left", fill="both", expand=True)

        self.text_area.tag_configure("INFO", foreground=TEXT_PRIMARY)
        self.text_area.tag_configure("SUCCESS", foreground=ACCENT_GREEN)
        self.text_area.tag_configure("WARNING", foreground="#ffb703")
        self.text_area.tag_configure("ERROR", foreground=ACCENT_RED)
        self.text_area.tag_configure("STEP", foreground=ACCENT_CYAN)

        self.text_area.configure(state="disabled")

    def append_log(self, message: str, level: str = "INFO"):
        self.text_area.configure(state="normal")
        self.text_area.insert("end", message + "\n", level)
        self.text_area.see("end")
        self.text_area.configure(state="disabled")

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")
