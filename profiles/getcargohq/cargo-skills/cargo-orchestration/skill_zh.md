# Cargo CLI — 编排

Cargo 平台的运行时操作。

**你想运行什么？**

```
需要运行某物？
├── 还不知道操作 → action list <关键词>
├── 一个操作，一个记录       → action execute
├── 一个操作，多个记录       → action execute-batch
├── 多个操作链式执行
│   ├── 一次性/临时         → run create --nodes (一个记录)
│   │                              batch create --nodes (多个记录)
│   └── 可重用工作流        → 创建一个工具，然后 run create --workflow-uuid
│                                  或 batch create --workflow-uuid
├── 对话式 AI 代理      → message create
└── 测试你正在构建的工作流中的一个节点     → node execute (仅调试 — 见下文)
```

> **跨多个记录扩展 (`action execute-batch`, `batch create`)？先采样。** 运行 10-20 个记录，报告观察到的成本和命中率，然后要求用户批准完整注册 — 引用 **记录数** 和 **信用估计**。参见 [创建批次 → 采样门](#the-sample-gate)。

> **每个节点执行成本 0.01 信用 — 每 100 个 1 信用 — 无论节点是什么。**
> `branch`, `filter`, `switch`, `variables` 和其他不携带提供者价格，但它们不是免费的：收费按 *执行* 计算，因此图的成本有两项，
> `(提供者成本 × 记录) + (节点 × 记录 ÷ 100)`。在计算密集、操作轻的工作流中，第二项占主导地位。它不会出现在 **没有** 按节点字段 — 不是 `executions[].creditsUsedCount`，不是 `spans.execution_credits_used_count` — 只有在 `billing usage get-metrics --unit orchestration.executions` 中出现。
> 在批准消息中引用这两项 ([`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) §1)。

> **在编写 JSON 之前找到操作。** `cargo-ai orchestration action list <keywords>` 一次搜索集成目录、Cargo 原生操作、工作空间工具和代理 — 免费，不运行任何操作 — 每个结果都带有可粘贴的 `action` 对象（`connectorUuid` 已预先填写），操作的 **信用成本** 和它的自动完成缩写。使用 `--kind connector|native|tool|agent`、`--integration-slug <slug>`、`--limit`（默认 20，最大 50）进行缩小。`unknown command` 表示 CLI 预先不知道它 — 刷新。

> **默认情况下，运行某物是 `action execute`，而不是 `node execute`。**
> `node execute` 是一个 **调试** 表面，用于已经存在于工作流中的节点：它需要 `--workflow-uuid`、`--release-uuid`、`--node`、`--computed-config`
> **和** `--context`（所有五个，客户端端强制执行），并且像任何实时调用一样计费。如果你只需要操作的输出 — 富化域，调用连接器操作，调用工具或代理 — 使用 `action execute` / `action execute-batch` 并带有小的 `--action` + `--data` 负载。只有在验证一个节点在运行完整图之前，才使用 `node execute`。

> **术语：** 一个编排 **工具** 是一个保存的按需工作流（通过 `tool list` 列出）。一个 **操作** 是一个你不需要构建工作流即可执行的单个操作 — 它可以嵌入一个保存的编排工具（`kind: "tool"`）、调用第三方连接器（`kind: "connector"`）、调用 AI 代理（`kind: "agent"`）或运行内置平台操作（`kind: "native"`）。

> **组合节点图？优先使用内置操作 + 表达式。** 使用 Cargo 已经提供的操作和模板表达式；避免 `python`、`script`（JS）和原始 HTTP 节点，除非你真的没有其他选择。重塑数据 → `variables`；调用一个 LLM 并获取解析的 JSON → 原生 `agent` 节点；调用 API → 集成专用的 **连接器操作**；路由 → `branch`/`filter`/`switch`。参见 **`references/node-selection.md`**。

> **显示图，而不是描述它。** 在部署草稿之前，以及每当用户询问工作流或播放的作用时，绘制它：
> `cargo-ai orchestration node diagram --workflow-uuid <uuid> --format ascii --raw`
> （免费，不运行任何操作；`--format` 需要 CLI ≥ 1.0.56，命令本身 ≥ 1.0.54）。
> 路由、回退边和哪些步骤计费是用户实际批准的内容，而文字会淡化所有三个。**根据输出位置选择格式：** `ascii` 渲染一个人可以在终端或聊天回复中阅读的图片；`mermaid`（默认）是源代码，只有在将内容粘贴到 PR、文档或可以渲染它的页面时才正确。源、ASCII 图例、成本标记和重复缩写字的枪：**`references/node-diagram.md`**。

**参考：**

> `references/examples/actions.md` — action execute 和 execute-batch 示例
> `references/examples/tools.md` — 工具（按需工作流）示例
> `references/examples/plays.md` — 播放（基于段的自动化）示例
> `references/examples/agents.md` — AI 代理聊天示例
> `references/examples/templates.md` — 预构建的工作流模板
> `references/examples/queries.md` — `orchestration query execute`（ClickHouse：运行/批次/跨度/记录）SQL 示例。对于 `storage query`（工作空间存储），请参阅 `cargo-storage` 技能。
> `references/examples/segments.md` — 段获取和过滤示例
> `references/nodes.md` — 完整节点创建指南（种类、原生操作、表达式、验证、路由）
> `references/node-diagram.md` — **绘制节点图作为 Mermaid 流程图** (`node diagram`)：每个源（工作流 / 草稿 / 发布 / 运行 / 原始节点）、标记付费节点、突出显示失败的节点，以及为什么图表基于 `uuid` 而不是 `slug`
> `references/node-selection.md` — **如何选择正确的节点并避免不必要的 `python` 节点**（决策表、原生 LLM `agent` 节点、模板表达式限制、静默未定义的枪、通过 `runContext` 检查节点数据、Pyodide 沙盒限制、`delay` 后幸存的内容、组结果访问）
> `references/filter-syntax.md` — 完整过滤条件参考
> `references/polling.md` — 异步轮询模式、错误处理、重试策略
> `references/response-shapes.md` — 完整 JSON 响应结构
> `references/troubleshooting.md` — 常见错误，以及运行成功但输出错误（错误分支路由、下游值空）的“调试工作流运行”部分

> **事后诊断？** 对于基于这些表面的有序法医运行程序 — 追踪一次运行、按根本原因扫描批次错误、分析播放的信用支出 — 加载 [`cargo-diagnostics`](../cargo-diagnostics/SKILL.md) 技能。

## 引导

已经登录（`cargo-ai whoami` 返回工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令添加 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送代码，无需浏览器；第一次使用时创建帐户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入之前确认活动工作区
```

每个命令都打印 JSON 到标准输出；失败时以非零退出并带有 `{"errorMessage": "..."}`。创建运行或批次的任何内容都是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装时，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 添加了 CLI 版本固定、令牌范围和仅管理员表面。

## 首先发现资源

大多数命令需要 UUID。始终在采取行动之前发现它们。

```bash
cargo-ai orchestration action list <query>  # 连接器、原生、工具、代理的操作（+ 信用）
cargo-ai orchestration play list            # 所有播放（名称、workflowUuid、modelUuid、segmentUuid）
cargo-ai orchestration tool list            # 所有工具（名称、workflowUuid、描述）
cargo-ai orchestration workflow list        # 所有工作流（仅 uuid — 无名称）
cargo-ai orchestration template list       # 所有工作流模板（slug、名称、种类）
cargo-ai ai agent list                     # 所有代理（uuid、名称）
cargo-ai ai template list                  # 所有 AI 代理模板（slug、名称、languageModelSlug）
cargo-ai storage model list                # 所有模型（uuid、名称、slug、列）
cargo-ai storage dataset list              # 所有数据集
cargo-ai segmentation segment list         # 所有段（uuid、名称、modelUuid）
cargo-ai connection connector list         # 所有连接器
```

**播放与工具：** 两者都由工作流支持。一个 **播放** 是基于段的自动化 — 它对段的更改做出反应（添加记录、更新、删除）。一个 **工具** 是按需工作流 — 手动触发、通过 API 或在 cron 定时器上触发。工作流没有 `name` 字段；使用 `play list` 或 `tool list` 找到名称并提取 `workflowUuid`。

**在 UI 中获取：** 播放位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/plays/<PLAY_UUID>`，工具位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/tools/<TOOL_UUID>`。从 `cargo-ai whoami` 获取 `<WORKSPACE_UUID>` 在 `workspace.uuid` 下。

**设计新的工具或播放？** 首先检查模板 — 它们是针对常见自动化模式的预构建节点图（富化管道、CRM 同步、潜在客户评分）并且是极好的起点。使用 `cargo-ai orchestration template list` 列出模板，并使用 `cargo-ai orchestration template get <slug>` 检查特定模板。模板按 `kind` 标记，因此你可以找到适合工具（`"kind":"tool"`）或播放（`"kind":"play"`）的模板。参见 `references/examples/templates.md` 获取完整指南。

**兼容性规则：**

- **`run create`** — 仅适用于 **工具** 工作流（或无 `workflowUuid`）。播放工作流返回 `playNotCompatible` — 使用 `batch create` 代替。

- **`batch create`** — 允许的数据种类取决于工作流类型：
  - **播放** 工作流：`filter`、`recordIds`、`segment`、`change`。使用 `filter` 触发播放；`segment` 仅接受一个独立的段，从不接受来自 `play list` 的 `segmentUuid`。

  - **工具** 工作流（或无 `workflowUuid`）：`file`、`records`

## 快速参考

```bash
# 查找一个操作（免费 — 不运行，不消费信用）
cargo-ai orchestration action list enrich company
cargo-ai orchestration action list send --kind connector --integration-slug slack

# 单个操作
cargo-ai orchestration action execute --action '{"kind":"tool","toolUuid":"<uuid>"}' --data '{"domain":"acme.com"}'
cargo-ai orchestration action execute-batch --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' --records '[{...},{...}]'
cargo-ai orchestration action get-output-schema --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' # → {"schema": <JSON Schema>} 而不执行

# 工作流（链式多个操作）
cargo-ai orchestration run create --workflow-uuid <uuid> --data '{"company":"Acme","domain":"acme.com"}'
cargo-ai orchestration run create --data '{"domain":"acme.com"}' --nodes '[...]'
cargo-ai orchestration batch create --workflow-uuid <uuid> --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}'

# AI 代理
cargo-ai ai message create --chat-uuid <uuid> --parts '[{"type":"text","text":"..."}]'

# 数据
cargo-ai orchestration query execute "SELECT count() FROM runs WHERE status='error'" # ClickHouse：spans、runs、batches、records
cargo-ai segmentation segment fetch --model-uuid <uuid> --filter '{"conjonction":"and","groups":[]}' --fetching-limit 100
# 对于针对工作空间存储（公司、联系人等）的 SQL，请参阅 cargo-storage 技能：`storage query execute`
```

## 异步操作轮询

所有操作都是异步的。要么轮询直到终端状态，要么传递 `--wait-until-finished` 以阻塞。

`action execute` 返回一个运行。`action execute-batch` 返回一个批次。它们以相同的方式轮询：

| 结果类型     | 轮询命令         | 间隔 | 完成时                                      |
| --------------- | -------------------- | -------- | ---------------------------------------------- |
| 运行             | `run get <uuid>`     | 2s       | `status` 是 `success`, `error`, 或 `cancelled` |
| 批次           | `batch get <uuid>`   | 5s       | `status` 是 `success`, `error`, 或 `cancelled` |
| 代理消息   | `message get <uuid>` | 2s       | `status` 是 `success` 或 `error`               |

对于长时间运行的批次（1000+ 记录），在第一分钟后将间隔增加到 10-15 秒。

## 执行操作

运行单个操作 — 不需要工作流或节点图。

### 首先找到它 — `action list`

```bash
cargo-ai orchestration action list enrich company          # 所有种类
cargo-ai orchestration action list --kind tool             # 此工作区的工具
cargo-ai orchestration action list send --kind connector --integration-slug slack
```

免费，不执行任何操作。所有查询术语必须匹配（AND）；操作 slug 或名称的命中排名高于集成，集成排名高于描述。返回 `{query, totalMatches, results[]}`，其中每个结果都带有可粘贴到 `execute` /
`execute-batch` / `get-output-schema` 的 `action` 对象，该集成的工作区 `connectors`，`credits`（操作计费的成本表），以及 `autocompletes`（需要选择的 ID 的配置字段 — HubSpot 对象类型、Slack 频道）。默认返回 20 个结果，最多 50 个。

```bash
# 一个操作，一个记录 → 返回一个运行
cargo-ai orchestration action execute \
  --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}' \
  --data '{"domain":"acme.com"}' \
  --wait-until-finished

# 一个操作，多个记录 → 返回一个批次
cargo-ai orchestration action execute-batch \
  --action '{"kind":"tool","toolUuid":"<tool-uuid>"}' \
  --records '[{"domain":"acme.com"},{"domain":"globex.com"}]' \
  --wait-until-finished
```

操作种类：`tool`, `connector`, `agent`, `native`. 参见 `references/examples/actions.md` 获取所有操作种类、参数、重试配置、响应形状和端到端示例。

> **顶层操作没有 `config` — 省略它。** 输入属于 `--data` /
> `--records`；`execute` 和 `execute-batch` 不带 `config` 键，完全一样，所以 `action list` 的结果可以立即粘贴。(`"config": {}` 在那里仍然接受，无害地。)
>
> **`get-output-schema` 使用相同的对。** 来自 `action list` 的操作对象，加上 `--data` 当操作输出取决于其输入时 — HubSpot 对象类型或目标表格决定哪些字段返回 (`--data` 需要 **CLI ≥ 1.0.67**；无 `config` 的 `--action` 在 1.0.66 时工作）。工作流 **节点**、警报的 `--actions`、播放的 `healthAlertActions`，以及代理或 MCP 服务器的 `--actions` 是 `config` 仍然存在的地方；那是节点的配置，而不是操作的输入。
>
> **放入 `config` 的输入现在被丢弃，而不是拒绝。** 以前用于回答 `A top-level action does not use action.config…` 的守卫已经消失，因此操作在没有输入的情况下运行 — 你会得到提供者端的缺失字段错误或一个空的响应，永远不会提到 `config`。当调用返回为空且没有明显原因时，首先检查这一点。

> **`execute-batch` 按记录计费。** 传递 10-20 个记录切片的 `--records` 首先进行采样，报告观察到的每个记录的成本和命中率，然后在发送其余内容之前获得批准（带有完整的记录数和信用估计） — 与 [创建批次](#the-sample-gate) 相同的关卡。

### 解析操作的输出模式（不执行）

**永远不要猜测操作输出什么。** 两个免费来源 — 不运行，不消费信用：

1. **连接器操作：** 集成目录包含内联的输出模式 — `integration get <slug>`（以及 `integration list`）返回 `actions.<actionSlug>.output.schema`，旁边是输入 `config.jsonSchema`。不是每个操作都声明一个。
2. **任何操作种类** (`tool` / `connector` / `agent` / `native`) — 使用与 `action execute` 相同的 `--action` 对象解析它：

```bash
cargo-ai orchestration action get-output-schema \
  --action '{"kind":"connector","integrationSlug":"clearbit","actionSlug":"enrichCompany"}'
# → {"schema": {"type": "object", "properties": {...}}}  — JSON Schema 在顶层 "schema" 键下
```

当输出取决于输入时，按 `execute` 接收的精确方式传递它们
(`--data` 需要 CLI ≥ 1.0.67):
cargo-ai orchestration action get-output-schema \
  --action '{"kind":"connector","integrationSlug":"hubspot","actionSlug":"findRecords"}' \
  --data '{"objectType":"contacts"}' 
```

声明没有输出模式的操作会以 `"Action has no output schema."`（非零退出，状态 404）失败 — 那是信号，要回退到检查 `runContext` 从实际运行中。使用这些来：

- 知道下游节点可以读取哪些字段 (`{{nodes.<slug>.<field>}}`) **在** 连接图之前。
- 查看代理操作的真正输出信封 — 默认免费文本代理解析为 `{"schema":{"type":"object","properties":{"answer":{"type":"string"}}}`，这就是为什么下游引用需要 `{{nodes.<slug>.answer...}}`。
- 将操作的输出映射到存储列，而无需浪费运行。

参见 `references/examples/actions.md` (“解析操作的输出模式”) 获取验证的每种类别示例和响应/错误形状。

## 创建运行

运行处理单个记录通过工作流。当你需要通过节点图链式多个操作时，或者运行现有的工具工作流，请使用 `run create`。

**运行仅适用于工具工作流。** 播放工作流返回 `playNotCompatible` — 使用 `batch create` 代替。

```bash
cargo-ai orchestration run create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"company":"Acme","domain":"acme.com"}'
# → Poll with: cargo-ai orchestration run get <run-uuid>

# 或者同步等待 — 阻塞直到运行达到终端状态并返回最终结果
cargo-ai orchestration run create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"company":"Acme","domain":"acme.com"}' \
  --wait-until-finished
```

还支持 `--release-uuid` 来固定特定发布。

**取消运行：**

```bash
cargo-ai orchestration run cancel --workflow-uuid <uuid> --uuids run-uuid-1,run-uuid-2
```

参见 `references/examples/tools.md` 用于文件上传、监控和取消。参见 `references/nodes.md` 用于自定义节点图。

## 创建批次

> **先采样，然后询问是否注册所有内容 — 阻塞。** 批次将一个工作流扩展到其数据源中的每个记录，因此一个错误和完整账单会一起出现。第一次尝试不要注册完整段/文件/模型：运行一个 **10-20 个记录的样本**，报告它的成本和返回，然后要求用户批准完整注册 — 引用 **记录数** 和 **信用估计**。参见 [创建批次 → 采样门](#the-sample-gate)。

### 采样门

**1. 首先计算池（免费）。** 永远不要从猜测中引用估计：

```bash
cargo-ai segmentation segment get <segment-uuid>          # → recordsCount (也位于 `segment list`)
cargo-ai storage query execute "SELECT count() FROM <dataset>.<model>"   # 对于过滤/模型源
# 对于文件源：CSV 的 `wc -l`，减去标题行。
```

**2. 通过精确的工作流和配置运行 10-20 个记录。** 按数据种类采样：

```bash
# 播放工作流，段源 → 重用段的自身过滤器，限制为 `limit`
cargo-ai segmentation segment get <segment-uuid>          # → 复制 .filter 和 .modelUuid
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"...","filter":<segment.filter>,"limit":15}' \
  --wait-until-finished

# 播放工作流，显式记录 → 选择 10-20 个 ID
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"recordIds","modelUuid":"<modelUuid>","ids":["id-1","…","id-15"}'

# 工具工作流，内联记录 → 切片数组
cargo-ai orchestration batch create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"kind":"records","records":[ /* 仅第一个 15 个 */ ]}
```

`limit` 是 `kind: "filter"` 的采样杠杆。`kind: "segment"` 和 `kind: "change"` 没有限制 — 它们总是注册整个集合，因此通过 `filter` 或 `recordIds` 采样，并且仅在批准完整运行时切换到 `segment`。

**3. 报告样本，然后询问。** 确认必须包含用户需要决定的两个数字：

```
样本：15 个中的 1,240 个记录 · 6.2 信用 (0.41/记录) · 13/15 富化 (87%)
完整注册：剩余 1,225 个记录 ≈ 502 信用 (余额：780)

注册所有 1,225? 或：
  1. 注册所有 1,225 (≈502 cr, 留下 ~278)
  2. 修剪范围 — 例如，具有已设置域的 610 个记录 (≈250 cr)
  3. 在审查样本输出之前停止这里
```

等待明确的答案。**不要在未回答的问题上注册完整集**，并且不要将样本的批准视为完整运行的批准。仅在批次免费（没有付费节点）*并且* 小，或者当用户在本会话中已经命名范围并批准成本时才跳过关卡。

批次一次处理多个记录。允许的数据种类取决于工作流类型：

- **播放** 工作流：`filter`, `recordIds`, `segment`, `change`
- **工具** 工作流（或无 `workflowUuid`）：`file`, `records`

使用 `filter` 触发播放 — 它直接查询模型。`segment` 仅接受一个 **独立的** 段从 `segmentation segment list`；传递 `play list` 返回的 `segmentUuid` 被拒绝 (`segmentLinkedToPlay`, 或 `noRecords` 在旧后端) 因为播放生成的段永远不会有一个填充的记录数。

```bash
# 播放工作流 — 运行播放的模型（空过滤器 = 所有行）
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}'

# 工具工作流 — 运行文件
cargo-ai orchestration batch create \
  --workflow-uuid <tool.workflowUuid> \
  --data '{"kind":"file","s3Filename":"..."}`

# 或同步等待 — 阻塞直到批次达到终端状态并返回最终结果
cargo-ai orchestration batch create \
  --workflow-uuid <play.workflowUuid> \
  --data '{"kind":"filter","modelUuid":"...","filter":{"conjonction":"and","groups":[]}}' \
  --wait-until-finished
```

**下载结果：** 从批次获取 `releaseUuid`，然后 `cargo-ai orchestration release get <release-uuid>` 以找到 `nodes[].slug`，然后 `cargo-ai orchestration batch download --uuid <batch-uuid> --output-node-slug <slug>`。

**取消批次：**

```bash
cargo-ai orchestration batch cancel <batch-uuid>
```

参见 `references/examples/plays.md` 和 `references/examples/tools.md` 用于过滤、记录 ID、文件上传、监控和取消。

## 向 AI 代理发送消息

```bash
cargo-ai ai agent list                                    # 1. 找到代理
cargo-ai ai chat create \                                 # 2. 创建聊天
  --trigger '{"type":"draft"}' \
  --agent-uuid <agent-uuid> --name "Research session"
cargo-ai ai message create \                              # 3. 发送消息
  --chat-uuid <chat-uuid> \
  --parts '[{"type":"text","text":"Find the VP of Sales at Acme Corp"}]'
# → 提取 assistantMessage.uuid，轮询：cargo-ai ai message get <uuid>
# 完成时 .message.status 是 "success"（读取 .parts）或 "error"（读取 .errorMessage）
```

还支持 `--actions`, `--resources`, `--language-model-slug`, `--temperature`, `--max-steps`, 和 `--wait-until-finished`（阻塞直到助手消息达到终端状态）。参见 `references/examples/agents.md` 用于多轮对话、操作/资源注入和模型选择。

## 检查记录

记录是工作流处理的单个项目。使用这些命令来列出、计数、下载或取消工作流内的记录。

`record download-outputs` 是 `record` 级别的 `run download-outputs` 的兄弟：每行对应一个记录而不是每个运行。它使用 `--limit` / `--offset` 进行分页（CLI ≥ 1.0.90），这是如何导出太大无法放入一个文件的一组 — 以固定切片逐步处理，而不是请求所有内容并超时。

```bash
# 列出工作流的记录
cargo-ai orchestration record list --workflow-uuid <uuid> --limit 50

# 按批次或状态过滤
cargo-ai orchestration record list --workflow-uuid <uuid> --batch-uuid <uuid> --statuses error

# 计数记录
cargo-ai orchestration record count --workflow-uuid <uuid>

# 下载记录作为文件
cargo-ai orchestration record download --workflow-uuid <uuid>

# 下载每个输出节点的数据，针对大型集合进行分页
cargo-ai orchestration record download-outputs \
  --workflow-uuid <uuid> \
  --output-node-slug <slug> \
  --limit 1000 --offset 2000

# 获取每个节点的执行指标
cargo-ai orchestration record get-metrics --workflow-uuid <uuid>

# 取消记录
cargo-ai orchestration record cancel --workflow-uuid <uuid> --ids record-id-1,record-id-2
```

## 查询编排历史 (orchestration query)

对编排运行时表运行 SQL — `spans`, `runs`, `batches`, `records` — 使用 `orchestration query execute`。用于工作流执行的自定义分析（错误率、吞吐量、最慢节点）而无需 `run get-metrics` / `run count` 的工作流范围。
