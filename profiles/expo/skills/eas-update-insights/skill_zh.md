# EAS 更新洞察

> **EAS 服务 - 适用费用。** 洞察涵盖通过 EAS Update 发布的更新，这是一个付费的 Expo 应用服务产品，具有免费层级限制。更新交付和这些命令背后的数据计入您计划的 EAS Update 使用量。请查看 https://expo.dev/pricing。

直接从 CLI 查询已发布的 EAS Update 的健康状况：启动次数、失败启动次数、崩溃率、独立用户数、有效载荷大小、每个渠道的嵌入式与 OTA 用户分割，以及每个运行时版本的最受欢迎更新。这些数据与 expo.dev 上更新和渠道详情页面使用的是相同的数据；这些命令将其以人类可读和 JSON 格式在终端中展示。

## 使用此技能的时机

当用户想要评估已发布的 EAS Update 的健康状况或采用情况时使用：崩溃率、安装次数、独立用户数、捆绑包大小，或某个渠道上嵌入式与 OTA 用户的分割情况。

示例提示：

- "最新更新表现如何？"
- "最新更新是否健康？"
- "新发布的崩溃是否比上一个版本更多？"
- "最新更新与嵌入式构建的用户数量是多少？"
- "目前生产环境中哪个更新最受欢迎？"
- "我们的更新捆绑包有多大？"

也适用于：发布后发布监控和回归检测。

当用户需要每个用户的崩溃详情或设备级报告时，不要使用此技能；此技能仅公开 EAS 汇总指标。

## 前置条件

- 安装 `eas-cli` (`npm install -g eas-cli`)。
- 登录：`eas login`。
- 对于 `channel:insights`：从 Expo 项目目录运行（该命令从 `app.json` 中解析项目 ID）。`update:insights` 仅需要登录。

## 命令概览

| 命令 | 目的 |
|---|---|
| `eas update:list` | 发现最近的更新组、它们的 `group` ID 和分支名称 |
| `eas update:insights <groupId>` | 每个平台的启动次数、失败启动次数、崩溃率、独立用户数、有效载荷大小、每日细分 |
| `eas update:view <groupId> --insights` | 更新组详情 + 相同指标追加 |
| `eas channel:insights --channel <name> --runtime-version <version>` | 嵌入式/OTA 用户数量、最受欢迎的更新、渠道 + 运行时的累积指标 |

所有这些都支持 `--json --non-interactive` 以便程序化解析。

## 发现 ID

在查询更新组的洞察之前，您需要它的 `group` ID。使用 `eas update:list` 并使用 `--branch <name>`（该分支上的更新）或 `--all`（所有分支上的更新）。在非交互式运行时始终传递 `--json --non-interactive`；如果没有分支/`--all` 标志，该命令将提示选择分支：

```bash
# 所有分支的最新组 ID
eas update:list --all --json --non-interactive | jq -r '.currentPage[0].group'

# 特定分支上的最新组 ID
eas update:list --branch production --json --non-interactive | jq -r '.currentPage[0].group'
```

JSON 响应有一个 `currentPage` 数组，其中包含每个更新组的条目（同一发布的两个平台合并为一个条目）：

```json
{
  "currentPage": [
    {
      "branch": "production",
      "message": "\"修复结账崩溃\" (1 周前由某人)",
      "runtimeVersion": "1.0.6",
      "group": "03d5dfcf-736c-475a-8730-af039c3f4d06",
      "platforms": "android, ios",
      "isRollBackToEmbedded": false
    }
  ]
}
```

条目还携带 `codeSigningKey` 和 `rolloutPercentage`，但仅当这些功能在组中使用时才包含（未定义的值从 JSON 输出中省略）。

使用 `--branch <name>` 调用时，响应还包括顶层级的 `name`（分支名称）和 `id`（分支 ID）。

## `eas update:insights <groupId>`

显示单个更新组的启动次数、失败启动次数、崩溃率、独立用户数、启动资产数量和平均有效载荷大小，按 **每个平台**（iOS、Android）细分，以及每日启动和失败的细分。

