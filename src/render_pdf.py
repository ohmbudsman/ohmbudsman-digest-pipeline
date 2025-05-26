#!/usr/bin/env python3
import os, json, re
from pathlib import Path
import subprocess
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")

ARTICLES = "output/articles.json"
PROMPTS_DIR = Path("prompts")
MD_OUT = Path("output/digest.md")
PDF_OUT = Path("output/digest.pdf")

def load_prompts():
    system = (PROMPTS_DIR / "style_guide.txt").read_text()
    example = (PROMPTS_DIR / "one_shot_example.md").read_text()
    return system, example

def call_openai(system_prompt, example, articles_json):
    openai.api_key = OPENAI_API_KEY
    with open(articles_json) as f:
        arts = json.load(f)
    messages = [
        {"role":"system","content":system_prompt},
        {"role":"user","content":example},
        {"role":"user","content": f"Generate digest for these articles:\n{json.dumps(arts, indent=2)}"}
    ]
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )
    return resp.choices[0].message.content

def lint_snap(md_text):
    if len(re.findall(r"^# ", md_text, flags=re.MULTILINE)) != 9:
        raise ValueError("Digest must contain 9 top-level headings")
    bullets = re.findall(r"^- .+", md_text, flags=re.MULTILINE)
    for b in bullets:
        if len(re.findall(r"[\U0001F300-\U0001FAFF]", b)) != 1:
            raise ValueError(f"Bullet '{b}' missing exactly one emoji")
    for sentence in re.split(r"[.?!]", md_text):
        if len(sentence.split()) > 15:
            raise ValueError("Sentence exceeds 15 words")

def md_to_pdf():
    subprocess.run(["typst", "compile", str(MD_OUT)], check=True)
    # or: subprocess.run(["pandoc", str(MD_OUT), "-o", str(PDF_OUT)], check=True)

def main():
    system, example = load_prompts()
    md = call_openai(system, example, ARTICLES)
    os.makedirs(MD_OUT.parent, exist_ok=True)
    MD_OUT.write_text(md)
    lint_snap(md)
    md_to_pdf()
    print(f"Generated PDF at {PDF_OUT}")

if __name__=="__main__":
    main()
