#!/usr/bin/env python3
"""Convert a markdown digest to PDF using pandoc."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def sha256_of(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def generate_pdf(md_path: Path, out_dir: Path) -> Path:
    if not md_path.exists():
        raise FileNotFoundError(md_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    sha = sha256_of(md_path)
    date = datetime.utcnow().strftime("%Y-%m-%d")
    version = "1.0"
    # Append footer with metadata
    footer = f"\n\n---\nGenerated {date} | version {version} | SHA256 {sha}\n"
    temp_md = out_dir / (md_path.stem + "_tmp.md")
    temp_md.write_text(md_path.read_text(encoding="utf-8") + footer, encoding="utf-8")

    pdf_path = out_dir / (md_path.stem + ".pdf")
    subprocess.run(
        ["pandoc", str(temp_md), "--pdf-engine=xelatex", "-o", str(pdf_path)],
        check=True,
    )
    temp_md.unlink()
    print(f"✔ PDF generated at {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: generate_pdf.py DIGEST_MD")
    md_file = Path(sys.argv[1])
    out = Path("outputs/pdfs")
    generate_pdf(md_file, out)
