# 案例管理技能

一个**案例**将相关的告警事件分组为一个具有状态、优先级、类别和指派者的调查单元。使用此技能检查案例并推动它们通过其生命周期（活跃 → 确认 → 解决 → 关闭）。

## CLI 命令

| 命令 | 目的 |
|---|---|
| `cx cases get <id>` | 通过 ID 获取单个案例 |
| `cx cases update <id> [--title] [--resolution-reason]` | 更新可变字段 |
| `cx cases comment <id> --text <text>` | 向案例时间线添加评论 |
| `cx cases assign <id> --user <email>` | 指派案例（电子邮件，或原始用户 ID） |
| `cx cases unassign <id>` | 移除指派者 |
| `cx cases acknowledge <id>` | 确认（表示您正在处理它；停止重新通知） |
| `cx cases unacknowledge <id>` | 移除确认状态 |
| `cx cases resolve <id> --reason <text>` | 解决案例（不可逆 — 详见下文） |
| `cx cases close <id>` | 关闭案例（最终状态） |
| `cx cases set-priority <id> --priority <P1..P5>` | 覆盖计算出的优先级 |
| `cx cases clear-priority <id>` | 移除优先级覆盖 |
| `cx cases events list <case-id>` | 事件时间线（状态变更、评论、指派） |
| `cx cases events get <event-id>` | 单个事件 — 深入挖掘，例如展开评论线程 |
| `cx cases notifications <case-id> [<case-id> ...]` | 通知交付（连接器、状态、时间） |

## 案例生命周期

```
PENDING_ACTIVATION ──► ACTIVE ◄────────► ACKNOWLEDGED
                         │ ╲                │ ╲
                         │  ╲               │  ╲
                         ▼   ╲              ▼   ╲
                      CLOSED  ╲──► RESOLVED ◄─── (from ACK)
                                       │
                                       ▼
                                    CLOSED  (最终状态)
```

| 从状态 | 允许的转换 | 备注 |
|---|---|---|
| `PENDING_ACTIVATION` | → `ACTIVE` | 系统驱动的激活；不可由用户控制 |
| `ACTIVE` | → `ACKNOWLEDGED`, `RESOLVED`, `CLOSED` | 确认是可选的；对于误报，直接 `close`（跳过 `resolve`） |
| `ACKNOWLEDGED` | → `ACTIVE`, `RESOLVED`, `CLOSED` | 唯一“回退”转换：`unacknowledge` 将其返回到 `ACTIVE` |
| `RESOLVED` | → `CLOSED` 仅 | **不可逆** — 不能重新打开到 `ACTIVE`/`ACKNOWLEDGED` |
| `CLOSED` | (无) | **最终状态** |

类别：`AVAILABILITY` 或 `SECURITY`。优先级：`P1`（最高）→ `P5`。

## 分诊工作流

1. **检查** — `cx cases get <id>`。负载包括 `groupings`、`labels`、`impactedEntities`、`kpiBreaches`、`aiSummary`，以及 `priorityDetails.system`（计算）和 `priorityDetails.override`（用户设置）。
2. **调查** — 通过查询告警的 DataPrime / PromQL 拉取底层遥测数据，在采取行动前找到根本原因。
   可选地通过 `cx olly` 导出调查结果，或拉取案例的 `impactedEntities` / `groupings` 确认影响。
   参考技能 `cx-telemetry-querying`。
3. **认领** — `cx cases assign <id> --user you@example.com` 然后执行 `cx cases acknowledge <id>`。
4. **记录发现** — `cx cases comment <id> --text "<note>"` 将调查笔记留在时间线上（根本原因、链接、下一步计划）。
   评论以 `comment` 事件的形式出现在 `cx cases events list` 中。
5. **解决或关闭** — 详见下文。
6. **重新优先级** 如果影响与计算值不同 — `cx cases set-priority <id> --priority P1` / `clear-priority`。只有在案例仍然打开时才可能；一旦案例为 `RESOLVED` 或 `CLOSED`，优先级就不能被覆盖。

### 解决

解决是**不可逆**的（`RESOLVED` 案例只能移动到 `CLOSED`），因此 CLI 需要同时提供原因和确认：

- 传递 `--reason "<text>"` — 一行事后分析（根本原因、修复方法、后续措施）对团队成员在时间线上可见。仅在确实没有原因时使用 `--no-reason`。
- 在代理 / 非交互模式下，还需要传递 `--yes`；没有它，命令会拒绝，必须由用户交互运行。

如果不确定，请保持在 `ACKNOWLEDGED`（可通过 `unacknowledge` 逆转）直到有信心。对于非解决编辑（标题、事后分析链接），使用 `cx cases update`。

## 批量操作

没有批量端点。要对多个案例采取行动，请将 ID 通过循环传递，例如 `... | jq -r '.[].id' | xargs -I {} cx cases acknowledge {}`。

## 关键原则

- **使用电子邮件，从不使用用户 ID** — 对于 `assign --user` 和所有输出。
- **`resolve` 是不可逆的，`close` 是最终状态** — 解决前确认；对于误报，直接从 `ACTIVE` `close`。
- **始终提供解决原因**，除非 `--no-reason` 真正适用。
- **接受 `P1`-风格缩写** 任何预期优先级/状态/类别的地方。
- **使用 `-p <profile>`（可重复）进行跨环境分诊的多配置分叉**。
- **链接到特定案例** — 构建 `<base>/cases?id=<case_id>`，其中 `<base>` 是 `View in Coralogix: <base>/...` 行中任何 `cx cases` 命令在此会话中打印的控制台 URL — 永远不要自己编造 `<base>`。

## 参考

- 案例分析：[`references/case-analytics.md`](references/case-analytics.md)
- 单个案例调查：[`references/single-case.md`](references/single-case.md)

## 相关技能

- **`cx-alerts`** — 案例中事件背后的告警定义。
- **`cx-slos`** — 驱动可靠性案例的 SLO 定义。
- **`cx-telemetry-querying`** — 从案例受影响实体转换到日志/跨度/指标。
