#!/usr/bin/env python3
"""Generate social snippets from a digest markdown file using OpenAI."""

from __future__ import annotations

import json
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
    "Extract 3-5 short insight capsules (<=280 chars each), "
    "a LinkedIn summary, and one Mastodon caption from the following markdown. "
    "Respond in JSON with keys 'insights', 'linkedin', 'mastodon'."
)


def create_snippets(md_path: Path, out_dir: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": text},
    ]
    resp = openai.ChatCompletion.create(model="gpt-4o", messages=messages, temperature=0.4)
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"raw": content}
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{md_path.stem}.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✔ Social snippets saved to {out_file}")
    return out_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: create_social_snippets.py DIGEST_MD")
    md_file = Path(sys.argv[1])
    create_snippets(md_file, Path("outputs/social"))
