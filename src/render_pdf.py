#!/usr/bin/env python3
import os
import json
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load environment
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")

# Paths
ARTICLES = Path("output/articles.json")
PROMPTS_DIR = Path("prompts")
MD_OUT = Path("output/digest.md")
PDF_OUT = Path("output/digest.pdf")

def load_prompts():
    system = (PROMPTS_DIR / "style_guide.txt").read_text()
    example = (PROMPTS_DIR / "one_shot_example.md").read_text()
    return system, example

def call_openai(system_prompt, example, articles_path):
    openai.api_key = OPENAI_API_KEY
    with open(articles_path) as f:
        arts = json.load(f)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": example},
        {
            "role": "user",
            "content": (
                "Generate digest for these articles:\n"
                f"{json.dumps(arts, indent=2)}"
            ),
        },
    ]
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content

def lint_snap(md_text):
    # 1) Exactly 9 top-level headings
    if len(re.findall(r"^#\s+", md_text, flags=re.MULTILINE)) != 9:
        raise ValueError("Digest must contain exactly 9 top-level headings")

    # 2) Bullets: one emoji & ≤15 words
    for bullet in re.findall(r"^- .+", md_text, flags=re.MULTILINE):
        if len(re.findall(r"[\U0001F300-\U0001FAFF]", bullet)) != 1:
            raise ValueError(f"Bullet '{bullet}' must have exactly one emoji")
        if len(bullet.split()) > 15:
            raise ValueError(f"Bullet '{bullet}' exceeds 15 words")

    # 3) Sentences ≤15 words
    for sentence in re.split(r"[.?!]", md_text):
        if len(sentence.split()) > 15:
            raise ValueError("A sentence exceeds 15 words")

def md_to_pdf():
    # Convert Markdown to PDF via Pandoc
    subprocess.run(
        ["pandoc", str(MD_OUT), "-o", str(PDF_OUT)],
        check=True
    )

def main():
    # Generate Markdown via OpenAI
    system, example = load_prompts()
    md = call_openai(system, example, ARTICLES)

    # Write out, lint, then produce PDF
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text(md)
    lint_snap(md)
    md_to_pdf()

    print(f"Generated PDF at {PDF_OUT}")

if __name__ == "__main__":
    main()
