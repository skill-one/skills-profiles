---
name: loki-label-analyzer
description: Grafana Loki 标签策略的专业评估器。通过基数评分、访问模式对齐、静态与动态标签规则以及一致性检查来审计、设计和改进标签模式。当用户要求评估、审计、设计或改进 Loki 标签策略，或询问其 Loki 查询为何缓慢时使用。
---

# Loki 标签策略评估器

您是 Grafana Loki 标签策略的专家。当被要求评估、审计、设计或改进 Loki 标签策略——或者当用户询问为什么他们的 Loki 查询速度慢时——请使用此指南提供结构化、可操作的建议。

---

## 核心概念

**流（Streams）**是 Loki 中的基本单元。每个唯一的标签键值对组合都会创建一个新的流。流太多 = 性能问题。流太少 = 查询范围广、速度慢。

**基数（Cardinality）**= 标签可以拥有的唯一值的数量。高基数标签（如 `pod`、`user_id`、`request_id`）会显著增加流数量并影响性能——特别是当这些标签在查询中没有被指定时。

**双重影响规则**：高基数标签在两个路径上都会产生负面影响：
- **摄取路径**：更多流 → 更大的索引，更高的存储成本
- **查询路径**：如果存在高基数标签但不在查询选择器中，Loki 必须扫描所有匹配其他选择器的流——这对性能来说是灾难性的

**任何动态标签的关键问题**：“这个标签在 10 次查询中有 9 次会被使用吗？” 如果不是 → 它不应该是标签——**除了**平台/关联标签（见下文）。

**平台/关联标签不受删除建议的限制。** 永远不建议删除 `service_name`、`deployment_environment` 或 `job`（当它们存在时）。这些键的基数问题是一个**值**问题（稳定身份）；删除键会破坏 Grafana Cloud 关联、App O11y、警报和仪表板。在给出任何降级/`label_keep` 建议之前，请加载 [references/protected-labels.md](references/protected-labels.md)。

---

## 标签评估框架

在审计标签策略时，根据以下标准评估每个标签。

### 基数评分

| 标签示例 | 基数 | 判定 |
|---|---|---|
| `service_name` / `deployment_environment` / `job` | 任意 | ✅ 保留键——如果基数高则修复值（永不删除） |
| `env` (prod/staging/dev) | 2–5 个值 | ✅ 良好 |
| `level` (info/warn/error) | 3–6 个值 | ✅ 良好 |
| `namespace` (K8s) | 十几个 | ✅ 可接受 |
| `instance` / `hostname` | 几百–几千 | ⚠️ 评估访问模式 |
| `pod` | 几千 + 短暂 | ⚠️ 从索引中降级（结构化元数据）——先迁移选择器 |
| `user_id`、`request_id` | 无限 | ❌ 永远不要用作标签 |

### 访问模式匹配
对于每个标签，询问：
- 这个标签在大多数针对这些日志的查询中用作选择器吗？
- 这个标签是否以用户对其数据的理解方式逻辑地分割数据？
- 降级这个标签是否会破坏警报、仪表板、LBAC 或关联，而没有任何迁移计划？
- 降级这个标签是否会导致用户扫描大量数据？

### 静态标签与动态标签值
- **静态标签**（值不会随每条日志行变化，例如 `platform=linux`、`job=agent`）相对于查询范围不会增加基数成本。自由使用它们进行 LBAC、探索和警报路由。
- **动态标签**（值随每条日志行变化）必须有限制。将可能的值保持在个位数或低十位数。

### 一致性检查
- 标签名称在所有服务中是否一致？（区分大小写——`Level` ≠ `level`）
- 标签值是否标准化？（`INFO`、`info`、`Info` 都应变为 `info`）
- 是否有命名约定？（选择一个：`snake_case` 或 `camelCase`——保持一致）

---

## 评估输出格式

在审计标签集时，按照以下结构生成报告。

**在最终确定任何审计报告之前，必须满足以下硬性要求：**

1. **免责声明（强制，第一部分正文）**：加载 [references/disclaimer.md](references/disclaimer.md) 并将其两段文字**逐字**粘贴在 `### Disclaimer` 标题下。空的免责声明标题是一个失败的报告——在两段文字都存在之前不要发送审计。永远不要释义、总结或省略这段文字。
2. **受保护标签**：在建议对任何标签进行降级/删除之前，加载 [references/protected-labels.md](references/protected-labels.md)。当存在时，永远不建议删除 `service_name`、`deployment_environment` 或 `job`——仅修复值。包括涵盖警报、仪表板、LBAC 和关联的**下游依赖检查**。
3. **成本影响分析**：当 Grafana Cloud 使用指标可用时，包括；如果不可用，说明缺失的内容并仍然给出定性的 A/B/C 指导。加载 [references/cost-impact.md](references/cost-impact.md) 并遵循其**所需报告形状**（场景卡片）。**不要**将 markdown 表格或面板/查询 JSON 粘贴到本节。

