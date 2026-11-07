# 参与贡献

感谢你愿意花时间。这个仓库刻意保持小而严：**宁可少一个功能，也不要多一个只在某个
平台上悄悄失效的功能。** 下面的规则不多，但会严格执行。

## 先看这些

- [README](README.md) —— 项目边界（"不做的事"那一节尤其重要）
- [docs/design-notes.md](docs/design-notes.md) —— 每个取舍的理由，以及已知限制
- [CHANGELOG.md](CHANGELOG.md) —— 版本历史与将要到来的改动

## 报告问题

请使用 Issue 模板（bug report / feature request）。**提 bug 时请务必附上**：

1. 操作系统与版本（`Windows 11 22H2` / `macOS 14.5` / `Ubuntu 22.04`）
2. Python 版本（`python -V` 的完整输出）
3. 最小复现片段，能直接粘贴运行
4. 期望结果与实际结果（包含完整异常文本，不要只写"报错了"）

如果问题只在某一个平台出现，请在标题里写出来，例如
`[win] atomic_replace 在只读目录上重试耗尽`。这类问题优先级最高——它们正是本项目
存在的理由。

## 提交改动

1. 从 `main` 切分支，命名 `<type>/<短描述>`，`type` 取 `feat` / `fix` / `docs` / `test` / `chore`。
   例：`fix/readonly-rename-retry`。
2. 提交信息用 **Conventional Commits**：`<type>(<scope>): <祈使句描述>`。
   例：`fix(fsops): retry os.replace after clearing the read-only bit`。
   一条提交只做一件事；不要混入无关的格式化改动。
3. 新行为必须有测试。**修 bug 必须先写一个能复现该 bug 的失败测试**，再改实现。
4. 跑通本地检查：

   ```bash
   python -m pip install -e .
   python -m unittest discover -s tests -v
   python -m safepath sanitize "a/b:c?.txt"
   ```

5. 开 PR，用 PR 模板填"改了什么 / 为什么 / 怎么验证"。CI 必须绿。

## 代码约定

- 仅用标准库。新增依赖需要在本 Issue 里说清必要性，默认拒绝。
- 公共函数必须有 docstring，写清参数、返回值与异常；类型注解必填。
- 错误用 `safepath.errors` 中的专用异常，不要抛裸 `Exception`，也不要用 `assert` 做输入校验。
- 保持 Windows 与 POSIX 行为一致；**无法一致时，在 docstring 明确写出差异**，并加测试。
- 不做静默兜底：非法输入报错，不猜测调用方意图。

## 评审标准

PR 合并看四条，缺一条就打回：

1. 行为正确，且边界情况（空串、`..`、保留名、超长、Unicode 折叠）有测试覆盖；
2. 没有引入平台相关的隐性假设，或已明确记录差异；
3. 公共 API 保持向后兼容；破坏性变更必须走版本号与 CHANGELOG；
4. 文档（README / design-notes / CHANGELOG）与实际行为同步更新。

## 版本策略

语义化版本：

- `PATCH`：修 bug、改文档、补测试，不改公共 API；
- `MINOR`：新增向后兼容的函数或参数；
- `MAJOR`：改签名、改默认行为、改异常类型。

每完成一个版本在 `CHANGELOG.md` 顶部加一节，写清"改了什么 / 为什么 / 升级要做什么"。

## 需要避免的

- **一次性大重构 PR**：拆成可独立评审的小步。
- **只改测试让 CI 变绿**：掩盖失败的测试比失败的测试更糟。
- **复制粘贴式新模块**：先看现有模块能否用参数覆盖。

## 行为准则

讨论对事不对人。技术分歧用可复现证据解决（最小复现 + 平台/版本信息），不接受
"我这里没问题"作为结论。
