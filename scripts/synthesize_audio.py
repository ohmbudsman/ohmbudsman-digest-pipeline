#!/usr/bin/env python3
"""Synthesize podcast audio using ElevenLabs API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
EL_API = os.getenv("ELEVENLABS_API_KEY")
TRANSISTOR_API = os.getenv("TRANSISTOR_API_KEY")
if not EL_API:
    sys.exit("ELEVENLABS_API_KEY not set")

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # default voice


def synthesize(script_path: Path, out_dir: Path) -> tuple[Path, Path]:
    text = script_path.read_text(encoding="utf-8")
    headers = {
        "xi-api-key": EL_API,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers=headers,
        data=json.dumps(payload),
    )
    resp.raise_for_status()
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = out_dir / f"{script_path.stem}.mp3"
    mp3_path.write_bytes(resp.content)
    transcript_path = out_dir / f"{script_path.stem}.txt"
    transcript_path.write_text(text, encoding="utf-8")
    print(f"✔ Audio saved to {mp3_path}")
    if TRANSISTOR_API:
        upload_to_transistor(mp3_path, transcript_path)
    return mp3_path, transcript_path


def upload_to_transistor(mp3: Path, transcript: Path) -> None:
    headers = {"x-api-key": TRANSISTOR_API}
    files = {"audio_file": mp3.open("rb"), "transcript": transcript.open("rb")}
    resp = requests.post("https://api.transistor.fm/v1/episodes", headers=headers, files=files)
    print("Transistor:", resp.status_code)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: synthesize_audio.py SCRIPT_TXT")
    synthesize(Path(sys.argv[1]), Path("outputs/podcasts"))
