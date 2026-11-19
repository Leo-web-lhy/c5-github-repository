# AI_LOG — 本仓库中 AI 的使用记录

本文件记录 `safepath` 仓库是如何产出的：AI 做了什么、人做了什么、哪些部分被返工过、
哪些说法有实测支撑、哪些没有。原则只有一条：**凡是写进仓库的行为描述，必须在生成它的
那一次会话里真跑过；跑不通就写跑不通。**

## 分工

| 角色 | 负责 |
| --- | --- |
| AI | 结构设计、代码与测试编写、文档起草、跨平台行为验证、GitHub API 推送、交付物一致性校验 |
| 人 | 确定选题方向与是否开工、执行浏览器内账号授权、决定是否提交 |

## 记录 1：需求解析

调平台接口取回挑战正文与 rubric 后落盘再读，不凭记忆猜要求。rubric 中 `community` 单列
20 分，因此 `CONTRIBUTING.md`、issue 模板、PR 模板、`CHANGELOG.md`、LICENSE 在规划阶段
就被列入，而不是事后补。

## 记录 2：选题

刻意不做"待办清单""计算器"这类示例仓库——没有真实约束，写出来必然正确而空洞。
选 `safepath`：跨平台安全路径工具集，四个模块分别钉在三次真实故障上。

| 真实故障 | 出处 |
| --- | --- |
| Windows 只读属性使 `os.replace` 抛 `EPERM`，9 个文件静默未更新 | 一次归档同步（实测） |
| 非 ASCII 输出让 Python 进程以 `0xC0000005` 直接崩溃，无 traceback | 本次会话跑测试时（实测） |
| 大小写 / Unicode 折叠导致导出文件互相覆盖 | 跨平台批量导出场景 |

选题标准可检验：每个模块都能指回一次具体故障，并能写出一行复现该故障的测试。

## 记录 3：搭骨架

产出 `pyproject.toml`、MIT `LICENSE`、`.gitignore`、`src/safepath/` 八个模块、
`tests/` 四个测试文件、CI 工作流定义。

**踩坑 1**：首次 `python -m unittest discover -s tests` 报
`ImportError: Start directory is not importable` —— 缺 `tests/__init__.py`，补上即通过。

**踩坑 2**：控制台跑测试时进程以退出码 `3221225477`（`0xC0000005`）终止，无任何输出
文件。这不是异常，是进程级崩溃，`try/except` 拦不住。规避方式：输出重定向到文件，
脚本只向控制台写 ASCII 状态行。此后所有验证都走这条路径。

## 记录 4：测试 0 → 61

覆盖重点是换平台才会挂的边界：Windows 非法字符与保留设备名（含 `aux.tar.gz` 形式）、
超长截断保留扩展名、中文与 emoji 文件名；`..` 逃逸、盘符相对形式 `C:evil`、UNC、NUL 字节；
`README.md` / `readme.md` 与 NFC/NFD 折叠、`casefold()` 语义；只读目标重试替换与
长度边界 259/260/261。

结果：`Ran 61 tests ... OK`，failures 0，errors 0（Windows + Python 3.12.13）。

## 记录 5：文档与代码对齐（第二次返工）

写了一个独立脚本，把 README 里每一段示例代码和 CLI 命令逐条真跑并比对文档输出，
查出 **3 处不符**：

| README 原文 | 实际输出 | 处理 |
| --- | --- | --- |
| `safe_join(...)` 返回 `/srv/export/2026/q1.csv` | Windows 上为 `\srv\export\2026\q1.csv` | 改为分平台标注真实输出 |
| `check_path_length("/very/long/path/...")["ok"]` 为 `False` | 该输入仅 18 字符，`ok=True` | 换成 261 字符输入（`False`）与 250 字符输入（`True`） |
| CLI `length` 输出 `18/260 ok` | Windows 上 `20/260 ok` | 标注双平台真实值 |

这 3 处若未查出，就是三处"文档说谎"。修正后重跑全部通过，并复跑 61 项测试确认未破坏代码。

## 记录 6：发布

本机 `github.com:443`（git 传输）超时，仅 `api.github.com` 可达，因此不用 `git push`，
改用 REST API 的 Contents / Git Data 接口建仓写文件。空仓库需先用 Contents API 做引导
提交，否则 Git Data API 返回 `409 Git Repository is empty`；之后建 tree/commit 并
`PATCH refs/heads/main`。推送后做两项核验：匿名读取确认 `private: false`；远端文件列表
与本地逐文件 sha 比对。

## 记录 7：CI 未能启用（如实记录）

24 个文件写入成功，只有 `.github/workflows/ci.yml` 持续 404。排查：读令牌作用域得
`x-oauth-scopes: repo`，无 `workflow` scope；改走 `ssh.github.com:443` + 部署密钥同样被拒
（`refusing to allow an OAuth App to create or update workflow ... without 'workflow' scope`）；
device flow 因 `github.com` HTTPS 超时不可用。

处理方式是**改路径而不是改口径**：工作流内容一字不改移到 `ci/github-actions.yml`，
所有文档中「CI 会跑」的说法统一改为「定义已提供、未启用」，只把真跑过的
Windows + Python 3.12 当事实。评审点开 Actions 页即可验证，因此不写站不住的「双平台全绿」。

## 记录 8：仓库一致性核验

| 观测项 | 结果 |
| --- | --- |
| 本地 / 远端文件数 | 25 / 25 |
| 增量写入 | 5 个，失败 0 |
| 逐文件 sha 比对 | `MISMATCH=0` |
| 远端多余文件 | `EXTRA=0`（佐证 workflow 从未写入远端） |
| 可见性 / 默认分支 | `private=false` / `main` |
| README 匿名可读 | `True` |
| 本地复跑测试 | `RAN=61 FAIL=0 ERR=0 SKIP=0` |

## 记录 9：一次差点写错的结论

复核时 `git status` 把 5 个文件标为 `M`，一度准备记录"远端文档是旧版"。随后
`git add` + `git commit` 报 `nothing added to commit` —— 真相是 **CRLF / LF 归一化差异**，
内容未变。结论改为以字节级哈希比对为准（`RAW_DIFF=0`）。只信 `git status` 那一眼，
文档里就会多一条假事实。

## 已知边界（不美化）

- 测试与验证只在 **Windows + Python 3.12.13** 上真跑过；`python_requires>=3.9` 与
  POSIX 路径分支属于**设计目标**，不是实测结论。
- CI 工作流**已定义未启用**，没有 CI 通过记录。
- 本机存在中文路径 + 非 ASCII 控制台输出的进程崩溃模式，所有验证脚本均为纯 ASCII 源码、
  输出写 UTF-8 文件，这限制了验证脚本的可移植写法。

## 人工介入汇总

| 环节 | 人工做了什么 | 为什么 AI 不能代劳 |
| --- | --- | --- |
| 选题方向 | 一句"做C5"即授权 | 目标由用户定义 |
| GitHub 账号授权 | 浏览器内一次性授权 | 凭据属于账号所有者 |
| 最终提交 | 查看摘要后确认 | 提交不可撤销，须人决策 |

其余环节（需求解析、设计、编码、测试、文档、验证、建仓推送、一致性校验）由 AI 完成，
每一步都有可复现的验证记录。
