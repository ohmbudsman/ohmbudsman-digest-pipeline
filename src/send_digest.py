import os
import hashlib
import datetime
import requests

# --- CONFIGURATION ---
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
ASSISTANT_DIGEST_OUTPUT = "digest_output.md"  # Expected output from assistant
DIGEST_DATE = datetime.date.today().strftime("%Y-%m-%d")
TITLE = f"Ohmbudsman Digest – {DIGEST_DATE}"
AUTHOR = "Justin Waldrop"
VENTURE = "Ohmbudsman Media LLC"
VERSION = "v1.0"
LICENSE = "CC-BY-NC"

# --- READ DIGEST CONTENT ---
def read_digest_content():
    if not os.path.exists(ASSISTANT_DIGEST_OUTPUT):
        raise FileNotFoundError(f"Digest output file '{ASSISTANT_DIGEST_OUTPUT}' not found.")
    with open(ASSISTANT_DIGEST_OUTPUT, "r", encoding="utf-8") as f:
        return f.read()

# --- GENERATE METADATA FRONTMATTER ---
def build_metadata(markdown_text):
    sha = hashlib.sha256(markdown_text.encode('utf-8')).hexdigest()
    frontmatter = f"""---
title: {TITLE}
author: {AUTHOR}
venture: {VENTURE}
version: {VERSION}
date: {DIGEST_DATE}
sha256: {sha}
license: {LICENSE}
---

"""
    return frontmatter + markdown_text + """

---
Licensed under Creative Commons BY-NC 4.0  
https://creativecommons.org/licenses/by-nc/4.0/
"""

# --- POST TO BUTTONDOWN ---
def post_to_buttondown(digest_content):
    headers = {"Authorization": f"Token {BUTTONDOWN_TOKEN}"}
    payload = {
        "subject": TITLE,
        "body": digest_content,
        "status": "draft"  # Always DRAFT
    }
    response = requests.post("https://api.buttondown.email/v1/emails", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print("Reading Disguised-SNAP formatted digest content...")
        markdown_text = read_digest_content()

        print("Building full metadata-wrapped digest body...")
        digest_full = build_metadata(markdown_text)

        print("Posting digest draft to Buttondown...")
        result = post_to_buttondown(digest_full)
        print("Draft created successfully. Email ID:", result['id'])

    except Exception as e:
        print("ERROR:", e)
        raise
