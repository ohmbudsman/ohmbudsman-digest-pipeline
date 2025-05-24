# Digest Automation Pipeline (Readwise Reader → GPT → Buttondown)

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
def fetch_readwise_reader_articles():
    url = "https://readwise.io/api/v3/list/"
    headers = {"Authorization": f"Token {READWISE_TOKEN}"}
    params = {"category": "articles"}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    items = res.json().get("results", [])

    print("Logging raw articles from Readwise Reader:")
    for item in items:
        title = item.get("title", "No Title")
        tags = item.get("tags", [])
        created_at = item.get("created_at", "No Timestamp")
        updated_at = item.get("updated_at", "No Timestamp")
        source = item.get("source_url", "No URL")
        print(f"- Title: {title}")
        print(f"  Tags: {tags}")
        print(f"  Created At: {created_at}")
        print(f"  Updated At: {updated_at}")
        print(f"  Source URL: {source}\n")

    return items  # No filtering, just dump everything for diagnostics

def summarize_articles(articles):
    chunks = [articles[i:i+num_articles] for i in range(0, len(articles), num_articles)]
    summaries = []
    for chunk in chunks:
        prompt = "Summarize the following articles for an Ohmbudsman digest. Output in Markdown:\n"
        for i, article in enumerate(chunk):
            prompt += f"{i+1}. {article['title']} – {article.get('source_url', 'Unknown')}\n"
            prompt += f"Excerpt: {article.get('content', '')[:500]}\n\n"
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
    try:
        print("Fetching Readwise Reader articles from the past 24 hours...")
        articles = fetch_readwise_reader_articles()
        print(f"Fetched {len(articles)} articles.")
        if not articles:
            print("No articles found in the past 24 hours.")
        else:
            print("Summarizing via GPT...")
            digest = summarize_articles(articles)
            print("Posting draft to Buttondown...")
            result = post_to_buttondown(digest)
            print("Success:", result['id'])
    except Exception as e:
        print("ERROR:", e)
        raise
