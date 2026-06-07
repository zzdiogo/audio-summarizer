import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.config import Settings, get_settings
from app.schemas import SummarizeResponse
from app.services.summarizer import SummarizerService
from app.services.transcriber import TranscriberService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["meetings"])


def _validate_audio_file(file: UploadFile, settings: Settings) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do ficheiro em falta.")

    extension = Path(file.filename).suffix.lower()
    allowed = {ext.strip() for ext in settings.allowed_extensions.split(",")}

    if extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Usa um destes: {', '.join(sorted(allowed))}",
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_meeting(
    audio: UploadFile = File(..., description="Ficheiro de áudio da reunião"),
    language: str | None = Query(
        None,
        description="Código ISO do idioma (ex: pt, en). Auto-detetado se omitido.",
        min_length=2,
        max_length=5,
    ),
    settings: Settings = get_settings,
) -> SummarizeResponse:
    """
    Transcreve um ficheiro de áudio e devolve um resumo estruturado da reunião.

    - **Tópicos discutidos**
    - **Decisões tomadas**
    - **Próximos passos**
    """
    _validate_audio_file(audio, settings)

    suffix = Path(audio.filename or "audio").suffix
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        total = 0

        while chunk := await audio.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                tmp_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"Ficheiro demasiado grande. Máximo: {settings.max_upload_size_mb} MB",
                )
            tmp.write(chunk)

    try:
        transcriber = TranscriberService(settings)
        summarizer = SummarizerService(settings)

        logger.info("A transcrever áudio: %s", audio.filename)
        transcription, detected_lang, duration = transcriber.transcribe(
            tmp_path, language=language
        )

        if not transcription:
            raise HTTPException(
                status_code=422,
                detail="Não foi possível extrair texto do áudio.",
            )

        logger.info("A gerar resumo (%d caracteres)...", len(transcription))
        summary = summarizer.summarize(transcription)

        return SummarizeResponse(
            transcription=transcription,
            summary=summary,
            duration_seconds=duration,
            language=detected_lang,
        )

    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Erro ao processar reunião")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar o áudio.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)
