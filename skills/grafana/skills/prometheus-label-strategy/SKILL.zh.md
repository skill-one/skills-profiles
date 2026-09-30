---
name: prometheus-label-strategy
description: Grafana Cloud上的Prometheus标签策略专家评估员。通过基数评分、访问模式对齐、静态与动态标签规则、直方图桶规范以及仪器卫生等手段，审计、设计和优化标签模式。从源头上防止高基数——在应用程序代码和抓取目标标签中——同时不丢弃使时间序列唯一的标签（这会破坏数据）。为降低已存在于Grafana Cloud中的时间序列成本，将路由至自适应指标技能。当用户要求评估、审计、设计或优化Prometheus标签，或询问如何从源头上防止高基数时使用。对于“为什么我的Prometheus现在变慢/变贵了”的紧急处理，请参考prometheus-cardinality-troubleshooter。
---

# Prometheus 标签策略评估器

您是 Prometheus 标签策略的专家。当被要求评估、审计、设计或改进 Prometheus 标签模式时——或者当用户询问如何防止源端出现高基数时——使用此指南提供结构化、可操作的建议。

这项技能是关于**在源端防止不良标签**——在应用程序instrumentation和抓取*目标*标签中——以便它们永远不会进入存储。它**不是**关于在指标发出后剥离标签：在抓取时移除使序列唯一的标签会无声地破坏数据（见下文[一条规则](#一条规则-永远不要移除使序列唯一的标签)）。要减少 Grafana Cloud 中现有序列的成本，请将用户引导至 `adaptive-metrics` 技能。要诊断活跃的基数火灾，请引导至 `prometheus-cardinality-troubleshooter`。

---

## 一条规则：永远不要移除使序列唯一的标签

**您不能在抓取时移除任何使序列唯一的标签。** 无论是 `pod`、`instance` 还是任何区分一个真实序列与其他序列的标签。这包括具有 `action: labeldrop` 的 `metric_relabel_configs` 以及 Alloy 中的等效 `prometheus.relabel` 规则。

看起来像是基数胜利。它不是——它**破坏了数据**，无声且永久：

- **计数器重置会被混合在一起。** 当两个 Pod 的计数器合并到一个序列中时，它们的独立重启会在合并的序列上交错。`rate()` 和 `increase()` 然后返回垃圾——通常是*荒谬地高*的值，因为每个 Pod 重启都看起来像计数器重置。
- **DPM 会膨胀而不是下降。** 多个样本现在在同一抓取中落在一个序列上——重复样本、顺序错误、样本每分钟膨胀。人们几周后回来问“为什么我的 DPM 这么高？”或“为什么 `rate()` 返回荒谬的数字？”——在数据中**没有留下任何证据**表明它在哪里出错了。
- **聚合是错误的，而不仅仅是粗糙的。** 对你移除的标签进行 `sum` 会根据合并的方式无声地重复计算或计数不足。

陷阱在于，这些都不会在配置时出错。管道保持运行；数字只是安静地错误，并且事后无法看到破坏点。

**正确的工具，按顺序：**

1. **从一开始就不要发出不良标签**——修复应用程序代码。这是唯一一个标签可以被*移除*而没有后果的地方，因为序列从一开始就没有在这个标签上唯一。
2. **对于已经流入 Grafana Cloud 且您无法在源端修复的序列→ Adaptive Metrics。** 这正是它的用途：它正确地聚合序列——计数器重置感知、有记录的审计跟踪，并且可逆——而不是盲目地剥离标签。将用户引导至 `adaptive-metrics` 技能。

`metric_relabel_configs` 有几个狭窄、安全的使用场景（移除*整个*不想要的指标；移除一个与目标标签*完全重复*的标签）——涵盖在[源端预防](#4-metric_relabel_configs-narrow-safe-uses-only)中——但**通过移除区分标签来降低基数绝不是其中之一。**

---

## 核心概念

**序列**是 Prometheus 中的基本单元。每个唯一的指标名称加上标签键值对组合都会创建一个新的活动序列。太多序列 = 内存压力、慢查询、摄取压力、高账单。

**基数**= 标签可以拥有的唯一值的数量。某个指标的序列总数 ≈ 其标签上基数的*乘积*。一个具有 `path`（100 个值）、`status_code`（10 个值）、`method`（5 个值）和 `instance`（50 个值）的指标 = **每个指标 250,000 个序列**。添加一个高基数标签通常会使计数增加 10–100 倍。

**双重影响规则**：高基数标签在两个路径上都会造成伤害：
- **摄取路径**：更多活动序列→更大的头块、更大的 WAL、更多内存、更大的 remote_write 负载、更高的 Grafana Cloud 账单（活动序列 + DPM）
- **查询路径**：PromQL 操作符（`sum by`、`rate`、连接）必须在内存中物化匹配的序列。高基数会使查询内存和延迟膨胀

**序列更替**是无声的杀手。如果一个标签值经常变化（部署版本、Pod 名称、临时 ID），每次变化都会创建一个*新的*序列，而旧的序列仍在继续老化。每日更替率为 100% 意味着你为了保留目的大约携带了 2× 的稳态序列计数。

**对于任何拟议标签的关键问题**：“使用此指标的查询是否可靠地指定或聚合在此标签上？” 如果不——它**不应该是**一个标签。

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
| `instance` (host:port) | 几百个–低几千个 | ⚠️ 评估——在单个实例指标上很好，在聚合指标上风险高 |
| `pod` (K8s) | 高基数+瞬态 = 高更替 | ⚠️ 对于 K8s 监控和序列唯一性是必需的——保留它。如果 `pod` 级别的序列太昂贵，用 Adaptive Metrics 减少它们；**永远**不要在抓取时移除 |
| `path` / `route` (HTTP) | 如果模板化则有限制；如果是原始 URL 则无限制 | ⚠️ 仅在模板化值（`/users/:id`）时使用 |
| `version`、`image_tag`、`git_sha` | 每次部署都会增长→更替 | ⚠️ 适量使用；考虑 info-metric 模式 |
| `user_id`、`request_id`、`trace_id` | 无限制 | ❌ 永远不要作为标签——使用 exemplars |
| `customer_id`、`tenant_id` | 通常无限制 | ❌ 仅适用于小固定租户计数时可接受 |
| `error_message`、`query`、`sql` | 无限制文本 | ❌ 永远不要 |

### 访问模式对齐

对于每个标签，询问：
- 查询此指标的查询是否可靠地按此标签聚合或过滤？
- 此标签是否以用户对其理解的方式逻辑地划分指标？
- 移除此标签是否会使用户被迫使用 exemplars、日志或跟踪——这对于罕见查找情况是否可接受？

### 静态与动态标签值

- **静态/目标标签**（通过 `relabel_configs` 每次抓取目标设置一次，例如 `env=prod`、`cluster=us-east`、`team=payments`）按*目标*增加基数，而不是按请求。廉价且高价值。自由使用。
- **动态/样本标签**（应用程序每测量一次发出一次，例如 `status_code`、`method`、`cache_hit`）按*值计数*乘基数。将可能的值保持在个位数或低十位数。**应用程序代码是真相来源——在 Prometheus 中修复它，而不是在 Prometheus 中修复它。**

### 一致性检查

- 标签*名称*在服务之间是否一致？（`status` vs `status_code` vs `http_status` 产生三个独立的标签系列——连接会中断）
- 标签*值*是否标准化？（`200` vs `"200"`，`GET` vs `get`，`Error` vs `error`）
- 命名约定是否一致？（Prometheus 约定是 `snake_case` 用于指标和标签名称）
- 相同的概念，相同的名称跨服务？（`service` vs `svc` vs `app_name`）

### 直方图桶纪律（关键，经常被忽略）

每个直方图指标都会将其基础基数乘以**（桶数 + 3）**——通过 `_bucket{le="..."}` 的桶加上 `_sum`、`_count` 和 `_created`（Prometheus 2.39+）。

- 默认 `prometheus.DefBuckets` 有 11 个桶 → **14× 乘数**
- 一个具有 `method`、`path`、`status` 的直方图已经达到 1,000 个序列，在添加直方图基数后会变成 **14,000 个序列**
- **始终首先修剪直方图标签基数**——在直方图上，标签比计数器/仪表的价值高 14 倍
- 考虑原生直方图（Prometheus 2.40+），它们使用单个稀疏序列而不是每个桶一个序列——对于高分辨率延迟跟踪，这是大幅降低基数的关键

### info-metric 模式（用于高更替元数据）

当你想*知道*关于一个标签（例如 `version`、`git_sha`、`image_tag`）而不想在每个指标上为此付费时，使用 info metric：

```
# 一个低基数的计数器/仪表，其值为 1，并附加了元数据
app_build_info{app="payment-api", version="2.4.1", git_sha="a1b2c3"} 1
```

然后在查询时连接。经典方法是用 `group_left` 的向量匹配：
```promql
sum by (version) (
  rate(http_requests_total{app="payment-api"}[5m])
  * on (app) group_left (version) app_build_info
)
```

`version` 标签在每个构建上只存在于一个序列上，而不是每个指标上。

#### `info()` 函数（更简单的连接）

PromQL 的 `info()` 函数（实验性，Prometheus 3.0+；通过 `--enable-feature=promql-experimental-functions` 启用）自动化了 info-metric 连接，因此你不必手动编写 `* on (...) group_left (...)` 匹配：

```promql
info(
  rate(http_requests_total{app="payment-api"}[5m]),
  {version=~".+"}
)
```

`info(v, [labelselector])` 接受一个范围/瞬时向量 `v`，并为每个序列找到匹配的 info 指标并添加它们的标签。可选的第二参数是限制附加哪些 info 标签的标签匹配器（这里，仅 `version`）。默认情况下，`info()` 与 `target_info` 指标连接并匹配识别标签（例如 `instance`、`job`），因此它对 OpenTelemetry 风格的 `target_info` 特别方便。对于自定义 info 指标（如 `app_build_info`），仍应使用上面显式的 `group_left` 形式，因为它更具可移植性。

当你在 Prometheus 3.x 上并连接到 `target_info` 时，请优先使用 `info()`；对于旧版本、自定义 info 指标或实验性功能标志未启用时，请回退到显式的 `group_left` 匹配。

---

## 评估输出格式

在审计标签集时，以以下结构生成报告：

```
## Prometheus 标签策略审计

### 摘要
[1-2 句话的整体评估——总估计活动序列，最大风险]

### 每个标签分析
| 指标系列 | 标签 | 基数 | 用于查询？ | 判定 | 操作 |
|---|---|---|---|---|---|
| http_requests_total | path | 无限制（原始 URL） | 有时 | ❌ 移除 | 在代码中模板化：`/users/:id` 而不是 `/users/12345` |
| http_requests_total | pod | 高+更替 | 很少 | ⚠️ 保留——它使序列唯一 | 如果太昂贵，用 Adaptive Metrics 聚合它们；**永远**不要在抓取时移除 |
| | | | | | | 如果常见情况下按 `workload` 查询 |

### 直方图特定发现
[突出显示具有高标签基数的任何直方图——这些会被 14×+ 放大]

### 预计影响
- 活动序列减少：[X 序列 → Y 序列]
- DPM 减少：[X DPM → Y DPM]  （每分钟样本 = 序列 × ~6 在 10 秒抓取时）
- 内存影响：[如果可测量]

### 推荐的标签集
[每个指标系列最终推荐的标签]

### 实施计划
1. [代码更改——instrumentation 卫生：在源端停止发出不良标签]
2. [抓取目标标签——relabel_configs（加性：env、cluster、team、workload）]
3. [在您无法在源端修复的序列上减少后摄入成本——Adaptive Metrics]
4. [记录规则以物化有用的聚合]
```

---

## 推荐的常见目标标签

这些应作为**目标标签**（通过抓取作业上的 `relabel_configs` 设置，**不是**由应用程序发出）——它们是按目标设置的，低基数，高查询价值：

| 标签 | 目的 | 备注 |
|---|---|---|
| `job` | Prometheus 抓取作业名称 | 由 Prometheus 自动设置 |
| `instance` | 目标端点 (`host:port`) | 由 Prometheus 自动设置；如果需要，可以通过 `relabel_configs` 重命名为一个更友好的值 |
| `env` | 环境 (`prod`、`staging`、`dev`) | 通过静态配置标签或服务发现设置 |
| `cluster` | 多集群区分 | 对于联合/Mimir 多租户至关重要 |
| `region` | 地理区域 | |
| `team` / `squad` | 所有者——也适用于访问控制 | |
| `service` | 逻辑服务标识 | 一个服务可能跨越多个作业 |

这些**不应**由应用程序重新发出。如果应用程序发出 `instance`/`node`，则会产生重复和 `honor_labels` 冲突。修复方法是在**应用程序**中——停止发出它们——而不是在抓取时 `labeldrop`。 （移除一个与目标标签*完全重复*的标签是狭窄的唯一例外；见 [metric_relabel_configs](#4-metric_relabel_configs-narrow-safe-uses-only)。）

---

## Kubernetes 模式

### 推荐标签（来自 kubernetes_sd_configs）

| 标签 | 来源 | 备注 |
|---|---|---|
| `namespace` | Pod 元数据 | 总是保留 |
| `container` | Pod spec | 低基数，对多容器 Pod 有用 |
| `workload` | 派生：`{controller_kind}/{controller_name}` | 作为稳定的聚合键*与 `pod` 一起添加*——静态、可预测。它是一个添加，而不是替代：不要用它作为移除 `pod` 的借口 |
| `service` | K8s Service | 如果通过 Service 抓取 |

### 处理 `pod` 标签

`pod` 是高基数且瞬态的——它在每次部署和重启时都会滚动，因此它主导更替和序列计数。但它也是一个使 K8s 序列唯一的标签，Kubernetes 监控（每个 Pod 资源归因、kube-state-metrics 连接）依赖于它。[一条规则](#一条规则-永远不要移除使序列唯一的标签)适用：**不要在抓取时移除 `pod`。** 将 Pod 合并到一个序列中会混合它们的计数器重置并破坏 `rate()`。

相反：
- **添加 `workload`** (`{controller_kind}/{controller_name}`) 作为*目标*标签通过 `relabel_configs`，以便仪表板和警报可以按稳定的作业标识符聚合（`sum by (workload)`）而不接触 `pod`。这是添加——它不会移除任何东西。
- **不要从应用程序代码中发出 `pod`** —— 让它来自 Kubernetes 服务发现，这样只有一个真相来源（见下文）。
- **如果 `pod` 级别的序列在 Grafana Cloud 中确实太昂贵**，用 **Adaptive Metrics** 减少它们，它正确地聚合 `pod` *后摄入*（计数器重置感知、可逆）而不是在抓取时破坏原始数据。引导至 `adaptive-metrics` 技能。

### 一开始就不要将临时字段映射到标签中

**`uid`** 在每个 Pod 重建时都会重新生成，并且没有合法的查询用途。修复方法是在**一开始就**不要将它映射到标签中——把它从你的 `relabel_configs` 中排除。（它不在默认的 `kubernetes_sd_configs` 输出中，除非你明确针对它）。不要试图在事后 `labeldrop` 它——那时它已经区分了序列，并且移除它就像移除任何其他唯一标签一样会破坏数据。

### 目标身份的一个来源

`instance`、`pod`、`node` 和 `host` 应来自**抓取目标标签**，而不是应用程序代码。如果应用程序*也*发出自己的 `instance`/`node`，则会产生重复和 `honor_labels` 冲突。修复方法是在**应用程序**中——停止发出它们——而不是在抓取时 `labeldrop`。（移除一个与目标标签*完全重复*的标签是狭窄的唯一例外；见 [metric_relabel_configs](#4-metric_relabel_configs-narrow-safe-uses-only)。）

### kube-state-metrics 标签传播 ⚠️
- `kube_pod_labels{label_app_kubernetes_io_*=...}` 可以携带十几个元数据标签
- 每个唯一的 Pod 标签组合都是一个新序列
- 在源端使用 kube-state-metrics 的 `--metric-labels-allowlist` 限制——这控制了*永远*发出什么，所以它是预防，而不是破坏性的事后移除

---

## 源端预防：在哪里修复什么

有五个杠杆，按**优先级**排序：

### 1. 在应用程序中修复（最佳）

由应用程序发出的不良标签是根本原因。示例：
- HTTP 路径：使用模板化路由（`/users/:id`）而不是原始路径
- 错误指标：使用一个小枚举（`error_type="timeout"`）而不是错误消息字符串
- 用户范围指标：不要包括 `user_id` —— 使用 exemplars 指向日志/跟踪
- 自由形式输入：永远不要将用户提供的字符串作为标签值发出

如果您控制代码，这始终是正确的修复方法。它为下游系统（Prometheus、remote_write、Mimir、Grafana Cloud）节省成本。

### 2. `relabel_configs` (目标时间重标记)

在抓取之前运行。用于：
- 为发现的目标设置目标标签（`env`、`cluster`、`team`）
- 删除您不想抓取的整个目标
- 将 `instance` 重写为友好的值
- 从服务发现元数据中添加身份信息

```yaml
scrape_configs:
  - job_name: my-app
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # 从控制器元数据设置工作负载
      - source_labels: [__meta_kubernetes_pod_controller_kind, __meta_kubernetes_pod_controller_name]
        target_label: workload
        separator: /
      # 从 Pod 标签设置环境
      - source_labels: [__meta_kubernetes_pod_label_env]
        target_label: env
      # 仅抓取明确选择加入的 Pod
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        regex: "true"
        action: keep
```

### 3. 自适应指标（Grafana Cloud — 抓取后，减少基数的安全方法）

当基数是结构性且您无法在源处修复时——标签确实存在并使序列唯一，您只是不需要每个值的全分辨率——**自适应指标是正确的工具，也是减少已存在序列成本的唯一安全方法。**

它在抓取后工作，作为 Grafana Cloud 中应用的聚合规则。关键在于，它正确地聚合序列：
- 它正确处理计数器重置，因此 `rate()` 和 `increase()` 保持准确。
- 它记录了聚合的内容，因此有审计记录——您可以在之后回答“为什么这个改变了？”。
- 它是可逆的：删除规则，全分辨率序列就会回来。

这是“数据现在更便宜”（自适应指标）和“数据现在错误”（抓取时的 `labeldrop`）之间的区别。将用户引导至 `adaptive-metrics` 技能进行规则设计。

### 4. `metric_relabel_configs` (仅限狭窄、安全用途)

在抓取后、存储前运行。

> ⚠️ **不要使用 `metric_relabel_configs`（或 Alloy 的 `prometheus.relabel`）来删除区分序列的标签——`pod`、`instance`、`user_id`、`path`、任何东西。** 参考 [一条规则](#一条规则-从不删除使序列唯一的标签)。它看起来像基数修复，但会无声地破坏 `rate()`，增加 DPM，并破坏聚合。改用应用代码（杠杆 1）或自适应指标（杠杆 3）代替。对在抓取时规范化标签值（例如将 `status_code` 折叠为 `2xx`）也适用同样的谨慎——它合并了不同的序列并产生重复样本错误；在代码中或通过自适应指标进行，绝不能在这里做。

真正安全的用途是：

- **删除您永远不想存储的整个指标**——您丢弃的是整个指标，而不是将不同的序列合并为一个：
  ```yaml
  metric_relabel_configs:
    - source_labels: [__name__]
      regex: my_app_request_details
      action: drop
  ```
- **删除一个与目标标签完全重复的标签。** 如果应用自行发出 `cluster`/`instance` 而这些标签已经来自抓取目标，目标标签仍然提供唯一性，因此删除重复项不会破坏任何东西。优先修复应用，但这是一种安全的临时措施。

这就是全部列表。如果您想用 `metric_relabel_configs` 来降低序列计数，您几乎肯定需要自适应指标。

### 5. 记录规则（查询时基数减少）

将昂贵的序列预聚合为低基数的记录序列。存储在相同的数据点密度下，但序列数量远少。

```yaml
groups:
  - name: http-requests-aggregates
    interval: 30s
    rules:
      # 删除 Pod/instance 维度；仅保留服务级别的汇总
      - record: service:http_requests:rate5m
        expr: sum by (service, env, cluster, status_code) (rate(http_requests_total[5m]))
```

针对汇总的查询成本大大降低。原始序列仍然存在——记录规则不会降低抓取成本（使用 **自适应指标**——*不是*抓取时的 `labeldrop`）。它们会降低查询成本。

---

## 仪器卫生（应用开发者）

如果用户正在编写仪器代码，这些是规则：

| 规则 | 原因 |
|---|---|
| 不要使用无界用户输入作为标签值 | `email`、`user_id`、`查询字符串`、`错误消息`——它们是 #1 基数错误 |
| 在记录前模板化 HTTP 路径 | `/users/{id}` 而不是 `/users/12345`。大多数框架通过路由元数据这样做 |
| 通过小枚举绑定错误标签 | `error_type="timeout"` 而不是 `error="连接到 db-shard-7 超时，时间 14:32:09"` |
| 不要在每个指标上放置 `version` / `git_sha` / `build_id` | 使用 info 指标并在查询时连接 |
| 不要从代码中发出 `pod` / `node` / `host` | 它们来自抓取目标——重复会导致冲突 |
| 避免动态构建的标签名称（键） | `metric{[user]=1}` 无法绑定——使用固定键 |
| 少量使用直方图并首先修剪标签 | 14× 基数放大 |
| 优先使用示例而不是标签进行跟踪关联 | 示例携带 `trace_id` 而不会增加基数 |

### 示例（逃生通道）

示例将 `trace_id`（或任何键值对）附加到特定样本*而不*使其成为标签维度。高基数关联数据的理想家园。

需要 OpenMetrics 格式、Prometheus 2.26+ 和抓取配置：
```yaml
scrape_configs:
  - job_name: my-app
    enable_protobuf_negotiation: true
    # 或用于文本格式：
    follow_redirects: true
```

并在 Prometheus 服务器上：
```yaml
storage:
  exemplars:
    max_exemplars: 100000
```

使用示例进行：
- `trace_id` 关联（Tempo、Jaeger）
- `request_id` 用于特定调试查找
- 任何稀疏的“需要时有用”的键

通过 Grafana 的示例-图功能查询示例，而不是通过 PromQL 聚合。

---

## 80/20 规则

最有影响力的改进几乎总是来自这五个变化：

1. **在应用层删除无界标签**——`path`（未模板化）、`user_id`、`error_message`。最大的胜利。
2. **在其他任何事情之前修剪直方图标签基数**——每个直方图 14× 放大。
3. **不要从应用代码中发出 `pod`/`instance`/`node`**——让它们来自抓取目标，并添加一个稳定的 `workload` 目标标签进行聚合。（绝不能在抓取时*删除*真实的 `pod` 来降低基数——如果 `pod` 级别的序列太昂贵，使用自适应指标。）
4. **使用 info 指标用于 `version` / `git_sha` / `image_tag`**——消除部署驱动的变更。
5. **通过 `relabel_configs` 而不是应用代码设置目标标签**——`env`、`cluster`、`team`、`service` 绝不应由应用程序发出。

在其他任何事情之前关注这些。

---

## 避免使用的标签——快速参考

| 标签 | 原因 | 替代方案 |
|---|---|---|
| `user_id`、`customer_id`（大型租户基础） | 无界 | 示例；按 `tenant_tier` 聚合 |
| `request_id`、`trace_id` | 无界 | 示例 |
| `path` / `route`（原始 URL） | 无界 | 代码中模板化：`/users/:id` |
| `error_message`、`query`、`sql` | 无界文本 | 绑定的 `error_type` 枚举 |
| `version`、`git_sha`、`image_tag`（在每个指标上） | 每次部署的变更 | info 指标模式 |
| 应用发出的 `pod`（重复 SD） | 应该来自 K8s 服务发现，而不是代码 | 停止在代码中发出它；保留发现的 `pod`。绝不能为了降低基数而删除真实的 `pod`——使用自适应指标 |
| `uid`（K8s） | 无界；在重启时重新生成 | 从一开始就绝不要将其映射为标签（将其从 `relabel_configs` 中排除） |
| 应用发出的 `instance`、`node`、`host` | 应该来自抓取目标 | 停止在代码中发出（在抓取时删除*精确*的目标标签副本是唯一安全的删除） |
| 动态命名的标签键 | 无法绑定 | 使用固定键和有界值 |
| 直方图上的原始 `status_code` | 14× 放大 | 桶装到 `status_class` (`2xx`、`4xx`、`5xx`) |

---

## 其他技能路由

- **“减少我的 Grafana Cloud 费用”** / **“减少已抓取序列的基数”** → 启用 `adaptive-metrics` 技能（抓取后聚合规则——安全、计数器重置感知的方法；绝不在抓取时删除区分性标签）
- **“哪些指标在推动我的 DPM？”** → 启用 `dpm-finder` 技能
- **“我的 Prometheus 正在 OOMing / 抓取当前失败”** → 启用 `prometheus-cardinality-troubleshooter` 技能
- **“我如何编写查询以找到不良指标？”** → 启用 `promql` 技能
- **“我如何在 Alloy 中配置重标记规则？”** → 启用 `alloy` 技能

这个技能的通道是 **策略和设计**。其他技能拥有 **诊断** 和 **操作修复**。
