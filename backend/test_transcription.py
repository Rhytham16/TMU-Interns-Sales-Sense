import requests
import os

# Configuration
backend_url = "http://localhost:8000"
audio_path = "D:\Sales Sense 2\data\dialpad_sample_voice_recordings\Sameer Firozi (623) 399-3688 Jul 30, 2025.mp3"  # Replace with path to your audio file

def test_transcription():
    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        print("Please update the 'audio_path' variable with your actual file path")
        return
    
    print(f"🎤 Testing transcription for: {audio_path}")
    
    try:
        # Send file to transcription endpoint
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
            response = requests.post(f"{backend_url}/transcribe/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            transcript = data.get("transcript", "No transcript returned")
            
            print("✅ Transcription successful!")
            print("=" * 50)
            print("TRANSCRIPT OUTPUT:")
            print("=" * 50)
            print(transcript)
            print("=" * 50)
            
            # If using AssemblyAI, transcript will show speaker labels like:
            # Speaker A: Hello, how are you?
            # Speaker B: I'm doing well, thank you!
            
        else:
            print(f"❌ Transcription failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.ConnectionError:
        print("❌ Cannot connect to backend. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    test_transcription()
