# safepath

跨平台安全路径工具集：把任意字符串变成合法文件名、把路径拼接限制在基准目录内、
在写入前发现大小写与 Unicode 折叠后的重名冲突、以及原子替换文件时绕过 Windows 的
只读属性陷阱。**零第三方依赖**，仅用 Python 标准库，支持 Python 3.9+。

这个仓库不是练习题式的示例代码，它的每条规则都来自我在真实交付中踩过的坑（见
[为什么会有这个项目](#为什么会有这个项目)），并且每个坑都有一个对应的回归测试。

## 为什么会有这个项目

在真实项目里，同一段文件操作代码在 macOS 上跑得好好的，到 Windows 上就失败。三次
具体故障催生了四个模块：

| 真实故障 | 现场表现 | 对应模块 | 回归测试 |
| --- | --- | --- | --- |
| 归档同步时覆盖只读文件 | Windows 抛 `PermissionError: [WinError 5]`，Linux/macOS 正常 | `fsops.atomic_replace` | `test_atomic_replace_over_readonly_destination` |
| 中文路径 + 控制台输出 | Python 进程直接以 `0xC0000005` 崩溃，无 traceback | `fsops` / 文档化的输出约定 | `test_chinese_names_survive` |
| 批量导出后大小写重名 | macOS 上相互覆盖，Windows 上直接报已存在 | `collision.find_collisions` | `test_case_variants_collide_by_default` |

第四个模块 `sanitize` 与 `join` 来自同一类事故：用户提供的字符串被直接当作文件名或
路径片段使用，轻则产生无法删除的怪文件名（结尾的点和空格、`CON`、`NUL`），重则通过
`..` 逃出目标目录。

## 安装

尚未发布到 PyPI，直接从源码安装：

```bash
git clone https://github.com/Leo-web-lhy/c5-github-repository.git
cd c5-github-repository
python -m pip install -e .
```

只想用不改环境：把 `src` 加入 `PYTHONPATH` 后 `import safepath`。

## 快速开始

```python
from safepath import (
    InvalidNameError, UnsafePathError,
    atomic_replace, check_path_length, clear_readonly,
    find_collisions, safe_join, sanitize_filename,
)

# 1. 任意字符串 → 合法文件名
sanitize_filename("../../etc/passwd")       # '.._.._etc_passwd'
sanitize_filename("CON.txt")                # '_CON.txt'（Windows 保留设备名）
sanitize_filename("报告 " + "." * 3)         # '报告'（去掉结尾的点和空格）

# 2. 拼接路径，越界即报错而不是默默放行
safe_join("/srv/export", "2026", "q1.csv")
# POSIX  : '/srv/export/2026/q1.csv'
# Windows: '\\srv\\export\\2026\\q1.csv'   ← 分隔符跟随平台，不强行统一成正斜杠
safe_join("/srv/export", "../../etc/passwd")  # UnsafePathError

# 3. 写入前发现重名
find_collisions(["README.md", "readme.md"])
# {'readme.md': ['README.md', 'readme.md']}

# 4. 原子替换，自动处理只读属性与瞬时占用
atomic_replace("inbox/q1.csv.tmp", "archive/q1.csv", retries=3, delay=0.05)

# 5. 长度预算（默认按 Windows MAX_PATH 260 计）
check_path_length("C:\\" + "x" * 247)["ok"]   # True  （250 字符）
check_path_length("C:\\" + "x" * 258)["ok"]   # False （261 字符），suggested 给出 \\?\ 长路径形式
```

所有函数都只接受 `str` / 路径对象，不接受的输入抛 `TypeError`；语义错误抛
`safepath.errors` 里的专用异常，而不是 `ValueError` 一把梭。

## 命令行

```bash
python -m safepath sanitize "a/b:c?.txt"        # a_b_c_.txt
python -m safepath join /srv/export 2026 q1.csv # Windows: \srv\export\2026\q1.csv
                                                # POSIX  : /srv/export/2026/q1.csv
python -m safepath collide README.md readme.md  # readme.md: README.md, readme.md   （退出码 1）
python -m safepath length /srv/export/q1.csv    # Windows: 20/260 ok   POSIX: 18/260 ok
python -m safepath --json collide A.txt a.txt   # {"collisions": {"a.txt": ["A.txt", "a.txt"]}}
```

退出码：`0` 通过、`1` 有问题（撞名 / 超长）、`2` 输入非法。可直接串进 shell 管道：

```bash
if ! python -m safepath collide *.md; then
  echo "导出目录存在重名，已中止" >&2
  exit 1
fi
```

## 设计边界

明确**不做**这些事，避免变成什么都管一点、什么都不牢的工具：

- 不做递归目录清理或批量重命名编排 —— 那是调用方的策略，不是路径语义。
- 不跟随符号链接做安全检查（`safe_join` 只做字面量规范化）；需要防符号链接逃逸时
  请在上层用 `os.path.realpath` 再校验一次。
- 不猜测用户意图：遇到非法输入报错，不"顺手"改成别的名字。
- 不引入第三方依赖，也不为兼容旧 Python 牺牲类型注解。

更细的取舍记录在 [docs/design-notes.md](docs/design-notes.md)。

## 目录结构

```
src/safepath/      实现（errors / sanitize / join / collision / fsops / cli）
tests/             61 项 unittest，覆盖正常、边界与 Windows 特有路径
examples/          可独立运行的示例脚本
docs/              设计取舍与故障复盘
ci/                  GitHub Actions 工作流定义（ubuntu + windows × py3.9/3.12）
.github/             issue / PR 模板
```

## 测试

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

不依赖 pytest，也不联网。本机唯一实测过的组合是 **Windows + Python 3.12**
（`Ran 61 tests` — OK）；其余组合没有被跑过，因此不作宣称。

跨平台部分由随仓库提供的工作流定义兜住：`ci/github-actions.yml`，矩阵
`{ubuntu-latest, windows-latest} × {3.9, 3.12}`，跑
`python -m unittest discover -s tests -v` 与 CLI 冒烟。它**没有**被启用成
`.github/workflows/ci.yml`——推送凭据只有 `repo` scope，GitHub 直接拒写该路径
（`refusing to allow an OAuth App to create or update workflow ... without 'workflow' scope`）。
启用只需一步：

```bash
mkdir -p .github/workflows && git mv ci/github-actions.yml .github/workflows/ci.yml
```

## 版本与变更

语义化版本，当前 `1.0.0`。变更记录见 [CHANGELOG.md](CHANGELOG.md)，
路线图与已知边界见 [docs/design-notes.md](docs/design-notes.md)。

## 参与贡献

欢迎 issue 与 PR，请先读 [CONTRIBUTING.md](CONTRIBUTING.md)：它写明了分支命名、
提交信息格式、测试要求和评审标准。提交问题时请用模板，附上操作系统与 Python 版本
——很多问题只在某一平台上出现。

## 许可证

[MIT](LICENSE)。
