#!/usr/bin/env python3
"""Fetch problems and submission status for a specific homework from CUHK-SZ OJ.

Usage:
    python3 scripts/fetch_homework_problems.py <doc_id>
    python3 scripts/fetch_homework_problems.py 69f0cb448a05e9cfde8f8eb6
    python3 scripts/fetch_homework_problems.py 69f0cb448a05e9cfde8f8eb6 --json
    python3 scripts/fetch_homework_problems.py 69f0cb448a05e9cfde8f8eb6 --update-csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from config import BASE_URL, COURSE_SLUG, STATUS_MAP
from oj_client import OJError, extract_ui_context, fetch_problem_title, get

CSV_FILE = Path(__file__).parent.parent / "all_problems_status.csv"
WEEK_CSV_FILE = Path(__file__).parent.parent / "each_week_link.csv"


def update_csv(doc_id: str, problems: list):
    """Update all_problems_status.csv with fetched problems for a given week."""
    # Read week metadata from each_week_link.csv
    week_meta = {}
    if WEEK_CSV_FILE.exists():
        with open(WEEK_CSV_FILE, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if row["doc_id"] == doc_id:
                    week_meta = row
                    break
    if not week_meta:
        print(f"Warning: doc_id {doc_id} not found in each_week_link.csv, skipping CSV update", file=sys.stderr)
        return

    week_title = week_meta["title"]
    begin_at = week_meta["begin_at"]
    end_at = week_meta["end_at"]

    # Read existing CSV
    rows = []
    if CSV_FILE.exists():
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    # Remove old entries for this week
    rows = [r for r in rows if r["week"] != week_title]

    # Add new entries
    for p in problems:
        rows.append({
            "week": week_title,
            "pid": p["pid"],
            "problem_title": p["title"],
            "url": p["url"],
            "status": p["status"],
            "status_code": p["status_code"],
            "score": p["score"],
            "lang": p["lang"],
            "rid": p["rid"],
            "begin_at": begin_at,
            "end_at": end_at,
        })

    # Write back
    fieldnames = ["week", "pid", "problem_title", "url", "status", "status_code", "score", "lang", "rid", "begin_at", "end_at"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {CSV_FILE} ({week_title}: {len(problems)} problems)")


def fetch_homework_problems(doc_id: str, json_output: bool = False):
    """Fetch all problems and their submission status for a homework."""
    url = f"{BASE_URL}/d/{COURSE_SLUG}/homework/{doc_id}"

    try:
        resp = get(f"/d/{COURSE_SLUG}/homework/{doc_id}")
    except OJError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    data = extract_ui_context(resp.text)
    tdoc = data.get("tdoc") or {}
    tsdoc = data.get("tsdoc") or {}

    homework_title = tdoc.get("title", "Unknown")
    pids = tdoc.get("pids", [])
    detail = tsdoc.get("detail", {})

    if json_output:
        result = {
            "homework_title": homework_title,
            "doc_id": doc_id,
            "url": url,
            "problems": [],
        }

    problems = []
    for pid in pids:
        problem_url = f"{BASE_URL}/d/{COURSE_SLUG}/p/{pid}"
        title = fetch_problem_title(pid)

        pid_str = str(pid)
        if pid_str in detail:
            sub = detail[pid_str]
            status_code = sub.get("status", 0)
            score = sub.get("score", 0)
            rid = sub.get("rid", "")
            lang = sub.get("lang", "")
            status_text = STATUS_MAP.get(status_code, f"Unknown({status_code})")
        else:
            status_code = 0
            score = 0
            rid = ""
            lang = ""
            status_text = "Not Submitted"

        prob = {
            "pid": pid,
            "title": title,
            "url": problem_url,
            "status_code": status_code,
            "status": status_text,
            "score": score,
            "rid": rid,
            "lang": lang,
        }
        problems.append(prob)

    if json_output:
        result["problems"] = problems
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Homework: {homework_title}")
        print(f"URL: {url}")
        print(f"Problems: {len(problems)}")
        print("-" * 80)
        for i, p in enumerate(problems, 1):
            status_icon = "AC" if p["status"] == "Accepted" else "XX" if p["status"] != "Not Submitted" else "--"
            print(f"{i}. [{p['pid']}] {p['title']}")
            print(f"   URL:    {p['url']}")
            print(f"   Status: [{status_icon}] {p['status']}  (score: {p['score']})")
            if p["rid"]:
                print(f"   RID:    {p['rid']}")
            print()

    return problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OJ homework problems and submission status")
    parser.add_argument("doc_id", help="Homework doc_id (e.g., 69f0cb448a05e9cfde8f8eb6)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--update-csv", action="store_true", help="Also update all_problems_status.csv")
    args = parser.parse_args()
    problems = fetch_homework_problems(args.doc_id, json_output=args.json)
    if args.update_csv:
        update_csv(args.doc_id, problems)
