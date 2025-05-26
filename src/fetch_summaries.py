#!/usr/bin/env python3
"""
Fetch articles added/updated in the last 24 h from Readwise Reader,
page through the list endpoint, and save to output/articles.json.

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

# ── Configuration ─────────────────────────────────────────────────────

load_dotenv()  # for local development

TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    sys.exit("❌  READWISE_TOKEN is missing")

API_URL = "https://readwise.io/api/v3/list/"
LOOKBACK_HOURS = 24
OUTPUT_FILE = Path("output/articles.json")

# ── Helpers ───────────────────────────────────────────────────────────


def iso_utc(dt: datetime) -> str:
    """Return an ISO-8601 UTC timestamp ending in 'Z'."""
    return (
        dt.astimezone(timezone.utc)
        .replace(tzinfo=None)
        .isoformat()
        + "Z"
    )


def fetch_reader_docs(updated_after: str) -> List[Dict]:
    """
    Page through Readwise Reader's list endpoint and gather all
    documents updated after the given timestamp.
    """
    headers = {"Authorization": f"Token {TOKEN}"}
    params: Dict[str, str] = {
        "updatedAfter": updated_after,
        "location": "new",
    }

    all_docs: List[Dict] = []
    next_cursor: str | None = None

    while True:
        if next_cursor:
            params["pageCursor"] = next_cursor

        resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Append this page's results
        docs = data.get("results", [])
        all_docs.extend(docs)

        # Prepare nextPageCursor; break if none
        next_cursor = data.get("nextPageCursor")
        if not next_cursor:
            break

        # Only send updatedAfter on first request
        params.pop("updatedAfter", None)

    return all_docs


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


# ── Main ──────────────────────────────────────────────────────────────


def main() -> None:
    cutoff_iso = iso_utc(datetime.utcnow() - timedelta(hours=LOOKBACK_HOURS))
    raw_docs = fetch_reader_docs(cutoff_iso)
    articles = normalise(raw_docs)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(articles, indent=2))
    print(f"✔  Saved {len(articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
