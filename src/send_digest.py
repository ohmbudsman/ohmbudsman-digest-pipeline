#!/usr/bin/env python3
"""
Create a Buttondown **draft** email from the Disguised-SNAP markdown digest.
It looks in 'output/digest_output.md' or, if missing, 'digest_output.md'.
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path

TOKEN = os.getenv("BUTTONDOWN_TOKEN")
if not TOKEN:
    sys.exit("❌ BUTTONDOWN_TOKEN not set")

# locate the digest markdown
out_md  = Path("output/digest_output.md")
root_md = Path("digest_output.md")

if out_md.exists():
    md_path = out_md
elif root_md.exists():
    md_path = root_md
else:
    sys.exit("❌ digest_output.md not found in output/ or repo root")

body_md = md_path.read_text(encoding="utf-8")
today   = datetime.utcnow().strftime("%Y-%m-%d")
subject = f"Ohmbudsman Digest — {today}"

payload = {
    "subject": subject,
    "body":    body_md,
    "status":  "draft"
}
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type":  "application/json"
}

print(f"→ Sending draft ({md_path}) to Buttondown…")
resp = requests.post(
    "https://api.buttondown.com/v1/emails",
    headers=headers,
    json=payload,
    timeout=30
)

print("← Buttondown response status:", resp.status_code)
print(resp.text)
resp.raise_for_status()
print("✔  Draft created successfully.")
