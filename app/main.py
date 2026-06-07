import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.meetings import router as meetings_router
from app.config import get_settings
from app.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="Meeting Summarizer",
    description=(
        "API que transcreve gravações de reuniões com Whisper "
        "e gera resumos estruturados com LLM."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        whisper_model=settings.whisper_model,
        llm_provider=settings.llm_provider,
    )


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {
        "message": "Meeting Summarizer API",
        "docs": "/docs",
        "health": "/health",
    }
