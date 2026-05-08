#!/usr/bin/env python3
"""Fetch homework list from CUHK-SZ OJ and extract homework links.

Usage:
    python3 scripts/fetch_each_week_link.py              # Print all homework details
    python3 scripts/fetch_each_week_link.py --urls-only  # Print URLs only
"""

import argparse
import sys

from config import BASE_URL
from oj_client import OJError, extract_ui_context, get


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
    args = parser.parse_args()
    fetch_homeworks(urls_only=args.urls_only)
