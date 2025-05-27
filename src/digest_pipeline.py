#!/usr/bin/env python3
"""
Ohmbudsman Digest pipeline – single-file version
------------------------------------------------
1. Fetch all Readwise articles tagged with READWISE_TAG from the past 24 h
2. Summarise in Disguised-SNAP via OpenAI Assistant (mini-4o-high)
3. Assemble markdown with front-matter and push a **draft** to Buttondown
   (no auto-send)

ENV VARS required
──────────────────────────────────────────────────────────────────────────
READWISE_TOKEN   – Readwise API token               (secret)
OPENAI_API_KEY   – OpenAI key                       (secret)
BUTTONDOWN_TOKEN – Buttondown API token             (secret)
READWISE_TAG     – Tag to filter (default: ohmbudsman)
"""

from __future__ import annotations
import os, sys, json, math, time, textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests, openai
from dotenv import load_dotenv

# ─── env ─────────────────────────────────────────────────────────────────
load_dotenv()
RW_TOKEN  = os.getenv("READWISE_TOKEN")
OPENAI_KEY= os.getenv("OPENAI_API_KEY")
BD_TOKEN  = os.getenv("BUTTONDOWN_TOKEN")
TAG       = os.getenv("READWISE_TAG", "ohmbudsman")  # default tag

if not (RW_TOKEN and OPENAI_KEY and BD_TOKEN):
    sys.exit("❌ Missing one of READWISE_TOKEN / OPENAI_API_KEY / BUTTONDOWN_TOKEN")

openai.api_key = OPENAI_KEY
ASSISTANT_ID   = "asst_aumVzFe2kUL0u0K0H88owQ1F"
MODEL          = "gpt-4o-mini-high"

# ─── 1. fetch tagged Reader docs ────────────────────────────────────────
def iso(dt: datetime)->str:
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat()+'Z'

cutoff = iso(datetime.utcnow() - timedelta(days=1))
base   = "https://readwise.io/api/v3/list/"
docs: list[dict]=[]
params={"updatedAfter": cutoff, "page_size":1000, "category":"article","tags":TAG}
hdr   = {"Authorization":f"Token {RW_TOKEN}"}

while True:
    r=requests.get(base,headers=hdr,params=params,timeout=30)
    r.raise_for_status()
    d=r.json(); docs.extend(d.get("results",[]))
    cursor=d.get("nextPageCursor")
    if not cursor: break
    params={"page_size":1000,"pageCursor":cursor}
    time.sleep(.2)

if not docs:
    sys.exit(f"❌ No articles tagged #{TAG} in past 24 h")

print(f"✔ Fetched {len(docs)} tagged articles")

# ─── 2. batch + summarise ───────────────────────────────────────────────
MAX_TOKENS=50000  # conservative chunk size
payload=json.dumps(docs,indent=2)
# naive token estimate: 4 chars ≈1 token
chunk_size_chars=MAX_TOKENS*4
chunks=[payload[i:i+chunk_size_chars] for i in range(0,len(payload),chunk_size_chars)]

def call_openai(chunk:str)->str:
    system=(
      "You are an expert newsletter writer. Produce a DAILY DIGEST "
      "in strict Disguised-SNAP markdown. Use these rules:\n"
      "• start with '## HEADLINE' (no top H1)\n"
      "• Preserve labels HEADLINE, NUTSHELL, HOOK, TAKEAWAY, LINKS, "
      "MOMENTUM, QUESTION, OUTLOOK, CTA.\n"
      "• ≤15-word sentences; one emoji per bullet. "
      "• Do NOT shorten labels or remove them."
    )
    messages=[{"role":"system","content":system},
              {"role":"user","content":f"Summarise the following JSON list of articles:\n{chunk}"}]
    resp=openai.ChatCompletion.create(model=MODEL,messages=messages,temperature=0.3)
    return resp.choices[0].message.content.strip()

parts=[call_openai(c) for c in chunks]
digest_md="\n\n".join(parts)
print("✔ Generated digest markdown")

# ─── 3. prepend YAML + write file ───────────────────────────────────────
today=datetime.utcnow().strftime("%Y-%m-%d")
front=f"""---\ntitle: "Ohmbudsman Digest — {today}"\ndate: {today}\nauthor: Ohmbudsman\nlicense: CC-BY-NC\n---\n\n"""
full_md=front+digest_md

out=Path("output"); out.mkdir(parents=True,exist_ok=True)
(out/"digest_output.md").write_text(full_md,encoding="utf-8")
print("✔ Saved output/digest_output.md")

# ─── 4. post draft to Buttondown ────────────────────────────────────────
headers_bd={"Authorization":f"Token {BD_TOKEN}","Content-Type":"application/json"}
payload_bd={"subject":f"Ohmbudsman Digest — {today}","body":full_md,"status":"draft"}
resp_bd=requests.post("https://api.buttondown.com/v1/emails",
                      headers=headers_bd,json=payload_bd,timeout=30)
print("Buttondown status:",resp_bd.status_code)
print(resp_bd.text)
resp_bd.raise_for_status()
print("✔ Draft created successfully")
