#!/usr/bin/env python3
"""Fetch homework list from CUHK-SZ OJ and extract homework links.

Usage:
    python3 scripts/fetch_each_week_link.py              # Print all homework details
    python3 scripts/fetch_each_week_link.py --urls-only  # Print URLs only
    python3 scripts/fetch_each_week_link.py --update-csv # Also update each_week_link.csv
"""

import argparse
import csv
import sys
from pathlib import Path

from config import BASE_URL
from oj_client import OJError, extract_ui_context, get

CSV_FILE = Path(__file__).parent.parent / "each_week_link.csv"


def update_csv(docs: list[dict]):
    """Write homework metadata to each_week_link.csv."""
    fieldnames = ["title", "url", "begin_at", "end_at", "pids", "attend", "rated", "doc_id"]
    rows = []
    for doc in docs:
        url = doc.get("url", "")
        doc_id = url.rstrip("/").split("/")[-1] if url else ""
        rows.append({
            "title": doc.get("title", ""),
            "url": f"{BASE_URL}{url}" if url.startswith("/") else url,
            "begin_at": doc.get("beginAt", ""),
            "end_at": doc.get("endAt", ""),
            "pids": doc.get("pids", ""),
            "attend": doc.get("attend", ""),
            "rated": doc.get("rated", ""),
            "doc_id": doc_id,
        })

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {CSV_FILE} ({len(rows)} homeworks)")


def fetch_homeworks(urls_only: bool = False) -> list[dict]:
    """Fetch homework list from page HTML UiContextNew embedded JSON."""
    try:
        resp = get("/d/csc5003_2026_spring/homework")
    except OJError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    data = extract_ui_context(resp.text)
    docs = data.get("docs", [])

    if not docs:
        print("No homeworks found.", file=sys.stderr)
        sys.exit(1)

    if urls_only:
        for doc in docs:
            url = doc.get("url", "")
            print(f"{BASE_URL}{url}" if url.startswith("/") else url)
    else:
        print(f"Found {len(docs)} homeworks:\n")
        for i, doc in enumerate(docs, 1):
            title = doc.get("title", "N/A")
            url = doc.get("url", "")
            begin = doc.get("beginAt", "N/A")
            end = doc.get("endAt", "N/A")
            pids = doc.get("pids", [])
            attend = doc.get("attend", "N/A")
            full_url = f"{BASE_URL}{url}" if url.startswith("/") else url

            print(f"{i:2d}. {title}")
            print(f"    URL:     {full_url}")
            print(f"    Begin:   {begin}")
            print(f"    End:     {end}")
            print(f"    PIDs:    {pids}")
            print(f"    Attend:  {attend}")
            print()

    return docs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch CUHK-SZ OJ homework links")
    parser.add_argument("--urls-only", action="store_true", help="Print URLs only")
    parser.add_argument("--update-csv", action="store_true", help="Also update each_week_link.csv")
    args = parser.parse_args()
    docs = fetch_homeworks(urls_only=args.urls_only)
    if args.update_csv:
        update_csv(docs)
