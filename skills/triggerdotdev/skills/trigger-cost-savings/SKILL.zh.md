---
name: trigger-cost-savings
description: 分析 Trigger.dev 任务、计划及运行情况，以寻找成本优化的机会。在需要减少支出、优化成本、审计使用情况、调整机器规模或审查任务效率时使用。通过 Trigger.dev MCP 工具（list_runs、get_run_details、get_current_worker）结合静态源分析与实时运行分析。
---

# Trigger.dev 成本节约分析

分析任务运行和配置以发现成本降低机会。这项技能结合静态源代码分析与 Trigger.dev MCP 服务器的实时运行分析。

## 开始前：阅读官方指南

权威的、版本固定的成本指导随此技能一同提供。首先阅读它，以确保您的建议与安装的 SDK 版本匹配：

- `@trigger.dev/sdk/docs/how-to-reduce-your-spend.mdx` — 官方的“降低成本”指南（机器尺寸、幂等性去重、并行性、重试、`maxDuration`、检查点等待、防抖）。
- 支持性参考：`@trigger.dev/sdk/docs/machines.mdx`、`runs/max-duration.mdx`、`queue-concurrency.mdx`、`idempotency.mdx`、`triggering.mdx`（防抖+批量）、`errors-retrying.mdx`（`AbortTaskRunError`）。

## 前置条件：MCP 工具

实时运行分析需要 **Trigger.dev MCP 服务器**。验证这些工具是否可用：

- `list_runs` — 带有过滤器（状态、任务、时间段、机器尺寸）列出运行
- `get_run_details` — 获取运行日志、持续时间和状态
- `get_current_worker` — 获取注册的任务及其配置

如果它们不可用，请指示用户安装 MCP 服务器：

```bash
npx trigger.dev@latest install-mcp
```

没有 MCP 工具，您仍然可以进行下方的静态源代码分析；不要编造运行数据。

## 分析工作流程

### 第 1 步：静态分析（源代码）

扫描任务文件以查找：

1. **过大的机器** — 在 `large-1x`/`large-2x` 上的任务没有明确的需要。
2. **缺少 `maxDuration`** — 没有执行时间限制（失控成本风险）。
3. **过多的重试** — `maxAttempts` > 5 且没有 `AbortTaskRunError` 用于已知永久性失败。
4. **缺少防抖** — 高频触发器没有防抖。
5. **缺少幂等性** — 支付/关键任务没有幂等性密钥。
6. **轮询代替等待** — `setTimeout`/`setInterval`/睡眠循环代替 `wait.for()`。
7. **短等待** — `wait.for()` 低于 5 秒（未检查点，浪费计算资源）。
8. **顺序代替批量** — 多个 `triggerAndWait()` 调用可以 `batchTriggerAndWait()`。
9. **过度调度的 cron** — 调度比需要时更频繁地触发。

### 第 2 步：运行分析（需要 MCP 工具）

- **2a. 昂贵的任务** — `list_runs` 过 `period: "30d"`/`"7d"`；查找高总计算量（持续时间 × 数量）、高失败率，以及短持续时间的大型机器（过度配置）。
- **2b. 失败模式** — `list_runs` 带有 `status: "FAILED"`/`"CRASHED"`；区分暂时性（可重试）与永久性；建议 `AbortTaskRunError` 用于后者；估计浪费的重试计算资源。
- **2c. 机器利用率** — 对样本运行使用 `get_run_details`；如果 `large-2x` 任务始终在不到一秒内运行，或者 I/O 密集型（API/数据库），则它是过度配置的。
- **2d. 调度频率** — 使用 `get_current_worker` 列出 cron 模式；标记其目的过于频繁的调度。

### 第 3 步：生成建议

提供按优先级排序的报告，并估计影响：

```markdown
## 成本优化报告

### 高影响
1. **调整 `process-images` 的尺寸** — 目前为 `large-2x`，平均运行 2 秒。`small-2x` 可将此任务的成本降低约 16 倍。
   `machine: { preset: "small-2x" }`  // 之前是 "large-2x"

### 中等影响
2. **防抖 `sync-user-data`** — 每天 847 次运行，通常突发。
   `debounce: { key: \`user-${userId}\`, delay: "5s" }`

### 低影响 / 最佳实践
3. **为 `generate-report` 添加 `maxDuration`** — 未配置超时。
   `maxDuration: 300`  // 5 分钟
```

## 机器预设成本（相对）

更大的机器每秒计算成本按比例更高：

| 预设 | vCPU | RAM | 相对成本 |
|------|------|-----|----------|
| micro | 0.25 | 0.25 GB | 0.25x |
| small-1x | 0.5 | 0.5 GB | 1x（基准） |
| small-2x | 1 | 1 GB | 2x |
| medium-1x | 1 | 2 GB | 2x |
| medium-2x | 2 | 4 GB | 4x |
| large-1x | 4 | 8 GB | 8x |
| large-2x | 8 | 16 GB | 16x |

## 关键原则

- **超过 5 秒的等待是免费的** — 检查点，无计算费用。
- **从小开始，逐步扩展** — 默认的 `small-1x` 对大多数任务都合适。
- **I/O 密集型任务不需要大机器** — API 调用和数据库查询等待网络。
- **防抖在高频任务上节省最多** — 它将突发合并为单个运行。
- **幂等性防止重复计费** — 特别是对于昂贵的操作。
- **`AbortTaskRunError` 停止浪费的重试** — 不要为永久性失败付费。

## 版本

这项技能包含在 `@trigger.dev/sdk` 中，并直接从 `node_modules` 读取，因此它始终与您安装的 SDK 版本匹配（参见旁边的 `package.json`）。完整的成本文档随其一同提供，位于 `@trigger.dev/sdk/docs/` 下。
