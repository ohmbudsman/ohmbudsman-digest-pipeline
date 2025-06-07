#!/usr/bin/env python3
"""Archive generated assets to a HuggingFace dataset."""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    sys.exit("HUGGINGFACE_TOKEN not set")

def create_zip(files: list[Path], out_path: Path) -> Path:
    with zipfile.ZipFile(out_path, "w") as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    return out_path


def upload_zip(zip_path: Path, repo: str) -> None:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    with zip_path.open("rb") as f:
        resp = requests.post(
            f"https://huggingface.co/api/datasets/{repo}/upload",
            headers=headers,
            files={"file": (zip_path.name, f)},
        )
    print("HuggingFace:", resp.status_code)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Usage: archive_assets.py ZIP_NAME FILE1 [FILE2 ...]")
    zip_name = sys.argv[1]
    files = [Path(p) for p in sys.argv[2:]]
    out = Path("outputs/archive")
    out.mkdir(parents=True, exist_ok=True)
    zip_path = create_zip(files, out / zip_name)
    upload_zip(zip_path, "ohmbudsman/digests")
