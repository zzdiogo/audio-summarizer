# 🎙️ Meeting Summarizer

> API que transcreve gravações de reuniões e gera resumos estruturados automaticamente.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-orange)](https://github.com/openai/whisper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## O que faz?

Envias um ficheiro de áudio de uma reunião (`.mp3`, `.wav`, `.m4a`, etc.) e a API devolve:

| Secção | Descrição |
|--------|-----------|
| **Tópicos discutidos** | Principais assuntos abordados |
| **Decisões tomadas** | Acordos e conclusões da reunião |
| **Próximos passos** | Ações e tarefas definidas |

Também recebes a transcrição completa do áudio.

```
Áudio da reunião  →  Whisper (transcrição)  →  LLM (resumo)  →  JSON estruturado
```

## Stack tecnológica

| Componente | Tecnologia | Função |
|------------|------------|--------|
| API | [FastAPI](https://fastapi.tiangolo.com) | Endpoints REST com documentação automática |
| Transcrição | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Modelos Whisper da OpenAI, otimizados |
| Resumo | OpenAI GPT / [Ollama](https://ollama.ai) | Geração do resumo estruturado |
| Container | Docker | Deploy reproduzível em qualquer máquina |

## Início rápido

### Pré-requisitos

- Python 3.11+
- [FFmpeg](https://ffmpeg.org/download.html) instalado no sistema
- Chave API da OpenAI **ou** [Ollama](https://ollama.ai) a correr localmente

### 1. Clonar e configurar

```bash
git clone https://github.com/SEU_USERNAME/meeting-summarizer.git
cd meeting-summarizer

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edita o `.env` com a tua configuração:

```env
# Opção A: OpenAI (recomendado para qualidade)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-sua-chave-aqui

# Opção B: Ollama (gratuito, local)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

### 2. Correr a API

**Windows (mais fácil):**

```powershell
.\run.ps1
```

**Manual:**

```bash
uvicorn app.main:app --reload
```

Abre [http://localhost:8000/docs](http://localhost:8000/docs) para a documentação interativa (Swagger).

### 3. Testar

**Via Swagger UI:** vai a `/docs`, endpoint `POST /api/v1/summarize`, faz upload do áudio.

**Via cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@reuniao.mp3"
```

**Via CLI:**

```bash
python scripts/summarize_cli.py reuniao.mp3 -o resultado.json
```

### 4. Docker (alternativa)

```bash
cp .env.example .env
# Edita .env com as tuas credenciais

docker compose up --build
```

A API fica disponível em `http://localhost:8000`.

## Exemplo de resposta

```json
{
  "transcription": "Bom dia a todos. Hoje vamos discutir o lançamento do produto...",
  "summary": {
    "topicos_discutidos": [
      "Lançamento do produto na próxima semana",
      "Orçamento de marketing para Q2",
      "Contratação de um designer"
    ],
    "decisoes_tomadas": [
      "Lançamento confirmado para dia 15",
      "Aprovação de 5000€ para campanha digital"
    ],
    "proximos_passos": [
      "João prepara landing page até sexta",
      "Maria contacta 3 designers até quarta",
      "Reunião de follow-up na próxima segunda"
    ]
  },
  "duration_seconds": 1847.5,
  "language": "pt"
}
```

## Estrutura do projeto

```
meeting-summarizer/
├── app/
│   ├── main.py              # Entrada FastAPI
│   ├── config.py            # Configuração via variáveis de ambiente
│   ├── schemas.py           # Modelos Pydantic (request/response)
│   ├── api/
│   │   └── meetings.py      # Endpoints da API
│   └── services/
│       ├── transcriber.py   # Serviço Whisper
│       └── summarizer.py    # Serviço LLM
├── scripts/
│   └── summarize_cli.py     # CLI para uso local
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuração avançada

| Variável | Default | Descrição |
|----------|---------|-----------|
| `WHISPER_MODEL` | `base` | Modelo Whisper (`tiny`, `base`, `small`, `medium`, `large-v3`) |
| `WHISPER_DEVICE` | `cpu` | `cpu` ou `cuda` (GPU NVIDIA) |
| `LLM_PROVIDER` | `openai` | `openai` ou `ollama` |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo OpenAI para resumo |
| `MAX_UPLOAD_SIZE_MB` | `100` | Tamanho máximo do upload |

> **Dica:** Para reuniões longas, usa `WHISPER_MODEL=small` ou `medium` para melhor precisão. O modelo `base` é um bom equilíbrio entre velocidade e qualidade.

> **Windows:** Se o download do modelo Whisper falhar, ativa o **Modo de Programador** nas definições do Windows, ou define `HF_HUB_DISABLE_SYMLINKS=1` no `.env` (já incluído no `.env.example`).

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Info da API |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Documentação Swagger |
| `POST` | `/api/v1/summarize` | Transcrever e resumir áudio |

## Roadmap

- [ ] Suporte a URLs de áudio (Google Drive, Dropbox)
- [ ] Identificação de speakers (diarização)
- [ ] Exportação para PDF/Markdown
- [ ] Interface web simples
- [ ] Suporte a vídeo (extrair áudio automaticamente)

## Licença

MIT — usa à vontade para portfolio, projetos pessoais ou comerciais.

---

Feito com ☕ e Python
