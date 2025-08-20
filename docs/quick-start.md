# Quick Start Guide

Get SalesSense up and running in 5 minutes! This guide assumes you've already completed the [installation](installation.md).

## Launch SalesSense

### Terminal 1: Start Backend

Navigate to your project directory
cd "D:\Sales Sense 2"

Activate virtual environment
.venv\Scripts\activate

Start the backend server

uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

text

!!! success "Backend Running"
    You should see:
    ```
    INFO: Uvicorn running on http://0.0.0.0:8000
    INFO: Application startup complete.
    ```

### Terminal 2: Start Frontend

Open a **new terminal** and run:

Navigate to project directory
cd "D:\Sales Sense 2"

Activate virtual environment
.venv\Scripts\activate

Start the frontend
uv run streamlit run streamlit_app.py

text

!!! success "Frontend Running"
    Your browser should automatically open to `http://localhost:8501`

## First Analysis

### 1. Upload Audio File

1. Click **"Data Ingestion"** in the sidebar
2. Upload a sales call recording (.mp3, .wav, .m4a, or .aac)
3. Fill in the required fields:
   - **Participants**: Names and roles (e.g., "John Smith (Sales Rep), Jane Doe (Prospect)")
   - **Call Details**: Context about the call
   - **Call Type**: Select appropriate type(s)

### 2. Analyze Call

1. Click **"🚀 Analyze Call"**
2. Wait for processing (usually 15-30 seconds)
3. You'll see progress indicators for:
   - Audio transcription
   - Multi-agent analysis

### 3. View Results

The system will automatically redirect you to the results page showing:

- **📋 Executive Summary**: High-level call overview
- **📈 Call Metrics**: Sentiment, talk ratios, questions, objections
- **✅ Strengths**: What the rep did well
- **🎯 Areas for Improvement**: Specific suggestions
- **💡 Coaching Tips**: Actionable advice
- **🎯 Next Steps**: Recommended follow-up actions

## Understanding Your Results

### Call Metrics Explained

| Metric | Description |
|--------|-------------|
| **Overall Sentiment** | Customer's emotional tone (positive/neutral/negative) |
| **Rep Talk Time** | Percentage of call time rep was speaking |
| **Questions Asked** | Number of questions asked by the sales rep |
| **Objections Detected** | Customer concerns or hesitations identified |
| **Follow-ups Committed** | Number of next steps or commitments made |

### Coaching Insights

The AI provides three types of coaching:

1. **Strengths**: Reinforces what worked well
2. **Areas for Improvement**: Specific skills to develop
3. **Coaching Tips**: Actionable advice with practice drills

## Sample Test Call

Don't have a sales call handy? Here's what to expect with a typical analysis:

!!! example "Sample Results"
    **Executive Summary**: "Discovery call with interested prospect discussing CRM needs. Rep effectively identified pain points around customer tracking and demonstrated strong listening skills. Customer expressed budget concerns but showed strong interest in a demo. Next step scheduled for product demonstration."

    **Key Metrics**:
    - Sentiment: Positive
    - Rep Talk Time: 45%
    - Questions Asked: 8
    - Objections: 1 (Budget)

## Common First-Time Issues

### Audio File Issues
- **Supported formats**: .mp3, .wav, .m4a, .aac
- **Max file size**: 25MB
- **Max duration**: 30 minutes for optimal performance

### Backend Not Starting
Check if port 8000 is in use
netstat -ano | findstr :8000

Kill process if needed (Windows)
taskkill /PID <process_id> /F

text

### Missing Analysis Results
- Ensure your OpenAI API key is valid
- Check that you have sufficient API credits
- Verify the audio file contains actual conversation


## Quick Commands Reference

Start everything (run in separate terminals)
Terminal 1 - Backend
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

Terminal 2 - Frontend
uv run streamlit run streamlit_app.py

Check health
curl http://localhost:8000/health

View API docs
Navigate to: http://localhost:8000/docs
text

!!! tip "Pro Tip"
    Bookmark `http://localhost:8501` for quick access to your SalesSense dashboard!