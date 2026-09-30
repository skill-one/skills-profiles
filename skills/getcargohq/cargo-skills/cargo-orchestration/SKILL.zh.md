---
name: cargo-orchestration
description: 让 Cargo 真正运行某些操作，或展示其将要运行的内容——执行一个连接器操作、运行多步骤工作流、触发整个分段或模型的批处理、向 AI 代理发送消息、构建或编辑节点图、绘制工作流、工具或以图表形式播放，并使用 SQL 查询运行时表（运行、批处理、跨度、记录）。触发器："在我的所有联系人上运行这个"、"执行该操作"、"启动批处理"、"构建工作流"、"安排播放"、"让它每天早上运行"、"询问代理"、"展示工作流"、"这个工具做什么"、"可视化这个播放"、"绘制图表"、"解释这个工作流"、"今天有多少运行失败"、"这个操作的输出模式是什么"、"添加一个步骤"。跳过情况：解释运行为何表现异常——使用 cargo-diagnostics；下载结果文件——使用 cargo-analytics；将工作流作为代码提交——使用 cargo-project。
---

# Cargo CLI — 协调

Cargo 平台的运行时操作。

**你想运行什么？**

```
需要运行某件事？
├── 还不知道操作方式    → action list <关键词>
├── 一个操作，一条记录   → action execute
├── 一个操作，多条记录   → action execute-batch
├── 多个操作串联
│   ├── 一次性/临时     → run create --nodes (一条记录)
│   │                              batch create --nodes (多条记录)
│   └── 可重复的工作流   → 先创建一个工具，然后 run create --workflow-uuid
│                                  或 batch create --workflow-uuid
├── 对话式 AI 代理     → message create
└── 测试你正在构建的工作流中的一个节点  → node execute (仅调试 — 见下文)
```

