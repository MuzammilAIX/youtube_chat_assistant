# TubeMind AI — YouTube RAG Assistant

TubeMind AI is an AI-powered YouTube assistant that lets users analyze video transcripts, generate summaries, explore key insights, and ask questions with source-grounded answers and timestamps.

**Live Demo:** [Try TubeMind AI](https://youtubechatassistant-fm87caqemn3ugmml75bweo.streamlit.app/)

## Features

- **Video Analysis:** Process YouTube videos using their available transcripts.
- **AI-Powered Q&A:** Ask questions and receive context-aware answers.
- **Smart Summaries:** Extract key takeaways, important topics, and action items.
- **Source-Based Responses:** Explore supporting transcript excerpts and timestamps.
- **Interactive Chat:** Maintain conversations and revisit previously analyzed videos.
- **Streamlit Interface:** Use a clean, interactive workspace for video analysis.

## Tech Stack

Python · Streamlit · LangChain · OpenAI · Embeddings · FAISS · Retrieval-Augmented Generation (RAG)

## How It Works

1. Submit a YouTube video URL.
2. Retrieve and process the available transcript.
3. Split the transcript into chunks and create vector embeddings.
4. Store and retrieve relevant content using FAISS.
5. Generate answers and summaries grounded in retrieved video content.

## Run Locally

```bash
git clone https://github.com/MuzammilAIX/youtube-rag-assistant.git
cd youtube-rag-assistant

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Configure your required API keys in a `.env` file before running the application.

## Project Goal

Built to demonstrate practical AI engineering skills in LLM integration, retrieval-augmented generation, semantic search, transcript processing, and interactive application deployment.

## Author

**Muhammad Muzammal Hussain (MuzammilAIX)**

[GitHub Profile](https://github.com/MuzammilAIX)
