#!/usr/bin/env python3
"""
1) Fetch all articles updated in the last 24 h from Readwise Reader.
2) Send them to OpenAI’s v1/assistants/{assistant_id}/runs endpoint,
   instructing strict Disguised-SNAP markdown.
3) Poll until completion, then write the assistant’s output
   to output/digest_output.md
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import requests

# ─── Config ──────────────────────────────────────────────────────────────
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_KEY     = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID   = "asst_aumVzFe2kUL0u0K0H88owQ1F"
BASE_OPENAI    = "https://api.openai.com/v1/assistants"
BASE_READWISE  = "https://readwise.io/api/v3/list/"

if not READWISE_TOKEN or not OPENAI_KEY:
    sys.exit("❌ Missing READWISE_TOKEN or OPENAI_API_KEY")

# ─── 1. Fetch articles from Reader ───────────────────────────────────────
cutoff = (datetime.utcnow() - timedelta(days=1)).replace(tzinfo=timezone.utc).isoformat()
params = {"updatedAfter": cutoff, "page_size": 1000, "category": "article"}
headers_rw = {"Authorization": f"Token {READWISE_TOKEN}"}

resp = requests.get(BASE_READWISE, headers=headers_rw, params=params, timeout=30)
if resp.status_code != 200:
    print("Readwise API error:", resp.status_code, resp.text, file=sys.stderr)
    resp.raise_for_status()

docs = resp.json().get("results", [])
if not docs:
    sys.exit("❌ No articles found in the past 24 h")

# ─── 2. Kick off Assistant run ───────────────────────────────────────────
run_body = {
    "assistant_id": ASSISTANT_ID,
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "instructions": (
        "Generate a daily newsletter in strict Disguised-SNAP markdown. "
        "Preserve labels HEADLINE, NUTSHELL, HOOK, TAKEAWAY, LINKS, MOMENTUM, "
        "QUESTION, OUTLOOK, CTA. ≤15-word sentences, one emoji per bullet."
    ),
    "messages": [
        {"role": "user", "content": json.dumps(docs, indent=2)}
    ],
}

resp = requests.post(
    f"{BASE_OPENAI}/{ASSISTANT_ID}/runs",
    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
    json=run_body,
    timeout=30,
)
if resp.status_code != 200 and resp.status_code != 201:
    print("OpenAI run error:", resp.status_code, resp.text, file=sys.stderr)
    resp.raise_for_status()

run = resp.json()
run_id = run["id"]
print(f"✔ Started Assistant run {run_id}")

# ─── 3. Poll until done ─────────────────────────────────────────────────
status = run.get("status", "")
while status not in ("succeeded", "failed"):
    time.sleep(1)
    poll = requests.get(
        f"{BASE_OPENAI}/{ASSISTANT_ID}/runs/{run_id}",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        timeout=30,
    )
    poll.raise_for_status()
    data = poll.json()
    status = data.get("status", "")
    print(f"… polling, status = {status}")

if status != "succeeded":
    sys.exit(f"❌ Assistant run failed: {data}")

# ─── 4. Extract markdown & write file ────────────────────────────────────
messages = data.get("output", {}).get("messages", [])
if not messages:
    sys.exit("❌ No messages in assistant output")

digest_md = messages[-1].get("content", "")
out = Path("output")
out.mkdir(exist_ok=True, parents=True)
path = out / "digest_output.md"
path.write_text(digest_md, encoding="utf-8")
print(f"✔  Saved markdown to {path}")
