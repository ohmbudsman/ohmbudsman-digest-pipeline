# Digest Automation Pipeline (Readwise → GPT → Buttondown)

import requests
import datetime
import hashlib
import os
from dateutil import tz

# --- CONFIG ---
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")

tag_filter = "ohmbudsman"
num_articles = 5

# --- FUNCTIONS ---
def fetch_readwise_articles_filtered():
    url = "https://readwise.io/api/v2/highlights/"
    headers = {"Authorization": f"Token {READWISE_TOKEN}"}

    # Set time window in CST and convert to UTC
    cst = tz.gettz('America/Chicago')
    utc = tz.gettz('UTC')
    now = datetime.datetime.now(tz=cst)
    start = now.replace(hour=6, minute=0, second=0, microsecond=0)
    end = now.replace(hour=20, minute=0, second=0, microsecond=0)
    start_utc = start.astimezone(utc).isoformat()
    end_utc = end.astimezone(utc).isoformat()

    # Fetch all highlights
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    highlights = res.json()["results"]

    # Filter by time window
    filtered = [h for h in highlights if start_utc <= h['updated'] <= end_utc and tag_filter in [t['name'] for t in h.get('tags', [])]]
    return filtered

def summarize_articles(articles):
    chunks = [articles[i:i+num_articles] for i in range(0, len(articles), num_articles)]
    summaries = []
    for chunk in chunks:
        prompt = "Summarize the following articles for an Ohmbudsman digest. Output in Markdown:\n"
        for i, article in enumerate(chunk):
            prompt += f"{i+1}. {article['title']} – {article.get('source_url', 'Unknown')}\n"
            prompt += f"Excerpt: {article.get('text', '')[:500]}\n\n"
        chat_payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a geopolitical media digest assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        response = requests.post("https://api.openai.com/v1/chat/completions", json=chat_payload, headers=headers)
        response.raise_for_status()
        summaries.append(response.json()['choices'][0]['message']['content'])
    return "\n---\n\n".join(summaries)

def post_to_buttondown(markdown_text):
    today = datetime.date.today().strftime("%Y-%m-%d")
    md_bytes = markdown_text.encode('utf-8')
    sha = hashlib.sha256(md_bytes).hexdigest()
    title = f"Ohmbudsman Digest – {today}"
    content = f"""---
title: {title}
author: Justin Waldrop
venture: Ohmbudsman Media LLC
version: v1.0
date: {today}
sha256: {sha}
license: CC-BY-NC
---

{markdown_text}

---
Licensed under Creative Commons BY-NC 4.0  
https://creativecommons.org/licenses/by-nc/4.0/
"""
    headers = {"Authorization": f"Token {BUTTONDOWN_TOKEN}"}
    payload = {"subject": title, "body": content, "draft": True}
    res = requests.post("https://api.buttondown.email/v1/emails", headers=headers, json=payload)
    res.raise_for_status()
    return res.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Fetching articles from 6 AM to 8 PM CST...")
    articles = fetch_readwise_articles_filtered()
    print(f"Fetched {len(articles)} articles.")
    if not articles:
        print("No articles found in the specified time window.")
    else:
        print("Summarizing via GPT...")
        digest = summarize_articles(articles)
        print("Posting draft to Buttondown...")
        result = post_to_buttondown(digest)
        print("Success:", result['id'])
