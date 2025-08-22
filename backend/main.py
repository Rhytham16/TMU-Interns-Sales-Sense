from dotenv import load_dotenv
load_dotenv(dotenv_path=r"backend\.env")

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import traceback
import json
import hashlib
import asyncio
from datetime import datetime, timedelta


from backend.logging_config import setup_logging

ENV = os.getenv("APP_ENV", "dev")  # dev|prod
setup_logging(ENV)
import logging
log = logging.getLogger("salessense.backend")


from backend.crewai_transcription import transcribe_crew_ai, remove_file

# Import your enhanced multi-agent system
try:
    from backend.multi_agent_system import analyze_call_multi_agent_fast
    USE_MULTI_AGENT = True
    print("✅ Enhanced multi-agent system loaded successfully")
except ImportError as e:
    USE_MULTI_AGENT = False
    print(f"❌ Failed to load multi-agent system: {e}")

# Simple but effective cache implementation
class SimpleCache:
    def __init__(self):
        self.store = {}
        self.lock = asyncio.Lock()
        self.max_size = 50
        self.ttl_hours = 24
    
    async def compute_key(self, file_bytes: bytes, context: str) -> str:
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        hasher.update(context.encode('utf-8'))
        return hasher.hexdigest()
    
    async def get(self, key: str):
        async with self.lock:
            item = self.store.get(key)
            if item is None:
                return None
            
            # Check TTL
            if datetime.now() - item['timestamp'] > timedelta(hours=self.ttl_hours):
                del self.store[key]
                return None
                
            return item['result']
    
    async def set(self, key: str, result: dict):
        async with self.lock:
            # Simple LRU eviction
            if len(self.store) >= self.max_size:
                oldest_key = min(self.store.keys(), key=lambda k: self.store[k]['timestamp'])
                del self.store[oldest_key]
                print(f"🗑️ Cache full, removed oldest entry")
            
            self.store[key] = {
                'result': result,
                'timestamp': datetime.now()
            }
            print(f"💾 Result cached (total entries: {len(self.store)})")
    
    async def get_stats(self):
        async with self.lock:
            return {
                "total_entries": len(self.store),
                "max_entries": self.max_size,
                "ttl_hours": self.ttl_hours
            }

# Global cache instance
cache = SimpleCache()

app = FastAPI(title="SalesSense Enhanced Multi-Agent Backend with Caching", version="2.0.0")

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
    cache_stats = await cache.get_stats()
    system_type = "Enhanced Multi-Agent with Caching" if USE_MULTI_AGENT else "Error"
    return {
        "status": "ok", 
        "message": f"{system_type} Backend is running", 
        "version": "2.0.0",
        "cache_stats": cache_stats
    }

@app.get("/cache/stats")
async def get_cache_stats():
    """Get current cache statistics"""
    return await cache.get_stats()

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached results"""
    global cache
    cache = SimpleCache()
    return {"message": "Cache cleared successfully"}

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Use AssemblyAI transcription with speaker labels
    with open(file_location, "rb") as audio_file:
        transcript = transcribe_crew_ai(audio_file)
    
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
        print(f"📁 Processing: {audio_file.filename}")
        
        # Read file bytes FIRST for caching
        file_bytes = await audio_file.read()
        file_size = len(file_bytes)
        print(f"📊 File size: {file_size} bytes")

        # Build normalized context string for consistent cache keys
        context = f"Participants: {participants.strip()}\nCall details: {details.strip()}\nCall types: {call_types.strip()}"

        # Compute cache key and check cache
        cache_key = await cache.compute_key(file_bytes, context)
        cached_result = await cache.get(cache_key)
        
        if cached_result is not None:
            print(f"✅ CACHE HIT for key: {cache_key[:12]}...")
            cached_result["cached"] = True
            cached_result["processing_time"] = "0.0s (cached)"
            cached_result["transcription_method"] = "AssemblyAI with Speaker Diarization (cached)"
            return cached_result

        # Cache miss - process the file
        print(f"❌ CACHE MISS for key: {cache_key[:12]}...")
        
        # Save file temporarily for processing
        file_location = os.path.join(UPLOAD_DIR, audio_file.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(file_bytes)
        
        print("🎤 AssemblyAI transcription with speaker diarization...")
        
        # Use AssemblyAI with speaker labels
        with open(file_location, "rb") as audio_file_obj:
            transcript = transcribe_crew_ai(audio_file_obj)
        
        print(f"✅ Transcribed with speaker labels: {len(transcript)} characters")
        remove_file(file_location)

        # Enhanced context for analysis
        analysis_context = (
            f"{context}\n"
            f"Note: This transcript includes speaker labels for better analysis"
        )

        # Multi-agent analysis
        if USE_MULTI_AGENT:
            print("🚀 Multi-agent analysis with speaker-aware context...")
            analysis_result = analyze_call_multi_agent_fast(analysis_context, transcript)
            print("✅ All 3 agents completed")

            # Ensure required frontend keys exist
            analysis_result.setdefault("improvement_areas", ["Continue developing sales skills", "Practice active listening"])
            analysis_result.setdefault("coaching_tips", [{"skill": "General", "tip": "Keep building rapport with prospects"}])
            
            # Add metadata
            analysis_result["transcription_method"] = "AssemblyAI with Speaker Diarization"
            analysis_result["cached"] = False
            
            # Cache the result for future use
            await cache.set(cache_key, analysis_result)
            
            print("🎉 PROCESSING COMPLETE - Result cached for future use!")
            return analysis_result
        else:
            return {
                "error": "Multi-agent system not available",
                "summary": f"Transcription completed ({len(transcript)} characters) but analysis system is not working.",
                "improvement_areas": ["Fix multi-agent system configuration"],
                "coaching_tips": [{"skill": "System", "tip": "Contact technical support"}],
                "cached": False
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
            "notable_quotes": [],
            "cached": False
        }
log.info("Backend starting…")
log.debug("Loaded config and environment")
log.warning("Potential config issue detected")
log.error("Processing failed", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