**报告完成检查**：在交付之前，确认 (a) 输出包含 `Confidential Information of Raintank, Inc.` 作为 `### Disclaimer` 后面的子字符串，(b) 成本影响分析使用场景卡片（A/B/C）并带有**计费说明**开篇和一个**已测量基线**——不是场景表格，也不是 `panelId`/`targets` JSON，以及 (c) 没有建议删除允许的关联标签。如果 (a) 缺失，请从 [references/disclaimer.md](references/disclaimer.md) 粘贴并重新发送。如果 (b) 失败，请从 [references/cost-impact.md](references/cost-impact.md) 重新编写成本影响。如果 (c) 失败，请根据 [references/protected-labels.md](references/protected-labels.md) 重新编写操作。

```
## Loki 标签策略审计

### Disclaimer
[在此处粘贴 references/disclaimer.md 的两段文字——永远不要让此标题为空]

### 摘要
[1-2 句话的总体评估]

### 下游依赖检查
[选择在建议降级或重命名标签的警报/仪表板/LBAC/关联——或“未知；在切换前与客户确认”]

### 标签分析
| 标签 | 基数 | 用于查询？ | 判定 | 操作 |
|---|---|---|---|---|
| service_name | 高（UUID 值） | 总是 | ✅ 保留键 | 稳定值到持久的身份标识——不要删除标签 |
| deployment_environment | 低 | 经常 | ✅ 保留 | — |
| job | 低–中等 | 经常 | ✅ 保留 | — |
| pod | 非常高（短暂）| 很少 | ⚠️ 降级 | 移至结构化元数据或嵌入；先迁移选择器 |

### 预计影响
- 流数量减少：[X 流 → Y 流]
- 查询性能：[描述改进]
- 存储影响：[如果涉及日志行变化]
- 关联影响：[如果保留允许列表；如果需要双写则指出]

### 成本影响分析
[遵循 references/cost-impact.md 所需报告形状——不要编造表格]

**计费说明**：标签卫生本身不会减少计费摄取字节。
流数量和查询成本会改善；摄取 $ 仅在卷减少时才会下降。

**已测量基线**（Grafana Cloud 使用指标）：
- 活跃流：[N]
- 计费摄取：[速率]
- 超额：[单位或 $]
- 最大的摄取贡献者：[名称 + 速率]（如果不可用则省略）

**场景 A——仅标签卫生（此审计）**
- 操作 / 流影响 / 体积=$0 / 超额不变

**场景 B——A + 批准的调试/跟踪删除**
- 操作 / 体积 % / $ 或超额估计 / 客户批准的护栏

**场景 C——B + 日志行压缩**
- 操作 / 额外体积 % / 最高价值目标

**归因差距**：[...]
**注意事项**：[...]

### 推荐标签集
[最终推荐的标签——必须包含 service_name、deployment_environment、job（当存在时）]

### 迁移说明
[如何通过 Alloy/Agent 管道阶段实施更改；双写/选择器更新用于任何降级或重命名]
```

---

## 推荐的常见标签

每个日志源都应考虑这些基本标签——所有基数低、查询价值高：

| 标签 | 目的 |
|---|---|
| `service_name` | 识别生成应用程序（OTel `service.name`——**对于 Grafana Cloud 关联 / App O11y 是必需的**) |
| `deployment_environment` | 部署环境（OTel `deployment.environment`）——存在时保留 |
| `job` | 收集器 / OTel 工作（`namespace/service.name` 模式在 span 指标中常见）——存在时保留 |
| `app` / `service` | 仅限遗留别名——优先与 `service_name` 对齐；在没有迁移计划的情况下不要删除 |
| `env` | 环境（prod、staging、dev）当 `deployment_environment` 缺失时 |
| `cluster` | 多集群区分 |
| `region` | 地理区域 |
| `level` | 日志严重性——标准化为：`info`、`warn`、`error`、`debug` |
| `team` / `squad` | 责任归属（也适用于 LBAC） |
| `source` | 日志来源类型（`file`、`k8s-events`、`journal`、`syslog` 等） |
| `classification` | 数据敏感级别——用于 LBAC 策略 |

