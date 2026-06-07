from pydantic import BaseModel, Field


class MeetingSummary(BaseModel):
    topicos_discutidos: list[str] = Field(
        ...,
        description="Principais tópicos abordados na reunião",
    )
    decisoes_tomadas: list[str] = Field(
        ...,
        description="Decisões concretas acordadas durante a reunião",
    )
    proximos_passos: list[str] = Field(
        ...,
        description="Ações e tarefas definidas para o futuro",
    )


class SummarizeResponse(BaseModel):
    transcription: str
    summary: MeetingSummary
    duration_seconds: float | None = None
    language: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    whisper_model: str
    llm_provider: str
