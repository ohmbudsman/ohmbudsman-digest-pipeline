#!/usr/bin/env python3
"""
Create a Buttondown **draft** email from output/digest_output.md
and log status + response.
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path

TOKEN = os.getenv("BUTTONDOWN_TOKEN")
if not TOKEN:
    sys.exit("❌ BUTTONDOWN_TOKEN not set")

md_file = Path("output/digest_output.md")
if not md_file.exists():
    sys.exit("❌ output/digest_output.md not found")

body_md = md_file.read_text(encoding="utf-8")
today = datetime.utcnow().strftime("%Y-%m-%d")
subject = f"Ohmbudsman Digest — {today}"

payload = {
    "subject": subject,
    "body": body_md,
    "status": "draft"
}
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

print("→ Sending draft to Buttondown…")
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
