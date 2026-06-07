import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.schemas import SummarizeResponse
from app.services.summarizer import SummarizerService
from app.services.transcriber import TranscriberService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["audio"])


def _validate_audio_file(file: UploadFile, settings: Settings) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    extension = Path(file.filename).suffix.lower()
    allowed = {ext.strip() for ext in settings.allowed_extensions.split(",")}

    if extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Use one of: {', '.join(sorted(allowed))}",
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_audio(
    audio: UploadFile = File(..., description="Audio or video file to summarize"),
    language: str | None = Form(
        default=None,
        description="ISO language code (e.g. en, pt). Auto-detected if omitted.",
    ),
    settings: Settings = Depends(get_settings),
) -> SummarizeResponse:
    """
    Transcribe an audio/video file and return a structured summary.

    - **Overview** — what the content is about
    - **Main topics** — subjects or sections covered
    - **Key points** — important details and facts
    - **Takeaways** — main conclusions to remember
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
                    detail=f"File too large. Maximum size: {settings.max_upload_size_mb} MB",
                )
            tmp.write(chunk)

    try:
        transcriber = TranscriberService(settings)
        summarizer = SummarizerService(settings)

        logger.info("Transcribing: %s", audio.filename)
        transcription, detected_lang, duration = transcriber.transcribe(
            tmp_path, language=language
        )

        if not transcription:
            raise HTTPException(
                status_code=422,
                detail="Could not extract speech from the audio.",
            )

        logger.info("Generating summary (%d characters)...", len(transcription))
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
        logger.exception("Failed to process audio")
        raise HTTPException(
            status_code=500,
            detail="Internal error while processing the audio.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)
