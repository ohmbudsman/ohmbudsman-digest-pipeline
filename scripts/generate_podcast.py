#!/usr/bin/env python3
"""Create a podcast script from a digest using OpenAI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("OPENAI_API_KEY not set")
openai.api_key = OPENAI_API_KEY

PROMPT = (
    "Compress the following digest into a 500-700 word podcast script. "
    "Write in a concise, conversational tone."
)


def generate_script(md_path: Path, out_dir: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": text},
    ]
    resp = openai.ChatCompletion.create(model="gpt-4o", messages=messages, temperature=0.4)
    script = resp.choices[0].message.content.strip()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{md_path.stem}_script.txt"
    out_file.write_text(script, encoding="utf-8")
    print(f"✔ Podcast script saved to {out_file}")
    return out_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: generate_podcast.py DIGEST_MD")
    md_file = Path(sys.argv[1])
    generate_script(md_file, Path("outputs/podcasts"))
