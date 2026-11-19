# ATTRIBUTION — 来源、引用与归属说明

本文件说明 `safepath` 仓库中各项内容的来源、第三方依赖情况、AI 生成部分的归属，
以及哪些内容**不是**原创、哪些结论**没有**实测支撑。

## 1. 第三方代码与依赖

**无。** 运行时零第三方依赖，仅使用 Python 标准库
（`os` / `pathlib` / `unicodedata` / `re` / `sys` / `argparse` / `dataclasses`）。
`pyproject.toml` 中不存在 `dependencies` 条目，`tests/` 亦无外部测试框架依赖
（使用标准库 `unittest`）。

因此本仓库不包含任何需要单独署名许可的第三方源码片段。

## 2. 设计与规范的参考来源

以下内容为**公开规范或事实性知识**，不是复制代码：

| 参考对象 | 用途 | 性质 |
| --- | --- | --- |
| Microsoft「Naming Files, Paths, and Namespaces」 | Windows 保留设备名清单（`CON`/`NUL`/`PRN`/`COM1`-`COM9`/`LPT1`-`LPT9`）、非法字符集、260 字符路径预算 | 公开文档中的事实性清单 |
| POSIX 路径语义（`..`、绝对路径、UNC） | `join` 模块的拒绝规则 | 通用规范行为 |
| Unicode 标准 Annex #15（NFC / NFD 规范化） | `collision` 模块的折叠比较依据 | 公开标准 |
| Python `str.casefold()` 语义 | `collision` 的大小写比较 | 标准库行为 |
| Keep a Changelog / Semantic Versioning | `CHANGELOG.md` 与版本号格式 | 公开约定 |

未使用任何第三方库源码、未复制其他开源项目的实现文件。

## 3. AI 生成内容的归属

本仓库的代码、测试、文档主要由 AI（大语言模型）生成，由人确定选题方向、执行账号授权
并决定是否发布。逐环节的分工与返工记录见 [`AI_LOG.md`](./AI_LOG.md)。

与本题相关的说明：

- 代码不是从既有项目派生，因此不存在原始作者署名需求。
- 文档中的**示例输出**均在该次会话中实跑得到，而非按经验填写；其中 3 处凭记忆写错的
  输出已被验证脚本查出并改正（见 `AI_LOG.md` 记录 5）。
- 失败与限制（CI 未启用、跨平台未实测）在 `README.md` 与 `AI_LOG.md` 中如实标注，
  未以"已验证"表述覆盖。

## 4. 用户/作者身份

- 项目作者：Leo（GitHub: [@Leo-web-lhy](https://github.com/Leo-web-lhy)）
- 课程提交身份：`2023108610260`
- 仓库地址：https://github.com/Leo-web-lhy/c5-github-repository

## 5. 许可证

本项目以 **MIT License** 发布，全文见 [`LICENSE`](./LICENSE)。
在此许可下，使用者可自由使用、修改、分发，需保留版权声明与许可声明。

## 6. 明确不属于本仓库的内容

- 本仓库**不包含**任何课程平台的私有内容、习题答案原文或受限制的第三方数据。
- 仓库中不含可执行凭据、令牌或私钥；发布所用的个人访问令牌未写入任何文件。
- `ci/github-actions.yml` 是**未启用**的工作流定义，仓库中不存在 CI 运行产物或覆盖率报告，
  因此没有任何"CI 通过"的证据可被引用。

## 7. 如何引用本仓库

```
Leo-web-lhy. safepath: cross-platform safe path utilities (v1.0.0). 2026.
https://github.com/Leo-web-lhy/c5-github-repository
```
