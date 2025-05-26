#!/usr/bin/env python3
"""
Download articles added/updated in the last 24 h from Readwise Reader and
save them to output/articles.json for later summarisation.

Requires READWISE_TOKEN set in GitHub Secrets.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

load_dotenv()  # for local testing

TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    sys.exit("❌  READWISE_TOKEN is missing")

API_URL = "https://readwise.io/api/v3/reader/list/"
LOOKBACK_HOURS = 24
PAGE_SIZE = 1000
OUTPUT_FILE = Path("output/articles.json")

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def iso_utc(dt: datetime) -> str:
    """Return ISO-8601 string with trailing Z (UTC)."""
    return (
        dt.astimezone(timezone.utc)
        .replace(tzinfo=None)
        .isoformat()
        + "Z"
    )


def fetch_reader_docs(updated_after: str) -> List[Dict]:
    """
    Paginate through the Readwise Reader API and return raw article dicts.
    """
    docs: List[Dict] = []
    headers = {"Authorization": f"Token {TOKEN}"}
    params = {
        "page_size": PAGE_SIZE,
        "category": "article",
        "updatedAfter": updated_after,
    }
    url: str | None = API_URL

    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        docs.extend(data.get("results", []))
        url = data.get("next")
        params = None  # params only on first request

    return docs


def normalise(docs: List[Dict]) -> List[Dict]:
    """
    Extract only the fields needed for AI summarisation.
    """
    return [
        {
            "title": d.get("title", "Untitled"),
            "link": d.get("url") or d.get("source_url", ""),
            "published": d.get("published_date", ""),
            "summary": d.get("summary", ""),
        }
        for d in docs
    ]


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main() -> None:
    cutoff = iso_utc(datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS))
    raw = fetch_reader_docs(cutoff)
    articles = normalise(raw)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(articles, indent=2))

    print(f"✔  Saved {len(articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
