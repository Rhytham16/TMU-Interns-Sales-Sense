import os
from faster_whisper import WhisperModel
import torch

_model = None

def _load_optimized_model():
    """Load fastest Whisper configuration"""
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Use tiny model for maximum speed - 4x faster than OpenAI Whisper
        _model = WhisperModel("tiny", device=device, compute_type="float32")
        print(f"🎤 Faster-Whisper TINY model loaded on {device}")
    return _model

def transcribe_mp3(file_path: str) -> str:
    """Ultra-fast transcription with faster-whisper"""
    model = _load_optimized_model()
    
    # Transcribe with optimized settings
    segments, info = model.transcribe(
        file_path,
        language="en",  # Skip auto-detection
        beam_size=1,    # Fastest setting
        word_timestamps=False  # Skip word-level timing
    )
    
    # Combine all segments
    transcript = " ".join([segment.text for segment in segments])
    return transcript.strip()

def remove_file(file_path: str) -> None:
    """Quick cleanup"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
