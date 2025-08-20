# SalesSense Documentation

<div align="center">
  <img src="assets/salessense-logo.png" alt="SalesSense Logo" width="200"/>
  <h2>🚀 Turn sales calls into coaching moments</h2>
  <p><strong>AI-powered sales call analysis with multi-agent coaching insights</strong></p>
</div>

## Overview

SalesSense gives instant, AI-powered feedback on your Dialpad calls—highlighting what worked, what didn't, and what to do next. Built with modern AI agents and designed for speed, it's perfect for sales teams and POCs.

## Key Features

- **🎤 Audio Transcription**: Ultra-fast speech-to-text using OpenAI Whisper
- **🤖 Multi-Agent Analysis**: 3 specialized AI agents for comprehensive insights
- **📊 Rich Metrics**: Sentiment, talk ratios, objections, and engagement analysis
- **💡 Actionable Coaching**: Specific improvement suggestions with practice drills
- **⚡ Fast Processing**: Complete analysis in under 30 seconds
- **🎯 Sales-Focused**: Built specifically for sales call optimization

## Quick Navigation

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **Quick Start**

    ---

    Get SalesSense running in 5 minutes

    [:octicons-arrow-right-24: Installation Guide](installation.md)

-   :material-upload:{ .lg .middle } **Upload Calls**

    ---

    Learn how to upload and analyze your sales calls

    [:octicons-arrow-right-24: User Guide](user-guide/uploading.md)

-   :material-chart-line:{ .lg .middle } **Understanding Results**

    ---

    Interpret analysis results and coaching insights

    [:octicons-arrow-right-24: Results Guide](user-guide/results.md)

-   :material-code-braces:{ .lg .middle } **API Reference**

    ---

    Technical documentation for developers

    [:octicons-arrow-right-24: API Docs](api/backend.md)

</div>

## Technology Stack

- **Frontend**: Streamlit for interactive web interface
- **Backend**: FastAPI for high-performance API
- **AI/ML**: OpenAI GPT models with LangChain and LangGraph
- **Audio**: Whisper for transcription, FFmpeg for processing
- **Package Manager**: UV for fast dependency management

## System Requirements

- Python 3.12+
- OpenAI API key
- FFmpeg for audio processing
- 4GB+ RAM recommended
- Windows, macOS, or Linux

!!! tip "Ready to get started?"
    Head over to our [Installation Guide](installation.md) to set up SalesSense in minutes!

## Support

Need help? Check out our [troubleshooting guide](development/troubleshooting.md) or reach out to our team.

---

<div align="center">
  <p><strong>Built by <a href="https://cogentinfo.com">Cogent Infotech Innovation Lab</a></strong></p>
</div>
