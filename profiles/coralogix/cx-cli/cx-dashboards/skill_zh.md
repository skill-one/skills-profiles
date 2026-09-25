# 创建 Coralogix 仪表板

为目标服务生成 Coralogix 仪表板，并通过 `cx` CLI 部署。工作流程：发现服务的遥测数据，与用户就意图达成一致，草拟计划，发出 JSON，通过 `cx` 进行实时验证每个查询，然后在选择的文件夹中创建仪表板。

仅使用可以从服务的代码、README、配置或返回结果的实时查询中引用的指标名称、日志字段和跨度属性。不要凭空捏造。

---

## 参考文件

加载这些文件以获取特定领域的指导：

| 任务 | 参考 |
|---|---|
| DataPrime 查询语法 | [`references/dataprime-reference.md`](references/dataprime-reference.md) |
| PromQL 查询语法、计数器与仪表板、直方图 | [`references/promql-guidelines.md`](references/promql-guidelines.md) |
| 日志字段发现、查询模式、wildfind 策略 | [`references/logs-querying.md`](references/logs-querying.md) |
| 跨度字段发现、延迟分析、跟踪查询 | [`references/spans-querying.md`](references/spans-querying.md) |
| 仪表板特定查询注意事项 (`${__range}`、`promqlQueryType`) | [`references/query-syntax.md`](references/query-syntax.md) |
| 组件 JSON 模板 | [`references/widget-templates.md`](references/widget-templates.md) |

对于选择正确的信号（指标 / 日志 / 跟踪），使用 `cx-telemetry-querying`。

---

## 仪表板管理

除了创建仪表板，还使用以下命令管理现有的仪表板：

| 命令 | 目的 |
|---|---|
| `cx dashboards catalog -o json` | 列出目录中的所有仪表板 |
| `cx dashboards get <id> -o json` | 获取仪表板定义（作为模板很有用） |
| `cx dashboards folders list -o json` | 列出仪表板文件夹 |
| `cx dashboards folders create --name "Name"` | 创建仪表板文件夹 |
| `cx dashboards folders create --name "Sub" --parent-id <id>` | 创建嵌套文件夹 |
| `cx dashboards replace --from-file dashboard.json` | 使用更新的 JSON 替换现有仪表板 |
| `cx dashboards check --from-file dashboard.json` | 验证仪表板定义而不持久化（服务器端严格检查；出错时退出非零） |
| `cx dashboards check <dashboard-id>` | 通过 ID 验证存储的仪表板 |

要更新现有仪表板：

```bash
cx dashboards get <dashboard-id> -o json > dashboard.json
# 编辑 dashboard.json（更改名称、修改组件等）
cx dashboards replace --from-file dashboard.json
```

要复制仪表板作为新副本：

```bash
cx dashboards get <dashboard-id> -o json > dashboard.json
# 删除 "id" 字段，然后作为新项目创建：
cx dashboards create --from-file dashboard.json
```

---

## 工作流程

通过此清单跟踪进度：

```
仪表板进度：
- [ ] 第一阶段：发现遥测数据与业务含义
- [ ] 第二阶段：从用户收集仪表板规范
- [ ] 第三阶段：草拟内部仪表板计划（部分/行/组件）
- [ ] 第四阶段：生成 Coralogix JSON
- [ ] 第五阶段：通过 `cx` CLI 实时验证每个查询
- [ ] 第六阶段：对照清单自我验证结构
- [ ] 第七阶段：通过 `cx dashboards check` 进行服务器端验证
- [ ] 第八阶段：通过 `cx dashboards create` 部署
- [ ] 第九阶段：与用户共享仪表板链接
```

按顺序进行。在用户批准第三阶段计划之前不要跳转到第四阶段，在第五至七阶段全部通过之前不要运行第八阶段。第九阶段是强制性的——直到用户有可点击的链接，工作流程才算完成。

---

## 第一阶段：发现遥测数据与业务含义

针对目标服务，收集：

