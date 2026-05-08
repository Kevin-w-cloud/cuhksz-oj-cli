#!/usr/bin/env python3
"""Submit a solution to CUHK-SZ OJ.

Usage:
    python3 do_submit.py <pid> <tid>
    python3 do_submit.py 42 69f0cb448a05e9cfde8f8eb6
"""

import argparse
import json
import sys
from pathlib import Path

from config import COURSE_SLUG
from oj_client import OJError, post, submit_url

SOLUTIONS_DIR = Path(__file__).parent / "solutions"


def main():
    parser = argparse.ArgumentParser(description="提交代码到 CUHK-SZ OJ")
    parser.add_argument("pid", type=int, help="题目编号")
    parser.add_argument("tid", help="作业 doc_id")
    args = parser.parse_args()

    pid = args.pid
    tid = args.tid
    code_file = SOLUTIONS_DIR / f"p{pid}.py"

    if not code_file.exists():
        print(f"Error: {code_file} not found", file=sys.stderr)
        sys.exit(1)

    code = code_file.read_text()

    extra_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://oj.cuhk.edu.cn/d/{COURSE_SLUG}/p/{pid}?tid={tid}",
    }

    print(f"Submitting p{pid} (tid={tid})...")
    try:
        resp = post(
            submit_url(pid),
            json_payload={"lang": "py.py3", "code": code},
            extra_headers=extra_headers,
            params={"tid": tid},
        )
    except OJError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except ValueError:
        print(f"Response:\n{resp.text}")


if __name__ == "__main__":
    main()
