#!/usr/bin/env python3
"""Fetch homework list from CUHK-SZ OJ and extract homework links.

Usage:
    python3 fetch_each_week_link.py              # 打印所有作业链接和详情
    python3 fetch_each_week_link.py --urls-only  # 仅打印 URL 列表
"""

import argparse
import sys

from config import BASE_URL
from oj_client import OJError, extract_ui_context, get


def fetch_homeworks(urls_only: bool = False) -> list[dict]:
    """获取作业列表，从页面 HTML 中解析 UiContextNew 嵌入的 JSON 数据。"""
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
        print(f"共找到 {len(docs)} 个作业:\n")
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
            print(f"    开始时间: {begin}")
            print(f"    结束时间: {end}")
            print(f"    题目ID:   {pids}")
            print(f"    参与人数: {attend}")
            print()

    return docs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取 CUHK-SZ OJ 作业链接")
    parser.add_argument("--urls-only", action="store_true", help="仅输出 URL 列表")
    args = parser.parse_args()
    fetch_homeworks(urls_only=args.urls_only)