### 基本用法

```bash
eas update:insights 03d5dfcf-...
```

### 标志

| 标志 | 描述 |
|---|---|
| `--days <N>` | 回溯 N 天。默认：**7**。与 `--start`/`--end` 互斥。 |
| `--start <iso-date>` / `--end <iso-date>` | 明确的时间范围，例如 `--start 2026-04-01 --end 2026-04-15`。 |
| `--platform <ios\|android>` | 筛选到单个平台。省略以查看组中的所有平台。 |
| `--json` | 机器可读输出。隐含 `--non-interactive`。 |
| `--non-interactive` | 脚本时需要。 |

### JSON 输出形状

顶层：`groupId`、`timespan`（`start`、`end`、`daysBack`），以及 `platforms[]`，其中包含每个组发布的平台的一个条目。每个平台条目有 `updateId`、`totals`（`uniqueUsers`、`installs`、`failedInstalls`、`crashRatePercent`）、`payload`（`launchAssetCount`、`averageUpdatePayloadBytes`），以及一个 `daily[]` 时间序列 `{ date, installs, failedInstalls }`。

有关完整模式和字段参考，请参阅 [references/update-insights-schema.md](./references/update-insights-schema.md)。

对健康评估重要的字段：

- `platforms[].totals.crashRatePercent`，计算为 `failedInstalls / (installs + failedInstalls) * 100`。没有安装时为零。
- `platforms[].totals.installs` 和 `uniqueUsers` 提供采用信号。
- `platforms[].daily` 是一个时间序列，用于发现失败的突然激增。

### 错误

- `Could not find any updates with group ID: "<id>"` — 组不存在或您没有访问权限。
- `Update group "<id>" has no ios update (available platforms: android)` — 使用了 `--platform ios`，但该组没有发布 iOS 版本。
- `EAS Update insights is not supported by this version of eas-cli. Please upgrade ...` — 服务器弃用了一个 CLI 依赖的字段。运行 `npm install -g eas-cli@latest`。

## `eas update:view <groupId> --insights`

扩展标准的 `update:view` 输出，追加相同的按平台洞察，内联显示。

```bash
# 人类可读
eas update:view 03d5dfcf-... --insights
eas update:view 03d5dfcf-... --insights --days 30

# JSON：作为 { updates: [...], insights: {...} } 包装
eas update:view 03d5dfcf-... --json --insights
```

不使用 `--insights` 时，`update:view` 的行为与之前完全相同——现有消费者不会改变 JSON 形状。`--days` / `--start` / `--end` 标志仅在设置 `--insights` 时适用；单独传递它们会报错。

## `eas channel:insights --channel <name> --runtime-version <version>`

显示每个渠道，嵌入式构建和 OTA 更新的用户数量，以及哪些更新正在拉动最多流量。必须从 Expo 项目目录运行。

### 基本用法

```bash
eas channel:insights --channel production --runtime-version 1.0.6
```

### 标志

| 标志 | 描述 |
|---|---|
| `--channel <name>` | **必需。** 渠道名称（例如 `production`、`staging`）。 |
| `--runtime-version <version>` | **必需。** 与发布的完全匹配。检查 `update:list` 中的 `runtimeVersion` 值。 |
| `--days <N>` | 回溯 N 天。默认：**7**。 |
| `--start` / `--end` | 明确的时间范围，如 `update:insights`。 |
| `--json` / `--non-interactive` | 机器可读输出。 |

### JSON 输出形状

顶层：`channel`、`runtimeVersion`、`timespan`、`embeddedUpdateTotalUniqueUsers`、`otaTotalUniqueUsers`、`mostPopularUpdates[]`（每个带有 `rank`、`groupId`、`message`、`platform`、`totalUniqueUsers`），`cumulativeMetricsAtLastTimestamp[]`，以及 `uniqueUsersOverTime` 和 `cumulativeMetricsOverTime` 对象，带有 `labels` 和 `datasets`。

