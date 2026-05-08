# Skill: CUHK-SZ OJ 批量操作流程

## 使用场景

通过命令行批量查询 CUHK-SZ OJ 题目状态、获取题目描述、提交代码。适用于需要处理多道题目时的标准化工作流。

## 文件夹内容

### 1. config.py
集中管理所有脚本共享的配置：`BASE_URL`、`COURSE_SLUG`、`OJ_USERNAME`/`OJ_PASSWORD`（环境变量）、`COOKIES`、`HEADERS`、`STATUS_MAP`。推荐通过环境变量配置登录凭据，Cookie 会自动刷新。

### 2. oj_client.py
共享 HTTP 客户端和工具函数：`get()`、`post()`、`login()`、`extract_ui_context()`、`fetch_problem_title()`、URL 拼接函数。所有脚本通过此模块发起请求，统一错误处理。`get()`/`post()` 在遇到 401/403 时会自动调用 `login()` 刷新 Cookie 并重试。

### 3. fetch_each_week_link.py
从 CUHK-SZ OJ 抓取作业列表，生成/更新 `each_week_link.csv`。
```bash
python3 fetch_each_week_link.py              # 打印所有作业的完整详情
python3 fetch_each_week_link.py --urls-only  # 仅打印 URL 列表
```

### 4. fetch_homework_problems.py
获取某周作业的所有题目链接和提交状态。
```bash
python3 fetch_homework_problems.py <doc_id>              # 文本格式输出
python3 fetch_homework_problems.py <doc_id> --json       # JSON 格式输出
python3 fetch_homework_problems.py <doc_id> --update-csv # 获取并更新 all_problems_status.csv
```

### 5. get_problem.py（推荐使用）
获取 OJ 具体题目的描述文本。支持命令行参数，HTML 解析更健壮。
```bash
python3 get_problem.py <pid> <tid>
```
- `pid`：题目编号
- `tid`：作业 ID（doc_id），从 `each_week_link.csv` 获取

### 6. do_submit.py（推荐使用）
向 OJ 提交代码。支持命令行参数。
```bash
python3 do_submit.py <pid> <tid>
```
- 自动从 `solutions/p{pid}.py` 读取代码
- `pid`：题目编号
- `tid`：作业 ID（doc_id）

---

## 标准工作流

### 第 1 步：查询题目状态
如果 `each_week_link.csv` 不完整，通过 `fetch_each_week_link.py` 更新。
将目标周的 doc_id 作为参数，调用 `fetch_homework_problems.py --update-csv` 查看状态并更新 `all_problems_status.csv`。

```bash
python3 fetch_homework_problems.py <doc_id> --update-csv
```

### 第 2 步：获取题目描述
```bash
python3 get_problem.py <pid> <tid>
```

### 第 3 步：编写解题代码
保存至 `solutions/p{pid}.py`。

**输入输出规范**：

| 规则 | 说明 |
|------|------|
| 使用 `input()` / `print()` | 标准输入输出 |
| 禁止 `sys.stdin` / `sys.stdout` | OJ 环境不支持，会导致 TLE 或 RE |

正确示例：
```python
def main():
    t = int(input())
    for _ in range(t):
        a, b = map(int, input().split())
        print(solve(a, b))

main()
```

### 第 4 步：提交代码
```bash
python3 do_submit.py <pid> <tid>
```

提交后建议等待判题结果返回，再进行下一题的提交。

---

## Cookie 管理

所有脚本通过 `config.py` 中的 `COOKIES` 字典统一配置，支持自动登录刷新。

### 自动登录（推荐）

设置环境变量后，脚本会在 Cookie 过期（401/403）时自动重新登录：

```bash
export OJ_USERNAME="学号"
export OJ_PASSWORD="密码"
```

### 手动获取 Cookie

1. 浏览器登录 oj.cuhk.edu.cn
2. 打开 DevTools → Network
3. 随便提交一次，找到 `submit` 请求
4. 复制请求头 `Cookie` 中的 `sid` 和 `sid.sig` 值
5. 修改 `config.py` 中的 `COOKIES` 字典

Cookie 有效期约一个月。

---

## 返回结果解读

| HTTP 状态码 | 含义 |
|------------|------|
| 200 | 提交成功，JSON 中包含 `rid`（记录ID）和查看结果的 URL |
| 401 / 403 | Cookie 失效，已配置环境变量时自动重新登录 |
| 其他 | 网络或服务器错误 |

成功响应示例：
```json
{
  "rid": "69f8531193e3b322b9e92ba0",
  "url": "/d/csc5003_2026_spring/record/69f8531193e3b322b9e92ba0"
}
```

拼接域名即可查看判题结果：
```
https://oj.cuhk.edu.cn/d/csc5003_2026_spring/record/{rid}
```

---

## 判题状态码

| 状态码 | 含义 |
|--------|------|
| 0 | 未提交 (Not Submitted) |
| 1 | 通过 (Accepted) |
| 2 | 答案错误 (Wrong Answer) |
| 3 | 超时 (Time Limit Exceeded) |
| 4 | 超内存 (Memory Limit Exceeded) |
| 5 | 运行错误 (Runtime Error) |
| 6 | 编译错误 (Compile Error) |
| 7 | 等待中 (Waiting) |
| 8 | 判题中 (Judging) |
| 9 | 输出超限 (Output Limit Exceeded) |
| 10 | 格式错误 (Presentation Error) |

---

## 常见问题

### Q: 提交返回非 200？
**A**: 已配置环境变量时脚本会自动重新登录。若仍失败，检查凭据是否正确。未配置环境变量时，需手动更新 `config.py` 中的 Cookie。

### Q: 代码在本机测试通过但 OJ 上 TLE/RE？
**A**: 检查是否使用了 `sys.stdin.readline`。OJ 的 Python 环境不支持该方式，必须使用 `input()` / `print()`。

### Q: WA/CE 但本地测试通过？
**A**: 最大可能是**输入输出格式不匹配**。OJ 的输入格式可能与预期有差异：

| 常见坑点 | 示例 |
|----------|------|
| 字符串 vs 空格分隔 | board 每行是字符串 `"ABCE"`，不是空格分隔 |
| 单行 vs 多行 | 八数码输入是一行 9 字符，不是 3×3 矩阵 |
| 多组测试数据 | 第一行是 T（测试组数），之后有 T 组数据 |
| 输出关键词 | `YES`/`NO` vs `true`/`false` vs `True`/`False` |

**建议**：用 `get_problem.py` 获取题目描述，仔细阅读样例输入输出和格式说明。
