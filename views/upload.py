import streamlit as st
import requests

st.markdown("### 🎧 Upload Dialpad Call")
st.caption("Provide the recording and a bit of context so SalesSense can generate accurate, actionable insights.")

# Initialize persistent session state variables
if "upload_ready" not in st.session_state:
    st.session_state.upload_ready = False
if "audio_file_data" not in st.session_state:
    st.session_state.audio_file_data = None
if "participants_data" not in st.session_state:
    st.session_state.participants_data = ""
if "details_data" not in st.session_state:
    st.session_state.details_data = ""
if "call_types_data" not in st.session_state:
    st.session_state.call_types_data = []

with st.form("upload_form", clear_on_submit=False):
    audio_file = st.file_uploader(
        label="Dialpad Call Recording",
        type=["mp3", "wav", "m4a", "aac"],
        help="Upload the audio file from your Dialpad call. We transcribe this to analyze sentiment, talk-time, objections, and more.",
        accept_multiple_files=False
    )

    participants = st.text_area(
        label="Call Participants (names and roles)",
        placeholder="John Smith (Sales Rep), Sarah Johnson (Prospect), Mike Davis (Prospect's Manager)",
        height=100,
        value=st.session_state.participants_data
    )

    details = st.text_area(
        label="Call Details & Context",
        placeholder="Product demo call for CRM software — discussed pricing and implementation timeline — prospect interested, follow-up scheduled.",
        height=120,
        value=st.session_state.details_data
    )

    call_types = st.multiselect(
        label="Call Type",
        options=["Prospecting", "Demo", "Follow-Up", "Negotiation", "Closing", "Customer Support", "Other"],
        default=st.session_state.call_types_data
    )

    submitted = st.form_submit_button("🚀 Analyze Call", type="primary", use_container_width=True)

if st.session_state.audio_file_data is not None:
    st.success(f"✅ Previous audio file: {st.session_state.audio_file_data.name}")

if submitted:
    errors = []
    if not audio_file:
        errors.append("Please upload a call recording.")
    if not participants.strip():
        errors.append("Please provide call participants and roles.")
    if not details.strip():
        errors.append("Please provide call details and context.")
    if not call_types:
        errors.append("Please select at least one call type.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Save form data to session state for persistence
        st.session_state.audio_file_data = audio_file
        st.session_state.participants_data = participants
        st.session_state.details_data = details
        st.session_state.call_types_data = call_types

        # Show processing message with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Uploading audio file...")
        progress_bar.progress(10)
        
        files = {'audio_file': (audio_file.name, audio_file.getvalue(), audio_file.type)}
        data = {
            'participants': participants,
            'details': details,
            'call_types': ",".join(call_types),
        }

        try:
            status_text.text("🎤 Transcribing audio...")
            progress_bar.progress(30)
            
            resp = requests.post(
                "http://localhost:8000/analyze_call", 
                files=files, 
                data=data, 
                timeout=300
            )
            
            progress_bar.progress(70)
            status_text.text("🤖 Running multi-agent analysis...")
            
            if resp.status_code == 200:
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                response_data = resp.json()
                
                # Validate response data structure
                if not response_data.get("summary"):
                    st.warning("⚠️ Analysis completed but some data may be incomplete")
                
                st.session_state.analysis_results = response_data
                st.session_state.upload_ready = True
                
                st.success("✅ Call analysis complete! Redirecting to results...")
                st.balloons()
                
                # Small delay to show success message
                import time
                time.sleep(1)
                st.switch_page("views/results.py")
                
            else:
                st.error(f"❌ Error analyzing call: {resp.status_code}")
                try:
                    error_data = resp.json()
                    st.error(f"Details: {error_data.get('detail', resp.text)}")
                except:
                    st.error(f"Response: {resp.text}")
                    
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. The audio file might be too large or the server is busy. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to backend API. Please ensure the backend server is running on http://localhost:8000")
        except Exception as ex:
            st.error(f"❌ Unexpected error: {ex}")
        finally:
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

# Show current data status
if st.session_state.get("upload_ready", False):
    st.info("✅ Analysis completed! You can view results in the Results page.")
else:
    st.caption("All fields are required for best results. Your audio is processed securely for transcription and analysis.")

# Additional help section
with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    **For optimal analysis:**
    - Upload clear audio files (< 10MB recommended)
    - Provide detailed participant information with roles
    - Include context about the call purpose and outcomes
    - Select appropriate call types
    - Ensure audio contains actual conversation (not just music/silence)
    """)
