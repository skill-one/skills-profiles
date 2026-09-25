# Trigger.dev 成本节约分析

分析任务运行和配置，寻找成本降低机会。这项技能结合静态源代码分析与 Trigger.dev MCP 服务器提供的实时运行分析。

## 开始前：阅读官方指南

权威的、版本固定的成本指导文档随此技能一同提供。请先阅读它，以确保您的建议与安装的 SDK 版本一致：

- `@trigger.dev/sdk/docs/how-to-reduce-your-spend.mdx` — 官方的“降低成本”指南（机器规格、幂等性去重、并行性、重试、`maxDuration`、检查点等待、防抖）。
- 支持性参考：`@trigger.dev/sdk/docs/machines.mdx`、`runs/max-duration.mdx`、`queue-concurrency.mdx`、`idempotency.mdx`、`triggering.mdx`（防抖+批量）、`errors-retrying.mdx`（`AbortTaskRunError`）。

## 前置条件：MCP 工具

实时运行分析需要 **Trigger.dev MCP 服务器**。请验证以下工具是否可用：

- `list_runs` — 带有过滤器（状态、任务、时间段、机器规格）列出运行记录
- `get_run_details` — 获取运行日志、持续时间和状态
- `get_current_worker` — 获取注册的任务及其配置

如果这些工具不可用，请告知用户安装 MCP 服务器：

```bash
npx trigger.dev@latest install-mcp
```

没有 MCP 工具，您仍然可以进行下方的静态源代码分析；不要编造运行数据。

## 分析工作流程

### 第 1 步：静态分析（源代码）

扫描任务文件，查找：

1. **规格过大的机器** — 在 `large-1x`/`large-2x` 上的任务没有明确需求。
2. **缺少 `maxDuration`** — 没有执行时间限制（运行成本失控风险）。
3. **过度重试** — `maxAttempts` > 5 且没有 `AbortTaskRunError`（针对已知永久性失败）。
4. **缺少防抖** — 高频触发任务没有防抖。
5. **缺少幂等性** — 支付/关键任务没有幂等性密钥。
6. **轮询代替等待** — 使用 `setTimeout`/`setInterval`/睡眠循环代替 `wait.for()`。
7. **短等待** — `wait.for()` 小于 5 秒（未检查点，浪费计算资源）。
8. **顺序代替批量** — 多个 `triggerAndWait()` 调用可以改为 `batchTriggerAndWait()`。
9. **过度调度的 cron** — 定时任务比需要时更频繁触发。

### 第 2 步：运行分析（需要 MCP 工具）

- **2a. 昂贵任务** — `list_runs` 过滤 `period: "30d"`/`"7d"`；查找总计算成本高（持续时间 × 数量）、失败率高、以及规格大但持续时间短（过度配置）的任务。
- **2b. 失败模式** — `list_runs` 过滤 `status: "FAILED"`/`"CRASHED"`；区分暂时性（可重试）与永久性；建议对后者使用 `AbortTaskRunError`；估计浪费的重试计算资源。
- **2c. 机器利用率** — 对样本运行使用 `get_run_details`；如果 `large-2x` 任务持续运行不足一秒，或 I/O 密集型（API/数据库），则属于过度配置。
- **2d. 定时任务频率** — 使用 `get_current_worker` 列出 cron 模式；标记其用途与其频率不符的定时任务。

### 第 3 步：生成建议

提供按优先级排序的报告，并估计影响：

```markdown
## 成本优化报告

### 高影响
1. **调整 `process-images` 规格** — 当前为 `large-2x`，平均运行 2 秒。`small-2x` 可将此任务成本降低约 16 倍。
   `machine: { preset: "small-2x" }`  // 原为 "large-2x"

### 中等影响
2. **防抖 `sync-user-data`** — 每日 847 次运行，通常突发性高。
   `debounce: { key: \`user-${userId}\`, delay: "5s" }`

### 低影响 / 最佳实践
3. **为 `generate-report` 添加 `maxDuration`** — 未配置超时。
   `maxDuration: 300`  // 5 分钟
```

## 机器规格成本（相对）

更大规格的机器每秒计算成本按比例更高：

| 规格 | vCPU | RAM | 相对成本 |
|------|------|-----|----------|
| micro | 0.25 | 0.25 GB | 0.25x |
| small-1x | 0.5 | 0.5 GB | 1x（基准） |
| small-2x | 1 | 1 GB | 2x |
| medium-1x | 1 | 2 GB | 2x |
| medium-2x | 2 | 4 GB | 4x |
| large-1x | 4 | 8 GB | 8x |
| large-2x | 8 | 16 GB | 16x |

## 关键原则

- **等待超过 5 秒免费** — 检查点，无计算资源费用。
- **从小开始，逐步扩展** — 默认 `small-1x` 适合大多数任务。
- **I/O 密集型任务不需要大机器** — API 调用和数据库查询依赖网络。
- **防抖在高频任务上效果最佳** — 它将突发合并为单个运行。
- **幂等性防止重复计费** — 特别适用于昂贵操作。
- **`AbortTaskRunError` 停止浪费的重试** — 不要为永久性失败付费。

## 版本

这项技能包含在 `@trigger.dev/sdk` 中，直接从 `node_modules` 读取，因此始终与您安装的 SDK 版本一致（请参考旁边的 `package.json`）。完整的成本文档随其一同提供，位于 `@trigger.dev/sdk/docs/` 下。
