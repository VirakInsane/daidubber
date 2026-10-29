import os
import numpy as np
import soundfile as sf
import librosa
from typing import Tuple, Optional
from utils.logger import logger

# Acoustic boundary: typical male speech is 85-165 Hz, female speech is 165-280+ Hz
PITCH_SPLIT_HZ = 165.0
CLEAR_MALE_MAX = 155.0
CLEAR_FEMALE_MIN = 175.0

class GenderDetector:
    """
    High-accuracy speaker gender detection combining acoustic fundamental frequency (F0)
    analysis with contextual LLM dialogue clues.
    """
    _is_warmed_up = False

    @classmethod
    def warmup(cls):
        """Warm up librosa/numba JIT compiler on a tiny synthetic signal."""
        if cls._is_warmed_up:
            return
        try:
            sr = 16000
            t = np.linspace(0, 0.2, int(sr * 0.2))
            dummy = 0.5 * np.sin(2 * np.pi * 150 * t)
            librosa.yin(dummy, fmin=65, fmax=350, sr=sr)
            cls._is_warmed_up = True
        except Exception:
            pass

    @classmethod
    def detect_pitch_f0(cls, audio_wav: str, start_sec: float, end_sec: float) -> Optional[float]:
        """
        Extracts median fundamental frequency (F0 in Hz) of the speech segment from vocals.wav.
        Returns median F0 (e.g. 120.5 Hz for male, 215.0 Hz for female), or None if unvoiced.
        """
        if not os.path.exists(audio_wav) or end_sec <= start_sec:
            return None

        try:
            cls.warmup()
            # Read only the segment slice to save memory and ensure high speed
            with sf.SoundFile(audio_wav) as f:
                sr = f.samplerate
                start_frame = int(start_sec * sr)
                num_frames = int((end_sec - start_sec) * sr)
                
                if start_frame >= len(f):
                    return None
                    
                f.seek(start_frame)
                y = f.read(num_frames)

            # Convert stereo to mono if needed
            if y.ndim > 1:
                y = np.mean(y, axis=1)

            if len(y) < sr * 0.25:  # Segment too short (< 250ms)
                return None

            # Downsample to 16kHz for ultra-fast YIN pitch estimation
            if sr != 16000:
                y = librosa.resample(y, orig_sr=sr, target_sr=16000)
                sr = 16000

            # Compute fundamental frequency using YIN (speech range: 65 Hz to 350 Hz)
            f0 = librosa.yin(y, fmin=65, fmax=350, sr=sr, frame_length=1024, hop_length=256)
            
            # Filter out unvoiced / NaN frames
            valid_f0 = f0[~np.isnan(f0)]
            if len(valid_f0) == 0:
                return None

            median_f0 = float(np.median(valid_f0))
            return median_f0

        except Exception as e:
            return None

    @classmethod
    def determine_voice(
        cls,
        pitch_f0: Optional[float],
        gemini_gender: Optional[str] = None,
        previous_voice: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Combines acoustic pitch (F0) with Gemini contextual gender tag to determine
        the most accurate Khmer voice.
        Returns (voice_id, detected_gender_label)
        - 'km-KH-PisethNeural' (Male)
        - 'km-KH-SreymomNeural' (Female)
        """
        # Clean gemini gender tag
        g_tag = (gemini_gender or "").lower().strip()
        is_gemini_male = ("male" in g_tag and "female" not in g_tag) or ("ប្រុស" in g_tag) or ("man" in g_tag)
        is_gemini_female = ("female" in g_tag) or ("ស្រី" in g_tag) or ("woman" in g_tag)

        # Case 1: Acoustic pitch is clearly defined
        if pitch_f0 is not None:
            if pitch_f0 < CLEAR_MALE_MAX:
                # Definitely Male pitch (typically 85-155 Hz)
                return "km-KH-PisethNeural", f"ប្រុស (Pitch {pitch_f0:.0f}Hz)"
            elif pitch_f0 > CLEAR_FEMALE_MIN:
                # Definitely Female pitch (typically 175-280+ Hz)
                return "km-KH-SreymomNeural", f"ស្រី (Pitch {pitch_f0:.0f}Hz)"
            else:
                # Ambiguous boundary zone (155-175 Hz): Use contextual clues if available
                if is_gemini_female:
                    return "km-KH-SreymomNeural", f"ស្រី (Context + {pitch_f0:.0f}Hz)"
                elif is_gemini_male:
                    return "km-KH-PisethNeural", f"ប្រុស (Context + {pitch_f0:.0f}Hz)"
                elif previous_voice:
                    label = "ស្រី" if "Sreymom" in previous_voice else "ប្រុស"
                    return previous_voice, f"{label} (Continuity + {pitch_f0:.0f}Hz)"
                else:
                    # Fallback to 165Hz threshold
                    if pitch_f0 >= PITCH_SPLIT_HZ:
                        return "km-KH-SreymomNeural", f"ស្រី ({pitch_f0:.0f}Hz)"
                    else:
                        return "km-KH-PisethNeural", f"ប្រុស ({pitch_f0:.0f}Hz)"

        # Case 2: Audio pitch was unvoiced/silent/short, rely on Gemini contextual inference
        if is_gemini_female:
            return "km-KH-SreymomNeural", "ស្រី (Context)"
        elif is_gemini_male:
            return "km-KH-PisethNeural", "ប្រុស (Context)"

        # Case 3: Continuity from previous speaker
        if previous_voice:
            label = "ស្រី" if "Sreymom" in previous_voice else "ប្រុស"
            return previous_voice, f"{label} (Continuity)"

        # Default fallback
        return "km-KH-PisethNeural", "ប្រុស (Default)"
