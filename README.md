# CUHK-SZ OJ HTTP 客户端

非官方 CUHK-SZ OJ（Hydro OJ）HTTP 客户端工具集，提供命令行方式与 OJ 平台交互，适用于批量查询题目状态、获取题目描述、提交代码等场景。

## 项目结构

```
.
├── README.md                       # 本文件
├── .gitignore                      # Git 忽略规则
├── .env.example                    # 环境变量示例
├── skill.md                        # 自动化流程规范（供 Claude Code 使用）
├── config.py                       # 共享配置（Cookie、URL、状态码等）
├── oj_client.py                    # 共享 HTTP 客户端和工具函数
├── fetch_each_week_link.py         # 抓取作业列表
├── fetch_homework_problems.py      # 获取某周作业的题目和提交状态
├── get_problem.py                  # 获取题目描述文本
├── do_submit.py                    # 提交代码到 OJ
└── solutions/                      # 用户自建，存放解题代码（p{pid}.py）
```

## 依赖

```bash
pip install requests
```

## 快速开始

1. 配置登录凭据：
   ```bash
   cp .env.example .env
   # 编辑 .env 填入学号和密码
   export $(cat .env | xargs)
   ```

2. 获取作业列表：
   ```bash
   python3 fetch_each_week_link.py
   ```

3. 获取某周题目和状态：
   ```bash
   python3 fetch_homework_problems.py <doc_id> --update-csv
   ```

4. 获取题目描述：
   ```bash
   python3 get_problem.py <pid> <tid>
   ```

5. 提交代码（需先创建 `solutions/` 目录并放入 `p{pid}.py`）：
   ```bash
   python3 do_submit.py <pid> <tid>
   ```

## 模块说明

### config.py

集中管理所有脚本共享的配置常量：

- `BASE_URL` — OJ 域名
- `COURSE_SLUG` — 课程标识（`csc5003_2026_spring`）
- `OJ_USERNAME` / `OJ_PASSWORD` — 登录凭据（从环境变量读取）
- `COOKIES` — 鉴权 Cookie（sid, sid.sig），自动登录时会更新
- `HEADERS` — HTTP 请求头
- `STATUS_MAP` — 判题状态码映射

推荐通过环境变量 `OJ_USERNAME` / `OJ_PASSWORD` 配置登录凭据，Cookie 会自动刷新。也可手动编辑 `COOKIES` 字典。

### oj_client.py

封装通用 HTTP 请求和工具函数，供各脚本复用：

- `get()` / `post()` — 自动附加 Cookie 和请求头，统一错误处理，401/403 时自动重新登录
- `login()` — 程序化登录 OJ，更新 Cookie
- `problem_url()` / `homework_url()` / `submit_url()` — URL 拼接
- `extract_ui_context()` — 从页面 HTML 提取嵌入的 JSON 数据
- `fetch_problem_title()` — 获取题目标题
- `OJError` — 统一异常类

### fetch_each_week_link.py

从 OJ 课程页抓取作业列表，生成/更新 `each_week_link.csv`。

```bash
python3 fetch_each_week_link.py              # 打印所有作业的完整详情
python3 fetch_each_week_link.py --urls-only  # 仅打印 URL 列表
```

### fetch_homework_problems.py

获取某周作业中所有题目的链接和提交状态。

```bash
python3 fetch_homework_problems.py <doc_id>              # 文本格式输出
python3 fetch_homework_problems.py <doc_id> --json       # JSON 格式输出
python3 fetch_homework_problems.py <doc_id> --update-csv # 获取并更新 all_problems_status.csv
```

### get_problem.py

获取 OJ 上具体题目的描述文本，纯文本输出到终端。

```bash
python3 get_problem.py <pid> <tid>
```

### do_submit.py

将代码提交到 OJ 判题服务器。

```bash
python3 do_submit.py <pid> <tid>
```

- 自动从 `solutions/p{pid}.py` 读取代码
- 语言固定为 `py.py3`（Python 3）

## Cookie 管理

所有脚本通过 `config.py` 中的 `COOKIES` 字典统一配置，支持自动登录刷新。

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
4. 修改 `config.py` 中的 `COOKIES` 字典

> Cookie 有效期约一个月。未配置环境变量时，返回 401/403 需手动重新获取。

### 切换账户

修改环境变量 `OJ_USERNAME` 和 `OJ_PASSWORD` 即可。所有脚本会自动使用新账户的身份发起请求。

## 判题状态码

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

## 注意事项

- OJ 的 Python 环境**不支持** `sys.stdin` / `sys.stdout`，必须使用 `input()` / `print()`
- 每题提交间隔建议 ≥ 60 秒，避免触发限流
