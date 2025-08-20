# Installation Guide

This guide will walk you through installing and setting up SalesSense on your system.

## Prerequisites

Before installing SalesSense, ensure you have:

- Python 3.12 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Administrative access (for installing system dependencies)

## Step 1: Install UV Package Manager

UV is a fast Python package manager that we use for dependency management.

=== "Windows"

    ```
    # Install UV using PowerShell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # Verify installation
    uv --version
    ```

=== "macOS"

    ```
    # Install UV using curl
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Verify installation
    uv --version
    ```

=== "Linux"

    ```
    # Install UV using curl
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Verify installation
    uv --version
    ```

## Step 2: Install FFmpeg

FFmpeg is required for audio processing and transcription.

=== "Windows"

    **Option 1: Using Chocolatey (Recommended)**
    ```
    choco install ffmpeg
    ```

    **Option 2: Using Winget**
    ```
    winget install Gyan.FFmpeg
    ```

    **Option 3: Manual Installation**
    1. Download FFmpeg from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
    2. Extract to `C:\ffmpeg\`
    3. Add `C:\ffmpeg\bin` to system PATH

=== "macOS"

    ```
    # Using Homebrew
    brew install ffmpeg
    ```

=== "Linux"

    **Ubuntu/Debian:**
    ```
    sudo apt update && sudo apt install ffmpeg
    ```

    **CentOS/RHEL/Fedora:**
    ```
    sudo dnf install ffmpeg
    ```

### Verify FFmpeg Installation


!!! success "Expected Output"
    You should see FFmpeg version information. If you get "'ffmpeg' is not recognized", restart your terminal and try again.

## Step 3: Setup Project Environment

### Clone or Download Project

Navigate to your desired directory and set up the project:

cd "D:\Sales Sense 2" # or your preferred location


### Create Virtual Environment

Create virtual environment with Python 3.12+
uv venv --python 3.12

Activate the environment
.venv\Scripts\activate # Windows

Install all project dependencies from pyproject.toml
uv pip install -e .


!!! tip "What happens here?"
    This command reads your `pyproject.toml` file and installs all required dependencies automatically. UV is much faster than pip for this process.

## Step 4: Configure Environment

### Create Backend Configuration

Create backend directory if it doesn't exist
mkdir backend

Create .env file
cd backend
echo. > .env # Windows

touch .env # macOS/Linux
text

### Add API Keys

Edit `backend/.env` and add your OpenAI API key:

Required: OpenAI API key for GPT models
OPENAI_API_KEY=your_openai_api_key_here

Optional: LangChain tracing (for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here

text

!!! warning "API Key Security"
    - Never commit your `.env` file to version control
    - Keep your API keys secure and don't share them
    - Monitor your OpenAI usage at [platform.openai.com/usage](https://platform.openai.com/usage)

## Step 5: Verify Installation

### System Check

Run these commands to verify everything is set up correctly:

Check Python version
python --version

Check UV installation
uv --version

Check FFmpeg installation
ffmpeg -version

Test Python imports
python -c "import openai, streamlit, fastapi; print('✅ Core packages OK')"

text

### Test Audio Processing

Test Whisper (this will download the model on first run)
python -c "import whisper; model = whisper.load_model('base'); print('✅ Whisper OK')"

text

## Next Steps

Great! You now have SalesSense installed. Next:

1. **[Quick Start Guide](quick-start.md)** - Run your first analysis
2. **[Configuration](configuration.md)** - Customize your setup  
3. **[User Guide](user-guide/uploading.md)** - Learn to use the interface

## Troubleshooting

If you encounter issues during installation:

- Check the [Troubleshooting Guide](development/troubleshooting.md)
- Ensure you have the latest versions of Python and system dependencies
- Verify your OpenAI API key is valid and has sufficient credits
- Make sure FFmpeg is properly installed and in your system PATH

!!! question "Need help?"
    If you're still having trouble, check our [troubleshooting section](development/troubleshooting.md) or reach out for support.

