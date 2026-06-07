import json
import logging
import re

import httpx
from openai import OpenAI

from app.config import Settings
from app.schemas import AudioSummary

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at summarizing audio content — lectures, podcasts, YouTube videos, interviews, and any spoken recording.

Given a transcript, produce a clear, detailed summary. Respond ONLY with valid JSON in this exact format:
{
  "overview": "2-3 complete sentences describing what the audio is about, who is speaking if identifiable, and the overall purpose.",
  "main_topics": [
    "Topic or section: explain the subject covered and its context in the recording."
  ],
  "key_points": [
    "Important detail: specific facts, definitions, arguments, examples, or explanations mentioned."
  ],
  "takeaways": [
    "Main conclusion or lesson: what the listener should remember from this content."
  ]
}

Rules:
- Write everything in English (unless the transcript is clearly in another language — then match that language).
- Each bullet must be a full, informative sentence — never single words or vague phrases.
- Extract names, dates, numbers, formulas, and terminology when mentioned.
- Works for lectures, tutorials, podcasts, video essays, interviews, and casual videos alike.
- If a list section has no relevant content, use an empty array [] (overview is always required).
- Do NOT invent information not present in the transcript.
- Prefer 3-8 detailed bullets per section when content exists."""


class SummarizerService:
    """Generates structured audio summaries using an LLM."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def summarize(self, transcription: str) -> AudioSummary:
        if not transcription.strip():
            return AudioSummary(
                overview="No speech could be extracted from the audio.",
                main_topics=[],
                key_points=[],
                takeaways=[],
            )

        if self._settings.llm_provider == "ollama":
            raw = self._summarize_with_ollama(transcription)
        else:
            raw = self._summarize_with_openai(transcription)

        return self._parse_summary(raw)

    def _summarize_with_openai(self, transcription: str) -> str:
        if not self._settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Add it to .env or set LLM_PROVIDER=ollama."
            )

        client = OpenAI(
            api_key=self._settings.openai_api_key,
            base_url=self._settings.openai_base_url,
        )

        response = client.chat.completions.create(
            model=self._settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Audio transcript:\n\n{transcription}",
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content or "{}"

    def _summarize_with_ollama(self, transcription: str) -> str:
        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/chat"

        payload = {
            "model": self._settings.ollama_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Audio transcript:\n\n{transcription}",
                },
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2, "num_predict": 2048},
        }

        with httpx.Client(timeout=300.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["message"]["content"]

    def _parse_summary(self, raw: str) -> AudioSummary:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("LLM did not return valid JSON.") from None
            data = json.loads(match.group())

        topics = (
            data.get("main_topics")
            or data.get("topics_discussed")
            or data.get("topicos_discutidos", [])
        )
        points = data.get("key_points") or data.get("decisions_made", [])
        takeaways = (
            data.get("takeaways")
            or data.get("action_items")
            or data.get("proximos_passos", [])
        )

        overview = data.get("overview", "")
        if not overview and topics:
            overview = "; ".join(topics[:2])
        if not overview:
            overview = "Summary generated from the audio transcript."

        return AudioSummary(
            overview=overview,
            main_topics=topics,
            key_points=points,
            takeaways=takeaways,
        )