> **跨多条记录分发 (`action execute-batch`, `batch create`)？先采样。** 运行 10-20 条记录，报告观察到的成本和命中率，然后请求用户批准完整注册 — 引用**记录数量**和**信用估计**。参见 [创建批次 → 采样门控](#the-sample-gate)。

> **每个节点执行成本为 0.01 信用 — 每 100 个 1 信用 — 无论节点是什么。**
> `branch`, `filter`, `switch`, `variables` 和其他不携带提供者价格，但不是免费的：收费按*执行*计算，所以一个图的成本有两项，
> `(提供者成本 × 记录) + (节点 × 记录 ÷ 100)`。在步骤密集、操作轻量级的工作图中第二项占主导。它不出现在**没有**按节点字段 — 不是 `executions[].creditsUsedCount`，不是 `spans.execution_credits_used_count` — 只在 `billing usage get-metrics --unit orchestration.executions` 中出现。
> 在批准消息中引用这两项 ([`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) §1)。

> **在手动编写 JSON 之前找到操作。** `cargo-ai orchestration action list <keywords>` 一次性搜索集成目录、Cargo 原生操作、工作空间工具和代理 — 免费、不运行任何操作 — 每个结果都带有可粘贴的 `action` 对象（`connectorUuid` 已填写），操作的**信用成本**及其自动完成缩写。使用 `--kind connector|native|tool|agent`, `--integration-slug <slug>`, `--limit`（默认 20，最大 50）进行缩小。`unknown command` 表示 CLI 早于它出现 — 刷新。

> **默认运行某件事是 `action execute`，不是 `node execute`。**
> `node execute` 是已存在于工作流中的节点的**调试**界面：需要 `--workflow-uuid`, `--release-uuid`, `--node`, `--computed-config`
> **和** `--context`（全部五个，客户端强制执行），并像任何实时调用一样计费。如果你只是想获取操作的输出 — 富化域、调用连接器操作、调用工具或代理 — 使用 `action execute` / `action execute-batch` 带有小的 `--action` + `--data` 负载。只有在验证完整图之前单个节点的行为时才使用 `node execute`。

> **术语：** 协调**工具**是保存的按需工作流（通过 `tool list` 列出）。**操作**是无需构建工作流即可执行的单个操作 — 它可以嵌入保存的协调工具 (`kind: "tool"`), 调用第三方连接器 (`kind: "connector"`), 调用 AI 代理 (`kind: "agent"`), 或运行内置平台操作 (`kind: "native"`)。

> **组合节点图？按此顺序从专用操作+表达式构建：**
> 1. **专用操作。** 首先使用 `action list <keywords>`（免费）：连接器操作、原生操作 (`agent`, `modelUpsert`, `branch`, `group`…), 工具。
> 2. **用于粘合的表达式。** 它是需要在需要值的字段中的内联 JavaScript：重塑、有效载荷、条件、数组。
> 3. **HTTP**，如果第 1 步未为该 API 找到操作。
> 4. **`script` 节点**，如果逻辑无法适应表达式。
>
> 参见 **`references/node-selection.md`**。

> **展示图，不要描述它。** 在部署草稿之前，以及每当用户询问工作流或 play 的作用时，绘制它：
> `cargo-ai orchestration node diagram --workflow-uuid <uuid> --format ascii --raw`
> （免费、不运行任何操作；`--format` 需要 CLI ≥ 1.0.56，命令本身 ≥ 1.0.54）。
> 路由、回退边和计费步骤是用户实际批准的内容，而文字会淡化所有这三者。**根据输出去向选择格式：** `ascii` 渲染人可以在终端或聊天回复中阅读的图片；`mermaid`（默认）是源代码，仅在粘贴到 PR、文档或渲染它的页面时正确。来源、ASCII 图例、成本标记和重复缩写枪：**`references/node-diagram.md`**。

**参考资料：**

> `references/examples/actions.md` — action execute 和 execute-batch 示例
> `references/examples/tools.md` — 工具（按需工作流）示例
> `references/examples/plays.md` — play（分段驱动自动化）示例
> `references/examples/agents.md` — AI 代理聊天示例
> `references/examples/templates.md` — 预构建工作流模板
> `references/examples/queries.md` — `orchestration query execute`（ClickHouse：运行/批次/跨度/记录）SQL 示例。对于 `storage query`（工作空间存储），请参阅 `cargo-storage` 技能。
> `references/examples/segments.md` — 分段获取和过滤示例
> `references/nodes.md` — 完整节点创建指南（种类、原生操作、表达式、验证、路由）
> `references/node-diagram.md` — **绘制节点图作为 Mermaid 流程图** (`node diagram`)：每个来源（工作流 / 草稿 / 发布 / 运行 / 原始节点），标记付费节点，突出显示失败节点，以及为什么图表基于 `uuid` 而不是 `slug`
> `references/node-selection.md` — **按专用操作+表达式构建**（操作 → 表达式 → HTTP → `script`，按此顺序）：表达式是内联 JavaScript，逻辑去向（一个字段内联、共享的 `variables` 节点或 `script`），优先选择原生操作而不是代码/HTTP，以及表达式陷阱（静默空路径、ISO 字符串作为 `Date` 到达、使用 `expression eval` 进行测试）
> `references/filter-syntax.md` — 完整过滤条件参考
> `references/polling.md` — 异步轮询模式、错误处理、重试策略
> `references/response-shapes.md` — 完整 JSON 响应结构
> `references/troubleshooting.md` — 常见错误，以及针对成功但输出错误的运行（分支路由、下游值空）“调试工作流运行”部分（运行成功但输出错误）

> **事后诊断？** 对于基于这些界面的有序法医运行簿 — 追踪一次运行、按根本原因分组扫描批次错误、分析 play 的信用支出 — 加载 [`cargo-diagnostics`](../cargo-diagnostics/SKILL.md) 技能。

## 引导

已登录 (`cargo-ai whoami` 返回工作空间)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送邮件代码，无需浏览器；首次使用时创建帐户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入之前确认活动工作空间
```

每个命令将 JSON 打印到标准输出；失败时以非零状态退出，并带有 `{"errorMessage": "..."}`。创建运行或批次的任何操作都是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装时，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 添加 CLI 版本固定、令牌范围和仅管理员界面。

## 首先发现资源

大多数命令需要 UUID。始终在行动前发现它们。

```bash
cargo-ai orchestration action list <query>  # 连接器、原生、工具、代理中的操作 (+ 信用)
cargo-ai orchestration play list            # 所有 play（名称、workflowUuid、modelUuid、segmentUuid）
cargo-ai orchestration tool list            # 所有工具（名称、workflowUuid、描述）
cargo-ai orchestration workflow list        # 所有工作流（仅 uuid — 无名称）
cargo-ai orchestration template list       # 所有工作流模板（slug、名称、种类）
cargo-ai ai agent list                     # 所有代理（uuid、名称）
cargo-ai ai template list                  # 所有 AI 代理模板（slug、名称、languageModelSlug）
cargo-ai storage model list                # 所有模型（uuid、名称、slug、列）
cargo-ai storage dataset list              # 所有数据集
cargo-ai segmentation segment list         # 所有分段（uuid、名称、modelUuid）
cargo-ai connection connector list         # 所有连接器
```

**Play 与工具：** 两者都由工作流支持。**Play** 是分段驱动自动化 — 它对分段中的数据变化做出反应（添加、更新、删除记录）。**工具** 是按需工作流 — 手动触发、通过 API 触发或按 cron 时间表触发。工作流没有 `name` 字段；使用 `play list` 或 `tool list` 找到名称并提取 `workflowUuid`。

**在 UI 中获取：** play 位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/plays/<PLAY_UUID>`，工具位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/tools/<TOOL_UUID>`。从 `cargo-ai whoami` 下的 `workspace.uuid` 获取 `<WORKSPACE_UUID>`。

**设计新的工具或 play？** 首先检查模板 — 它们是常见自动化模式（富化管道、CRM 同步、潜在客户评分）的预构建节点图，并且是极好的起点。使用 `cargo-ai orchestration template list` 列出模板，并使用 `cargo-ai orchestration template get <slug>` 检查特定模板。模板按 `kind` 标记，因此你可以立即找到适合工具 (`"kind":"tool"`) 或 play (`"kind":"play"`) 的模板。参见 `references/examples/templates.md` 获取完整指南。

**兼容性规则：**

- **`run create`** — 仅适用于 **工具** 工作流（或无 `workflowUuid`）。Play 工作流返回 `playNotCompatible`。
- **`batch create`** — 允许的数据类型取决于工作流类型：
  - **Play** 工作流：`filter`, `recordIds`, `segment`, `change`。使用 `filter` 触发 play；`segment` 只接受独立分段，从不接受 `play list` 中的 `segmentUuid`。
  - **工具** 工作流（或无 `workflowUuid`）：`file`, `records`

## 快速参考

```bash
# 查找操作（免费 — 无运行、无信用）
cargo-ai orchestration action list enrich company          # 所有种类
cargo-ai orchestration action list --kind tool             # 此工作空间的工具
cargo-ai orchestration action list send --kind connector --integration-slug slack

# 单个操作
cargo-ai orchestration action execute --action '{"kind":"tool","toolUuid":"<uuid>"}' --data '{"domain":"acme.com"}'
cargo-ai orchestration action execute-batch --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' --records '[{...},{...}]'
cargo-ai orchestration action get-output-schema --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' # → {"schema": <JSON Schema>} 而不执行

# 工作流（串联多个操作）
cargo-ai orchestration run create --workflow-uuid <uuid> --data '{"company":"Acme","domain":"acme.com"}'
cargo-ai orchestration run create --data '{"domain":"acme.com"}' --nodes '[...]'
cargo-ai orchestration batch create --workflow-uuid <uuid> --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}'

# AI 代理
cargo-ai ai message create --chat-uuid <uuid> --parts '[{"type":"text","text":"..."}]'

# 数据
cargo-ai orchestration query execute "SELECT count() FROM runs WHERE status='error'" # ClickHouse: spans, runs, batches, records
cargo-ai segmentation segment fetch --model-uuid <uuid> --filter '{"conjonction":"and","groups":[]}' --fetching-limit 100
# 对工作空间存储（公司、联系人、…）进行 SQL 查询，请参阅 cargo-storage 技能：`storage query execute`
```

## 轮询异步操作

所有操作都是异步的。要么轮询直到终端状态，要么传递 `--wait-until-finished` 以阻塞。

`action execute` 返回运行。`action execute-batch` 返回批次。它们以相同的方式轮询：

| 结果类型     | 轮询命令         | 间隔 | 完成时                                      |
| --------------- | -------------------- | -------- | ---------------------------------------------- |
| 运行             | `run get <uuid>`     | 2s       | `status` 是 `success`, `error`, 或 `cancelled` |
| 批次           | `batch get <uuid>`   | 5s       | `status` 是 `success`, `error`, 或 `cancelled` |
| 代理消息       | `message get <uuid>` | 2s       | `status` 是 `success` 或 `error`               |

对于长运行批次（1000+ 记录），在第一分钟后将间隔增加到 10-15s。

## 执行操作

运行单个操作 — 无需工作流或节点图。

### 首先找到它 — `action list`

```bash
cargo-ai orchestration action list enrich company          # 所有种类
cargo-ai orchestration action list --kind tool             # 此工作空间的工具
cargo-ai orchestration action list send --kind connector --integration-slug slack
```

免费，不执行任何操作。所有查询术语必须匹配（AND）；操作 slug 或名称的命中排名高于集成，集成排名高于描述。
返回 `{query, totalMatches, results[]}`，其中每个结果都带有可粘贴的 `action` 对象（`connectorUuid` 已填写），操作的**信用成本**及其自动完成缩写。默认返回 20 个结果，最大 50 个。

```bash
# 一个操作，一条记录 → 返回运行
cargo-ai orchestration action execute \
  --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' \
  --data '{"domain":"acme.com"}' \
  --wait-until-finished

# 一个操作，多条记录 → 返回批次
cargo-ai orchestration action execute-batch \
  --action '{"kind":"tool","toolUuid":"<tool-uuid>"}' \
  --records '[{"domain":"acme.com"},{"domain":"globex.com"}]' \
  --wait-until-finished
```

操作种类：`tool`, `connector`, `agent`, `native`。参见 `references/examples/actions.md` 获取所有操作种类、参数、重试配置、响应形状和端到端示例。

> **顶层操作没有 `config` — 省略它。** 输入属于 `--data` /
> `--records`；`execute` 和 `execute-batch` 完全不带 `config` 键，这正是 `action list` 返回的，所以结果可以直接粘贴。
>
> (`"config": {}` 在那里仍然被接受，无害。)
>
> **`get-output-schema` 也采用相同的组合。** 来自 `action list` 的操作对象，加上 `--data` 当操作的输出取决于其输入时 — 一个 HubSpot 对象类型或目标表格决定哪些字段返回
> (`--data` 需要 **CLI ≥ 1.0.67**；无 `config` 的 `--action` 从 1.0.66 开始工作）。
> 工作流**节点**、警报的 `--actions`、play 的 `healthAlertActions`，以及代理的或 MCP 服务器的 `--actions` 是 `config` 仍然存在的地方；那是节点的配置，而不是操作的输入。
>
> **放入 `config` 的输入现在被丢弃，而不是拒绝。** 以前用于回答 `A top-level action does not use action.config…` 的守卫已消失，因此操作使用*无输入* — 你会得到提供者端的缺失字段错误或一个永远不会提及 `config` 的空结果。当调用因明显原因为空时，首先检查这一点。

> **`execute-batch` 按记录计费。** 首先传递 `--records` 的 10-20 条记录切片，报告观察到的每条记录成本和命中率，并在发送其余部分之前获得批准（带有完整记录数量和信用估计）— 与 [创建批次](#the-sample-gate) 相同的门控。

### 解决操作的输出模式（不执行）

**永远不要猜测操作输出什么。** 两个免费来源 — 无运行、无信用：

1. **连接器操作：** 集成目录以内联方式包含输出模式——`integration get <slug>`（以及 `integration list`）返回 `actions.<actionSlug>.output.schema`，紧随输入 `config.jsonSchema` 旁边。并非每个操作都声明一个。

2. **任何操作类型**（`tool` / `connector` / `agent` / `native`）——使用与 `action execute` 相同的 `--action` 对象进行解析：

```bash
cargo-ai orchestration action get-output-schema \
  --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}'
# → {"schema": {"type": "object", "properties": {...}}}  — JSON 模式位于顶层 "schema" 键下

# 当输出依赖于输入时，请按 `execute` 接收的精确方式传递它们（`--data` 需要 CLI ≥ 1.0.67）：
cargo-ai orchestration action get-output-schema \
  --action '{"kind":"connector","integrationSlug":"hubspot","actionSlug":"findRecords"}' \
  --data '{"objectType":"contacts"}' 
```

声明无输出模式的操作会以 `"Action has no output schema."`（非零退出，状态 404）失败——这是回退到检查实际运行中的 `runContext` 的信号。使用这些操作来：

- 在连接图之前，知道下游节点可以读取哪些字段（`{{nodes.<slug>.<field>}}`）。
- 查看 `agent` 操作的真实输出信封——默认的自由文本 `agent` 解析为 `{"schema":{"type":"object","properties":{"answer":{"type":"string"}}}}`，这就是为什么下游引用需要 `{{nodes.<slug>.answer...}}`。
- 将操作的输出映射到没有一次性运行的存储列。

参考 `references/examples/actions.md`（“解析操作的输出模式”）获取经过验证的按类型示例和响应/错误形状。

## 创建运行

运行通过工作流处理单个记录。当您需要通过节点图链式连接多个操作，或运行现有工具工作流时，请使用 `run create`。

**运行仅适用于工具工作流。** 播放工作流返回 `playNotCompatible`——请使用 `batch create`。

```bash
cargo-ai orchestration run create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"company":"Acme","domain":"acme.com"}'
# → Poll with: cargo-ai orchestration run get <run-uuid>

# 或者同步等待——阻塞直到运行达到终端状态并返回最终结果
cargo-ai orchestration run create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"company":"Acme","domain":"acme.com"}' \
  --wait-until-finished
```

也支持 `--release-uuid` 以固定特定版本。

**取消运行：**

```bash
cargo-ai orchestration run cancel --workflow-uuid <uuid> --uuids run-uuid-1,run-uuid-2
```

参考 `references/examples/tools.md` 获取文件上传、监控和取消信息。参考 `references/nodes.md` 获取自定义节点图。

## 创建批次

> **先采样，再询问是否全部加入——阻塞。** 批次将一个工作流应用于其数据源中的每条记录，因此错误和完整账单将一起到来。切勿在第一次尝试中全部加入一个分段/文件/模型：运行 **10–20 条记录的样本**，报告其成本和返回值，然后要求用户在问题中提供记录数量和信用估计以批准完整加入。以下是机制；其背后的支出规则是 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md)。

### 采样门

**1. 首先计算池（免费）。** 不要从猜测中引用估计：

```bash
cargo-ai segmentation segment get <segment-uuid>          # → recordsCount (也位于 `segment list`)
cargo-ai storage query execute "SELECT count() FROM <dataset>.<model>"   # 对于过滤器/模型源
# 对于文件源：CSV 的 `wc -l`，减去标题行。
```

**2. 运行 10–20 条记录通过精确的工作流和配置。** 按数据类型采样：

```bash
# 播放工作流，分段源 → 重用分段的自身过滤器，由 `limit` 限制
cargo-ai segmentation segment get <segment-uuid>          # → 复制 .filter 和 .modelUuid
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"<modelUuid>","filter":<segment.filter>,"limit":15}' \
  --wait-until-finished

# 播放工作流，显式记录 → 选择 10–20 个 ID
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"recordIds","modelUuid":"<modelUuid>","ids":["id-1","…","id-15"]}'

# 工具工作流，内联记录 → 切片数组
cargo-ai orchestration batch create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"kind":"records","records":[ /* 仅第一个 15 条 */ ]}'

# 工具工作流，文件 → 上传截断的 CSV（标题 + 15 行），不是完整文件
head -n 16 leads.csv > leads-sample.csv
cargo-ai workspaceManagement file upload --file ./leads-sample.csv
```

`limit` 是 `kind: "filter"` 的采样杠杆。`kind: "segment"` 和 `kind: "change"` 没有限制——它们始终加入整个集合，因此通过 `filter` 或 `recordIds` 采样，仅在批准的完整运行中切换到 `segment`。

**3. 报告样本，然后询问。** 确认必须包含用户需要决策的两个数字：

```
样本：15 条中的 1,240 条记录 · 6.2 信用点（0.41/条）· 13/15 富集（87%）
完整加入：剩余 1,225 条记录 ≈ 502 信用点（余额：780）

加入所有 1,225 条？或：
  1. 加入所有 1,225 条（≈502 cr，剩余 ~278）
  2. 缩小范围——例如具有设置域的 610 条记录（≈250 cr）
  3. 停止此处并首先查看样本输出
```

等待明确答复。**不要在未回答的问题上加入完整集合**，并且不要将样本的批准视为完整运行的批准。仅在批次免费（没有付费节点）*且*较小，或用户在本会话中已命名范围并批准成本时才跳过此门。

批次一次处理多条记录。允许的数据类型取决于工作流类型：

- **Play** 工作流：`filter`，`recordIds`，`segment`，`change`
- **Tool** 工作流（或无 `workflowUuid`）：`file`，`records`

使用 `filter` 触发播放——它直接查询模型。`segment` 仅接受来自 `segmentation segment list` 的**独立**分段；传递 `play list` 返回的 `segmentUuid` 被拒绝（`segmentLinkedToPlay`，或在旧后端上 `noRecords`），因为播放生成的分段永远不会具有填充的记录数。

```bash
# 播放工作流——运行播放的模型（空过滤器 = 所有行）
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}'

# 工具工作流——基于文件运行
cargo-ai orchestration batch create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"kind":"file","s3Filename":"..."}'
# → Poll with: cargo-ai orchestration batch get <batch-uuid>

# 或者同步等待——阻塞直到批次达到终端状态并返回最终结果
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}' \
  --wait-until-finished
```

**下载结果：** 从批次获取中获取 `releaseUuid`，然后 `cargo-ai orchestration release get <release-uuid>` 找到 `nodes[].slug`，然后 `cargo-ai orchestration batch download --uuid <batch-uuid> --output-node-slug <slug>`。

**取消批次：**

```bash
cargo-ai orchestration batch cancel <batch-uuid>
```

参考 `references/examples/plays.md` 和 `references/examples/tools.md` 获取过滤、记录 ID、文件上传、监控和取消信息。

## 向 AI 代理发送消息

```bash
cargo-ai ai agent list                                    # 1. 找到代理
cargo-ai ai chat create \                                 # 2. 创建聊天
  --trigger '{"type":"draft"}' \
  --agent-uuid <agent-uuid> --name "Research session"
cargo-ai ai message create \                              # 3. 发送消息
  --chat-uuid <chat-uuid> \
  --parts '[{"type":"text","text":"Find the VP of Sales at Acme Corp"}]'
# → 提取 assistantMessage.uuid，使用：cargo-ai ai message get <uuid>
#   完成时 .message.status 为 "success"（读取 .parts）或 "error"（读取 .errorMessage）
```

也支持 `--actions`，`--resources`，`--language-model-slug`，`--temperature`，`--max-steps` 和 `--wait-until-finished`（阻塞直到助手消息达到终端状态）。参考 `references/examples/agents.md` 获取多轮对话、操作/资源注入和模型选择信息。

## 检查记录

记录是工作流处理的单个项目。使用这些命令列出、计数、下载或取消工作流中的记录。

`record download-outputs` 是 `run download-outputs` 的**记录**粒度兄弟：每条记录一行，而不是每条运行一行。它使用 `--limit` / `--offset` 分页（CLI ≥ 1.0.90），这是如何导出对于单个文件太大的一组——以固定切片的方式逐步处理，而不是请求所有内容并超时。

```bash
# 列出工作流的记录
cargo-ai orchestration record list --workflow-uuid <uuid> --limit 50

# 按批次或状态过滤
cargo-ai orchestration record list --workflow-uuid <uuid> --batch-uuid <uuid> --statuses error

# 计数记录
cargo-ai orchestration record count --workflow-uuid <uuid>

# 下载记录为文件
cargo-ai orchestration record download --workflow-uuid <uuid>

# 下载每个输出节点的数据，按记录分页，处理大型集合
cargo-ai orchestration record download-outputs \
  --workflow-uuid <uuid> \
  --output-node-slug <slug> \
  --limit 1000 --offset 2000

# 获取每个节点的执行指标
cargo-ai orchestration record get-metrics --workflow-uuid <uuid>

# 取消记录
cargo-ai orchestration record cancel --workflow-uuid <uuid> --ids record-id-1,record-id-2
```

## 查询编排历史（编排查询）

对编排运行时表（`spans`，`runs`，`batches`，`records`）运行 SQL——使用 `orchestration query execute`。用于在工作流执行上进行即席分析（错误率、吞吐量、最慢节点），而无需 `run get-metrics` / `run count` 的工作流范围过滤器。

```bash
cargo-ai orchestration query execute "SELECT count() FROM runs WHERE status = 'error'"
cargo-ai orchestration query execute "SELECT status, count() FROM batches GROUP BY status"
cargo-ai orchestration query execute "SELECT * FROM spans ORDER BY execution_started_at DESC LIMIT 10"
```

表引用时不带模式前缀——只需 `spans`，`runs`，`batches` 或 `records`。工作区范围自动应用。查询是只读的；DDL、表函数、字典访问器和内省被拒绝。参考 `references/examples/queries.md` 获取模式、示例查询和限制。

## 获取分段数据

从分段中检索实时记录。**重要提示：** 需要 `--model-uuid`（不是 `--segment-uuid`）。从 `segment list` 获取 `modelUuid`。过滤器 JSON 使用 `conjonction`（不是 `conjunction`）——这是有意为之。

```bash
cargo-ai segmentation segment fetch \
  --model-uuid <uuid> \
  --filter '{"conjonction":"and","groups":[]}' \
  --fetching-limit 100 --fetching-offset 0
```

支持 `--sort`，`--enrich` 和 `--sync`。参考 `references/filter-syntax.md` 获取完整过滤器语法和 `references/examples/segments.md` 获取过滤、分页、排序、加入过滤器以及丰富信息。

**管理分段：**

```bash
# 更新分段的名称或过滤器
cargo-ai segmentation segment update --uuid <segment-uuid> --name "Updated Name"
cargo-ai segmentation segment update --uuid <segment-uuid> --filter '{"conjonction":"and","groups":[...]}'

# 删除分段（如果链接到工作流则失败）
cargo-ai segmentation segment remove <segment-uuid>
```

## 使用工作流模板

模板是用于常见自动化模式（丰富管道、CRM 同步、潜在客户评分）的预构建节点图。使用 `template list` 浏览，使用 `template get <slug>` 检查，填写占位符，验证，然后运行。

```bash
cargo-ai orchestration template list              # 列出可用模板
cargo-ai orchestration template get <slug>        # 获取模板节点 + 配置
```

参考 `references/examples/templates.md` 获取完整指南，包括占位符约定和端到端示例。

## 验证和测试节点

始终在运行自定义节点图之前验证它们。

```bash
cargo-ai orchestration node validate --nodes '[...]'
# → { "outcome": "valid" } 或 { "outcome": "notValid", "invalidNodes": [...] }
```

然后 **在部署之前显示它**——`validate` 证明图是格式良好的，而不是用户请求的功能：

```bash
cargo-ai orchestration node diagram --nodes '[...]' --format ascii --raw   # 免费，不运行任何操作
```

相同命令绘制已部署工作流（`--workflow-uuid`），草稿（`--draft`），发布（`--release-uuid`），或运行执行的图（`--run-uuid`）。参考 `references/node-diagram.md`。

对于调试，使用 `node compute`（干运行表达式）或 `node execute`（现有工作流中单个节点的实时测试——需要 `--workflow-uuid` + `--release-uuid` + `--computed-config`，并消耗信用点；对于任何不是节点级调试的内容，请使用 `action execute`）。对于状态为 `success` 但返回错误输出的运行（错误分支被选中，下游值为空），使用 `run.get` 中的 `run.executions[].title` 仅作为快速摘要——它可能被截断——并读取 `runContext.<nodeSlug>`（在相同 `run.get <run-uuid>` 响应的顶层返回）以验证字段级数据。参考 `references/troubleshooting.md` → “调试工作流运行”和 `references/nodes.md` 获取完整的节点创建指南、验证错误代码和示例。

## 帮助

每个命令支持 `--help`：

```bash
cargo-ai orchestration run create --help
cargo-ai orchestration template list --help
cargo-ai orchestration node validate --help
cargo-ai ai message create --help
cargo-ai orchestration query execute --help
```
