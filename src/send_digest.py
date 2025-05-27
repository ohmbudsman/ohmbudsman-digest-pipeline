#!/usr/bin/env python3
"""
Create a Buttondown **draft** email from the Disguised-SNAP markdown digest.
Removes any top-level headings and prepends YAML frontmatter:
  - title
  - date
  - author
Retains full body. Logs status and response.
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# ─── Config ─────────────────────────────────────────────────────────────
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
if not BUTTONDOWN_TOKEN:
    sys.exit("❌ BUTTONDOWN_TOKEN not set")

# ─── Locate digest markdown ───────────────────────────────────────────────
out_path = Path("output/digest_output.md")
root_path = Path("digest_output.md")

if out_path.exists():
    md_file = out_path
elif root_path.exists():
    md_file = root_path
else:
    sys.exit("❌ digest_output.md not found in output/ or repo root")

raw = md_file.read_text(encoding="utf-8")
# Strip any top-level headings and blank lines
lines = raw.splitlines()
body_lines = []
header_skipped = False
for line in lines:
    if not header_skipped:
        if line.startswith("# ") or not line.strip():
            continue
        header_skipped = True
    body_lines.append(line)
body_content = "\n".join(body_lines)

# ─── Prepend YAML frontmatter ────────────────────────────────────────────
today = datetime.utcnow().strftime("%Y-%m-%d")
frontmatter = (
    f"---\n"
    f"title: \"Ohmbudsman Digest — {today}\"\n"
    f"date: {today}\n"
    f"author: Ohmbudsman\n"
    f"---\n\n"
)
body_md = frontmatter + body_content

# ─── Prepare and send payload ────────────────────────────────────────────
subject = f"Ohmbudsman Digest — {today}"
payload = {
    "subject": subject,
    "body":    body_md,
    "status":  "draft"
}
headers = {
    "Authorization": f"Token {BUTTONDOWN_TOKEN}",
    "Content-Type":  "application/json"
}

print("→ Sending draft to Buttondown…")
resp = requests.post(
    "https://api.buttondown.com/v1/emails",
    headers=headers,
    json=payload,
    timeout=30
)

print("← Buttondown status:", resp.status_code)
print(resp.text)
resp.raise_for_status()
print("✔ Draft created successfully.")
