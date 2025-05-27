#!/usr/bin/env python3
"""
Send the daily digest email via Buttondown.

Needs:
  BUTTONDOWN_TOKEN  – stored in GitHub Secrets.

Reads PDF_URL from env (set by the render job). If missing, it builds a
fallback URL based on GitHub Pages.
"""

import os
import sys
from datetime import datetime
import requests

# ─── Env vars ──────────────────────────────────────────────────────────
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
PDF_URL          = os.getenv("PDF_URL")
RUN_ID           = os.getenv("GITHUB_RUN_ID")
PAGES_BASE       = "https://ohmbudsman.github.io/ohmbudsman-digest-pipeline"

if not BUTTONDOWN_TOKEN:
    sys.exit("❌ BUTTONDOWN_TOKEN not set")

# Fallback URL if pipeline didn't export one
if not PDF_URL:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    PDF_URL = f"{PAGES_BASE}/digests/{today}.pdf"

# Final check
if not PDF_URL:
    sys.exit("❌ PDF_URL could not be resolved")

# ─── Send email ────────────────────────────────────────────────────────
def main() -> None:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    subject = f"Ohmbudsman Digest {today}"
    body = (
        f"Hello,\n\n"
        f"Your Ohmbudsman Digest for **{today}** is ready.\n\n"
        f"[Download the PDF version]({PDF_URL})\n\n"
        f"— Ohmbudsman"
    )

    headers = {
        "Authorization": f"Token {BUTTONDOWN_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"subject": subject, "body": body}

    resp = requests.post(
        "https://api.buttondown.com/v1/emails",
        headers=headers,
        json=payload,
        timeout=30,
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print(resp.text, file=sys.stderr)
        raise

    print("✔ Email sent!", resp.json())

if __name__ == "__main__":
    main()
