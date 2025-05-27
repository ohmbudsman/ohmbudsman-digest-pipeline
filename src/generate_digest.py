#!/usr/bin/env python3
"""
1) Fetch all articles updated in the last 24 hours from Readwise Reader.
2) Summarize them using OpenAI’s ChatCompletion in strict Disguised-SNAP format.
3) Save the markdown to output/digest_output.md.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import requests
import openai
from dotenv import load_dotenv

# ─── Load environment ────────────────────────────────────────────────────
load_dotenv()
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_KEY     = os.getenv("OPENAI_API_KEY")

if not READWISE_TOKEN or not OPENAI_KEY:
    sys.exit("❌ Missing READWISE_TOKEN or OPENAI_API_KEY")

openai.api_key = OPENAI_KEY

# ─── Fetch Reader articles ───────────────────────────────────────────────
cutoff = (datetime.utcnow() - timedelta(days=1)) \
    .replace(tzinfo=timezone.utc) \
    .isoformat()
params = {
    "updatedAfter": cutoff,
    "page_size": 1000,
    "category": "article"
}
headers_rw = {"Authorization": f"Token {READWISE_TOKEN}"}

resp = requests.get(
    "https://readwise.io/api/v3/list/",
    headers=headers_rw,
    params=params,
    timeout=30
)
if resp.status_code != 200:
    print("Readwise API error:", resp.status_code, resp.text, file=sys.stderr)
    resp.raise_for_status()

docs = resp.json().get("results", [])
if not docs:
    sys.exit("❌ No articles found in the past 24 hours")

# ─── Prepare prompts for ChatCompletion ─────────────────────────────────
system_prompt = (
    "You are an expert newsletter writer. Generate a daily digest in strict "
    "Disguised-SNAP markdown. Preserve labels HEADLINE, NUTSHELL, HOOK, TAKEAWAY, "
    "LINKS, MOMENTUM, QUESTION, OUTLOOK, CTA. Use ≤15-word sentences and one emoji per bullet."
)
user_content = json.dumps(docs, indent=2)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user",   "content": "Summarize these articles in Disguised-SNAP format:\n" + user_content},
]

# ─── Call OpenAI ChatCompletion ───────────────────────────────────────────
print("→ Calling OpenAI ChatCompletion...")
chat_resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.3,
)

digest_md = chat_resp.choices[0].message.content
print("✔ Received digest from OpenAI")

# ─── Write output file ───────────────────────────────────────────────────
out_dir = Path("output")
out_dir.mkdir(exist_ok=True, parents=True)

output_file = out_dir / "digest_output.md"
output_file.write_text(digest_md, encoding="utf-8")
print(f"✔ Saved markdown to {output_file}")
