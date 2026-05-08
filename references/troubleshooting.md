# Troubleshooting Guide

## Common Issues

### Scripts return HTTP 401/403

**Cause**: Cookie expired or not configured.

**Fix**:
1. Ensure environment variables are set:
   ```bash
   export OJ_USERNAME="your_student_id"
   export OJ_PASSWORD="your_password"
   ```
2. Scripts will auto-relogin on 401/403 when credentials are configured.
3. If still failing, verify credentials are correct.

### Code passes locally but gets TLE/RE on OJ

**Cause**: Using `sys.stdin.readline` or `sys.stdout`.

**Fix**: OJ Python environment does NOT support `sys.stdin`/`sys.stdout`. You must use `input()`/`print()`.

```python
# CORRECT
def main():
    n = int(input())
    nums = list(map(int, input().split()))
    print(solve(n, nums))

main()

# WRONG — causes TLE or RE on OJ
import sys
input = sys.stdin.readline
```

### WA or CE but passes local tests

**Cause**: Input/output format mismatch with OJ expectations.

**Common pitfalls**:

| Pitfall | Example |
|---------|---------|
| String vs space-separated | Board rows are strings `"ABCE"`, not `A B C E` |
| Single-line vs multi-line | 8-puzzle input is one line of 9 chars `"283104765"`, not 3x3 matrix |
| Multiple test cases | First line is T (count), followed by T groups — not just one group |
| Output keywords | `YES`/`NO` vs `true`/`false` vs `True`/`False` — read the problem spec carefully |
| No-solution output | Some problems want empty line, others want `"invalid"` |

**Debugging strategy**:
1. Submit minimal code to test compilation (rule out syntax issues).
2. Try common format variants (YES/NO, True/False, etc.).
3. **Most reliable**: Use `get_problem.py` to fetch the full problem description and read the sample I/O carefully.
4. **Always fetch the problem description before writing code** — do not guess from the title.

### fetch_problem.py cannot extract problem content

**Cause**: Old script uses incorrect HTML selector.

**Fix**: Use `get_problem.py` instead — it has more robust HTML parsing with fallback selectors (`problem-content-container` and `problem-content`).

### Submission returns non-200 (not auth-related)

**Cause**: Rate limiting or server error.

**Fix**: Wait at least 60 seconds between submissions. If persistent, check if the OJ server is reachable.

### Batch submission strategy

**Recommended**: Write all code first, then submit one by one with 60-second intervals.

Benefits:
- Avoids ignoring results from other problems while writing one
- Allows unified code review before submission
- Synchronized status checking after each submission

### Cookie management

**Auto-login (recommended)**: Set `OJ_USERNAME` and `OJ_PASSWORD` environment variables. Cookies refresh automatically on 401/403.

**Manual cookie**: Browser login → DevTools → Network → copy `sid` and `sid.sig` from Cookie header of any request → update `config.py`.

Cookies last approximately one month.

**Switching accounts**: Change `OJ_USERNAME` and `OJ_PASSWORD` environment variables. All scripts will use the new identity.