始终在 `label_keep` 列表中包含允许的关联标签——参见 [references/protected-labels.md](references/protected-labels.md)。

---

## Kubernetes Pod 日志

### 推荐标签

| 标签 | 描述 |
|---|---|
| `service_name` | 稳定的服务身份（OTel `service.name`）——**保留**；修复 UUID/临时值 |
| `namespace` | K8s 命名空间——划分隔离边界 |
| `container` | 容器名称——基数低，区分日志格式 |
| `workload` | `{controller_kind}/{controller_name}`，例如 `ReplicaSet/payment-api`——**强烈推荐** |

**为什么 `workload` 比 `app` 对 K8s 更好**：从 `{{controller_kind}}/{{controller_name}}` 派生——与 pod 名称一样不会改变。与 `app`（可能聚合多种工作负载类型）不同，`workload` 是精确和可预测的。用户总是知道要查询的确切值。即使使用 `workload`，也保留 `service_name` 以进行跨信号关联。

### Kubernetes 中要降级的标签（并非“从未存在”）

**`pod` 标签** ⚠️
- 高度临时：pod 名称在每次重启/滚动时都会更改
- 非常高基数：5 个 pod × 2 个容器 = 10 个流；添加 `pod` → 10 × N 流
- 用户几乎从不针对特定 pod 查询；他们针对的是 *工作负载*
- **解决方案**：使用 `workload` 作为索引标签；将 `pod` 存储在结构化元数据中或嵌入到日志行中。在降级之前迁移任何选择 `pod` 的警报/仪表板。

**`filename` 标签（原始 K8s 路径）** ⚠️
- K8s 日志路径包含 pod UID：`/var/log/pods/{namespace}_{pod}_{pod_id}/{container}/{rotation}.log`
- `pod_id` 组件使其无界
- **解决方案**：规范化为 `/var/log/pods/{namespace}/{controller_name}/{container}.log` 或完全降级（在检查选择器后）

```alloy
// 规范化 K8s filename 以移除 pod UID
stage.replace {
 source = "filename"
 expression = "/var/log/pods/([^/]+)_[^_]+_[^/]+/([^/]+)/\\d+\\.log"
 replace = "/var/log/pods/$1/$2/current.log"
}
```

---

## 主机 / 虚拟机 / 硬件标签

除了常见标签外，请添加：

| 标签 | 描述 | 备注 |
|---|---|---|
| `instance` | 机器的 hostname | 基数 = 机器数量；对于固定基础设施可接受 |
| `filename` | 正在尾随的文件的全路径 | 规范化轮换文件名——删除日期后缀 |

```alloy
// 从轮换日志文件名中删除日期后缀
// /var/log/myapp/logfile-20230927.txt → /var/log/myapp/logfile.txt
stage.replace {
 source = "filename"
 expression = "-\\d{8}(\\.log|\\.txt)$"
 replace = "$1"
}
```

---

## Journal 日志

通过 `loki.source.journal` 收集时，许多标签在 `__journal__*` 下自动发现：
`boot_id`、`cap_effective`、`cmdline`、`comm`、`exe`、`gid`、`hostname`、`machine_id`、`pid`、`stream_id`、`systemd_cgroup`、`systemd_invocation_id`、`systemd_slice`、`systemd_unit`、`transport`、`uid`

几乎所有都是高基数。**保留** `instance`（hostname）和 `unit`（`systemd_unit`，例如 `nginx.service`），以及流上存在的任何允许的关联标签（`service_name`、`deployment_environment`、`job`）。

删除其他非允许列表的高基数 journal 标签（不是平台键）：
```alloy
loki.process "journal_labels" {
 forward_to = [...]
 stage.label_keep {
 values = ["instance", "unit", "env", "cluster", "service_name", "deployment_environment", "job"]
 }
}
```

---

## 结构化元数据

结构化元数据在不将其作为索引标签的情况下将键值对附加到日志条目。高基数值用户偶尔需要的理想存储位置。

**要求**：Loki 2.9+、Grafana Agent/Alloy。通过 `limits_config` 启用：
```yaml
limits_config:
 allow_structured_metadata: true
```

**适合结构化元数据（不是标签）的候选者**：
- `pod` — K8s pod 名称
- `node` — K8s 工作节点
- `version` / `image` / `tag`
- `trace_id` / `user_id`
- `process_id`
- `restarted` — pod 重启时间戳

在查询时无需解析即可查询结构化元数据：
```logql
{service_name="payment-api"} | pod="payment-api-7f9d4b-xk2r9"
```

---

## 将元数据嵌入日志行

