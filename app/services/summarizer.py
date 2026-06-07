import json
import logging
import re

import httpx
from openai import OpenAI

from app.config import Settings
from app.schemas import MeetingSummary

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """És um assistente especializado em analisar transcrições de reuniões.
O teu trabalho é extrair informação estruturada e responder APENAS em JSON válido.

Formato obrigatório:
{
  "topicos_discutidos": ["tópico 1", "tópico 2"],
  "decisoes_tomadas": ["decisão 1", "decisão 2"],
  "proximos_passos": ["ação 1", "ação 2"]
}

Regras:
- Escreve em português, a menos que a transcrição esteja noutro idioma
- Sê conciso mas completo
- Se uma secção não tiver conteúdo relevante, usa uma lista vazia []
- Não inventes informação que não esteja na transcrição"""


class SummarizerService:
    """Gera resumos estruturados de reuniões usando um LLM."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def summarize(self, transcription: str) -> MeetingSummary:
        if not transcription.strip():
            return MeetingSummary(
                topicos_discutidos=[],
                decisoes_tomadas=[],
                proximos_passos=[],
            )

        if self._settings.llm_provider == "ollama":
            raw = self._summarize_with_ollama(transcription)
        else:
            raw = self._summarize_with_openai(transcription)

        return self._parse_summary(raw)

    def _summarize_with_openai(self, transcription: str) -> str:
        if not self._settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Define a variável no .env ou usa LLM_PROVIDER=ollama."
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
                    "content": f"Transcrição da reunião:\n\n{transcription}",
                },
            ],
            temperature=0.3,
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
                    "content": f"Transcrição da reunião:\n\n{transcription}",
                },
            ],
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["message"]["content"]

    def _parse_summary(self, raw: str) -> MeetingSummary:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("O LLM não devolveu JSON válido.") from None
            data = json.loads(match.group())

        return MeetingSummary(
            topicos_discutidos=data.get("topicos_discutidos", []),
            decisoes_tomadas=data.get("decisoes_tomadas", []),
            proximos_passos=data.get("proximos_passos", []),
        )
