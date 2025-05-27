#!/usr/bin/env python3
"""
Convert output/digest_output.md → output/digest.pdf via Pandoc/XeLaTeX.
"""

import subprocess
from pathlib import Path

md_in  = Path("output/digest_output.md")
pdf_out = Path("output/digest.pdf")
pdf_out.parent.mkdir(exist_ok=True, parents=True)

print(f"→ Rendering {md_in} → {pdf_out}")
subprocess.run(
    ["pandoc", str(md_in),
     "--pdf-engine=xelatex",
     "-o", str(pdf_out)],
    check=True
)
print(f"✔  PDF written to {pdf_out}")