1. **业务目的** - 阅读 `README.md` 和顶层入口点（`main.*`、`index.*`、`cmd/main.go` 等）。用 2-3 句话总结它做什么、它的关键阶段以及可能出错的地方。
2. **指标** - 对于每个候选关键字（服务名称、子系统、动词如 `request`、`error`、`latency`、`dlq`），运行 `cx metrics search --name '*<keyword>*'`。当一个指标看起来很有希望时，使用 `cx metrics get-labels <metric>` 列出其标签。仅使用 `cx metrics search` 返回的名称——这是防止凭空捏造的指标进入第五阶段的方法。对照服务的仪器 (`prometheus_client`、`promauto.NewCounter/Histogram/Gauge`、OTel 计数器、`prom-client`、Micrometer、`metrics.py`) 检查语义和直方图桶（`_sum`、`_count`、`_bucket`）。
3. **日志** - 在假设字段存在之前，使用 `cx search-fields "<description>" --dataset logs` 发现自定义 `$d.*` 字段。采样消息模板和严重性使用 `cx logs "filter \$l.applicationname == '<app>'" --limit 5 -o json`。标准字段（`$m.severity`、`$m.timestamp`、`$l.applicationname`、`$l.subsystemname`）不需要发现。
4. **跨度 / 跟踪** - 使用 `cx search-fields "<description>" --dataset spans` 发现跨度属性。使用 `cx spans "filter \$l.serviceName == '<svc>'" --limit 5 -o json` 采样。错误约定不同（`$d.tags.error`、`$d.http.status_code`）；在过滤之前检查样本。
5. **消息总线 & DLQs** - 搜索 Kafka、RabbitMQ、SQS、Pub/Sub 客户端和任何 `dlq`/`DLQ` 引用。注意 DLQ 面板的主题/队列名称。
6. **服务配置** - 检查 `meta.yaml`、Helm `values.yaml`、`Deployment`、`Dockerfile`、`chart.yaml`。提取：
   - `applicationname` / `subsystemname` 标签值，如它们在 Coralogix 中出现的样子。
   - 作为指标或日志标签使用的租户/帐户/团队标识符。
   - 部署环境（`prod`、`staging`、`dev`、…）。

如果一个问题的信号不明确（例如，“上周收入多少”），首先委托给 `cx-telemetry-querying`。

在继续之前生成简短的内部摘要。如果关键遥测数据缺失（例如，没有指标），向用户指出，询问他们是否想要一个仅日志或仅跟踪的仪表板。

---

## 第二阶段：收集仪表板规范

向用户提出一个集中的问题集（≤6）。优先使用 `AskQuestion`：

1. **受众 & 用途** - 紧急响应分类、产品/业务跟踪、容量规划、客户成功？
2. **默认时间范围** - 典型的查看窗口（例如 24h、7d）。查询仍然使用 `${__range}`，因此用户可以缩放。
3. **切片维度** - 顶层过滤器（`tenant_id`、`account_id`、`subsystem_name`、`region`、`env`、…）。
4. **环境范围** - 要包含/排除哪些环境（常见默认：排除 `dev`、`staging`、`test`）。
5. **SLO 信号** - 要突出显示的成功率、延迟或吞吐量目标？
6. **优先级** - 首先看到什么（驱动行顺序和哪个部分是 `collapsed: true`）。

不要在可以合理推断的答案上阻塞——继续进行。

---

## 第三阶段：草拟内部计划

在生成 JSON 之前，向用户批准一个 markdown 计划：

```
## 仪表板：<服务> - <目的>

### 部分 1：<概述> (collapsed: false)
- 行 1：[组件类型] <标题> - <显示什么> - 来源：指标|日志|跨度
- 行 2：...

### 部分 2：<深入分析> (collapsed: false)
...

### 部分 N：<日志 & 错误> (collapsed: true)
...

### 顶层过滤器
- <标签> (<来源>)

### 假设 / 缺失
- ...
```

**部分设计**：
- 第一部分：概览健康（仪表板 + 关键比率），始终展开。
- 在同一行中成对相关的时间序列（比率 + 延迟）。
- 最后部分（原始日志、罕见细分）：`collapsed: true`。
- 目标是 3-5 个部分，总共 6-20 个组件。

