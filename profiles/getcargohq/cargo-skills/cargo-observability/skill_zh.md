# Cargo CLI — 可观测性

**警报**。警报是一个定时的阈值检查。在每次 cron 时间点，它会测量一个**范围**（要监控的内容），将测量值与一个**阈值**（越界条件）进行比较，在越界时触发**动作**——每个动作作为一个独立的运行——并记录一个**事件**。这是 `cargo-diagnostics` 的主动对应部分：诊断是在你注意到故障之后解释故障；而警报会在指标越过界限的瞬间通知你。

所有内容都位于一个 CLI 域下：

```bash
cargo-ai observability alert   …   # 警报的 CRUD + 预览界面
cargo-ai observability event   …   # 警报触发的历史记录
```

## 初始化

已经登录 (`cargo-ai whoami` 返回一个工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送邮件，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在进行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。任何创建运行或批次的操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。警报受 `observability:read` / `observability:write` 权限保护。如果创建/更新/删除返回权限错误，则令牌缺少 `observability:write`——使用管理员令牌或有权限授予 ([`../cargo-workspace-management/SKILL.md`](../cargo-workspace-management/SKILL.md))。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌作用域和管理员专用的界面。

## 每个警报的三个移动部分

| 部分 | 标志 | 是什么 |
| --- | --- | --- |
| **范围** | `--scope <json>` | *要测量什么*——六种来源之一：`spans`、`runs`、`records`、`orchestrationQuery`、`storageQuery`、`model`。 |
| **阈值** | `--threshold <json>` | *何时越界*——一个 `metric` + `operator` (`gte`/`lte`) + `value`。指标菜单取决于范围。 |
| **动作** | `--actions <json>` | *越界时发生什么*——一个 `Action[]`（连接器 / 工具 / 代理 / 原生节点），每个动作作为一个独立的运行触发。可选；省略以创建一个静默警报，其越界事件从其事件中读取。 |

范围和阈值是一对**匹配**——一个指标只能在其产生的范围内计算（例如 `errorRate` 需要遥测，`freshness` 需要模型）。完整的兼容性矩阵、每个指标的含义和单位、每个范围过滤字段都在 **[`references/scopes-and-thresholds.md`](references/scopes-and-thresholds.md)** 中——在编写未使用过的 `--scope`/`--threshold` 对之前阅读它。

## 金科玉律：`preview` 之后再 `create`

`alert preview` 会立即评估范围 + 阈值**，不触发动作或写入事件**。它返回警报将测量的值以及该值是否越界——因此你可以根据实际情况校准阈值而不是猜测，并在提交到计划之前确认范围/阈值配对是否有效。

```bash
cargo-ai observability alert preview \
  --scope '{"kind":"runs","workflowUuid":"<uuid>","statuses":["error"]}' \
  --threshold '{"metric":"errorRate","operator":"gte","value":10}' \
  --window-minutes 1440          # 最后 24 小时；默认 60
```

- `outcome: "computed"` → `{ value, total, failed, isBreached }`。从 `value` 设置你的阈值。
- `outcome: "empty"` → 时间窗口内没有可测量的内容（参见 `references/alert-lifecycle.md` 中的空值规则）。
- `outcome: "notComputed"` → `{ errorMessage }`。一个坏的 SQL 查询、一个已删除的模型或一个**无效的范围/阈值配对**都会导致此结果——在创建前修复它。

`--window-minutes` 仅适用于遥测范围 (`spans`/`runs`/`records`)。一个 `model` 是根据其当前状态测量的；一个查询范围在其 SQL 中自己窗口化。

**始终先预览**。它是免费的，是正确调整阈值唯一的方法，并且可以在它成为写入每个时间点 `error` 事件的计划之前捕获无效配对。

## 命令

所有命令输出 JSON。读取需要具有 `observability:read` 的令牌；创建/更新/删除需要 `observability:write`（管理员令牌具有两者；普通成员令牌可能没有——参见 Bootstrap 部分）。

### 创建警报

```bash
cargo-ai observability alert create \
  --name "CRM 同步错误率" \
  --description "当 HubSpot 同步开始失败时显示页面" \
  --cron "*/30 * * * *" \
  --scope '{"kind":"runs","workflowUuid":"<workflow-uuid>","statuses":["error"]}' \
  --threshold '{"metric":"errorRate","operator":"gte","value":10}' \
  --actions '[{"kind":"agent","agentUuid":"<agent-uuid>","config":{"message":"{{alert.name}} breached: {{event.value}}% errors. {{alert.url}}"}}]'
```

- `--cron` — 5 字段 cron **或** `@every <interval>`（例如 `@every 30m`），始终 **UTC**，最多每分钟一次。UI 预设的底部为 30 分钟；更紧密的间隔只有在有理由时才使用（每个时间点扫描 ClickHouse 并可以触发付费运行）。
- `--disabled` — 创建时暂停（直到你 `update --enabled true` 之前不评估任何内容）。
- `--folder <uuid>` — 将其归档到文件夹（来自 `cargo-workspace-management`）。
- `--actions` — 可选。省略以创建一个静默警报。每个条目是一个**配置好的**动作：与 `orchestration action execute` 不同，后者没有任何 `config`，警报动作**需要**一个——模板消息就存在于其中。配置是针对触发上下文 (`{{alert.*}}`, `{{event.*}}`) 进行模板化的——参见 [`references/alert-lifecycle.md`](references/alert-lifecycle.md) 获取完整变量列表。每个动作的目标 (`agentUuid`/`toolUuid`/`connectorUuid`) 在创建时进行验证以存在于工作区中。

### 列出、获取、更新、删除

```bash
cargo-ai observability alert list                      # 所有警报，每个警报及其最后事件
cargo-ai observability alert get <uuid>                # 一个警报 + 其最后事件

cargo-ai observability alert update --uuid <uuid> \
  --enabled false                                      # 暂停它 (true/false —— 必须是字面量)
cargo-ai observability alert update --uuid <uuid> \
  --threshold '{"metric":"errorRate","operator":"gte","value":20}'   # 提高门槛
cargo-ai observability alert update --uuid <uuid> \
  --description none                                    # "none" 清除；--folder none 取消归档

cargo-ai observability alert remove <uuid>
```

`--enabled` 是严格的：只有字面量 `true` 或 `false` 被接受——`--enabled yes` 会被拒绝而不是静默禁用警报。在 `update` 时，任何省略的标志都保持不变；`--description none` / `--folder none` 是明确的“清除它”咒语。

### 检查触发历史

```bash
cargo-ai observability event list <alertUuid>          # 最新评估事件，最新优先
```

每个事件都包含 `status` (`healthy` / `unhealthy` / `error`)、测量的 `value`、触发时的 `scope`/`threshold`/`actions` 的**快照**（警报之后可以更改）、`runUuids`（动作触发的运行——将这些传递给 `cargo-diagnostics` 或 `orchestration run get`）、评估窗口和 `errorMessage`（对于 `error` 事件）。`unhealthy` = 越界并触发；`error` = 指标无法计算。

## 评估实际工作原理

生命周期——cron 窗口和 ClickHouse 索引延迟、**最多一次**触发保证（警报不会在同一行重新触发；持续越界会在下一个时间点重新检测）、空窗口与实际零规则使 `lte` 成为死锁开关，以及完整的 `{{alert.*}}`/`{{event.*}}` 模板化上下文——在 **[`references/alert-lifecycle.md`](references/alert-lifecycle.md)** 中记录。在依赖警报进行任何时间敏感操作之前阅读它。

## 实用配方

**[`references/examples/recipes.md`](references/examples/recipes.md)** — 复制粘贴起点：错误率分页器、信用预算保护、P95 延迟监控、一个**死锁开关**（`count lte 0`——当工作流*停止*运行时触发警报）、模型新鲜度 / 空模型警报，以及一个自定义 SQL 查询警报。

## 声明式替代方案：`defineAlert` (CDK)

这个技能是**命令式**界面——一次性的 `cargo-ai observability alert …` 调用。要**以代码管理**警报（在 git 中、可重复、与被监控的工作流一起部署），请使用 CDK 的 `defineAlert` 构建器——参见 [`../cargo-project/SKILL.md`](../cargo-project/SKILL.md) 和路由器中的“声明式 vs 命令式”。相同的范围/阈值/动作模型；不同的编写模式。

## 成本纪律

警报的**动作作为实际运行触发**——如果动作调用付费连接器动作或代理，每次越界都会重新计费。一个过小的阈值在紧密的 cron 下可能会每分钟越界（并计费）。有两个保护措施：

- **预览以调整阈值**，使其在真实异常时触发，而不是正常波动。
- 如果动作节点调用**基于计分的提供者动作**，将其像任何计划付费工作流一样对待：阅读该提供者的剧本（尤其是其 *定期使用* 部分）在 `../cargo-gtm/provider-playbooks/`，并应用 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) 中的支出规则。优先选择廉价通知动作（一个向 Slack 发送消息的代理、一个连接器通知）而不是任何分叉的动作。

## 当 CLI 让你惊讶时

如果文档中记录的标志、范围字段或响应形状与你的观察不符（可能已经发布了修复程序，或者文档可能已经漂移），重新刷新 CLI 和技能；如果仍然无法解释，请提交报告——团队会阅读它：

```bash
cargo-ai workspaceManagement report create \
  --title "<一句话总结>" \
  --description "<精确的命令、errorMessage 原文、预期与实际、UUIDs>"
```

## 展示结果

遵循 [`../cargo/references/interaction.md`](../cargo/references/interaction.md)：以结果开头（“警报已创建，当 CRM 同步的错误率达到 10% 时将通知值班代理”），将警报或其事件总结为紧凑表格，永远不要将原始 `alert get` / `event list` JSON 投入对话。
