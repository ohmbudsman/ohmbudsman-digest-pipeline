import os
import requests
import hashlib
import datetime

# Configuration
BUTTONDOWN_API_KEY = os.getenv("BUTTONDOWN_API_KEY")
DIGEST_FILE = "digest_output.md"
DIGEST_DATE = datetime.date.today().strftime("%Y-%m-%d")
TITLE = f"Ohmbudsman Digest – {DIGEST_DATE}"
AUTHOR = "Justin Waldrop"
VENTURE = "Ohmbudsman Media LLC"
VERSION = "v1.0"
LICENSE = "CC-BY-NC"

# Read digest content
def read_digest():
    with open(DIGEST_FILE, "r", encoding="utf-8") as file:
        return file.read()

# Build metadata
def build_metadata(content):
    sha256_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    metadata = f"""---
title: {TITLE}
author: {AUTHOR}
venture: {VENTURE}
version: {VERSION}
date: {DIGEST_DATE}
sha256: {sha256_hash}
license: {LICENSE}
---

"""
    return metadata + content + f"""

---
Licensed under Creative Commons BY-NC 4.0  
https://creativecommons.org/licenses/by-nc/4.0/
"""

# Create draft email
def create_draft_email(content):
    url = "https://api.buttondown.email/v1/emails"
    headers = {
        "Authorization": f"Token {BUTTONDOWN_API_KEY}"
    }
    data = {
        "subject": TITLE,
        "body": content,
        "status": "draft"
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Main execution
if __name__ == "__main__":
    try:
        digest_content = read_digest()
        full_content = build_metadata(digest_content)
        result = create_draft_email(full_content)
        print(f"Draft created successfully. Email ID: {result['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")