**组件类型选择**：

| 信号 | 组件类型 |
|---|---|
| 单个标题数字（计数、成功率、总计） | `gauge` (Coralogix 称之为 "stat") |
| 在 ≤8 类别中分解 | `pieChart` |
| 随时间变化（比率、延迟、每个桶的计数） | `lineChart` |
| 顶部 N 表格、最后错误、每个实体列表 | `dataTable` |

除非用户要求，否则不要使用其他组件类型。

在用户批准或调整计划之前，不要发出 JSON。

---

## 第四阶段：生成 Coralogix JSON

生成一个遵循 [`references/widget-templates.md`](references/widget-templates.md) 的单个 JSON 文档。关键规则：

1. **顶层形状**：
   ```
   {
     "id": "<21-character-nanoid>",
     "name": "<Dashboard Name>",
     "layout": { "sections": [ ... ] },
     "variables": [],
     "variablesV2": [],
     "filters": [ ... ],
     "relativeTimeFrame": "<seconds>s",
     "annotations": [],
     "off": {},
     "actions": []
   }
   ```
2. **ID** - 每个 `section`、`row`、`widget` 和查询 `id` 使用新的 UUID。
3. **行高度** - `"appearance": { "height": 19 }`，除非有理由更改。
4. **部分选项** - 包括 `options.custom.name`、`collapsed` 和 `color.predefined: "SECTION_PREDEFINED_COLOR_UNSPECIFIED"`。
5. **过滤器** - 每个切片维度（来自第二阶段）的一个条目。默认操作 `equals`，`values` 为空，以便用户可以填写。使用 `notEquals` 进行环境排除（参见 [`references/widget-templates.md`](references/widget-templates.md)）。
6. **relativeTimeFrame** - 默认 `"172800s"`（48h），除非用户指定了其他值。

对于查询语法遵循 [`references/query-syntax.md`](references/query-syntax.md)；对于完整的查询语言加载 [`references/dataprime-reference.md`](references/dataprime-reference.md) 和 [`references/promql-guidelines.md`](references/promql-guidelines.md)。

---

## 第五阶段：通过 `cx` CLI 实时验证每个查询

在第五阶段之前，仪表板中的每个 PromQL 和 DataPrime 查询都必须通过 `cx` 成功运行。这可以捕获凭空捏造的指标名称、拼写错误的字段路径和格式错误的管道。

### 频繁 vs 存档（什么 / 何时 / JSON 中的位置）

**什么**：
- **频繁** (`TIER_FREQUENT_SEARCH`)：用于快速搜索最近日志/跨度的高频层。
- **存档** (`TIER_ARCHIVE`)：用于旧日志/跨度（长期）的冷层。

**何时选择**：
- 选择 **频繁** 用于紧急响应和最近调查（小时/天）。
- 选择 **存档** 用于长期回溯（周/月）或时间范围超出热保留时。

这两种语言针对不同的窗口进行验证：

- **PromQL**：将 `relativeTimeFrame` 映射到 `$RANGE` 令牌（例如 `48h` 对应 `172800s`），在 CLI 调用中用 `[$RANGE]` 替换 `${__range}`，然后在第六阶段之前将 `${__range}` 恢复到 JSON 中。范围向量对窗口敏感，因此检查必须与仪表板将评估的内容匹配。
- **DataPrime**：针对固定短窗口验证（`now-15m` → `now`，`--limit 1`）。目标是语法/字段/管道验证，而不是仪表板窗口上的数据存在——短窗口更快，失败的信号更清晰。

完整程序（CLI 调用、`$RANGE` 映射表、重试预算、失败模式）：[`references/verification.md`](references/verification.md)。

如果一个查询在重试预算内无法通过，将 CLI 错误原样显示给用户——不要发布有问题的组件。

---

## 第六阶段：自我验证结构

对最终 JSON 运行此清单。如果任何项目在第五阶段之前失败，请修复并重新检查。

