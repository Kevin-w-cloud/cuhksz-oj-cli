# CUHK-SZ OJ 全自动化作业提交工具

CSC5003（2026春季）课程 OJ 作业的自动化解题与提交系统。通过 HTTP 请求直接与 OJ 判题服务器交互，跳过浏览器操作，实现**获取题目 → 编写代码 → 提交 → 检查结果**全流程自动化。

## 项目结构

```
.
├── SKILL.md                           # Agent Skill 规范（供 AI 自动化使用）
├── README.md                          # 本文件
├── .gitignore                         # Git 忽略规则
├── scripts/                           # 可执行脚本
│   ├── config.py                      # 共享配置（Cookie、URL、状态码等）
│   ├── oj_client.py                   # 共享 HTTP 客户端和工具函数
│   ├── fetch_each_week_link.py        # 抓取作业列表
│   ├── fetch_homework_problems.py     # 获取某周作业的题目和提交状态
│   ├── get_problem.py                 # 获取题目描述文本
│   └── do_submit.py                   # 提交代码到 OJ
├── references/                        # 参考文档（按需加载）
│   ├── status_codes.md                # 判题状态码完整表
│   └── troubleshooting.md             # FAQ 和调试策略
├── assets/                            # 模板和静态资源
│   └── .env.example                   # 环境变量模板
├── solutions/                         # 用户自建，存放解题代码（p{pid}.py）
├── each_week_link.csv                 # 每周作业链接元数据（运行时生成）
├── all_problems_status.csv            # 全部题目状态追踪表（运行时生成）
└── .cookies.json                      # Cookie 缓存（自动生成，含会话令牌）
```

## 依赖

```bash
pip install requests
```

## 快速开始

1. 配置登录凭据：
   ```bash
   export OJ_USERNAME="学号"
   export OJ_PASSWORD="密码"
   ```

2. 获取作业列表：
   ```bash
   python3 scripts/fetch_each_week_link.py
   ```

3. 获取某周题目和状态：
   ```bash
   python3 scripts/fetch_homework_problems.py <doc_id> --update-csv
   ```

4. 获取题目描述：
   ```bash
   python3 scripts/get_problem.py <pid>
   ```

5. 提交代码（需先创建 `solutions/` 目录并放入 `p{pid}.py`）：
   ```bash
   python3 scripts/do_submit.py <pid> <tid>
   ```

6. 验证判题结果（重新查询题目状态）：
   ```bash
   python3 scripts/fetch_homework_problems.py <doc_id> --update-csv
   ```

## 共享模块

### scripts/config.py

集中管理所有脚本共享的配置常量：

- `BASE_URL` — OJ 域名（`https://oj.cuhk.edu.cn`）
- `COURSE_SLUG` — 课程标识（`csc5003_2026_spring`）
- `OJ_USERNAME` / `OJ_PASSWORD` — 登录凭据（从环境变量读取）
- `COOKIES` — 鉴权 Cookie（sid, sid.sig），自动登录时会更新
- `HEADERS` — HTTP 请求头
- `STATUS_MAP` — 判题状态码映射

推荐通过环境变量 `OJ_USERNAME` / `OJ_PASSWORD` 配置登录凭据，Cookie 会自动刷新。也可手动编辑 `COOKIES` 字典。

### scripts/oj_client.py

封装通用 HTTP 请求和工具函数，供各脚本复用：

- `get()` / `post()` — 自动附加 Cookie 和请求头，统一错误处理，401/403 时自动重新登录
- `login()` — 程序化登录 OJ，更新 Cookie
- `problem_url()` / `homework_url()` / `submit_url()` — URL 拼接
- `extract_ui_context()` — 从页面 HTML 提取嵌入的 JSON 数据
- `fetch_problem_title()` — 获取题目标题
- `OJError` — 统一异常类

## 脚本说明

### scripts/fetch_each_week_link.py

从 OJ 课程页抓取作业列表，输出每周作业的详情和 `doc_id`。

```bash
python3 scripts/fetch_each_week_link.py              # 打印所有作业的完整详情
python3 scripts/fetch_each_week_link.py --urls-only  # 仅打印 URL 列表
python3 scripts/fetch_each_week_link.py --update-csv # 同时更新 each_week_link.csv
```

### scripts/fetch_homework_problems.py

获取某周作业中所有题目的链接和提交状态。**同时用于提交后查询判题结果**。

```bash
python3 scripts/fetch_homework_problems.py <doc_id>              # 文本格式输出
python3 scripts/fetch_homework_problems.py <doc_id> --json       # JSON 格式输出
python3 scripts/fetch_homework_problems.py <doc_id> --update-csv # 更新 all_problems_status.csv
```

