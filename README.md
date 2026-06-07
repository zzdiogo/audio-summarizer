<p align="center">
  <h1 align="center">🎧 Audio Summarizer</h1>
  <p align="center">
    Turn any recording into a transcript and a structured summary — powered by Whisper &amp; LLMs.
  </p>
</p>

<p align="center">
  <a href="https://github.com/zzdiogo/audio-summarizer"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://github.com/openai/whisper"><img src="https://img.shields.io/badge/Whisper-OpenAI-412991?style=flat" alt="Whisper"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
</p>

<p align="center">
  <b>Built by <a href="https://github.com/zzdiogo">Diogo Botelho</a></b>
</p>

---

## About

**Audio Summarizer** is a full-stack AI application that transcribes and summarizes spoken content from audio and video files. Upload a lecture, podcast, YouTube video, or any recording — get back a full transcript plus a clean, structured summary.

Perfect for students, developers, and anyone who wants to digest long-form audio without listening to the entire thing.

### Use cases

| | |
|---|---|
| 🎓 Lectures & classes | Summarize hour-long recordings into key points |
| 🎬 YouTube & tutorials | Extract what was taught from video audio |
| 🎙️ Podcasts & interviews | Get topics and takeaways in seconds |
| 📼 Voice memos & recordings | Transcribe and organize any spoken content |

<!-- Uncomment after adding a demo GIF to docs/demo.gif -->
<!-- <p align="center"><img src="docs/demo.gif" width="700" alt="Demo"></p> -->

---

## How it works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌────────────────┐
│  Audio/MP4  │ ──▶ │  faster-whisper  │ ──▶ │  LLM        │ ──▶ │  Summary +     │
│  upload     │     │  (transcription) │     │  (Ollama /  │     │  Transcript    │
│             │     │                  │     │   OpenAI)   │     │                │
└─────────────┘     └──────────────────┘     └─────────────┘     └────────────────┘
```

**Output sections:**

| Section | What you get |
|---------|--------------|
| **Summary** | 2–3 sentence overview of the content |
| **Main topics** | Subjects and sections covered |
| **Key points** | Important facts, definitions, and details |
| **Takeaways** | Main conclusions worth remembering |
| **Full transcript** | Complete text of everything spoken |

---

## Features

- **Web UI** — drag-and-drop upload, no setup needed in the browser
- **REST API** — auto-generated Swagger docs at `/docs`
- **Multiple formats** — MP3, WAV, M4A, MP4, OGG, FLAC, WebM
- **Flexible LLM** — [Ollama](https://ollama.ai) (free, offline) or OpenAI (best quality)
- **Docker** — run anywhere with one command
- **CLI** — scriptable for automation
- **Privacy-first** — runs locally by default; uploaded files are deleted after processing

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | [FastAPI](https://fastapi.tiangolo.com) |
| Transcription | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper) |
| Summarization | [Ollama](https://ollama.ai) / OpenAI GPT |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Docker, docker-compose |

---

## Quick start

### Requirements

- Python 3.11+
- [FFmpeg](https://ffmpeg.org/download.html)
- [Ollama](https://ollama.ai) **or** an OpenAI API key

### Install

```bash
git clone https://github.com/zzdiogo/audio-summarizer.git
cd audio-summarizer

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### Configure

Edit `.env`:

```env
# Free & local (recommended to start)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# Or OpenAI for best quality
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-api-key-here
```

Pull an Ollama model:

```bash
ollama pull llama3.2
```

> For richer summaries, use `ollama pull llama3.1:8b` and set `OLLAMA_MODEL=llama3.1:8b`.

### Run

```powershell
# Windows
.\run.ps1
```

```bash
# macOS / Linux
uvicorn app.main:app --reload
```

Open **http://localhost:8000** → drop a file → click **Generate summary**.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API docs |
| `POST` | `/api/v1/summarize` | Transcribe & summarize |

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -F "audio=@lecture.mp4" \
  -F "language=en"
```

<details>
<summary><b>Example JSON response</b></summary>

```json
{
  "transcription": "Today we'll cover the fundamentals of machine learning...",
  "summary": {
    "overview": "This lecture introduces machine learning basics, covering supervised vs unsupervised learning and real-world applications.",
    "main_topics": [
      "Introduction to machine learning: definition and why it matters in modern software.",
      "Supervised learning: labeled data, training, and prediction with examples."
    ],
    "key_points": [
      "Supervised learning uses labeled datasets to train models that predict outcomes.",
      "Common algorithms include linear regression, decision trees, and neural networks."
    ],
    "takeaways": [
      "Machine learning enables computers to learn patterns from data without explicit programming.",
      "Choosing the right algorithm depends on the problem type and available data."
    ]
  },
  "duration_seconds": 2847.0,
  "language": "en"
}
```

</details>

---

## Project structure

```
audio-summarizer/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Environment settings
│   ├── schemas.py              # Request/response models
│   ├── api/meetings.py         # REST endpoints
│   ├── services/
│   │   ├── transcriber.py      # Whisper transcription
│   │   └── summarizer.py       # LLM summarization
│   └── static/                 # Web UI
├── scripts/summarize_cli.py    # Command-line tool
├── tests/test_api.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.ps1
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `base` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_DEVICE` | `cpu` | `cpu` or `cuda` (GPU) |
| `LLM_PROVIDER` | `openai` | `openai` or `ollama` |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model |
| `MAX_UPLOAD_SIZE_MB` | `100` | Max file size |

**Windows tip:** If Whisper model download fails, set `HF_HUB_DISABLE_SYMLINKS=1` in `.env`.

---

## Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Security & privacy

- API keys live **only** in `.env` (never committed)
- Uploaded audio is stored in a **temporary file** and **deleted immediately** after processing
- With **Ollama**, everything runs **offline** on your machine
- With **OpenAI**, only the transcript text is sent to their API

---

## Author

**Diogo Botelho** — [@zzdiogo](https://github.com/zzdiogo)

---

## License

This project is licensed under the [MIT License](LICENSE).
