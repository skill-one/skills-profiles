# LaunchDarkly 实验设置

您正在使用一个技能，它将指导您完成在 LaunchDarkly 中设置和运行实验的过程。您的工作是设计实验，使用正确的指标、处理方式和标志配置来创建它，开始数据收集，在需要时在迭代之间调整设计，并最终确定一个获胜者。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-experiment` — 创建一个新的实验及其初始迭代（假设、指标、处理方式和标志配置）。
- `start-experiment-iteration` — 开始为实验的当前草稿迭代收集数据。
- `get-experiment` — 检查实验状态、处理方式、指标和当前迭代。

**可选的 MCP 工具：**
- `list-experiments` — 浏览项目中的现有实验。
- `update-experiment` — 更新实验或其当前迭代的字段。它尊重 `mutableFieldsByStatus`，因此可编辑的内容取决于迭代是 `not_started`、`running` 还是 `stopped`。它会在 `skipped` 下返回拒绝的输入。
- `save-and-start-experiment-iteration` — API 推荐的方式，用于更改正在运行的实验的锁定字段。它会停止当前迭代，创建一个带有所提供字段更新的新草稿，并在一次调用中启动它。
- `stop-experiment-iteration` — 停止正在运行的迭代。您必须声明一个获胜者：传递 `winningTreatmentId`（以及 `winningReason`）。如果没有变体表现优于控制组，则选择基线/控制组为获胜者。
- `list-metrics`, `create-metric`, `list-metric-events` — 管理实验引用的指标。

## 核心概念

### 什么是实验？

LaunchDarkly 中的实验测量功能标志变体对关键指标的影响。一个实验包括：

- **处理方式**：正在比较的标志变体（控制组与测试组）。每个处理方式都有一个 `allocationPercent`；所有处理方式中的值应加起来为 100。
- **指标**：您正在测量的内容（转化率、延迟、收入等）。必须有一个主要指标。
- **标志配置**：驱动实验的目标规则（`flagKey`、`ruleId` 和 `flagConfigVersion`）。
- **迭代**：一个数据收集窗口。在 `not_started` 状态下创建，启动时变为 `running`，结束时转换为 `stopped`。
- **排除组**（可选）：项目级别的用户组，被排除在实验之外以进行基线测量（`holdoutId`）。

### 实验生命周期

1. **创建** 实验及其第一个迭代（`create-experiment`）。
2. **启动迭代** 以开始数据收集（`start-experiment-iteration`）。
3. **监控** 随着数据的积累，结果（`get-experiment`）。
4. **在实验中途调整设计**（如果需要）—— 通过调用 `save-and-start-experiment-iteration` 更改锁定字段（如 `treatments`、`metrics` 或 `methodology`），该调用会停止当前迭代，创建一个带有您更改的新草稿，并启动它。
5. **停止迭代** 当您有一个获胜者或有明确结论时（`stop-experiment-iteration`）。
6. **发布** 获胜变体。

## 核心原则

1. **指标优先**：在创建实验之前，确保您将要引用的指标存在。
2. **清晰的假设**：每个迭代都需要一个 `hypothesis` 字符串；说明您期望改进的内容和程度。
3. **适当的控制组**：必须恰好有一个处理方式具有 `baseline: true`。
4. **足够的样本量**：让迭代运行足够长的时间，以获得统计显著性。
5. **一次只改一个变量**：每个实验测试一个变量，以便进行清晰的归因。

## 工作流程

### 第 1 步：准备指标

1. 使用 `list-metrics` 查找现有指标。
2. 如果需要新的指标，请使用 `create-metric` 并记下其键。
3. 确定哪个是**主要指标**（单个指标或漏斗组）。您将在迭代中传递其键作为 `primarySingleMetricKey` 或 `primaryFunnelKey`。

| 目标 | 指标类型 | 示例键 |
|------|-------------|-------------|
| 转化 | 自定义转化 | `checkout-completed` |
| 性能 | 自定义数值 | `page-load-time-ms` |
| 用户参与度 | 自定义转化 | `feature-clicked` |
| 收入 | 自定义数值 | `order-value` |

### 第 2 步：确定目标规则

您需要驱动实验的标志规则的 `ruleId` 和当前 `flagConfigVersion`。使用 `get-flag` 在标志（或其环境范围的状态）上查找它们。默认降级规则的 ID 是字符串 `"fallthrough"`。

### 第 3 步：创建实验

调用 `create-experiment`。顶层字段描述实验；嵌套的 `iteration` 对象描述第一个数据收集窗口。

```json
{
  "projectKey": "my-project",
  "environmentKey": "production",
  "key": "checkout-flow-v2-experiment",
  "name": "Checkout Flow v2 Experiment",
  "description": "比较重新设计的结账流程与当前流程。",
  "tags": ["growth", "checkout"],
  "methodology": "bayesian",
  "iteration": {
    "hypothesis": "重新设计的结账流程将使完成率提升 3%。",
    "primarySingleMetricKey": "checkout-completed",
    "metrics": [
      { "key": "checkout-completed" },
      { "key": "checkout-time-seconds" }
    ],
    "treatments": [
      {
        "name": "Control",
        "baseline": true,
        "allocationPercent": 50,
        "parameters": [
          { "flagKey": "checkout-flow-v2", "variationId": "variation-a-id" }
        ]
      },
      {
        "name": "New Checkout",
        "baseline": false,
        "allocationPercent": 50,
        "parameters": [
          { "flagKey": "checkout-flow-v2", "variationId": "variation-b-id" }
        ]
      }
    ],
    "flags": {
      "checkout-flow-v2": {
        "ruleId": "fallthrough",
        "flagConfigVersion": 7
      }
    },
    "randomizationUnit": "user"
  }
}
```

有用的可选顶层字段：
- `holdoutId` — 附加现有的排除组。
- `dataSource` — `"launchdarkly"`（默认）、`"snowflake"` 或 `"databricks"`。
- `methodology` — `"bayesian"`（默认）、`"frequentist"` 或 `"export_only"`。
- `analysisConfig` — 设置阈值、多重比较校正或顺序测试。

有用的可选迭代字段：
- `attributes` — 要按其切片结果的上下文属性键数组（例如 `["country", "device"]`）。
- `covariateId` — 分层采样的协变量 CSV ID。
- `canReshuffleTraffic` — 默认为 `true`；设置为 `false` 以在分配更改时将用户锁定到其初始变体。

### 第 4 步：开始数据收集

```json
{
  "projectKey": "my-project",
  "environmentKey": "production",
  "experimentKey": "checkout-flow-v2-experiment"
}
```

在启动之前，API 要求：
- 标志已打开，
- 迭代具有 `randomizationUnit`，
- 至少一个处理方式的 `allocationPercent` 不为零。

如果您在先前迭代停止后重新启动，请传递 `changeJustification`。

### 第 5 步：验证

1. 调用 `get-experiment` 并确认 `currentIteration.status === "running"`。
2. 检查处理方式是否存在并具有预期的分配。
3. 检查指标列表和主要指标。

### 第 6 步：在实验中途调整设计（当需要时）

大多数结构字段（处理方式、指标、方法、假设等）在迭代处于 `running` 状态时是锁定的。更改它们有两种方式：

- **运行时的轻量级编辑** — `update-experiment` 将允许通过任何 `mutableFieldsByStatus` 在 `running` 状态下允许的内容（通常只是元数据，如 `name`、`description`、`maintainerId`、`tags`，以及附加 `metrics`/`attributes`）。它会在 `skipped` 下显示被拒绝的字段及其原因。
- **真正的设计更改** — 调用 `save-and-start-experiment-iteration`。它会停止当前迭代，创建一个带有所提供字段更新的新草稿，并在一次调用中启动它。输入与 `update-experiment` 匹配，加上 `changeJustification`。可变性检查针对 `not_started`，因为更新会落在新的草稿上。

示例：在单个调用中交换处理方式分配并添加一个指标。

```json
{
  "projectKey": "my-project",
  "environmentKey": "production",
  "experimentKey": "checkout-flow-v2-experiment",
  "changeJustification": "现在变体看起来安全，降低控制组分配。",
  "treatments": [
    {
      "name": "Control",
      "baseline": true,
      "allocationPercent": 30,
      "parameters": [{ "flagKey": "checkout-flow-v2", "variationId": "variation-a-id" }]
    },
    {
      "name": "New Checkout",
      "baseline": false,
      "allocationPercent": 70,
      "parameters": [{ "flagKey": "checkout-flow-v2", "variationId": "variation-b-id" }]
    }
  ],
  "metrics": [
    { "key": "checkout-completed" },
    { "key": "checkout-time-seconds" },
    { "key": "checkout-error-rate" }
  ]
}
```

### 第 7 步：停止迭代

当您达到显著性或有明确结论时，停止迭代。**必须有一个获胜的处理方式才能停止**—— LaunchDarkly 不允许您在不声明获胜者的情况下结束迭代。传递获胜处理方式的 ID（在 `get-experiment` 中作为每个处理方式的 `_id` 返回）以及 `winningReason`。

如果实验没有结论或没有变体优于控制组，请将**基线/控制处理方式声明为获胜者**，并在 `winningReason` 中说明（例如，“无结论——没有显著提升，保留控制组”）。没有“无获胜者停止”的路径。

```json
{
  "projectKey": "my-project",
  "environmentKey": "production",
  "experimentKey": "checkout-flow-v2-experiment",
  "winningTreatmentId": "treat-002",
  "winningReason": "两周的数据，主要指标提升 4.1%，PBBL > 95%。"
}
```

**报告结果：**
- 迭代停止，并声明了 `winningTreatmentId`（如果无结论，则为控制组/基线）。
- 主要指标的提升/显著性摘要。
- 下一步行动（发布获胜者、回滚或开始后续迭代）。

## 边缘情况

| 情况 | 操作 |
|-----------|--------|
| 指标不存在 | 首先使用 `create-metric` 创建它。 |
| 标志没有可比较的变体 | 在设计处理方式之前创建标志变体。 |
| 您不知道标志的 `ruleId` / `flagConfigVersion` | 使用 `get-flag` 或 `get-flag-status-across-envs`。默认降级规则的 ID 是字符串 `"fallthrough"`。 |
| 实验已存在 | 使用 `list-experiments` 查找它；`get-experiment` 查看详细信息。 |
| 需要在实验中途更改锁定字段 | 使用 `save-and-start-experiment-iteration`（单次调用）而不是手动停止和重新创建。 |
| `update-experiment` 返回 `skipped` 对于一个字段 | 检查响应中的 `currentStatus` 和 `allowedFields` —— 该字段在当前迭代状态下不可变。要么先停止迭代，要么使用 `save-and-start-experiment-iteration`。 |

## 不要做的事情

- 不要在 `create-experiment` 中省略 `iteration` —— 它是必需的。
- 不要在多个处理方式上设置 `baseline: true`。
- 不要让 `allocationPercent` 值在处理方式之间加起来不为 100。
- 不要在迭代处于 `running` 状态时尝试使用 `update-experiment` 更改锁定的迭代字段 —— 转而使用 `save-and-start-experiment-iteration`。
- 不要提前停止迭代 —— 等待统计显著性。
- 不要在相同标志上同时运行多个实验，而没有仔细设计的排除组。