CSV 字段：`week, pid, problem_title, url, status, status_code, score, lang, rid, begin_at, end_at`

### scripts/get_problem.py

获取 OJ 上具体题目的描述文本，纯文本输出到终端。

```bash
python3 scripts/get_problem.py <pid>
python3 scripts/get_problem.py 42
```

### scripts/do_submit.py

将代码提交到 OJ 判题服务器。

```bash
python3 scripts/do_submit.py <pid> <tid>
python3 scripts/do_submit.py 42 69c1637c8a05e9cfde89e27b
```

- `pid` — 题目编号
- `tid` — 该题所属作业周的 `doc_id`（从 `fetch_each_week_link.py` 获取）
- 自动从 `solutions/p{pid}.py` 读取代码
- 语言固定为 `py.py3`（Python 3）

## Cookie 管理

所有脚本通过 `scripts/config.py` 中的 `COOKIES` 字典统一配置，支持自动登录刷新。

### 自动登录（推荐）

设置环境变量后，脚本会在 Cookie 过期（401/403）时自动重新登录：

```bash
export OJ_USERNAME="你的学号"
export OJ_PASSWORD="你的密码"
```

也可写入 `~/.zshrc` 或 `~/.bash_profile` 持久化。

### 手动获取 Cookie

如果不想使用自动登录，仍可手动获取：

1. 浏览器登录 [oj.cuhk.edu.cn](https://oj.cuhk.edu.cn)
2. 打开 DevTools → Network → 随便提交一次代码
3. 找到 `submit` 请求，复制 `Cookie` 请求头中的 `sid` 和 `sid.sig`
4. 修改 `scripts/config.py` 中的 `COOKIES` 字典

> Cookie 有效期约一个月。未配置环境变量时，返回 401/403 需手动重新获取。

### 切换账户

修改环境变量 `OJ_USERNAME` 和 `OJ_PASSWORD` 即可。所有脚本会自动使用新账户的身份发起请求。

## 自动化流程

完整流程见 [SKILL.md](SKILL.md)，核心步骤：

1. **获取作业列表** — 用 `fetch_each_week_link.py` 获取所有周的 `doc_id`
2. **查询题目状态** — 用 `fetch_homework_problems.py --update-csv` 查询各周题目状态并更新 `all_problems_status.csv`
3. **筛选待完成题目** — 过滤 status_code 为 0（未提交）、2（WA）、3（TLE）、6（CE）的题目
4. **批量获取题目描述** — 用 `get_problem.py` 一次性获取所有待完成题目的描述
5. **批量编写代码** — 根据描述和测试用例编写解题代码，保存到 `solutions/p{pid}.py`
6. **逐个提交并验证** — 用 `do_submit.py` 提交，**每题提交后 sleep 60 秒**，用 `fetch_homework_problems.py --update-csv` 同步结果

### 代码编写规范

**必须使用 `input()` / `print()`，禁止使用 `sys.stdin` / `sys.stdout`。**

OJ 的 Python 环境不支持 `sys.stdin.readline`，会导致 TLE 或 RE。

```python
# ✅ 正确
def main():
    n = int(input())
    nums = list(map(int, input().split()))
    print(solve(n, nums))

main()

# ❌ 错误 — 禁止
import sys
input = sys.stdin.readline
```

## 解题状态码

| 状态码 | 含义 |
|--------|------|
| 0 | 未提交 (Not Submitted) |
| 1 | 通过 (Accepted) |
| 2 | 答案错误 (Wrong Answer) |
| 3 | 超时 (TLE) |
| 4 | 超内存 (MRE) |
| 5 | 运行错误 (RE) |
| 6 | 编译错误 (CE) |
| 7 | 等待中 |
| 8 | 判题中 |
| 9 | 输出超限 (OLE) |
| 10 | 格式错误 (PE) |

完整状态码说明见 [references/status_codes.md](references/status_codes.md)。

## 当前进度

查看 [all_problems_status.csv](all_problems_status.csv) 了解各题完成状态。

## 注意事项

- 所有脚本必须从**项目根目录**执行（`python3 scripts/<脚本名>.py`）
- OJ 的 Python 环境**不支持** `sys.stdin` / `sys.stdout`，必须使用 `input()` / `print()`
- 每题提交间隔建议 ≥ 60 秒，避免触发限流
- 编写代码前必须先用 `get_problem.py` 获取题目描述，不要凭题目名称猜测输入输出格式
- WA/CE 时优先检查输入输出格式，详见 [references/troubleshooting.md](references/troubleshooting.md)
