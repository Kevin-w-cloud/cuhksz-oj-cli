---
name: cuhksz-oj-batch
description: >
  CUHK-SZ OJ (Hydro OJ) 全自动化作业提交系统。通过 CLI 脚本批量查询题目状态、获取题目描述、编写解题代码、提交并验证结果。
  当用户需要与 CUHK-SZ OJ 交互（批量查询、代码提交、作业状态追踪）时触发。
version: "1.1.0"
author: Kevin Wu
metadata:
  course: csc5003_2026_spring
  platform: Hydro OJ
  base_url: "https://oj.cuhk.edu.cn"
compatibility:
  runtime: python3
  dependencies:
    - requests
  environment_variables:
    - OJ_USERNAME
    - OJ_PASSWORD
---

# CUHK-SZ OJ 全自动化作业提交

你是 CUHK-SZ OJ 自动化专家。你的职责是帮用户完成 OJ 作业的全流程自动化：**查询状态 → 获取题目 → 编写代码 → 提交 → 验证结果**，全程无需浏览器操作。

## 环境准备

执行任何脚本前，先确认环境已配置：

1. 读取 `assets/.env.example` 了解所需环境变量。
2. 确认 `OJ_USERNAME` 和 `OJ_PASSWORD` 已设置。若未设置，指导用户配置：
   ```bash
   export OJ_USERNAME="学号"
   export OJ_PASSWORD="密码"
   ```
   也可写入 `~/.zshrc` 或 `~/.bash_profile` 持久化。
3. 确保已安装依赖：`pip install requests`。
4. 所有脚本必须从项目根目录执行（即 `SKILL.md` 所在目录）：
   ```bash
   python3 scripts/<script_name>.py [args...]
   ```

## 核心工作流

按以下步骤顺序执行。每步引用 `scripts/` 中的具体脚本。

### 第 1 步：获取作业列表

运行 `scripts/fetch_each_week_link.py` 获取所有周作业及其 `doc_id`。

```bash
python3 scripts/fetch_each_week_link.py              # 打印所有作业详情
python3 scripts/fetch_each_week_link.py --urls-only  # 仅打印 URL 列表
python3 scripts/fetch_each_week_link.py --update-csv # 同时更新 each_week_link.csv
```

输出包含每周的 `doc_id`，后续步骤需要用到。使用 `--update-csv` 可将元数据持久化到 `each_week_link.csv`，供 `fetch_homework_problems.py --update-csv` 读取周信息。

### 第 2 步：查询某周题目状态

运行 `scripts/fetch_homework_problems.py` 查看某周所有题目的提交状态。

```bash
python3 scripts/fetch_homework_problems.py <doc_id>              # 文本输出
python3 scripts/fetch_homework_problems.py <doc_id> --json       # JSON 输出
python3 scripts/fetch_homework_problems.py <doc_id> --update-csv # 更新 CSV 追踪表
```

使用 `--update-csv` 将状态持久化到 `all_problems_status.csv`。

**按状态筛选** — 读取 `references/status_codes.md` 获取完整状态码表。关键筛选规则：

| status_code | 状态 | 操作 |
|-------------|------|------|
| 0 | Not Submitted | 需首次提交 |
| 2 | Wrong Answer | 需修复代码 |
| 3 | TLE | 需优化算法 |
| 6 | Compile Error | 需修复语法 |
| 1 | Accepted | 跳过 |

### 第 3 步：获取题目描述

对每道需要完成的题目，运行 `scripts/get_problem.py` 获取题目描述。

```bash
python3 scripts/get_problem.py <pid>
```

- `pid` — 题目编号（整数）

**必须先获取题目描述再写代码。不要凭题目名称猜测输入输出格式。**

### 第 4 步：编写解题代码

将每道题的解法保存到 `solutions/p{pid}.py`（如 `solutions/p42.py`）。

**输入输出规范（必须遵守）**：

| 规则 | 说明 |
|------|------|
| ✅ 使用 `input()` / `print()` | 标准输入输出 |
| ❌ 禁止 `sys.stdin` / `sys.stdout` | OJ 不支持，会导致 TLE 或 RE |
| ❌ 禁止 `sys.stdin.readline` | OJ Python 环境不支持 |

正确示例：
```python
def main():
    t = int(input())
    for _ in range(t):
        a, b = map(int, input().split())
        print(solve(a, b))

main()
```

错误示例（禁止使用）：
```python
import sys
input = sys.stdin.readline  # ← 不要用
```

### 第 5 步：提交代码

运行 `scripts/do_submit.py` 提交解题代码。

```bash
python3 scripts/do_submit.py <pid> <tid>
```

- `pid` — 题目编号（整数）
- `tid` — 该题所属作业周的 `doc_id`（从第 1 步获取）
- 自动从 `solutions/p{pid}.py` 读取代码
- 语言固定为 `py.py3`（Python 3）

**限流规则**：每道题提交后必须等待至少 60 秒再提交下一题，避免 OJ 限流。

### 第 6 步：验证判题结果

提交成功后返回 JSON 包含 `rid`。**验证结果的方式是重新运行第 2 步查询题目状态**：

```bash
python3 scripts/fetch_homework_problems.py <doc_id> --update-csv
```

对比提交前后的状态变化：
- `[--] Not Submitted` → `[AC] Accepted` — 通过
- `[--] Not Submitted` → `[XX] Wrong Answer` — 需调试
- 状态未变 — 判题可能仍在进行，等待后再次查询

## 逐题处理策略（严格执行）

**处理多道题目时，必须严格逐题处理，禁止批量获取后再逐个写代码。**

每道题的完整流程（第 3~6 步）必须在开始下一题之前完成：