### 查询语法（仪表板特定）
- [ ] 每个指标组件中的 PromQL 范围向量使用 `[${__range}]` - 永远不要 `[$__range]`，永远不要 `[5m]`（除非面板有意是滑动窗口）。
- [ ] `promqlQueryType` 是 `PROM_QL_QUERY_TYPE_INSTANT` 用于单个值组件（gauge、pieChart、dataTable）。省略 `lineChart`。
- [ ] DataPrime 日志查询使用 `$d.message` / `$l.applicationname` / 未引号化的严重性枚举（完整规则：[`references/dataprime-reference.md`](references/dataprime-reference.md)）。
- [ ] 每个DataPrime 组件查询以 `source logs` 或 `source spans` 开头（仪表板组件需要源前缀；第五阶段验证在将管道交给 `cx logs` / `cx spans` 之前移除了它）。
- [ ] 成功率分母包裹在 `clamp_min(..., 1)` 中。
- [ ] 直方图查询使用正确的后缀（`_sum`、`_count`、`_bucket`）。
- [ ] 组件查询在仪表板级 `filters` 之前是有效的——Coralogix 在渲染时注入它们。

### 结构
- [ ] 每个部分都有 `id.value`、`rows` 和 `options.custom`。
- [ ] 每行都有 `id.value`、`appearance.height` 和 `widgets`。
- [ ] 每个组件都有一个唯一的 `id.value` 和一个 `definition`，其中包含 `gauge` / `pieChart` / `lineChart` / `dataTable` 中的一个。
- [ ] 每个gauge都有数字 `min` 和 `max`，且 `min < max`。
- [ ] 成功率gauge使用 `thresholdType: "THRESHOLD_TYPE_ABSOLUTE"`，在值较高时显示绿色；错误/DLQ gauge在值较高时显示红色。
- [ ] "总计" / "stat" 组件编码为 `gauge`，而不是 stat 类型。
- [ ] 顶层 `filters` 包括第二阶段中的每个切片维度。
- [ ] 所有 ID 都是新生成的 UUID，在文档中唯一。

### 内容
- [ ] 仪表板名称是描述性的（`"<Service> - <Purpose>"`）。
- [ ] 组件标题简短、人类可读，并匹配查询计算的内容。
- [ ] 日志/错误部分是 `collapsed: true`，除非用户另有说明。

---

## 第七阶段：通过 `cx dashboards check` 进行服务器端验证

第六阶段通过手动捕获结构问题。此阶段通过 Coralogix 仪表板服务器的严格验证器（`CheckDashboard`）运行整个仪表板——`create`/`replace` 在写入时应用的相同验证，加上编译每个 PromQL/DataPrime 查询和强制变量和过滤器所需 ID 的超集。

1. 运行 `cx dashboards check --from-file /tmp/cx-dashboard-<slug>.json`。
2. 如果命令退出非零，输出将列出具有 `severity`、`location`（一个 RFC 6901 JSON 指针到仪表板，例如 `/sections/0/rows/1/widgets/2`）和 `message` 的问题。在 JSON 中修复每个问题（回到第四阶段），重新运行第五阶段以任何更改的查询，然后重新运行此阶段。
3. 当 `check` 退出 0（文本输出：`Dashboard is valid (no issues)`）时，继续到第八阶段。

`check` 是只读的——它永远不会持久化仪表板。警告（`SEVERITY_WARNING`）打印但不会失败门；只有错误（`SEVERITY_ERROR`）会导致非零退出。在多配置分叉中，任何返回错误的配置都会导致命令失败。

---

## 第八阶段：通过 `cx dashboards create` 部署

不要告诉用户将 JSON 粘贴到 Coralogix UI 中——直接部署它。

1. 列出文件夹：`cx dashboards folders list -o json`。
2. 建议最佳文件夹匹配（团队、产品领域或以服务命名的文件夹）。如果没有匹配的，默认为根（省略 `--folder`）。
3. 将验证的 JSON 写入临时文件并运行 `cx dashboards create --from-file /tmp/cx-dashboard-<slug>.json --folder <id>`。CLI 生成 `requestId` 信封并打印创建的仪表板 ID。

