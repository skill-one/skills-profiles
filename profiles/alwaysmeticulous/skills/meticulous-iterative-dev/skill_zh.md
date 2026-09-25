# 使用细致进行迭代式前端开发

在实现多步前端变更时使用此技能。每完成一步，使用细致进行快速本地可视化检查，以便尽早捕获回归和意外副作用。所有步骤完成后，运行完整的云端测试以跨所有记录的会话进行验证。

> 开始之前，运行 `meticulous-cli-update` 技能以确保细致 CLI 和技能是最新版本——除非它已经在此对话早期运行过，在这种情况下可以跳过。

## 前置条件

- 本地开发服务器正在运行（例如 `npm run dev` 或 `pnpm dev`），并将应用程序提供到已知 URL，例如 `http://localhost:3000`
- 已使用细致进行身份验证：运行 `meticulous auth whoami` 通过 OAuth 登录（也可以通过 `METICULOUS_API_TOKEN` 或 `~/.meticulous/config.json` 中的 API 令牌登录）
- 已安装细致 CLI 并在 `PATH` 中（`meticulous-cli-update` 技能会处理此问题）

---

## 每步循环

对变更的每一步重复以下操作。

### 第 1 步 — 实现该步骤的变更

为此步骤进行代码变更。

### 第 2 步 — 查找相关会话

运行：

```bash
meticulous local relevant-sessions
```

如果您已经提交了之前的步骤，并且只想查找仅与该步骤未提交变更相关的会话，请传递最后一个提交的 SHA：

```bash
meticulous local relevant-sessions --startingPointSha=<最后一个提交的sha>
```

有关完整选项参考，请参阅 `meticulous-cli` 技能的 [`local` 参考](../meticulous-cli/references/local.md)。从输出中的每个会话中提取的关键字段：

- **会话 ID** — 在模拟时作为 `--sessionId` 传递
- **基础回放 ID** — 该会话在基础分支上的回放；作为 `--baseReplayId` 传递以进行差异比较。如果该会话从未在基础分支上回放过，则可能不存在。
- **相关性** — `IsRelevant` / `IsRelevantBeta` 表示该会话直接执行了变更的代码。

如果没有返回会话，则变更的代码未覆盖任何记录的会话。继续第 4 步（提交），并依赖最终的云端运行来覆盖。

### 第 3 步 — 模拟和分析

选择 1-2 个最相关的会话（优先选择 `IsRelevant` 而不是 `IsRelevantBeta`）。对于每个会话，使用 `meticulous-simulate-and-diff` 技能，并使用：

- 第 2 步输出中的 `--sessionId` 和 `--baseReplayId`
- `--appUrl=http://localhost:<端口>` 指向您的本地开发服务器
- `--headless`（必需——代理不应操作可见的浏览器）

如果输出中缺少 `baseReplayId`，则省略它；改用该技能的快速检查模式。

还考虑模拟 `local relevant-sessions` 揭示的意外流程的会话——一个覆盖了您未打算更改的代码的会话——以检查意外副作用。

分析完成后，对每个视觉差异进行分类：

- **预期** — 该步骤变更的直接、预期结果。继续。
- **意外** — 不是该步骤目标的视觉变化（包括代码的副作用，即使可以解释）。调查。

**如果意外且原因明确：** 修复代码并重新模拟。

**如果原因不明确：** 使用模拟输出 URL 中的回放 ID 创建一个自包含的 AI 可读调试工作区（见 debug.md）：

```bash
meticulous debug replay <headReplayId> --baseReplayId=<baseReplayId>
```

这两个 ID 都来自模拟输出 URL：头部回放 ID 是 `View simulation at:` URL 的最后一个路径段；基础回放 ID 是模拟命令中使用的 `--baseReplayId`。打开工作区以诊断、修复和重新模拟。

### 第 4 步 — 提交

一旦该步骤的视觉输出正确，提交您的变更：

```bash
git add -p
git commit -m "<对该步骤的简洁描述>"
```

每步提交后，下一次迭代的 `--startingPointSha` 调用将相对于此检查点计算差异，防止先前步骤的变更导致相关会话集膨胀。

返回第 1 步进行下一步。

---

## 所有步骤完成后 — 完整云端测试运行

所有步骤完成后并提交后，运行完整云端测试运行以跨所有记录的会话进行验证（而不仅仅是您本地模拟的 1-2 个会话）：

> 跟随 `meticulous-test` 技能。

云端运行跨完整黄金集会话比较您的分支与基础分支，并报告任何视觉回归。

---

## 最后一步 — 向细致提交反馈

云端测试运行完成后（`meticulous-test`/`meticulous-review` 技能以涵盖运行本身的反馈步骤结束），提交一条简短的反馈笔记关于迭代循环：每步模拟是否尽早捕获了回归，以及什么能让工作流程更简单？

```bash
# CLI
meticulous agent submit-feedback --message="<一到两句话>" --outcome=<helped|neutral|hindered> --skill=meticulous-iterative-dev

# MCP
submit_feedback(message="<一到两句话>", outcome="<helped|neutral|hindered>", skill="meticulous-iterative-dev")
```
