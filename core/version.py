# -*- coding: utf-8 -*-
"""
Central Version & Release Metadata for JAI AUTO DUBBING.
Single source of truth for UI, Installer, and Build tools.
"""

__version__ = "2.5.1"
__release_date__ = "2026-10-22"
__build_code__ = "20261022.02"
__edition__ = "Imperial Pro"

CHANGELOG = [
    {
        "version": "2.5.1",
        "date": "2026-10-22",
        "title": "Zero-Cut Audio & 3D Cinema Mastering Release",
        "highlights": [
            "100% Zero-Cut Dialogue Preservation (Whisper directly transcribes original audio)",
            "Zero-Drop TTS Emergency Recovery via gTTS fallback",
            "Foley Impact Gate: isolates battle impacts & horse hooves while dampening background songs",
            "Dynamic Character Role Cadence: custom pitch & rate for hero, elder, girl, and mother personas",
            "Studio Cinema Broadcast Mastering EQ (85Hz High-Pass, 220Hz Chest Warmth, 3.5kHz Clarity, Loudnorm)",
            "Web Audio API celebration chime sound and finish notification modal",
            "Official 3D Imperial Golden Dragon application & desktop icon"
        ]
    },
    {
        "version": "2.5.0",
        "date": "2026-10-15",
        "title": "Modern Animated WebView2 Architecture",
        "highlights": [
            "Hardware-accelerated modern web interface powered by Microsoft Edge WebView2",
            "Multi-video concurrent dubbing engine with individual thread workers",
            "Multi-Key Gemini API pool rotation with automatic quota failover",
            "Live audio spectrum equalizer visualizer"
        ]
    }
]

def get_version_string() -> str:
    return f"v{__version__}"

def get_full_title() -> str:
    return f"JAI AUTO DUBBING {get_version_string()} ({__edition__}) 🎬⚡"

def get_setup_filename() -> str:
    return f"AutoDaiDubber_Setup_v{__version__}.exe"
