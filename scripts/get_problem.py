#!/usr/bin/env python3
"""Fetch problem description from CUHK-SZ OJ.

Usage:
    python3 scripts/get_problem.py <pid> <tid>
    python3 scripts/get_problem.py 42 69f0cb448a05e9cfde8f8eb6
"""

import argparse
import re
import sys

from config import COURSE_SLUG
from oj_client import OJError, get


def extract_problem_text(html: str) -> str:
    start_idx = html.find('<div class="problem-content-container">')
    if start_idx == -1:
        start_idx = html.find('<div class="problem-content"')
        if start_idx == -1:
            return "(Could not locate problem content area)"

    content_start = html.find('>', start_idx) + 1

    content_end = html.find('<div class="medium-3 columns">', content_start)
    if content_end == -1:
        content_end = html.find('class="section side__panel"', content_start)
    if content_end == -1:
        content_end = content_start + 80000

    raw = html[content_start:content_end]

    raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL)

    raw = re.sub(r'<h[1-6][^>]*>', '\n== ', raw)
    raw = re.sub(r'</h[1-6]>', ' ==\n', raw)

    raw = re.sub(r'<p[^>]*>', '\n', raw)
    raw = re.sub(r'</p>', '\n', raw)

    raw = re.sub(r'<br\s*/?>', '\n', raw)

    raw = re.sub(r'<li[^>]*>', '  - ', raw)
    raw = re.sub(r'</li>', '\n', raw)

    raw = re.sub(r'<code[^>]*>', '`', raw)
    raw = re.sub(r'</code>', '`', raw)

    text = re.sub(r'<[^>]+>', '', raw)

    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')

    lines = [line.rstrip() for line in text.splitlines()]
    result = []
    prev_empty = False
    for line in lines:
        if line == '':
            if not prev_empty:
                result.append('')
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    return '\n'.join(result).strip()


def main():
    parser = argparse.ArgumentParser(description="Fetch OJ problem description")
    parser.add_argument("pid", type=int, help="Problem ID (integer)")
    parser.add_argument("tid", help="Homework doc_id")
    args = parser.parse_args()

    print(f"Fetching problem {args.pid} (tid={args.tid})...")
    try:
        resp = get(f"/d/{COURSE_SLUG}/p/{args.pid}", params={"tid": args.tid})
    except OJError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    text = extract_problem_text(resp.text)
    print(text)


if __name__ == "__main__":
    main()
