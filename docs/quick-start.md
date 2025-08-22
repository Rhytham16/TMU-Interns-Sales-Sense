# Quick Start

Run SalesSense in minutes. Copy/paste these commands in order.

## 1) Create project folder and virtual environment

### Windows (PowerShell)
cd "D:\Sales Sense 2"

python -m venv .venv

..venv\Scripts\activate


### macOS/Linux
mkdir -p ~/SalesSense && cd ~/SalesSense

python3 -m venv .venv

source .venv/bin/activate


## 2) Install dependencies

Using pyproject.toml (recommended):

pip install -e .


## 3) Add API keys

Create a file: `backend/.env`

OPENAI_API_KEY=your_openai_api_key

ASSEMBLYAI_API_KEY=your_assemblyai_api_key


## 4) Start backend (FastAPI)

Open Terminal 1:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

text

Health check:
curl http://localhost:8000/health

text

Expected: JSON with status ok and basic info.

## 5) Start frontend (Streamlit)

Open a new terminal (activate the same venv), then:
streamlit run streamlit_app.py

text

Open:
http://localhost:8501

text

## 6) First analysis (UI flow)

- Go to “Data Ingestion”
- Upload a call recording (.mp3, .wav, .m4a, .aac)
- Fill in Participants, Call details, Call type
- Click “Analyze Call”
- You’ll be redirected to Results after processing

## Useful endpoints

- API docs: `http://localhost:8000/docs`
- Health: `GET /health`
- Transcribe: `POST /transcribe/` (file)
- Analyze combined: `POST /analyze_call` (file + form)

## Troubleshooting (fast)

- Backend not starting: ensure port 8000 is free; activate the venv; restart terminal.
- Frontend not starting: verify Streamlit is installed in the venv.
- Empty analysis: check keys in `backend/.env` and API usage limits.
- AssemblyAI errors: confirm `ASSEMBLYAI_API_KEY` and try a clean mp3/wav.

## Tips

- Re-uploading the same file with the same context returns cached results instantly.
- Keep Windows project paths short (e.g., `D:\SalesSense`) to avoid long-path issues.
text
undefined