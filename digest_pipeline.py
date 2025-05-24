# Digest Automation Pipeline (Readwise Reader → GPT → Buttondown)

import requests
import datetime
import hashlib
import os

# --- CONFIG ---
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")

# --- FUNCTIONS ---
def fetch_readwise_reader_articles():
    url = "https://readwise.io/api/v3/list/"
    headers = {"Authorization": f"Token {READWISE_TOKEN}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    items = res.json().get("results", [])

    print("Logging all Reader items from Readwise:")
    for item in items:
        title = item.get("title", "No Title")
        tags = item.get("tags", [])
        category = item.get("category", "No Category")
        location = item.get("location", "No Location")
        created_at = item.get("created_at", "No Timestamp")
        updated_at = item.get("updated_at", "No Timestamp")
        source = item.get("source_url", "No URL")
        print(f"- Title: {title}")
        print(f"  Tags: {tags}")
        print(f"  Category: {category}")
        print(f"  Location: {location}")
        print(f"  Created At: {created_at}")
        print(f"  Updated At: {updated_at}")
        print(f"  Source URL: {source}\n")

    return items

def summarize_articles(articles):
    return "No summary – diagnostic mode only."

def post_to_buttondown(markdown_text):
    print("[SKIPPED] Draft posting disabled during diagnostics.")
    return {"id": "N/A"}

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print("Fetching ALL Readwise Reader items (no filters)...")
        articles = fetch_readwise_reader_articles()
        print(f"Total items retrieved: {len(articles)}")
        if not articles:
            print("No items found.")
        else:
            print("Diagnostics complete.")
    except Exception as e:
        print("ERROR:", e)
        raise
