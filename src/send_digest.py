#!/usr/bin/env python3
import os
from buttondown import Buttondown
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("BUTTONDOWN_TOKEN")
if not TOKEN:
    raise RuntimeError("BUTTONDOWN_TOKEN missing")

client = Buttondown(api_key=TOKEN)
PDF = Path("output/digest.pdf")

def main():
    with open(PDF, "rb") as f:
        pdf_bytes = f.read()
    resp = client.create(
        data={
            "title": f"Ohmbudsman Digest – {PDF.stem}",
            "body": "Attached is today's digest PDF.",
        },
        files={"attachment": ("digest.pdf", pdf_bytes, "application/pdf")},
    )
    print("Published:", resp.get("status"))

if __name__=="__main__":
    main()
