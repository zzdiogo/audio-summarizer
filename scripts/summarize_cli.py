#!/usr/bin/env python3
"""CLI to transcribe and summarize audio files."""

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
        description="Transcribe and summarize an audio or video file.",
    )
    parser.add_argument("audio", type=Path, help="Path to the audio/video file")
    parser.add_argument(
        "--language",
        "-l",
        help="ISO language code (e.g. en, pt)",
        default=None,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Save result as JSON",
        default=None,
    )
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"Error: file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    settings = get_settings()
    transcriber = TranscriberService(settings)
    summarizer = SummarizerService(settings)

    print(f"Transcribing: {args.audio}")
    transcription, language, duration = transcriber.transcribe(
        args.audio, language=args.language
    )

    if duration:
        print(f"Language: {language} | Duration: {duration:.1f}s")
    print("Generating summary...")

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
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
