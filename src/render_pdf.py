#!/usr/bin/env python3
"""Utilities for rendering and linting Disguised-SNAP digests.

The ``render_pdf`` module converts ``output/digest_output.md`` to ``output/digest.pdf``
via Pandoc and XeLaTeX.  It also exposes :func:`lint_snap` used by tests to
validate basic structural rules of the markdown.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = ["lint_snap"]


def lint_snap(md: str) -> None:
    """Validate Disguised-SNAP markdown structure.

    The style guide requires exactly nine top-level headings.  If the document
    contains a different number of headings, a ``ValueError`` is raised.
    """

    headings = [line for line in md.splitlines() if line.startswith("# ")]
    if len(headings) != 9:
        raise ValueError(
            f"Document must contain exactly 9 top-level headings (found {len(headings)})"
        )


md_in  = Path("output/digest_output.md")
pdf_out = Path("output/digest.pdf")
pdf_out.parent.mkdir(exist_ok=True, parents=True)


def render_pdf() -> None:
    """Convert the generated markdown digest into a PDF using Pandoc."""

    print(f"→ Rendering {md_in} → {pdf_out}")
    subprocess.run(
        [
            "pandoc",
            str(md_in),
            "--pdf-engine=xelatex",
            "-o",
            str(pdf_out),
        ],
        check=True,
    )
    print(f"✔  PDF written to {pdf_out}")


if __name__ == "__main__":
    render_pdf()
