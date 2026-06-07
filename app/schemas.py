from pydantic import BaseModel, Field


class AudioSummary(BaseModel):
    overview: str = Field(
        ...,
        description="2-3 sentence summary of what the audio is about",
    )
    main_topics: list[str] = Field(
        ...,
        description="Main subjects or sections covered",
    )
    key_points: list[str] = Field(
        ...,
        description="Important facts, explanations, or details mentioned",
    )
    takeaways: list[str] = Field(
        ...,
        description="Main conclusions or things worth remembering",
    )


class SummarizeResponse(BaseModel):
    transcription: str
    summary: AudioSummary
    duration_seconds: float | None = None
    language: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    whisper_model: str
    llm_provider: str
