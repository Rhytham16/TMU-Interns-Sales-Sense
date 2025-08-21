from dotenv import load_dotenv
load_dotenv(dotenv_path=r"backend\.env")

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import traceback
import json

from backend.transcription import transcribe_mp3, remove_file

# Import your enhanced multi-agent system
try:
    from backend.multi_agent_system import analyze_call_multi_agent_fast
    USE_MULTI_AGENT = True
    print("✅ Enhanced multi-agent system loaded successfully")
except ImportError as e:
    USE_MULTI_AGENT = False
    print(f"❌ Failed to load multi-agent system: {e}")

app = FastAPI(title="SalesSense Enhanced Multi-Agent Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
async def health():
    system_type = "Enhanced Multi-Agent" if USE_MULTI_AGENT else "Error"
    return {"status": "ok", "message": f"{system_type} Backend is running", "version": "1.0.0"}

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    transcript = transcribe_mp3(file_location)
    remove_file(file_location)
    return {"transcript": transcript}

@app.post("/analyze/")
async def analyze_call_endpoint(
    transcript: str = Form(...),
    context: str = Form(...)
):
    if USE_MULTI_AGENT:
        result = analyze_call_multi_agent_fast(context, transcript)
        return result
    else:
        return {
            "error": "Multi-agent system not available",
            "summary": "System configuration error",
            "improvement_areas": ["Check system configuration"],
            "coaching_tips": [{"skill": "System", "tip": "Contact technical support"}]
        }

@app.post("/analyze_call")
async def analyze_call_combined(
    audio_file: UploadFile = File(...),
    participants: str = Form(...),
    details: str = Form(...),
    call_types: str = Form(...)
):
    try:
        # 1) Save and transcribe
        file_location = os.path.join(UPLOAD_DIR, audio_file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        file_size = os.path.getsize(file_location)
        print(f"📁 Processing: {audio_file.filename} ({file_size} bytes)")

        print("🎤 Ultra-fast transcription (max 45s)...")
        transcript = transcribe_mp3(file_location)
        print(f"✅ Transcribed in {len(transcript)} characters")
        remove_file(file_location)

        # 2) Build context string
        context = (
            f"Participants: {participants}\n"
            f"Call details: {details}\n"
            f"Call types: {call_types}"
        )

        # 3) Use enhanced multi-agent system
        if USE_MULTI_AGENT:
            print("🚀 Multi-agent analysis (max 25s)...")
            analysis_result = analyze_call_multi_agent_fast(context, transcript)
            print("✅ All 3 agents completed")

            # Ensure required frontend keys exist
            analysis_result.setdefault("improvement_areas", ["Continue developing sales skills", "Practice active listening"])
            analysis_result.setdefault("coaching_tips", [{"skill": "General", "tip": "Keep building rapport with prospects"}])

            print("🎉 TOTAL PROCESSING: Analysis complete with ALL 3 AGENTS!")
            return analysis_result
        else:
            return {
                "error": "Multi-agent system not available",
                "summary": f"Transcription completed ({len(transcript)} characters) but analysis system is not working.",
                "improvement_areas": ["Fix multi-agent system configuration"],
                "coaching_tips": [{"skill": "System", "tip": "Contact technical support"}]
            }
    except Exception as e:
        print(f"❌ Error in analyze_call_combined: {e}")
        print(traceback.format_exc())
        return {
            "error": f"Processing failed: {str(e)}",
            "summary": f"Error occurred during processing: {str(e)}",
            "improvement_areas": ["Contact support for assistance"],
            "coaching_tips": [{"skill": "Technical", "tip": "Try again with a different audio file"}],
            "metrics": {
                "overall_sentiment": "neutral",
                "rep_talk_ratio_percent": 0,
                "customer_talk_ratio_percent": 0,
                "questions_asked_by_rep": 0,
                "objections_detected": 0,
                "followups_committed": 0
            },
            "strengths": [],
            "customer_objections": [],
            "next_steps": [],
            "notable_quotes": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
