from __future__ import annotations

import math
import struct
from pathlib import Path


def synthesize_placeholder_audio(text: str, output_path: Path, sample_rate: int = 22050) -> Path:
    """Generate a simple sine wave to act as placeholder narration audio."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration_seconds = min(60.0, max(2.0, len(text) / 25))
    total_frames = int(sample_rate * duration_seconds)
    amplitude = 12000
    base_frequency = 220.0

    with open(output_path, "wb") as fh:
        import wave

        with wave.open(fh, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for frame in range(total_frames):
                # Vary the pitch slightly using the text content to make each file unique
                char = text[frame % len(text)] if text else "A"
                frequency = base_frequency + (ord(char) % 60)
                value = int(amplitude * math.sin(2 * math.pi * frequency * frame / sample_rate))
                wav_file.writeframesraw(struct.pack("<h", value))

    return output_path


def generate_audio_file(text: str, storage_dir: Path, filename: str) -> Path:
    """Generate placeholder audio and return the file path."""

    output_path = storage_dir / filename
    synthesize_placeholder_audio(text=text or "Generated audio", output_path=output_path)
    return output_path