有关完整模式和字段参考，请参阅 [references/channel-insights-schema.md](./references/channel-insights-schema.md)。

重要的字段：

- `embeddedUpdateTotalUniqueUsers` 是运行嵌入式（二进制捆绑）构建的用户数量。
- `mostPopularUpdates[]` 是按 `totalUniqueUsers` 排序的更新。**注意**：这是服务器返回的顶级-N；`otaTotalUniqueUsers` 是该列表的总和，如果活动更新超过顶级-N，可能会低估总 OTA 覆盖范围。
- `uniqueUsersOverTime` 和 `cumulativeMetricsOverTime` 是每日数据序列，用于图表。

### 错误

- `Could not find channel with the name <name>` — 拼写错误或错误账户。
- "在表格中没有记录更新启动" / JSON 中的 `mostPopularUpdates` 为空 — 尚未为该渠道 + 运行时启动 OTA 更新。通常意味着该渠道仍在仅服务嵌入式构建。

## 常见工作流

### 验证我刚刚发布的更新是否健康

```bash
# 1. 获取 production 上的最新发布
GROUP_ID=$(eas update:list --branch production --json --non-interactive \
  | jq -r '.currentPage[0].group')

# 2. 给它一些采用时间（分钟到小时），然后检查崩溃率
eas update:insights "$GROUP_ID" --json --non-interactive \
  | jq '.platforms[] | {platform, installs: .totals.installs, crashRate: .totals.crashRatePercent}'
```

比较跨平台的 `crashRate` 与之前的发布；突然的激增或非对称行为（iOS 激增而 Android 平坦，反之亦然）是调查的信号。

### 比较两个渠道之间的采用情况

```bash
for channel in production staging; do
  echo "--- $channel ---"
  eas channel:insights --channel "$channel" --runtime-version 1.0.6 --json --non-interactive \
    | jq '{
        channel,
        embedded: .embeddedUpdateTotalUniqueUsers,
        ota: .otaTotalUniqueUsers,
        topUpdate: .mostPopularUpdates[0]
      }'
done
```

### 检测过去 24 小时内的发布回归

```bash
eas update:insights "$GROUP_ID" --days 1 --json --non-interactive \
  | jq '.platforms[] | select(.totals.crashRatePercent > 1)'
```

### 为发布说明总结组指标

```bash
eas update:view "$GROUP_ID" --insights --days 30
```

人类可读的组详情加上 30 天的每个平台的启动/失败——适合粘贴到变更日志或事件回顾中。

## 输出技巧

- 将 JSON 通过 `jq`；有效载荷结构便于过滤。
- `--json` 隐含 `--non-interactive`，但显式传递两者更脚本化。
- `daily[].date` 中的日期是 UTC ISO 时间戳；人类可读表格将它们渲染为 `YYYY-MM-DD`（UTC）。
- CLI 表格标签说 "启动" / "崩溃" 而 JSON 使用 `installs` / `failedInstalls`。相同字段，不同显示名称。

## 限制

- **跨平台的独立用户数** 可能会重复计算在 iOS 和 Android 上运行相同发布的学生。相同的注意事项适用于渠道洞察中的 `otaTotalUniqueUsers`，如果活动更新超过顶级-N，可能会低估总 OTA 覆盖范围。
- **新发布** 在指标管道追赶上可能会在短时间内显示零。
- **安装是下载，不是启动**：`installs` / "启动" 字段计算下载了清单和启动资产的用户。确认运行仅在用户下次更新检查时注册（通常最多 24 小时后，具体取决于应用程序的更新策略）。因此，指标稍微滞后于实际状态。
- **崩溃是自我报告的**：`failedInstalls` / "崩溃" 计算在安装/启动期间出错并在下次更新检查中报告的更新。不会触发更新请求的崩溃（例如进程在恢复前被杀死）不会出现。

## 提交反馈
如果您在此技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-update-insights" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含相关的上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
