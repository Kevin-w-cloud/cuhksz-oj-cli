"""Shared configuration for CUHK-SZ OJ scripts."""

import json
import os
from pathlib import Path

BASE_URL = "https://oj.cuhk.edu.cn"
COURSE_SLUG = "csc5003_2026_spring"

OJ_USERNAME = os.environ.get("OJ_USERNAME", "")
OJ_PASSWORD = os.environ.get("OJ_PASSWORD", "")

_COOKIE_CACHE = Path(__file__).parent / ".cookies.json"

COOKIES = {
    "sid": "",
    "sid.sig": "",
}

if _COOKIE_CACHE.exists():
    try:
        COOKIES.update(json.loads(_COOKIE_CACHE.read_text()))
    except (json.JSONDecodeError, OSError):
        pass

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
}

STATUS_MAP = {
    0: "Not Submitted",
    1: "Accepted",
    2: "Wrong Answer",
    3: "Time Limit Exceeded",
    4: "Memory Limit Exceeded",
    5: "Runtime Error",
    6: "Compile Error",
    7: "Waiting",
    8: "Judging",
    9: "Output Limit Exceeded",
    10: "Presentation Error",
}
