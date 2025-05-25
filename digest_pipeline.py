import os
import time
import hashlib
import datetime
import requests
import openai

# --- CONFIG ---
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BUTTONDOWN_TOKEN = os.getenv("BUTTONDOWN_TOKEN")
ASSISTANT_ID = "asst_aumVzFe2kUL0u0K0H88owQ1F"
SAFE_MODE = True  # Always true, hardcoded for security
TAG_FILTER = "ohmbudsman"
NUM_ARTICLES = 5

openai.api_key = OPENAI_API_KEY

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
        content = item.get("content") or ''
        if created_time >= past_24:
            filtered.append(item)

    return filtered

def summarize_articles_with_assistant(articles):
    today = datetime.date.today().strftime("%Y-%m-%d")
    summaries = [f"# The Rundown – {today}\n"]
    for article in articles:
        title = article['title']
        source = article.get('source_url', 'Unknown')
        content = article.get('content') or ''
        prompt = (
            f"Title: {title}\n"
            f"Source: {source}\n"
            f"Content: {content[:1000]}\n\n"
            "Please summarize the above article using the Disguised-SNAP format."
        )

        # Create a new thread
        thread = openai.beta.threads.create()

        # Add a message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        # Run the assistant on the thread
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the run to complete
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == 'completed':
                break
            time.sleep(1)

        # Retrieve messages from the thread
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        assistant_messages = [msg for msg in messages.data if msg.role == 'assistant']
        if assistant_messages:
            summaries.append(assistant_messages[-1].content[0].text.value)
        else:
            summaries.append("No summary available.")

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
        "status": "draft"  # Explicitly set as draft
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
            print("Summarizing via OpenAI Assistant...")
            digest = summarize_articles_with_assistant(articles)
            print("Posting draft to Buttondown...")
            result = post_to_buttondown(digest)
            print("Success:", result['id'])
    except Exception as e:
        print("ERROR:", e)
        raise
