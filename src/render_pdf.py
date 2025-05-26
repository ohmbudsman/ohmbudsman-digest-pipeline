#!/usr/bin/env python3
"""
Render the digest by calling OpenAI’s legacy ChatCompletion.create,
then convert it to PDF via Pandoc.
"""

import os
import json
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import openai

# ─── Env Setup ─────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")
openai.api_key = API_KEY

# ─── Paths ──────────────────────────────────────────────────────────────
ARTICLES_JSON = Path("output/articles.json")
PROMPTS_DIR   = Path("prompts")
MD_OUT        = Path("output/digest.md")
PDF_OUT       = Path("output/digest.pdf")

# ─── Prompt Loading ─────────────────────────────────────────────────────
def load_prompts() -> tuple[str, str]:
    system  = (PROMPTS_DIR / "style_guide.txt").read_text()
    example = (PROMPTS_DIR / "one_shot_example.md").read_text()
    return system, example

# ─── OpenAI Call ────────────────────────────────────────────────────────
def call_openai(system: str, example: str, articles_path: Path) -> str:
    articles = json.loads(articles_path.read_text())
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": example},
        {
            "role":    "user",
            "content": "Generate digest for these articles:\n"
                       + json.dumps(articles, indent=2),
        },
    ]
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content

# ─── Markdown Linting ───────────────────────────────────────────────────
def lint_markdown(md: str) -> None:
    if len(re.findall(r"^#\s+", md, flags=re.MULTILINE)) != 9:
        raise ValueError("Digest must have exactly 9 top-level headings")
    for b in re.findall(r"^- .+", md, flags=re.MULTILINE):
        if len(re.findall(r"[\U0001F300-\U0001FAFF]", b)) != 1:
            raise ValueError(f"Bullet '{b}' needs one emoji")
        if len(b.split()) > 15:
            raise ValueError(f"Bullet '{b}' exceeds 15 words")
    for s in re.split(r"[.?!]", md):
        if len(s.split()) > 15:
            raise ValueError("A sentence exceeds 15 words")

# ─── Convert to PDF ─────────────────────────────────────────────────────
def md_to_pdf() -> None:
    subprocess.run(
        ["pandoc", str(MD_OUT), "-o", str(PDF_OUT)],
        check=True,
    )

# ─── Main Flow ─────────────────────────────────────────────────────────
def main() -> None:
    system, example = load_prompts()
    md_content      = call_openai(system, example, ARTICLES_JSON)
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text(md_content)
    lint_markdown(md_content)
    md_to_pdf()
    print(f"✔ Generated PDF at {PDF_OUT}")

if __name__ == "__main__":
    main()
