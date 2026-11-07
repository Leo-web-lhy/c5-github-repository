# 变更记录

本文件记录所有值得注意的改动。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中

- `fsops.atomic_replace` 支持目录整树替换（当前只处理单文件）。
- 新增 `safepath scan <dir>` 子命令：一次性检查一个导出目录的重名、保留名与超长路径。
- 为 macOS 的 NFD 默认文件系统补充更多折叠用例。

## [1.0.0] - 2026-11-07

首个可用版本。四个模块都源自真实交付中遇到的跨平台故障，每个故障都有对应回归测试。

### 新增

- `sanitize.sanitize_filename()`：替换 Windows 非法字符、控制字符，剔除结尾的点与空格，
  处理 `CON`/`NUL`/`COM1`/`LPT9` 等保留设备名，按长度上限截断且保留扩展名。
- `sanitize.is_reserved_name()`：判断一个名字是否是 Windows 保留设备名（含带扩展名形式，
  例如 `aux.tar.gz`），并正确排除 `console.txt`、`COM10.log` 这类形似而非的写法。
- `join.safe_join()`：拼接路径片段并把结果限制在基准目录内，拒绝 `..` 逃逸、绝对路径片段、
  盘符相对形式（`C:evil`）、UNC 路径与 NUL 字节。
- `join.is_within()`：前缀安全的包含判断，避免 `base_evil` 被 `base` 误判为子路径。
- `collision.find_collisions()`：按大小写（或 `str.casefold`）与 Unicode NFC/NFD 折叠后
  分组报告重名，供写入前拦截。
- `collision.fold_name()`：暴露单个名字的折叠结果，便于上层自定义索引。
- `fsops.clear_readonly()`：清除只读属性；对目录同样有效（Windows 上删除目录条目需要写权限）。
- `fsops.atomic_replace()`：`os.replace` 封装，替换前清除目标只读位，遇 `PermissionError`
  清除并重试，重试耗尽后抛出最后一次异常而不是自定义异常。
- `fsops.check_path_length()`：按 MAX_PATH 预算检查绝对路径长度，超限时在 Windows 上给出
  `\\?\` 长路径形式建议。
- 命令行 `python -m safepath {sanitize,join,collide,length}`，支持 `--json`，
  退出码 `0` 通过 / `1` 有问题 / `2` 输入非法。
- 专用异常层次：`SafePathError` → `UnsafePathError` / `InvalidNameError`。
- 61 项 `unittest` 测试，本机 Windows + Python 3.12 实跑通过；跨平台工作流定义见
  `ci/github-actions.yml`（未启用，原因见 README「测试」一节）。

### 说明

- 未经发布到 PyPI，请从源码安装（`python -m pip install -e .`）。
- `safe_join()` 只做字面量规范化，不解析符号链接；需要防符号链接逃逸时请在上层再校验。

[Unreleased]: https://github.com/Leo-web-lhy/c5-github-repository/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Leo-web-lhy/c5-github-repository/releases/tag/v1.0.0
