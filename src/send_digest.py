#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime

# Configuration: ensure these env vars are set in your GitHub Action or shell
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
PDF_URL           = os.getenv("PDF_URL")  # e.g. https://mycdn.com/2025-05-26_digest.pdf

if not BUTTONDOWN_TOKEN:
    print("ERROR: BUTTONDOWN_TOKEN not set", file=sys.stderr)
    sys.exit(1)

if not PDF_URL:
    print("ERROR: PDF_URL not set", file=sys.stderr)
    sys.exit(1)

def main():
    # Prepare email metadata
    today = datetime.utcnow().strftime("%Y-%m-%d")
    subject = f"Ohmbudsman Digest {today}"
    body_md = (
        f"Hello,\n\n"
        f"Your Ohmbudsman Digest for **{today}** is available here:\n\n"
        f"[Download the PDF version]({PDF_URL})\n\n"
        f"— Ohmbudsman\n"
    )

    # Build request
    url = "https://api.buttondown.com/v1/emails"
    headers = {
        "Authorization": f"Token {BUTTONDOWN_TOKEN}",
        "Content-Type":  "application/json",
    }
    payload = {
        "subject": subject,
        "body":    body_md,
        # omit "status" to send immediately; use "scheduled" + "publish_date" to schedule
    }

    # Send
    resp = requests.post(url, headers=headers, json=payload)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"ERROR: Buttondown responded {resp.status_code}:\n{resp.text}", file=sys.stderr)
        sys.exit(1)

    print("✔ Email sent successfully!")
    print(resp.json())  # log the API response for auditing

if __name__ == "__main__":
    main()