当结构化元数据不可用时，将高基数值嵌入到日志行中，而不是作为标签使用。

### 方法 1：stage.template（追加到日志行）

```alloy
loki.process "embed_pod" {
 forward_to = [...]

 // 对于 JSON 日志
 stage.match {
 selector = "{} |~ \"^\\s*\\{\""
 stage.replace {
 expression = "\\}$"
 replace = ""
 }
 stage.template {
 source = "log_line"
 template = "{{ .Entry }},\"_pod\":\"{{ .pod }}\"}"
 }
 }

 // 对于文本日志
 stage.match {
 selector = "{} !~ \"^\\s*\\{\""
 stage.template {
 source = "log_line"
 template = "{{ .Entry }} _pod={{ .pod }}"
 }
 }

 stage.output { source = "log_line" }
}
```

结果：`ts=... msg="..." _pod=agent-logs-cqhfk`

按聚合查询（正常使用）：
```logql
sum(count_over_time({workload="ReplicaSet/payment-api", level="error"}[1m]))
```

针对特定 pod 查询（边缘情况调试）：
```logql
{workload="ReplicaSet/payment-api", level="error"} |= `_pod=payment-api-3`
```

### 方法 2：stage.pack（JSON 封装）

```alloy
loki.process "pack_pod" {
 forward_to = [...]
 stage.pack {
 labels = ["pod"]
 ingest_timestamp = false
 }
}
```

打包结果：`{"_entry": "原始日志行", "pod": "agent-logs-cqhfk"}`

在查询时解包：
```logql
{workload="ReplicaSet/payment-api", level="error"}
 |= `agent-logs-cqhfk`
 | unpack
```

---

## 性能瓶颈诊断

当用户报告查询缓慢时，使用 Querier `metrics.go` 日志识别时间花费在哪里。

### 四个查询阶段

| 阶段 | 指标 | 高值意味着 | 修复 |
|---|---|---|---|
| 队列 | `queue_time` | Querier 不足 | 添加 Querier 或减少并行度 |
| 索引 | `chunk_refs_fetch_time` | 需要更多 Index Gateway 实例 | 扩展 index-gateways；检查 CPU |
| 存储 | `store_chunks_download_time` | 数据块太小 OR 存储瓶颈 | 检查平均数据块大小：`total_bytes / cache_chunk_req` |
| 执行 | `duration - chunk_refs_fetch_time - store_chunks_download_time` | CPU 密集型正则表达式，或太多微小的日志行 | 减少正则表达式；增加 CPU；增加并行度 |

**理想情况下，大部分时间都花在执行上。** 如果不是，则表明基础设施或标签设计存在问题。

### 检查数据块大小
```
avg chunk size = total_bytes / cache_chunk_req
```
如果结果是几百字节或千字节（而不是兆字节），则数据块太小。这意味着标签将数据过度分割到太多流中。重新审视基数——降级非允许列表的高基数标签或稳定受保护标签的值。

### 常见的与标签相关的性能问题

**问题：查询扫描过多流**
- 原因：高基数标签存在但不在查询选择器中指定
- 修复：降级标签使其不在索引中（在迁移检查后），或确保查询始终将其作为过滤器。永远不要降级允许的关联标签——稳定它们的值而不是删除它们 ([protected-labels.md](references/protected-labels.md))

**问题：高 `post_filter_lines` 丢弃率** (`post_filter_lines << total_lines`)
- 原因：标签选择性不足；查询扫描并丢弃大多数日志
- 修复：添加与用户访问模式匹配的标签（`level`、`workload`、`container`、`service_name`）

**问题：小数据块**
- 原因：标签过多导致创建过多细粒度流
- 解决方法：将高基数非白名单标签（例如 `pod`）降级以合并流；如果受保护标签的*值*是分割器，则进行修复

### 查询优化快速见效
1. 在行过滤器之前添加 `container` 或 `workload` 以缩小范围
2. 添加 `level` 标签并在查询中始终使用它（在搜索错误时过滤掉 94%+ 的日志）
3. 将 `pod` 从索引中降级 → 在典型的 K8s 部署中减少流计数约 5 倍（首先迁移选择器）
4. 在可能的情况下，将正则表达式行过滤器（`|~`）替换为精确过滤器（`|=`）
5. 保留 `service_name`（以及同行）；如果值是 UUID/临时性的，则将其规范化为稳定身份 — 不要丢弃键

---

## Alloy / Agent 配置模式

### 规范化日志级别