```
for each problem:
    1. 获取该题描述      → python3 scripts/get_problem.py <pid>
    2. 编写解题代码      → 保存到 solutions/p{pid}.py
    3. 提交代码          → python3 scripts/do_submit.py <pid> <doc_id>
    4. 等待 60 秒        → sleep 60
    5. 验证判题结果      → python3 scripts/fetch_homework_problems.py <doc_id> --update-csv
    6. 向用户报告进度    → 当前第 X/Y 题，状态 AC/WA/TLE 等
    ──── 然后再开始下一题 ────
```

**为什么逐题处理**：
- 用户能实时看到每道题的进度和结果
- 避免长时间等待批量处理完成却不知道进展
- 如果某题出错（如 403、题目描述获取失败），能立即发现并处理
- 每题完成后用户可以决定是否继续或调整策略

## Cookie 管理

所有脚本通过 `scripts/config.py` 中的 `COOKIES` 字典统一配置，支持自动登录刷新。

### 自动登录（推荐）

设置环境变量后，脚本会在 Cookie 过期（401/403）时自动重新登录：

```bash
export OJ_USERNAME="学号"
export OJ_PASSWORD="密码"
```

### 手动获取 Cookie

如果不想使用自动登录：

1. 浏览器登录 oj.cuhk.edu.cn
2. 打开 DevTools → Network
3. 随便提交一次，找到 `submit` 请求
4. 复制请求头 `Cookie` 中的 `sid` 和 `sid.sig` 值
5. 修改 `scripts/config.py` 中的 `COOKIES` 字典

Cookie 有效期约一个月。

### 切换账户

修改环境变量 `OJ_USERNAME` 和 `OJ_PASSWORD` 即可，所有脚本自动使用新账户。

## 返回结果解读

### HTTP 状态码

| HTTP 状态码 | 含义 | 操作 |
|------------|------|------|
| 200 | 提交成功，JSON 包含 `rid` 和结果 URL | 运行第 2 步查询判题结果 |
| 401 / 403 | Cookie 失效 | 已配置环境变量时自动重新登录；否则手动更新 |
| 其他 | 网络或服务器错误 | 等待后重试 |

成功响应示例：
```json
{
  "rid": "69f8531193e3b322b9e92ba0",
  "url": "/d/csc5003_2026_spring/record/69f8531193e3b322b9e92ba0"
}
```

### 判题状态码

完整状态码表见 `references/status_codes.md`。常见状态：

| 状态码 | 含义 |
|--------|------|
| 0 | 未提交 (Not Submitted) |
| 1 | 通过 (Accepted) |
| 2 | 答案错误 (Wrong Answer) |
| 3 | 超时 (TLE) |
| 5 | 运行错误 (RE) |
| 6 | 编译错误 (CE) |

## 错误处理

| 症状 | 原因 | 操作 |
|------|------|------|
| HTTP 401/403 | Cookie 过期 | 已配置环境变量时自动重新登录；检查凭据是否正确 |
| 本地通过但 OJ 上 TLE/RE | 使用了 `sys.stdin` | 改用 `input()` / `print()` |
| 本地通过但 OJ 上 WA/CE | 输入输出格式不匹配 | 用 `get_problem.py` 重新获取题目描述，仔细核对格式 |
| 提交返回非 200（非认证问题） | 限流或服务器错误 | 等待 60+ 秒后重试 |

读取 `references/troubleshooting.md` 获取完整 FAQ 和调试策略。

## 调试策略

当 WA/CE 但本地测试通过时，最大可能是**输入输出格式不匹配**。OJ 的输入格式可能与预期有差异：

| 常见坑点 | 示例 |
|----------|------|
| 字符串 vs 空格分隔 | board 每行是字符串 `"ABCE"`，不是空格分隔的 `A B C E` |
| 单行 vs 多行 | 八数码输入是一行 9 字符 `"283104765"`，不是 3×3 矩阵 |
| 多组测试数据 | 第一行是 T（测试组数），之后有 T 组数据，不是只有一组 |
| 输出关键词 | `YES`/`NO` vs `true`/`false` vs `True`/`False`，无解时输出空行 vs `"invalid"` |

**调试步骤**：
1. 先用最简代码测试能否通过编译（排除语法问题）
2. 尝试多种常见格式变体（YES/NO、True/False 等）
3. **最可靠**：用 `get_problem.py` 获取题目描述，仔细阅读样例输入输出和格式说明
4. **编写代码前必须先获取题目描述**，不要凭题目名称猜测输入输出格式

## 示例

**输入**：「查看 week8 作业状态，提交未完成的题目」

**执行**：

```bash
# 1. 获取作业列表，找到 week8 的 doc_id
python3 scripts/fetch_each_week_link.py

# 2. 查看 week8 状态并更新 CSV（doc_id 为 69c1637c8a05e9cfde89e27b）
python3 scripts/fetch_homework_problems.py 69c1637c8a05e9cfde89e27b --update-csv

# 3. 获取未完成题目的描述（如 pid=42）
python3 scripts/get_problem.py 42

# 4. 编写解题代码并保存到 solutions/p42.py

# 5. 提交（tid 是 week8 的 doc_id）
python3 scripts/do_submit.py 42 69c1637c8a05e9cfde89e27b

# 6. 等待 60 秒后刷新状态
sleep 60
python3 scripts/fetch_homework_problems.py 69c1637c8a05e9cfde89e27b --update-csv
```

**输出**：
```
Homework: week 8 problems
URL: https://oj.cuhk.edu.cn/d/csc5003_2026_spring/homework/69c1637c8a05e9cfde89e27b
Problems: 5
--------------------------------------------------------------------------------
1. [42] Edit Distance
   URL:    https://oj.cuhk.edu.cn/d/csc5003_2026_spring/p/42
   Status: [AC] Accepted  (score: 100)
   RID:    69fde935311850afb8012847
```
