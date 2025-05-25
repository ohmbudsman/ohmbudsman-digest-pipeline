# Digest Automation Pipeline (Readwise Reader → GPT → Buttondown)

import requests
import datetime
import hashlib
import os

# --- CONFIG ---
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")

SAFE_MODE = True  # Always true, hardcoded for security

tag_filter = "ohmbudsman"

# --- FUNCTIONS ---
def fetch_readwise_reader_articles():
    url = "https://readwise.io/api/v3/list/"
    headers = {"Authorization": f"Token {READWISE_TOKEN}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    items = res.json().get("results", [])

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    past_24 = utc_now - datetime.timedelta(hours=24)

    filtered = []
    for item in items:
        tags = item.get("tags", {})
        if tag_filter not in tags:
            continue
        created_time = datetime.datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        content = item.get("content") or ''
        if created_time >= past_24:
            filtered.append(item)

    return filtered

def summarize_articles(articles):
    today = datetime.date.today().strftime("%Y-%m-%d")
    summaries = [f"# The Rundown – {today}\n"]
    prompt = (
        "For each of the following articles, create a digest summary using Disguised-SNAP format. Structure each as follows:\n"
        "🧠 HEADLINE\n"
        "— NUTSHELL\n"
        "📍 DATELINE / ACTORS\n"
        "🟢 IMPACT\n"
        "📊 DATA\n"
        "💬 QUOTE\n"
        "BRIDGE\n"
        "❓ HOOK\n"
        "🔚 TAKEAWAY\n"
        "(Source: URL)\n\n"
    )
    for article in articles:
        title = article['title']
        source = article.get('source_url', 'Unknown')
        content = article.get('content') or ''
        prompt += f"Title: {title}\nSource: {source}\nContent: {content[:1000]}\n\n"

    chat_payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a formatting assistant writing geopolitical digest content in Disguised-SNAP format."},
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
    payload = {
        "subject": title,
        "body": content,
        "status": "draft"
    }
    print("SAFE MODE ENABLED: Posting as draft only.")
    res = requests.post("https://api.buttondown.email/v1/emails", headers=headers, json=payload)
    res.raise_for_status()
    return res.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print("Fetching tagged Readwise Reader articles from the past 24 hours...")
        articles = fetch_readwise_reader_articles()
        print(f"Fetched {len(articles)} articles.")
        if not articles:
            print("No tagged articles found in the past 24 hours.")
        else:
            print("Summarizing via GPT...")
            digest = summarize_articles(articles)
            print("Posting draft to Buttondown...")
            result = post_to_buttondown(digest)
            print("Success:", result['id'])
    except Exception as e:
        print("ERROR:", e)
        raise
