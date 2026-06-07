#!/usr/bin/env python3
"""CLI para resumir reuniões a partir da linha de comandos."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.services.summarizer import SummarizerService
from app.services.transcriber import TranscriberService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcreve e resume um ficheiro de áudio de reunião.",
    )
    parser.add_argument("audio", type=Path, help="Caminho para o ficheiro de áudio")
    parser.add_argument(
        "--language",
        "-l",
        help="Código ISO do idioma (ex: pt, en)",
        default=None,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Guardar resultado em JSON",
        default=None,
    )
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"Erro: ficheiro não encontrado: {args.audio}", file=sys.stderr)
        sys.exit(1)

    settings = get_settings()
    transcriber = TranscriberService(settings)
    summarizer = SummarizerService(settings)

    print(f"A transcrever: {args.audio}")
    transcription, language, duration = transcriber.transcribe(
        args.audio, language=args.language
    )

    print(f"Idioma: {language} | Duração: {duration:.1f}s" if duration else "")
    print("A gerar resumo...")

    summary = summarizer.summarize(transcription)

    result = {
        "transcription": transcription,
        "summary": summary.model_dump(),
        "language": language,
        "duration_seconds": duration,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print("\n" + output)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"\nGuardado em: {args.output}")


if __name__ == "__main__":
    main()
