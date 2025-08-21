import os
from faster_whisper import WhisperModel
import torch

_model = None

def _load_optimized_model():
    """Load fastest Whisper configuration"""
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = WhisperModel("tiny", device=device, compute_type="float32")
        print(f"🎤 Faster-Whisper TINY model loaded on {device}")
    return _model

def transcribe_mp3(file_path: str) -> str:
    """Ultra-fast transcription with faster-whisper"""
    model = _load_optimized_model()
    segments, info = model.transcribe(
        file_path,
        language="en",
        beam_size=1,
        word_timestamps=False
    )
    transcript = " ".join([segment.text for segment in segments]) if segments else ""
    return (transcript or "").strip()

def remove_file(file_path: str) -> None:
    """Quick cleanup"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
