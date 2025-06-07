#!/usr/bin/env python3
"""Append digest metadata to metadata/content_index.csv."""

from __future__ import annotations

import csv
import hashlib
import sys
from datetime import datetime
from pathlib import Path


def compute_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update_csv(md_path: Path, pdf: Path, mp3: Path, social: Path, version: str = "1.0") -> None:
    date = datetime.utcnow().strftime("%Y-%m-%d")
    sha = compute_sha(md_path)
    row = [date, md_path.stem, str(pdf), str(mp3), str(social), sha, version]
    csv_path = Path("metadata/content_index.csv")
    exists = csv_path.exists()
    with csv_path.open("a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["date", "title", "pdf_path", "podcast_path", "social_path", "sha256", "version"])
        writer.writerow(row)
    print(f"✔ Metadata row appended to {csv_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("Usage: update_metadata.py DIGEST_MD PDF MP3 SOCIAL_JSON")
    update_csv(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