完整程序（文件夹选择 UX、命令模板、幂等性说明）：[`references/deploy.md`](references/deploy.md)。

失败时：原样显示 CLI 错误并返回到第五阶段。最常见的原因是一个在本地解析但实时 API 拒绝的查询。

---

## 第九阶段：共享仪表板链接

工作流程**未完成**，直到用户有可点击的仪表板链接。仅打印 ID 强制用户手动导航 Coralogix UI，这破坏了自动化部署的目的。

在第八阶段成功后，捕获 `View in Coralogix: <url>` 行，该行由 `cx dashboards create` 打印到 stderr（参见 [`references/deploy.md`](references/deploy.md) § "共享链接" 以了解何时省略它）并发出以下输出模板。将仪表板**名称**作为链接文本——这是用户点击的。

通过 `cx dashboards catalog` 找到的仪表板（而不是你刚刚创建的）的工作方式不同：`catalog` 仅打印一个链接到目录页面，而不是每个仪表板的链接。要从该列表链接到特定的仪表板，构建 `<base>/dashboards/<dashboard_id>`，其中 `<base>` 是该会话中任何 `cx dashboards` 命令打印的 `View in Coralogix: <base>/...` 行中看到的控制台 URL——永远不要自己编造 `<base>`，如果尚未打印此类行，也永远不要编造它。

---

## 面向用户的输出格式

当 `cx dashboards create` 打印了 `View in Coralogix:` 链接时：

````
## 计划
<批准的第三阶段计划>

## 验证
- PromQL 查询验证： <N>/<N>
- DataPrime 查询验证： <N>/<N>

## 部署
- 仪表板： **[<Name>](<url from the View in Coralogix line>)**
- ID: `<id>`
- 文件夹: `<folder name or "root">`
- 配置文件: `<cx profile>`

打开它: [<Name>](<url from the View in Coralogix line>)

打开后调整过滤器值（例如 `account_id`）。
````

当 `cx dashboards create` 没有打印 `View in Coralogix:` 链接（对于配置文件和未配置的 `console_url` 没有可解析的控制台链接）时，完全省略链接——不要编造 URL。使用此模板：

````
## 计划
<批准的第三阶段计划>

## 验证
- PromQL 查询验证： <N>/<N>
- DataPrime 查询验证： <N>/<N>

## 部署
- 仪表板： **<Name>**（通过 Coralogix UI 打开；ID `<id>`）
- ID: `<id>`
- 文件夹: `<folder name or "root">`
- 配置文件: `<cx profile>`

打开后调整过滤器值（例如 `account_id`）。
````

---

## 参考

- 仪表板查询注意事项 & 交叉引用: [`references/query-syntax.md`](references/query-syntax.md)
- 组件 JSON 模板: [`references/widget-templates.md`](references/widget-templates.md)
- 实时验证程序: [`references/verification.md`](references/verification.md)
- 部署程序: [`references/deploy.md`](references/deploy.md)
- DataPrime 语言参考: [`references/dataprime-reference.md`](references/dataprime-reference.md)
- PromQL 参考: [`references/promql-guidelines.md`](references/promql-guidelines.md)
- 日志查询模式: [`references/logs-querying.md`](references/logs-querying.md)
- 跨度查询模式: [`references/spans-querying.md`](references/spans-querying.md)
- 内联 DataPrime 帮助: `cx dataprime list`, `cx dataprime show <command>`
- Coralogix 自定义仪表板文档: <https://www.coralogix.com/docs/user-guides/custom-dashboards/introduction/>

### 相关技能

- **`cx-observability-setup`** - 完整监控设置工作流（视图、webhooks、通知、集成）
- **`cx-slos`** - 与 SLO 连接的可靠性目标，以显示在仪表板上
- **`cx-cases`** - 对仪表板监控的服务进行分类
- **`cx-telemetry-querying`** - 在构建仪表板之前发现正确的遥测信号
