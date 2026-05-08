# OJ Submission Status Codes

Reference table for interpreting submission results from CUHK-SZ OJ (Hydro OJ).

| Status Code | Status | Description | Action Required |
|-------------|--------|-------------|-----------------|
| 0 | Not Submitted | Problem has not been submitted yet | Write solution and submit |
| 1 | Accepted (AC) | Solution passed all test cases | None — problem is complete |
| 2 | Wrong Answer (WA) | Output does not match expected | Re-read problem description, check I/O format |
| 3 | Time Limit Exceeded (TLE) | Solution too slow | Optimize algorithm, check for `sys.stdin` usage |
| 4 | Memory Limit Exceeded (MLE) | Solution uses too much memory | Reduce data structure size |
| 5 | Runtime Error (RE) | Program crashed during execution | Check array bounds, division by zero, recursion depth |
| 6 | Compile Error (CE) | Code failed to compile | Fix syntax errors |
| 7 | Waiting | Queued for judging | Wait for result |
| 8 | Judging | Currently being judged | Wait for result |
| 9 | Output Limit Exceeded (OLE) | Output exceeds size limit | Reduce output volume |
| 10 | Presentation Error (PE) | Correct values but wrong formatting | Check whitespace, newlines, trailing spaces |

## HTTP Response Codes

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Response contains `rid` (record ID) and result URL |
| 401 / 403 | Authentication failure | Cookie expired — auto-relogin if env vars set, otherwise manually update cookies |
| Other | Network or server error | Retry after delay |

## Successful Submission Response

```json
{
  "rid": "69f8531193e3b322b9e92ba0",
  "url": "/d/csc5003_2026_spring/record/69f8531193e3b322b9e92ba0"
}
```

View result at: `https://oj.cuhk.edu.cn/d/csc5003_2026_spring/record/{rid}`
