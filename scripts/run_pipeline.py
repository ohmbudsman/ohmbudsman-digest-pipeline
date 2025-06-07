#!/usr/bin/env python3
"""Run the full automation pipeline for a digest file."""

from __future__ import annotations

import sys
from pathlib import Path

from generate_pdf import generate_pdf
from create_social_snippets import create_snippets
from generate_podcast import generate_script
from synthesize_audio import synthesize
from update_metadata import update_csv
from archive_assets import create_zip, upload_zip


def run(md_path: Path) -> None:
    pdf = generate_pdf(md_path, Path("outputs/pdfs"))
    social = create_snippets(md_path, Path("outputs/social"))
    script = generate_script(md_path, Path("outputs/podcasts"))
    mp3, transcript = synthesize(script, Path("outputs/podcasts"))
    update_csv(md_path, pdf, mp3, social)
    zip_path = Path("outputs/archive") / f"{md_path.stem}.zip"
    create_zip([pdf, mp3, transcript, social], zip_path)
    upload_zip(zip_path, "ohmbudsman/digests")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: run_pipeline.py DIGEST_MD")
    run(Path(sys.argv[1]))
