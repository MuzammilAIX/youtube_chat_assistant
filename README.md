# YouTube RAG Assistant

A portfolio project that answers questions about YouTube videos using transcript retrieval, embeddings, FAISS, LangChain, OpenAI, and Streamlit.

## Features
- Fetches a video's transcript from YouTube
- Splits transcript text into chunks and preserves approximate timestamps
- Creates and persists a FAISS vector index
- Retrieves relevant chunks for a question
- Generates answers grounded in retrieved transcript evidence
- Displays source chunks and clickable YouTube timestamps
- Includes basic automated tests

## Requirements
- Python 3.12 recommended
- An OpenAI API key with API access and billing configured
- Network access to YouTube and OpenAI

## Setup (Windows PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Open `.env` and replace `OPENAI_API_KEY` with your own key. Never commit `.env`.

## Run
```powershell
$env:PYTHONPATH = "src"
streamlit run app/streamlit_app.py
```
Enter a YouTube URL or video ID in the sidebar, index it, then ask questions.

## Test
```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
```

## What goes in `data/`?
The app creates these automatically:
- `faiss_index/`: `index.faiss` and `index.pkl`, the local vector index and document store
- `manifest.json`: embedding model and chunking metadata

You do not need to download a separate dataset. The transcript is fetched from YouTube at indexing time. The generated index is excluded from Git.

## Important notes
- Transcript availability depends on the video and YouTube's current access behavior.
- Timestamp assignment to character chunks is approximate; for higher accuracy, split on transcript segments and preserve exact segment boundaries.
- The local FAISS `index.pkl` is loaded with pickle deserialization. Only load an index that your own application generated and that you trust.
- This initial version builds one active index at a time. It overwrites the current index when another video is indexed. Multi-video collections and safe index versioning are future improvements.
- The prompt asks the model to cite source labels, but LLM citations must still be checked against the displayed source chunks.
