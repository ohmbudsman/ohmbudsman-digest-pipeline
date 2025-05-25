import requests
import datetime
import hashlib
import os
import openai

# --- CONFIG ---
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
ASSISTANT_ID = "asst_aumVzFe2kUL0u0K0H88owQ1F"

SAFE_MODE = True  # Always true, hardcoded for safety
TAG_FILTER = "ohmbudsman"
BATCH_SIZE = 3

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
        if TAG_FILTER not in tags:
            continue
        created_time = datetime.datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        if created_time >= past_24:
            filtered.append(item)
    return filtered

def summarize_articles_with_assistant(articles):
    openai.api_key = OPENAI_API_KEY
    today = datetime.date.today().strftime("%Y-%m-%d")
    summaries = [f"# The Rundown – {today}\n"]

    for i in range(0, len(articles), BATCH_SIZE):
        chunk = articles[i:i+BATCH_SIZE]
        messages = [
            {"role": "system", "content": "You are a digest writer using Disguised-SNAP format. Output must strictly follow structure and include all required components."}
        ]

        for article in chunk:
            title = article.get("title", "No Title")
            url = article.get("source_url", "No URL")
            content = article.get("content") or ""
            if not content:
                summaries.append(f"CANNOT ACCESS: {url}. Provide full text or alternate source.\n")
                continue
            excerpt = content[:2000]  # Limit to safe size
            messages.append({
                "role": "user",
                "content": f"Title: {title}\nSource: {url}\nContent: {excerpt}"
            })

        if len(messages) <= 1:
            continue

        thread = openai.beta.threads.create(messages=messages)
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions="Format summaries in Disguised-SNAP, markdown output only, no commentary."
        )
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        while run.status not in ("completed", "failed"):
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            response_text = messages.data[0].content[0].text.value
            summaries.append(response_text)
        else:
            summaries.append("GPT ASSISTANT RUN FAILED\n")

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
            print("Summarizing via GPT Assistant...")
            digest = summarize_articles_with_assistant(articles)
            print("Posting draft to Buttondown...")
            result = post_to_buttondown(digest)
            print("Success:", result['id'])
    except Exception as e:
        print("ERROR:", e)
        raise
