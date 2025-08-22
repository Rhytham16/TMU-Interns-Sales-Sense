# backend/crewai_transcription.py
import assemblyai as aai
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=r"backend\.env")

# Set AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_crew_ai(audio_file):
    """
    Transcribes an uploaded audio file using AssemblyAI with speaker labels.
    Returns transcript text with speaker diarization.
    """
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    try:
        # Transcription config with speaker diarization
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            format_text=True,
            punctuate=True,
            speech_model=aai.SpeechModel.best,
            language_detection=True
        )

        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(tmp_path)

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        # Format transcript with speaker labels
        if transcript.utterances:
            formatted_transcript = "\n".join([
                f"Speaker {utterance.speaker}: {utterance.text}" 
                for utterance in transcript.utterances
            ])
        else:
            # Fallback to regular transcript if no utterances
            formatted_transcript = transcript.text or "No speech detected"

        return formatted_transcript

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def remove_file(file_path: str) -> None:
    """Quick cleanup - keeping same interface as your current code"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
