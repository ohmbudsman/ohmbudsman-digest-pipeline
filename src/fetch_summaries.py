#!/usr/bin/env python3
import os, json
import feedparser
from dotenv import load_dotenv

load_dotenv()
FEEDS_FILE = "config/feeds.yml"
OUTPUT = "output/articles.json"

def load_feeds(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)["feeds"]

def fetch_entries(feeds):
    entries = []
    for feed in feeds:
        d = feedparser.parse(feed)
        for e in d.entries[:5]:
            entries.append({
                "title": e.title,
                "link": e.link,
                "published": e.get("published", ""),
                "summary": e.get("summary", "")
            })
    return entries

def main():
    feeds = load_feeds(FEEDS_FILE)
    articles = fetch_entries(feeds)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(articles, f, indent=2)
    print(f"Wrote {len(articles)} articles to {OUTPUT}")

if __name__ == "__main__":
    main()