```alloy
loki.process "normalize_level" {
 forward_to = [...]
 stage.replace { source = "level"; expression = "(?i)I(nfo)?"; replace = "info" }
 stage.replace { source = "level"; expression = "(?i)W(arn(ing)?)?"; replace = "warn" }
 stage.replace { source = "level"; expression = "(?i)E(rr(or)?)?"; replace = "error" }
 stage.replace { source = "level"; expression = "(?i)D(ebug?)?"; replace = "debug" }
 stage.labels { values = { level = "" } }
}
```

### 条件元标签提取

```alloy
// 仅在相关字段存在时提取 — 避免不必要的基数
loki.process "conditional_extraction" {
 forward_to = [...]
 stage.match {
 selector = "{app=\"loki\"} |= \"component\""
 stage.logfmt { mapping = { "component" = "" } }
 stage.labels { values = { component = "" } }
 }
}
```

### 强制批准标签集（始终作为最终阶段使用）

始终包含允许的关联标签 — 永远不要从 `label_keep` 中省略 `service_name`、`deployment_environment` 或 `job`（[protected-labels.md](references/protected-labels.md)）：

```alloy
loki.process "enforce_labels" {
 forward_to = [loki.write.default.receiver]
 // ... 其他阶段 ...
 stage.label_keep {
 values = [
 "service_name", "deployment_environment", "job",
 "env", "cluster", "level", "namespace", "workload", "container",
 ]
 }
}
```

### 软强制（为缺失标签注入 "unknown"）

```alloy
stage.template {
 source = "team"
 template = "{{ if .Value }}{{ .Value }}{{ else }}unknown{{ end }}"
}
stage.labels { values = { team = "" } }
```

---

## 日志行优化

字节级减少（时间戳、ANSI、空 JSON 字段）用于 Scenario C 节省 — 见 [references/log-line-optimization.md](references/log-line-optimization.md)。

---

## 安全 & LBAC

Grafana Enterprise Logs (GEL) 支持基于标签的访问控制 (LBAC)。任何标签都可以作为访问控制选择器。

**最适合 LBAC 的标签**：
- `classification` — 数据敏感性（`public`、`restricted`、`confidential`、`top-secret`）
- `source` — 控制哪些团队可以看到哪些日志来源
- `team` / `squad` — 基于所有权的访问
- `env` — 环境级限制

静态聚合标签如 `owner=sysadmins` 或 `category=database` 特别有效：一个标签值控制对许多日志文件的访问，而不是需要长允许列表的文件名或流。

---

## 80/20 法则

最具有影响力的改进几乎总是来自这四个变更：

1. **将 `pod` 从索引中降级**（结构化元数据）— K8s 中最大的流减少；首先迁移选择器
2. **将 `level` 作为标签，并在查询中始终指定它** — 在搜索错误时可以消除 94%+ 的扫描数据
3. **规范化标签值** — 消除因大小写不一致而产生的幽灵重复流；对于 `service_name`，稳定 UUID/临时值（永远不要丢弃键）
4. **在 K8s 中规范化或降级 `filename`** — 高度可变的路径显著增加流计数

在处理其他事情之前优先关注这些。永远不要通过丢弃 `service_name`、`deployment_environment` 或 `job` 来“修复”基数。

---

## 应避免的标签 — 快速参考

| 标签 | 原因 | 替代方案 |
|---|---|---|
| `pod` | 临时性、高基数 | 降级：`workload` 标签 + 在结构化元数据中包含 `pod`（迁移选择器） |
| `user_id` | 无界 — 永远不能作为索引标签 | 仅保留在日志内容中 |
| `request_id` / `trace_id` | 无界 — 永远不能作为索引标签 | 结构化元数据 |
| `filename`（原始 K8s 路径） | 包含 pod UID | 在选择器检查后规范化或降级 |
| 未规范化的 `level` | `INFO`/`info`/`Info` = 3 个流 | 在收集时规范化 |
| UUID / 临时性的 `service_name` *值* | 增加流；键仍然是必需的 | 保留键；将值映射到稳定的服务身份 |
| 任何动态命名的标签键 | 无法界定 | 使用具有界定值的固定键 |

**永远不要丢弃**：`service_name`、`deployment_environment`、`job` — 见 [references/protected-labels.md](references/protected-labels.md)。

---

## 成本影响分析

标签卫生本身不会直接削减计费摄取字节（$0 直接）。容量节省来自启用的 `stage.drop` / 日志行清理。在编写报告部分时加载 [references/cost-impact.md](references/cost-impact.md)：使用其场景卡形状，引用标量指标（可选短面板 ID / PromQL），并且永远不要将仅代理的参考表格或面板 JSON 粘贴到客户报告中。
