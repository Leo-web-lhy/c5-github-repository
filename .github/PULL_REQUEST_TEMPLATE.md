## 改了什么

<!-- 一段话说明本 PR 的单一目标 -->

## 为什么

<!-- 关联 Issue；写清动机而不是复述 diff -->

Closes #

## 怎么验证

```bash
python -m unittest discover -s tests -v
```

- [ ] 新增/修改的行为都有测试，且测试**先失败后通过**
- [ ] 在 Windows 上验证过（或说明为什么不能）
- [ ] 在 POSIX 上验证过（或说明为什么不能）
- [ ] README / docs/design-notes.md / CHANGELOG.md 已同步

## 影响面

- [ ] 向后兼容
- [ ] 破坏性变更（已在 CHANGELOG 的 Unreleased 中说明升级步骤）

## 检查清单

- [ ] 仅使用标准库
- [ ] 公共函数有 docstring 与类型注解
- [ ] 未使用裸 `except` / `assert` 做输入校验
- [ ] 提交信息符合 Conventional Commits
