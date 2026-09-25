# LaunchDarkly 受保护发布

您正在使用一个技能，它将指导您配置 LaunchDarkly 中的受保护发布。您的工作是设计发布阶段、选择监控指标、配置回归阈值并启动发布。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `start-guarded-rollout` -- 启动带监控的渐进式发布
- `get-flag` -- 检查标志及其变体
- `list-metrics` -- 查找发布期间要监控的指标

**可选的 MCP 工具：**
- `stop-guarded-rollout` -- 立即停止活动发布
- `toggle-flag` -- 确保在启动前标志已开启
- `create-metric` -- 如果指标不存在则创建指标

## 核心概念

### 什么是受保护发布？

受保护发布通过一系列阶段逐步将流量增加到新功能标志变体。在每个阶段，LaunchDarkly 都会监控选定的指标以检测回归。如果检测到回归，发布可以自动暂停并通知团队——甚至可以回滚。

### 关键组件

| 组件 | 描述 |
|-------|-------------|
| **测试变体** | 正在发布的变体 |
| **控制变体** | 现有/基线变体 |
| **阶段** | 流量百分比和监控窗口递增的步骤 |
| **指标** | 用于检测回归的内容（错误率、延迟等） |
| **回归阈值** | 指标在触发操作之前可以降级多少 |
| **发生回归时** | 当阈值被突破时是否通知、回滚或两者都执行 |

### 发布权重单位

发布权重使用千分之几（基点）：
- `1000` = 1%
- `10000` = 10%
- `50000` = 50%
- `100000` = 100%

### 监控窗口

监控窗口以毫秒指定：
- `3600000` = 1 小时
- `86400000` = 24 小时
- `604800000` = 7 天

## 核心原则

1. **从小处开始**：从低百分比（1-5%）开始以尽早发现问题
2. **监控重要内容**：选择反映用户体验的指标
3. **设置现实阈值**：太紧 = 假警报；太松 = 错过回归
4. **留出时间**：每个阶段需要足够的监控时间以显现信号
5. **准备回滚计划**：始终在发生回归时配置至少通知

## 工作流程

### 第 1 步：准备

在启动受保护发布之前：

1. 使用 `get-flag` 检查标志——记下测试和控制变体的 ID
2. 使用 `list-metrics` 查找适合监控的指标
3. 确保在目标环境中标志已**开启**（如有必要，使用 `toggle-flag`）
4. 确认此标志上没有活跃的受保护发布

### 第 2 步：设计阶段

规划发布进程。典型模式：

| 阶段 | 流量 | 监控窗口 | 目的 |
|-------|---------|-------------------|---------|
| 1 | 1% | 1 小时 | 烟雾测试——捕获明显的崩溃 |
| 2 | 10% | 24 小时 | 指标早期信号 |
| 3 | 50% | 24 小时 | 建立信心 |
| 4 | 100% | 24 小时 | 全部发布并监控 |

### 第 3 步：配置指标

选择指示问题的指标：

| 指标类型 | 示例 | 阈值 | 操作 |
|-------------|---------|-----------|--------|
| 错误率 | `api-error-rate` | 0.05 (5% 增加量) | 回滚 |
| 延迟 | `p99-response-time` | 0.2 (20% 增加量) | 通知 |
| 转化率 | `checkout-completed` | 0.1 (10% 减少量) | 通知 + 回滚 |

### 第 4 步：启动发布

使用 `start-guarded-rollout`：

```json
{
  "projectKey": "my-project",
  "flagKey": "new-checkout-flow",
  "environmentKey": "production",
  "testVariationId": "variation-id-for-new-flow",
  "controlVariationId": "variation-id-for-current-flow",
  "randomizationUnit": "user",
  "stages": [
    {"rolloutWeight": 1000, "monitoringWindowMilliseconds": 3600000},
    {"rolloutWeight": 10000, "monitoringWindowMilliseconds": 86400000},
    {"rolloutWeight": 50000, "monitoringWindowMilliseconds": 86400000},
    {"rolloutWeight": 100000, "monitoringWindowMilliseconds": 86400000}
  ],
  "metrics": [
    {
      "metricKey": "api-error-rate",
      "onRegression": {"notify": true, "rollback": true},
      "regressionThreshold": 0.05
    },
    {
      "metricKey": "checkout-completed",
      "onRegression": {"notify": true, "rollback": false},
      "regressionThreshold": 0.1
    }
  ]
}
```

### 第 5 步：验证

1. 使用 `get-flag` 确认受保护发布已激活
2. 检查标志在环境中显示发布配置
3. 监控任何即时回归通知

**报告结果：**
- 受保护发布启动，N 个阶段
- M 个指标被监控
- 第 1 阶段 X% 流量，持续 Y 小时

## 停止发布

如果出现问题或需要停止发布：

```json
{
  "projectKey": "my-project",
  "flagKey": "new-checkout-flow",
  "environmentKey": "production"
}
```

这将立即停止渐进式发布并将标志锁定在其当前状态。

## 边缘情况

| 情况 | 操作 |
|-----------|--------|
| 标志关闭 | 首先使用 `toggle-flag` 开启它——发布需要标志开启 |
| 活动发布存在 | 首先使用 `stop-guarded-rollout` 停止它，然后启动新的发布 |
| 没有合适的指标 | 首先使用 `create-metric` 创建指标 |
| 需要审批 | 如果环境需要审批，工具将返回审批 URL |

## 不要做的事情

- 不要在已关闭的标志上启动受保护发布
- 不要跳过监控窗口设计——急于通过阶段会失去意义
- 不要将回归阈值设置为 0——小的波动是正常的
- 不要忘记配置至少一个指标——没有监控的发布只是常规发布
