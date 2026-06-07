import logging
from pathlib import Path

from faster_whisper import WhisperModel

from app.config import Settings

logger = logging.getLogger(__name__)


class TranscriberService:
    """Transcreve áudio de reuniões usando modelos Whisper (via faster-whisper)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            logger.info(
                "A carregar modelo Whisper '%s' em %s...",
                self._settings.whisper_model,
                self._settings.whisper_device,
            )
            self._model = WhisperModel(
                self._settings.whisper_model,
                device=self._settings.whisper_device,
                compute_type=self._settings.whisper_compute_type,
            )
        return self._model

    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
    ) -> tuple[str, str | None, float | None]:
        """
        Transcreve um ficheiro de áudio.

        Returns:
            Tuplo (texto, idioma detetado, duração em segundos).
        """
        model = self._get_model()

        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,
        )

        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text, info.language, info.duration
