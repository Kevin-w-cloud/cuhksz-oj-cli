"""Shared HTTP client and utilities for CUHK-SZ OJ scripts."""

import json
import re

import requests

from config import BASE_URL, COOKIES, COURSE_SLUG, HEADERS, OJ_PASSWORD, OJ_USERNAME, _COOKIE_CACHE


class OJError(Exception):
    """Raised when an OJ request fails."""


def login():
    """Log in to OJ and update COOKIES in-place. Raises OJError on failure."""
    if not OJ_USERNAME or not OJ_PASSWORD:
        raise OJError(
            "No credentials configured. Set OJ_USERNAME and OJ_PASSWORD environment variables."
        )

    login_url = f"{BASE_URL}/d/{COURSE_SLUG}/login"
    session = requests.Session()
    try:
        resp = session.post(
            login_url,
            data={"uname": OJ_USERNAME, "password": OJ_PASSWORD},
            headers=HEADERS,
            timeout=30,
            allow_redirects=True,
        )
    except requests.RequestException as e:
        raise OJError(f"Login request failed: {e}") from e

    new_cookies = session.cookies.get_dict()
    if "sid" not in new_cookies:
        raise OJError(
            f"Login succeeded (HTTP {resp.status_code}) but no 'sid' cookie was set. "
            "Check credentials."
        )

    COOKIES.clear()
    COOKIES.update(new_cookies)

    try:
        _COOKIE_CACHE.write_text(json.dumps(new_cookies))
    except OSError:
        pass


def get(path, *, params=None, timeout=30, _retrying=False):
    """GET request with shared cookies/headers. Returns Response."""
    url = f"{BASE_URL}{path}" if path.startswith("/") else path
    try:
        resp = requests.get(url, params=params, headers=HEADERS, cookies=COOKIES, timeout=timeout)
    except requests.RequestException as e:
        raise OJError(f"Request failed: {e}") from e
    if _is_auth_failure(resp) and not _retrying:
        login()
        return get(path, params=params, timeout=timeout, _retrying=True)
    if resp.status_code != 200:
        raise OJError(f"HTTP {resp.status_code} for {url}")
    return resp


def _is_auth_failure(resp):
    """Check if response indicates authentication failure."""
    if resp.status_code in (401, 403):
        return True
    if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/json"):
        try:
            data = resp.json()
            url = data.get("url", "")
            if "/login" in url:
                return True
        except (ValueError, KeyError):
            pass
    return False


def post(path, *, json_payload=None, extra_headers=None, params=None, timeout=30, _retrying=False):
    """POST request with shared cookies/headers. Returns Response."""
    url = f"{BASE_URL}{path}" if path.startswith("/") else path
    headers = {**HEADERS, **(extra_headers or {})}
    try:
        resp = requests.post(url, params=params, json=json_payload, headers=headers, cookies=COOKIES, timeout=timeout)
    except requests.RequestException as e:
        raise OJError(f"Request failed: {e}") from e
    if _is_auth_failure(resp) and not _retrying:
        login()
        return post(path, json_payload=json_payload, extra_headers=extra_headers, params=params, timeout=timeout, _retrying=True)
    return resp


def problem_url(pid):
    """Build problem page URL."""
    return f"{BASE_URL}/d/{COURSE_SLUG}/p/{pid}"


def homework_url(doc_id):
    """Build homework page URL."""
    return f"{BASE_URL}/d/{COURSE_SLUG}/homework/{doc_id}"


def submit_url(pid):
    """Build submission endpoint URL."""
    return f"{BASE_URL}/d/{COURSE_SLUG}/p/{pid}/submit"


def extract_title(html):
    """Extract problem title from HTML <title> tag."""
    m = re.search(r"<title>(.*?)</title>", html)
    if m:
        return m.group(1).replace(" - Problem Detail - CUHK-Shenzhen OJ", "").strip()
    return "Unknown"


def extract_ui_context(html):
    """Extract UiContextNew JSON from page HTML. Returns parsed dict."""
    match = re.search(r"var UiContextNew = '(.*?)';", html, re.DOTALL)
    if not match:
        raise OJError("UiContextNew not found in page HTML")
    raw_json = match.group(1).replace("\\'", "'")
    return json.loads(raw_json)


def fetch_problem_title(pid):
    """Fetch problem page and return its title."""
    try:
        resp = get(f"/d/{COURSE_SLUG}/p/{pid}")
        return extract_title(resp.text)
    except OJError:
        return f"Problem {pid}"
