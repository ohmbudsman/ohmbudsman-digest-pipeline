#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()
TOKEN = os.environ.get("BUTTONDOWN_TOKEN")
if not TOKEN:
    raise RuntimeError("BUTTONDOWN_TOKEN missing")

PDF_PATH = Path("output/digest.pdf")
API_URL = "https://api.buttondown.email/v1/emails"

def main():
    # Prepare headers, JSON payload, and file upload
    headers = {
        "Authorization": f"Token {TOKEN}"
    }
    data = {
        "subject": f"Ohmbudsman Digest – {PDF_PATH.stem}",
        "body": "Please find today's digest attached."
        # If you want to draft instead of send immediately, add "status": "draft"
    }
    with open(PDF_PATH, "rb") as pdf_file:
        files = {
            "attachment": ("digest.pdf", pdf_file, "application/pdf")
        }
        resp = requests.post(
            API_URL,
            headers=headers,
            data=data,
            files=files,
        )
    resp.raise_for_status()
    print("Published, status code:", resp.status_code)

if __name__ == "__main__":
    main()
