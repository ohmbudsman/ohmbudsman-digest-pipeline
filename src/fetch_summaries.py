#!/usr/bin/env python3
"""
Pull the last 24 hours of articles from Readwise Reader and
write them to output/articles.json for the downstream summary step.

Requires READWISE_TOKEN set as a GitHub Actions secret.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    sys.exit("❌  READWISE_TOKEN is missing")

API_URL = "https://readwise.io/api/v3/reader/list"
LOOKBACK_HOURS = 24
PAGE_SIZE = 1000
OUTPUT_FILE = Path("output/articles.json")


def iso_utc(dt: datetime) -> str:
    """Return an ISO-8601 UTC timestamp ending in 'Z'."""
    return (
        dt.astimezone(timezone.utc)
        .replace(tzinfo=None)
        .isoformat()
        + "Z"
    )


def fetch_reader_articles(updated_after: str) -> List[Dict]:
    """
    Paginate through Readwise Reader's list endpoint and return all articles
    updated after the given ISO timestamp.
    """
    articles: List[Dict] = []
    headers = {"Authorization": f"Token {TOKEN}"}
    params = {
        "location": "new",
        "category": "article",
        "date": updated_after,
        "page_size": PAGE_SIZE,
    }
    url = API_URL

    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("results", [])
        if isinstance(batch, list):
            articles.extend(batch)
        else:
            articles.append(batch)
        url = data.get("next")
        params = None  # only send params on first request

    return articles


def normalise(docs: List[Dict]) -> List[Dict]:
    """Extract only the fields needed for LLM summarisation."""
    return [
        {
            "title": d.get("title", "Untitled"),
            "link": d.get("url") or d.get("source_url", ""),
            "published": d.get("published_date", ""),
            "summary": d.get("summary", ""),
        }
        for d in docs
    ]


def main() -> None:
    cutoff = iso_utc(datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS))
    raw = fetch_reader_articles(cutoff)
    articles = normalise(raw)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(articles, indent=2))
    print(f"✔  Saved {len(articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
