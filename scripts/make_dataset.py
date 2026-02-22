# scripts/makedataset.py
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import feedparser

FEED_URL = "https://feeds.bbci.co.uk/news/business/rss.xml"

OUT_DIR = Path("data")
JSON_PATH = OUT_DIR / "dataset.json"
CSV_PATH = OUT_DIR / "dataset.csv"


def extract_records(feed: Any) -> List[Dict[str, str]]:
    """
    Convert a parsed RSS feed into a list of records with consistent keys.

    Each record contains:
      - title: article headline
      - url: link to the article
      - published: publication time string (if available)
      - summary: RSS summary/description (if available)

    Returns:
        List of dictionaries (records).
    """
    records: List[Dict[str, str]] = []

    for entry in getattr(feed, "entries", []):
        title = str(getattr(entry, "title", "")).strip()
        url = str(getattr(entry, "link", "")).strip()
        published = str(getattr(entry, "published", "")).strip()
        summary = str(getattr(entry, "summary", "")).strip()

        # Skip completely empty items
        if not title and not url:
            continue

        records.append(
            {
                "title": title,
                "url": url,
                "published": published,
                "summary": summary,
            }
        )

    return records


def save_json_snapshot(records: List[Dict[str, str]], out_path: Path) -> None:
    """
    Save a snapshot JSON with metadata + records.

    Format:
    {
      "source": "...",
      "created_utc": "...",
      "count": N,
      "records": [...]
    }
    """
    created_utc = datetime.now(timezone.utc).isoformat()

    payload: Dict[str, Any] = {
        "source": FEED_URL,
        "created_utc": created_utc,
        "count": len(records),
        "records": records,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def save_csv(records: List[Dict[str, str]], out_path: Path) -> None:
    """
    Save records to a CSV file (flat format).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["title", "url", "published", "summary"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    """
    Entry point:
    - Fetch RSS feed
    - Extract records
    - Save JSON + CSV snapshot
    """
    print("✅ makedataset.py started")
    print(f"➡️  Fetching RSS feed: {FEED_URL}")

    feed = feedparser.parse(FEED_URL)

    # If the feed is broken or blocked, this helps you see why.
    bozo = getattr(feed, "bozo", 0)
    if bozo:
        bozo_exc = getattr(feed, "bozo_exception", None)
        raise RuntimeError(f"RSS parsing error (bozo=1): {bozo_exc}")

    records = extract_records(feed)
    print(f"🧾 Entries found: {len(records)}")

    if len(records) == 0:
        raise RuntimeError("No records extracted. The feed may be unreachable or empty.")

    save_json_snapshot(records, JSON_PATH)
    print(f"💾 Saved JSON snapshot -> {JSON_PATH.resolve()}")

    save_csv(records, CSV_PATH)
    print(f"💾 Saved CSV -> {CSV_PATH.resolve()}")

    print("🎉 Done! Dataset is now fixed (snapshot). Commit the files in /data to keep it constant.")


if __name__ == "__main__":
    main()