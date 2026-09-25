# Prometheus 标签策略评估器

您是 Prometheus 标签策略的专家。当被要求评估、审计、设计或改进 Prometheus 标签模式时——或者当用户询问如何在源头上防止高基数时——使用此指南提供结构化、可操作的建议。

这项技能是关于**在源头上防止不良标签**——在应用程序instrumentation和抓取*目标*标签中——以便它们永远不会进入存储。它**不是**关于在指标发出后剥离标签：在抓取时移除使序列唯一的标签会无声地破坏数据（见下文[一条规则](#一条规则-从不丢弃使序列唯一的标签)）。为了降低 Grafana Cloud 中已存在序列的成本，将用户引导至 `adaptive-metrics` 技能。为了诊断活跃的基数火灾，将用户引导至 `prometheus-cardinality-troubleshooter`。

---

## 一条规则：从不丢弃使序列唯一的标签

**您不能在抓取时移除任何使序列唯一的标签。** 无论是 `pod`，还是 `instance`，或是任何区分一个真实序列与其他序列的东西。这包括具有 `action: labeldrop` 的 `metric_relabel_configs` 以及 Alloy 中的等效 `prometheus.relabel` 规则。

看起来像是基数胜利。它不是——它**破坏了数据**，无声且永久：

- **计数器重置被混合在一起。** 当两个 pod 的计数器合并到一个序列中时，它们的独立重启会在合并的序列中交错。`rate()` 和 `increase()` 然后返回垃圾——通常*荒谬地高*的值，因为每个 pod 重启看起来都像计数器重置。
- **DPM 膨胀而不是下降。** 多个样本现在在同一抓取中落在同一个序列上——重复样本、顺序错误、样本数/分钟膨胀。人们几周后回来问“为什么我的 DPM 这么高？”或“为什么 `rate()` 返回荒谬的数字？”——在数据中**没有留下任何证据**表明它在哪里出错了。
- **聚合不正确，而不仅仅是粗糙。** 对你丢弃的标签进行 `sum` 会无声地重复计算或计算不足，具体取决于崩溃是如何发生的。

陷阱在于，这些在配置时都不会出错。管道保持运行；数字只是安静地错误，并且事后无法看到破坏点。

**正确的工具，按顺序：**

1. **从一开始就不要发出不良标签**——修复应用程序代码。这是唯一一个标签可以被*移除*而没有后果的地方，因为序列从一开始就不是基于它的唯一。
2. **对于已经流入 Grafana Cloud 而且您无法在源头上修复的序列→ Adaptive Metrics。** 这正是它的用途：它正确地聚合序列——计数器重置感知、有记录的审计跟踪，并且可逆——而不是盲目地剥离标签。将用户引导至 `adaptive-metrics` 技能。

`metric_relabel_configs` 有几个狭窄且安全的使用场景（丢弃*整个*不想要的指标；移除一个*完全重复*目标标签的标签）——涵盖在[源头预防](#4-metric_relabel_configs-narrow-safe-uses-only)中——但**通过丢弃区分性标签来降低基数绝不是其中之一。**

---

## 核心概念

**序列**是 Prometheus 中的基本单元。每个唯一的指标名称加上标签键值对组合都会创建一个新的活跃序列。太多序列 = 内存压力、慢查询、摄取压力、高账单。

**基数**= 标签可以拥有的唯一值的数量。某个指标的序列总数 ≈ 其标签基数*的乘积。具有 `path`（100 个值）、`status_code`（10 个值）、`method`（5 个值）和 `instance`（50 个值）的指标 = **每指标 250,000 个序列**。添加一个更多高基数字段通常会使计数增加 10–100 倍。

**双重影响规则**：高基数字段在两个路径上都会造成伤害：
- **摄取路径**：更多活跃序列 → 更大的头块、更大的 WAL、更多内存、更大的远程写入有效载荷、更高的 Grafana Cloud 账单（活跃序列 + DPM）
- **查询路径**：PromQL 操作符（`sum by`、`rate`、连接）必须在内存中材料化匹配的序列。高基数会使查询内存和延迟膨胀

**序列更替**是无声的杀手。如果一个标签值经常变化（部署版本、pod 名称、临时 ID），每次变化都会创建一个*新的*序列，而旧的序列仍在继续过期。每日更替率为 100% 意味着你大约携带了 2× 的稳态序列计数用于保留目的。

**针对任何提议的标签的关键问题**：“使用此指标的查询是否可靠地指定或聚合在此标签上？” 如果不 → 它不应该是标签。

---

## 标签评估框架

在审计标签集时，根据这些标准评估每个标签。

### 基数评分

| 标签示例 | 基数 | 判定 |
|---|---|---|
| `env` (prod/staging/dev) | 2–5 个值 | ✅ 良好 |
| `job` (Prometheus 抓取作业) | 5–50 个值 | ✅ 良好 |
| `cluster`、`region` | 十几个 | ✅ 良好 |
| `namespace` (K8s) | 十几个–低几百个 | ✅ 可接受 |
| `service`、`workload`、`container` | 十几个–几百个 | ✅ 可接受 |
| `instance` (host:port) | 几百个–低几千个 | ⚠️ 评估——在单个实例指标上良好，在聚合指标上风险 |
| `pod` (K8s) | 高基数+更替 = 高 | ⚠️ 对于 K8s 监控和序列唯一性是必需的——保留它。如果 `pod`-级序列太昂贵，用 Adaptive Metrics 减少；**永不**在抓取时丢弃 |
| `path` / `route` (HTTP) | 如果模板化则有限制；如果是原始 URL 则无限制 | ⚠️ 仅用于模板化值 (`/users/:id`) |
| `version`、`image_tag`、`git_sha` | 每次部署都会增长→更替 | ⚠️ 谨慎使用；考虑 info-metric 模式 |
| `user_id`、`request_id`、`trace_id` | 无限制 | ❌ 永远不作为标签——使用 exemplars |
| `customer_id`、`tenant_id` | 通常无限制 | ❌ 仅适用于小固定租户计数 |
| `error_message`、`query`、`sql` | 无限制文本 | ❌ 永远不 |

### 访问模式对齐

对于每个标签，询问：
- 查询此指标的查询是否可靠地按此标签聚合或过滤？
- 此标签是否逻辑上分割了指标，就像用户对其所想的那样？
- 是否会移除此标签，迫使用户使用 exemplars、日志或跟踪，而这对于稀有的查找情况是否可接受？

### 静态与动态标签值

- **静态/目标标签**（通过 `relabel_configs` 每次抓取目标设置一次，例如 `env=prod`、`cluster=us-east`、`team=payments`）增加的基数与*目标*成正比，而不是请求。便宜且高价值。自由使用。
- **动态/样本标签**（应用程序每条测量发出一次，例如 `status_code`、`method`、`cache_hit`）通过*值计数*乘基数。将可能的值保持在个位数或低十位数。**应用程序代码是真相来源——在 Prometheus 中修复它，而不是在 Prometheus 中修复它。**

### 一致性检查

- 标签*名称*在服务之间是否一致？（`status` vs `status_code` vs `http_status` 产生三个独立的标签系列——连接会中断）
- 标签*值*是否标准化？（`200` vs `"200"`、`GET` vs `get`、`Error` vs `error`）
- 命名约定是否一致？（Prometheus 约定是 `snake_case`，用于指标和标签名称）
- 相同概念，相同名称跨服务？（`service` vs `svc` vs `app_name`）

### 直方图桶纪律（关键，经常被忽略）

每个直方图指标都会将其基础基数乘以**（桶计数 + 3）**——通过 `_bucket{le="..."}` 的桶加上 `_sum`、`_count` 和 `_created`（Prometheus 2.39+）。

- 默认 `prometheus.DefBuckets` 有 11 个桶 → **14× 乘数**
- 具有 `method`、`path`、`status` 的直方图在添加直方图基数后成为 **14,000 个序列**
- **始终首先修剪直方图标签基数**——在直方图上，标签比计数器/仪表更重要 14×
- 考虑原生直方图（Prometheus 2.40+），它们使用单个稀疏序列而不是每个桶一个序列——对于高分辨率延迟跟踪，这是主要的基数减少

### info-metric 模式（用于高更替元数据）

当你想*知道*关于一个标签的信息（例如 `version`、`git_sha`、`image_tag`）而不需要在每个指标上为此付费时，使用 info metric：

```
# 一个低基数的计数器/仪表，值为 1，并附加元数据
app_build_info{app="payment-api", version="2.4.1", git_sha="a1b2c3"} 1
```

然后在查询时连接。经典方法是一个向量匹配与 `group_left`：
```promql
sum by (version) (
  rate(http_requests_total{app="payment-api"}[5m])
  * on (app) group_left (version) app_build_info
)
```

`version` 标签在每个构建上恰好存在于一个序列上，而不是在每个指标上。

#### `info()` 函数（更简单的连接）

PromQL 的 `info()` 函数（实验性，Prometheus 3.0+；通过 `--enable-feature=promql-experimental-functions` 启用）自动执行 info-metric 连接，因此你不必手动编写 `* on (...) group_left (...)` 匹配：

```promql
info(
  rate(http_requests_total{app="payment-api"}[5m]),
  {version=~".+"}
)
```

`info(v, [labelselector])` 接收一个范围/瞬时向量 `v`，并为每个序列找到匹配的 info 指标并添加它们的标签。可选的第二参数是限制附加哪些 info 标签的标签匹配器（在这里，仅 `version`）。默认情况下 `info()` 与 `target_info` 指标连接并匹配标识标签（例如 `instance`、`job`），因此它对 OpenTelemetry 风格的 `target_info` 特别方便。对于自定义 info 指标（如 `app_build_info`），仍然使用上面的显式 `group_left` 形式，因为它更具可移植性。

在 Prometheus 3.x 上使用时优先 `info()`；对于旧版本、自定义 info 指标或实验性功能标志未启用时，回退到显式 `group_left` 匹配。

---

## 评估输出格式

在审计标签集时，以以下结构生成报告：

```
## Prometheus 标签策略审计

### 摘要
[1-2 句话的总体评估——估计的活跃序列总数、最大风险]

### 每个标签分析
| 指标系列 | 标签 | 基数 | 用于查询？ | 判定 | 操作 |
|---|---|---|---|---|---|
| http_requests_total | path | 无限制 (原始 URL) | 有时 | ❌ 移除 | 在代码中模板化：`/users/:id` 而不是 `/users/12345` |
| http_requests_total | pod | 高基数+更替 | 很少 | ⚠️ 保留——使序列唯一 | 如果太昂贵，用 Adaptive Metrics 聚合；对于常见情况，按 `workload` 查询 |

### 直方图特定发现
[突出显示具有高标签基数的任何直方图——这些被放大 14×+]

### 估计影响
- 活跃序列减少：[X 序列 → Y 序列]
- DPM 减少：[X DPM → Y DPM]  （样本数/分钟 = 序列 × ~6 在 10 秒抓取中）
- 内存影响：[如果可测量]

### 推荐的标签集
[每个指标系列的最终推荐标签]

### 实施计划
1. [代码更改——instrumentation 卫生：停止在源头发送不良标签]
2. [抓取目标标签——relabel_configs（加性：env、cluster、team、workload）]
3. [在您无法在源头发修的序列上进行后摄取成本降低——Adaptive Metrics]
4. [记录规则以材料化有用的聚合]
```

---

## 推荐的常见目标标签

这些应作为**目标标签**（通过抓取作业的 `relabel_configs` 设置，**不是**由应用程序发出）——它们是每个目标、低基数、高查询价值：

| 标签 | 目的 | 备注 |
|---|---|---|
| `job` | Prometheus 抓取作业名称 | 由 Prometheus 自动设置 |
| `instance` | 目标端点 (`host:port`) | 由 Prometheus 自动设置；如果需要，通过 `relabel_configs` 重命名为一个更友好的值 |
| `env` | 环境 (`prod`、`staging`、`dev`) | 通过静态配置标签或服务发现设置 |
| `cluster` | 多集群区分 | 对于联合/Mimir 多租户至关重要 |
| `region` | 地理区域 | |
| `team` / `squad` | 拥有——也适用于访问控制 | |
| `service` | 逻辑服务标识 | 一个服务可能跨越多个作业 |

这些**不应**由应用程序重新发出。如果应用程序发出 `cluster` 标签，它会重复目标标签并创建冲突/`honor_labels` 决策，您不想做出。

---

## Kubernetes 模式

### 推荐标签（来自 kubernetes_sd_configs）

| 标签 | 来源 | 备注 |
|---|---|---|
| `namespace` | Pod 元数据 | 始终保留 |
| `container` | Pod spec | 低基数，对于多容器 Pod 有用 |
| `workload` | 派生：`{controller_kind}/{controller_name}` | 作为稳定的聚合键*与 `pod` 一起添加*——静态、可预测。它是一个添加，而不是替代：不要用它作为丢弃 `pod` 的借口 |
| `service` | K8s Service | 如果通过 Service 抓取 |

### 处理 `pod` 标签

`pod` 是高基数且短暂的——它每个部署和重启都会滚动，因此它主导更替和序列计数。但它也是一个使 K8s 序列唯一的标签，Kubernetes 监控（每个 pod 资源归因、kube-state-metrics 连接）依赖于它。[一条规则](#一条规则-从不丢弃使序列唯一的标签) 适用：**不要在抓取时丢弃 `pod`。** 将 pod 合并到一个序列中会混合它们的计数器重置并破坏 `rate()`。

相反：
- **添加 `workload`** (`{controller_kind}/{controller_name}`) 作为*目标*标签通过 `relabel_configs`，以便仪表板和警报可以按稳定的作业标识聚合（`sum by (workload)`）而不接触 `pod`。这是一个添加——它不丢弃任何东西。
- **不要从应用程序代码发出 `pod`**——让它来自 Kubernetes 服务发现，以便有一个确切的真实来源（见下文）。
- **如果 `pod`-级序列在 Grafana Cloud 中确实太昂贵**，用 **Adaptive Metrics** 减少，它正确地聚合 `pod` *（后摄取、计数器重置感知、可逆）* 而不是在抓取时破坏原始数据。将用户引导至 `adaptive-metrics` 技能。

### 一开始就不要将临时字段映射到标签中

**`uid`** 每次 pod 重建时都会重新生成，并且没有合法的查询用途。修复方法是**永远不要将它映射到标签中**——把它从你的 `relabel_configs` 中排除。（除非你明确针对它进行 `kubernetes_sd_configs` 输出，否则默认 `kubernetes_sd_configs` 输出不包括它。）不要试图在事后 `labeldrop` 它——那时它已经区分了序列，并且移除它就像移除任何其他唯一标签一样会破坏数据。

### 目标身份的一个来源

`instance`、`pod`、`node` 和 `host` 应来自**抓取目标标签**，而不是来自应用程序代码。如果应用程序*也*发出自己的 `instance`/`node`，你会得到重复和 `honor_labels` 冲突。修复方法是**在应用程序中**——停止发出它们——而不是在抓取时 `labeldrop`。 （移除一个*完全重复*目标标签是狭窄的唯一例外；见 [metric_relabel_configs](#4-metric_relabel_configs-narrow-safe-uses-only)。）

### kube-state-metrics 标签传播 ⚠️
- `kube_pod_labels{label_app_kubernetes_io_*=...}` 可以携带十几个元数据标签
- 每个唯一的 pod 标签组合都是一个新序列
- 通过 kube-state-metrics 的 `--metric-labels-allowlist` 在源头上进行限制——这控制了*永远*发出什么，所以它是预防，而不是破坏性的事后丢弃

---

## 源头预防：在哪里修复什么

有五个杠杆，按**优先级**排序：

### 1. 在应用程序中修复（最佳）

应用程序发出的不良标签是根本原因。示例：
- HTTP 路径：使用模板化路由 (`/users/:id`) 而不是原始路径
- 错误指标：使用一个小型枚举 (`error_type="timeout"`) 而不是错误消息字符串
- 用户范围指标：不要包含 `user_id` — 使用 exemplars 指向日志/跟踪
- 自由输入：永远不要将用户提供的字符串作为标签值发出

如果您控制代码，这始终是正确的修复。它为下游系统（Prometheus、远程写入、Mimir、Grafana Cloud）节省成本。

### 2. `relabel_configs`（目标时重新标签）

在抓取*之前*运行。用于：
- 在发现的*目标*上设置目标标签（`env`、`cluster`、`team`）
- 删除您不想抓取的*整个*目标
- 重写 `instance` 为一个友好的值
- 添加来自服务发现元数据的身份

```yaml
scrape_configs:
  - job_name: my-app
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # 从控制器元数据设置 workload
      - source_labels: [__meta_kubernetes_pod_controller_kind, __meta_kubernetes_pod_controller_name]
        target_label: workload
        separator: /
      # 从 pod 标签设置 env
      - source_labels: [__meta_kubernetes_pod_label_env]
        target_label: env
      # 仅抓取明确选择加入的 pod
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        regex: "true"
        action: keep
```

### 3. Adaptive Metrics (Grafana Cloud — 后摄取，降低基数的安全方式)

当基数是结构性时，您*无法*在源头上修复它——标签确实存在并使序列唯一，您只是不需要每个值在完整分辨率下——**Adaptive Metrics 是正确的工具，并且是降低已存在序列成本的唯一安全方式。**

它工作*在摄取之后*，作为 Grafana Cloud 中应用的聚合规则。关键在于，它正确地聚合序列：
- 它正确处理计数器重置，因此 `rate()` 和 `increase()` 保持准确。
- 它记录了被聚合的内容，因此有一个审计跟踪——您可以回答“为什么后来发生了变化？”
- 它是可逆的：删除规则，完整的分辨率序列就会回来。

这是“数据现在更便宜”（Adaptive Metrics）与“数据现在不正确”（在抓取时 `labeldrop`）之间的区别。将用户引导至 `adaptive-metrics` 技能进行规则设计。

### 4. `metric_relabel_configs`（狭窄、安全使用仅限）

在抓取*之后*、存储*之前*运行。

> ⚠️ **不要使用 `metric_relabel_configs`（或 Alloy `prometheus.relabel`）来丢弃区分序列的标签——`pod`、`instance`、`user_id`、`path`，任何东西。** 见 [一条规则](#一条规则-从不丢弃使序列唯一的标签)。它看起来像基数修复，并无声地破坏 `rate()`、膨胀 DPM、破坏聚合。使用应用程序代码（杠杆 1）或 Adaptive Metrics（杠杆 3）代替。对于*规范化*标签值（例如将 `status_code` 规范为 `2xx`）在抓取时——在代码或 via Adaptive Metrics 中，永远不要在这里做。

真正安全的使用是：

- **丢弃您永远不想存储的*整个*指标**——您正在丢弃整个指标，而不是合并不同的序列到一个序列中：
  ```yaml
  metric_relabel_configs:
    - source_labels: [__name__]
      regex: my_app_request_details
      action: drop
  ```
- **移除一个标签，它*完全重复*目标标签。** 如果应用程序发出自己的 `cluster`/`instance`，它已经来自抓取目标，目标标签仍然提供唯一性，所以移除它不会破坏任何东西。优先修复应用程序，但这是一个安全的临时措施。

这就是全部列表。如果您正在使用 `metric_relabel_configs` 来降低序列计数，您几乎肯定需要 Adaptive Metrics 而不是。
