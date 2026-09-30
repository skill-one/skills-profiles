---
name: genshijin-commit
description: 超压缩提交信息生成。采用Conventional Commits格式，标题≤50字符，更注重“为何”而非“做了什么”。支持日语和英语双语。通过“写提交信息”、“/commit”、“/genshijin-commit”启动。在staging变更时自动建议启动。
---

提交信息应简洁且准确。采用 Conventional Commits 格式。禁止冗长。「做了什么」不如「为什么做」。

## 规则

### 标题

- `<类型>(<范围>): <动词短语摘要>` — `<范围>` 可选
- 类型: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- 动词短语: 「添加」「修复」「删除」 — 「添加了」「将添加」不可
- ≤50字符目标，72字符上限
- 结尾无需句号
- 日语/英语与仓库现有提交历史保持一致（`git log` 确认）

### 正文（必要时）

- 标题已自明则省略
- 添加时:
  - 非自明的「为什么」
  - 破坏性变更
  - 迁移注意事项
  - 相关Issue/PR
- 72字符折行
- 项目符号使用 `-`（不使用 `*`）
- 结尾添加Issue/PR引用: `Closes #42` `Refs #17`

### 绝对禁止

- 「这个提交会...」「我」「我们」「现在」「现在」— diff 足以自明
- 「根据XX请求」— 使用 `Co-authored-by` 后缀
- 「Generated with Claude Code」等AI归属声明
- 表情符号（项目惯例必须时除外）
- 范围内已存在的文件名重述

## 示例

diff: 为用户资料新增端点，原因在正文中说明
- ❌ `feat: 添加从DB获取用户资料信息的全新端点`
- ✅
  ```
  feat(api): GET /users/:id/profile 添加

  移动端客户端冷启动时
  为减少LTE带宽消耗，需要获取无需完整user payload的profile数据
  因此需要新增端点。

  Closes #128
  ```

diff: 破坏性API变更
- ✅
  ```
  feat(api)!: /v1/orders 重命名为 /v1/checkout

  BREAKING CHANGE: /v1/orders 客户端必须在2026-06-01前
  迁移至 /v1/checkout。之后旧路径将返回410状态。
  ```

diff: 小型bug修复（无需正文示例）
- ✅ `fix(auth): 修正令牌过期边界条件`

## 自动明确化

以下仅禁止标题，必须包含正文:
- 破坏性变更
- 安全修复
- 数据迁移
- revert 提交

为未来调试者保留上下文。避免过度压缩。

## 边界

- 仅生成消息。不执行 `git commit`、不进行暂存、不修改提交
- 输出可粘贴到代码块
- 使用「原始人提交停止」「普通模式」可解除
