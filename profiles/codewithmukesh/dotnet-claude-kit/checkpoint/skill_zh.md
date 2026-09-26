# /checkpoint

## 什么是

一种快速的中途保存，通过两步操作将已知良好状态保存下来：

1. **描述性 git 提交** — 阶段相关更改，并使用总结工作的消息提交。
2. **简短的手交笔记** — 编写 `.claude/handoff.md`，以便恢复会话（或在重构失败后，你知道确切的状态）。

Checkpoint 是中途保存；`/wrap-up` 是会话结束的仪式。Checkpoint 提交并记录笔记，然后继续工作。Wrap-up 执行完整的手交并从 `MEMORY.md` 中提取学习内容。

## 何时使用

- 在进行有风险的重构或破坏性更改之前 — 保存已知良好状态
- 在会话中途切换到不同的任务或功能
- 完成一个逻辑工作单元后 — 保存下来
- 用户说 "checkpoint"、"save progress"、"save state"、"pause here"
- 如果会话实际上正在结束，使用 `/wrap-up` 进行完整仪式

## 如何使用

1. **评估状态** — 使用 `git status` 和 `git diff` 查看已阶段和未阶段的更改。
2. **阶段更改** — 阶段特定文件；永远不要使用 `git add -A`。排除生成文件、构建工件和密钥（`.env`、凭证）。
3. **提交** — 遵循仓库的提交风格（常规前缀：`feat:`、`fix:`、`refactor:`）。新的提交，永远不要修改。如果没有可提交的内容，跳到手交笔记。
4. **编写手交笔记** — `.claude/handoff.md`，与 `/wrap-up` 相同的格式，但简短：已完成、待办（带有具体的下一步）、学习（只有当出现非明显内容时）、上下文（分支 + 提交哈希）。一个文件，总是被覆盖。
5. **确认** — 报告提交哈希和手交摘要，然后继续工作。

### 安全规则

- 永远不要推送、强制推送或触摸远程分支
- 永远不要提交密钥
- 永远不要修改 — Checkpoint 是你可以返回的新提交
- 没有可提交的更改？仅更新手交笔记

## 示例

```
用户: /checkpoint — 即将尝试 EF Core 分查询重构

Claude: 3 个文件已修改，1 个新文件。

  提交 a1b2c3d: "feat: 使用 FluentValidation 添加 CreateOrder 验证"
  - src/Orders/Features/CreateOrder.cs
  - src/Orders/Features/CreateOrderValidator.cs (新文件)
  - tests/Orders.Tests/Features/CreateOrderTests.cs

  手交笔记已更新 (.claude/handoff.md):
  ## 已完成
  - [x] CreateOrder 验证 + 3 个测试场景
  ## 待办
  - [ ] 在 GetOrderDetails 中进行分查询重构（即将尝试）
  ## 上下文
  - 分支: feature/order-validation | Checkpoint: a1b2c3d

  Checkpoint 已保存 — 可以安全地进行有风险的重构。
```

## 相关

- `/wrap-up` — 会话结束仪式：完整手交格式定义以及从 MEMORY.md 中提取学习内容
- `/build-fix` — 在 Checkpoint 之前使构建变绿
