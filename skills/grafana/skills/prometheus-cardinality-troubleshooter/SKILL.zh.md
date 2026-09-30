---
name: prometheus-cardinality-troubleshooter
description: 活动 Prometheus 基数问题诊断指南——慢查询、OOMing Prometheus、高 Grafana Cloud 活跃序列或 DPM 账单、"样本过多"摄取错误、序列漂移或快速内存增长。通过 tsdb 状态端点、按指标和按标签的深入分析、常见问题排查库以及修复路径进行说明。适用于用户*当前正在经历*基数问题。若需从源头上预防基数问题，请路由至 prometheus-label-strategy。若需摄取后聚合，请路由至 adaptive-metrics。若需 DPM 特定分析，请路由至 dpm-finder。
---

# Prometheus 核心基数故障排除器

你是一位诊断 Prometheus 实时基数问题的专家。当用户报告 Prometheus 性能、内存或成本问题时，如果怀疑与基数有关，请使用此指南进行系统化排查。

这项技能是**诊断和操作**性的。对于模式设计和预防，请路由到 `prometheus-label-strategy`。

---

## 在修复之前：一条规则

在压力下，诱人的做法是在抓取时 `labeldrop` 高基数标签。**不要这样做**。你无法在抓取时删除任何使时间序列唯一的标签——无论是 `pod`、`instance` 还是任何区分一个真实时间序列与其他时间序列的标签。它看起来像是止住了出血；实际上它**破坏了数据**：

- 来自不同时间序列的计数器重置被合并 → `rate()` 和 `increase()` 返回垃圾值，通常 *异常高*。
- 多个样本在同一抓取周期落在同一时间序列上 → 出现重复样本/顺序错误，并且 DPM **膨胀**，而不是减少。
- 这种破坏是静默的（没有配置错误），并且不会在数据中留下任何错误迹象。几周后有人问“为什么我的 DPM 这么高 / 为什么 `rate()` 异常？”，但找不到原因。

唯一安全的修复措施是：

1. **删除一个*整个*不需要的指标** (`action: drop` on `__name__`) — 你丢弃的是整个指标，而不是合并不同的时间序列。
2. **修复源** — 停止发出不良标签的应用程序（无界 `path`、`user_id` 等的真实修复方法）。
3. **自适应指标** — 对于你无法在源处修复的时间序列的结构性基数。它聚合*正确*（计数器重置感知、可审计、可逆）。这是减少 `pod` 标签成本的正确方法。路由到 `adaptive-metrics`。

在下面的内容中，如果提到“删除一个标签”，请根据此规则理解：删除整个指标，修复源，或使用自适应指标——永远不要 `labeldrop` 一个区分性标签。

---

## 症状 → 可能原因

| 症状 | 可能原因 | 首要操作 |
|---|---|---|
| Prometheus OOMKilled 或内存线性增长 | 活跃时间序列增长（通常来自新的不良指标或标签） | [活跃时间序列排查](#步骤-1-活跃时间序列排查) |
| 单个 PromQL 查询缓慢或 OOMs 查询器 | 查询中的一个或多个指标具有高基数 | [按查询深入排查](#步骤-3-按指标深入排查) |
| 远程写入延迟，WAL 增长 | 样本吞吐量激增——时间序列数量 OR 抓取间隔改变 | [活跃时间序列排查](#步骤-1-活跃时间序列排查) + 检查抓取间隔 |
| `429 Too Many Samples` / `out of bounds` 错误 | 达到 Mimir/Cortex 消费器租户时间序列限制 | [按指标深入排查](#步骤-3-按指标深入排查)，找到新的违规者 |
| Grafana Cloud 活跃时间序列账单激增 | 新指标、新标签或发布导致波动 | [按指标深入排查](#步骤-3-按指标深入排查) + 波动检查 |
| Grafana Cloud DPM 账单激增但活跃时间序列平稳 | 抓取间隔缩短，OR 远程写入发送重复数据 | DPM 端问题——路由到 `dpm-finder` |
| 部署后出现 `series_limit_per_user` 错误 | 应用程序更改引入了新的不良标签 | [最近更改差异](#步骤-4-最近更改差异) |
| 时间序列计数增长然后在每次重启时重置 | 来自易失性标签值的系列波动 | [波动诊断](#步骤-5-波动诊断) |

---

## 步骤 1：活跃时间序列排查

### 获取头条数字

```promql
# 本地 Prometheus 中的活跃时间序列总数
prometheus_tsdb_head_series

# 或对于 Mimir / Grafana Cloud 指标（按租户）
cortex_ingester_memory_series{user="<租户>"}
```

与最近的历史比较：
```promql
# 过去 7 天的增长
deriv(prometheus_tsdb_head_series[7d]) * 86400
```

在稳定的应用程序中，每天增长率 > 几 % 是一个危险信号。

### 使用 TSDB 状态端点

Prometheus 提供了一个内置的基数分解：

```bash
curl -s http://prometheus:9090/api/v1/status/tsdb | jq
```

返回：
- `seriesCountByMetricName` — 按时间序列数量排序的顶级指标
- `labelValueCountByLabelName` — 按唯一值数量排序的顶级标签
- `memoryInBytesByLabelName` — 按内存占用排序的顶级标签
- `seriesCountByLabelValuePair` — 按时间序列数量排序的顶级标签值对

这通常是快速找到“哪个指标 / 哪个标签是问题”的路径。

对于 Grafana Cloud：
```bash
# 相同端点，针对每个租户的 Mimir 进行身份验证
curl -s -u "<用户>:<令牌>" \
  "https://prometheus-prod-XX.grafana.net/api/prom/api/v1/status/tsdb" | jq
```

---

## 步骤 2：阅读输出

### 按时间序列数量排序的顶级指标

```json
"seriesCountByMetricName": [
  { "name": "http_request_duration_seconds_bucket", "value": 184320 },
  { "name": "go_gc_duration_seconds",               "value": 80 },
  ...
]
```

**启发式方法**：
- 顶部的直方图 (`_bucket`) 几乎总是答案——这些有一个 14× 的乘数（桶数量 + 3）。修复方法通常是**在源处减少底层直方图的标签**（在仪器代码中），而不是在抓取时剥离它们，也不触摸桶本身。
- 顶级 5 中的一个你不认识的指标 → 在代码库中搜索它；它很可能是一个新的功能标志或发到生产环境的调试指标
- 同一个指标以多个变体出现 (`_total`、`_count`、`_sum`) — 那是一个直方图或汇总，将所有变体一起计算以获得真实影响

### 按唯一值数量排序的顶级标签

```json
"labelValueCountByLabelName": [
  { "name": "url",       "value": 84210 },
  { "name": "trace_id",  "value": 41000 },
  { "name": "pod",       "value": 1820 }
]
```

**危险信号**：
- 任何唯一值 >10K 的标签几乎肯定是错误。唯一的例外是大规模舰队中故意用于每个目标的标签。
- `trace_id`、`request_id`、`session_id`、`query`、`email`、`path`、`url` — 这些永远不应该是标签。它们应该存在于示例中、日志或跟踪中。
- `pod` 有数千个值 — 查看 [波动诊断](#步骤-5-波动诊断)；最近的波动通常会使这个数字膨胀

---

## 步骤 3：按指标深入排查

一旦你确定了一个可疑指标，找出哪个标签是负责的。

### 每个标签的每个指标上的唯一标签值计数

```promql
# 这个指标上的每个标签有多少个唯一值？
count by (__name__) (
  count by (__name__, label_name_here) (
    http_request_duration_seconds_bucket
  )
)
```

逐个标签重复，或使用辅助工具：

```bash
# 通过 Prometheus HTTP API
curl -s "http://prometheus:9090/api/v1/labels?match[]=http_request_duration_seconds_bucket" | jq -r '.data[]' | \
  while read label; do
    count=$(curl -s "http://prometheus:9090/api/v1/label/${label}/values?match[]=http_request_duration_seconds_bucket" | jq '.data | length')
    echo "${count}  ${label}"
  done | sort -rn | head -20
```

### 查找单个标签的顶级标签值

```promql
# http_requests_total 的顶级 20 个 path 值
topk(20,
  count by (path) (http_requests_total)
)
```

如果你看到 UUID、哈希、时间戳或数字 ID 在顶级值中 → 这个标签从源处有无限值。

### 按指标分组的时间序列计数

```promql
# 按实例的系列-实例分解——如果 uneven，一个实例行为异常
sum by (job, instance) ({__name__=~"my_metric.*"})
```

---

## 步骤 4：最近更改差异

如果基数火灾是最近开始的，原因几乎总是最近的更改。将当前状态与之前的状态进行比较。

### 指标的当前值与昨天的列表

通过 Grafana Cloud 基数仪表板，或：
```promql
# 当前指标
group by (__name__) ({__name__!=""})

# 与上周（偏移）比较
group by (__name__) ({__name__!=""} offset 7d)
```

外部比较。一周前在 `seriesCountByMetricName` 顶部附近出现的新指标 → 那是你的违规者。

### 与部署相关联

```promql
# 活跃时间序列与 build_info 相关
prometheus_tsdb_head_series
# 叠加：
changes(app_build_info[1d])
```

时间序列计数与部署垂直对齐是结论性的。

---

## 步骤 5：波动诊断

高波动意味着时间序列被创建和放弃的速度比它们老化得快。症状：时间序列计数不断上升，然后在 Prometheus 重启时急剧下降。

### 波动信号

```promql
# 每秒创建的时间序列与删除的时间序列
rate(prometheus_tsdb_head_series_created_total[5m])
rate(prometheus_tsdb_head_series_removed_total[5m])

# 波动与活跃的比率
prometheus_tsdb_head_series_created_total / prometheus_tsdb_head_series
```

创建率实质性超过删除率，并持续存在，意味着基数正在单向上升。常见原因：

| 原因 | 告知 |
|---|---|
| Pod 展开发出 `pod` 标签 | 波动峰值与部署时间对齐；影响 pod-discovered 抓取 |
| 每个指标上的 `version` / `git_sha` / `image_tag` 标签 | 每个部署在许多指标上出现波动 |
| `instance` 中的易失性主机名 | 云自动缩放事件时间 |
| 错误：动态标签名称 | 波动无限上升，永远不会达到平台期 |
| 应用程序错误发出作为标签的新 UUID | 线性无界增长，没有部署相关性 |

### 波动对内存的影响

```promql
# 波动驱动的头块携带旧时间序列，直到 tsdb 压缩
prometheus_tsdb_head_chunks
go_memstats_heap_inuse_bytes{job="prometheus"}
```

重启 Prometheus 会删除波动的系列，但这不是修复方法。修复方法在源处。

---

## 常见元凶图库

### 直方图爆炸

**告知**：`*_bucket` 指标在 `seriesCountByMetricName` 顶部。乘数 ≈ 14×。

**修复**：
1. 首先，**在源处减少直方图的标签**——每个删除的标签节省 14× 时间序列。在仪器代码中修剪 `path`、`method` 或 `status_code`（不要在抓取时 `labeldrop` 它们——那会合并不同的直方图并损坏桶）。对于无法更改的 Grafana Cloud 时间序列，使用自适应指标进行聚合。
2. 然后，如果合适，减少桶数量。
3. 对于高分辨率延迟跟踪，考虑**原生直方图**（Prometheus 2.40+）——单个稀疏时间序列取代桶家族。

### kube-state-metrics 标签爆炸

**告知**：`kube_pod_labels` 或 `kube_pod_annotations` 在顶部，`label_*` 或 `annotation_*` 标签驱动基数。

**修复**：配置 kube-state-metrics 使用 `--metric-labels-allowlist` 和 `--metric-annotations-allowlist`。默认情况下它发出*所有*标签和注解作为时间序列。

```yaml
# kube-state-metrics 标志
--metric-labels-allowlist=pods=[app,team,version]
--metric-annotations-allowlist=pods=[checksum/config]
```

### 新端点从路径 / 路由爆炸

**告知**：`http_requests_total`（或框架等效项）在一夜之间增长了 10×+。`topk(20, count by (path) (http_requests_total))` 显示数百个 `/users/123456`-样式的值。

**修复**：真正的修复方法是在应用程序代码中**模板路径**（`/users/:id`）——将用户路由到 `prometheus-label-strategy`。对于已存在于 Grafana Cloud 中的时间序列，**自适应指标**可以正确聚合 `path` —— 路由到 `adaptive-metrics`。

不要用重命名规则“规范化” `path` —— 在抓取时将 `/users/123`、`/users/456`、… 合并成一个 `/users/:id` 值——合并了不同的时间序列，并产生重复样本错误和损坏的 `rate()`。合并必须在源处（模板化）或摄取后（自适应指标）进行，永远不在抓取时进行。

如果你必须立即停止生产火灾*并且*模板化不可用，唯一安全的抓取时操作是删除**整个**违规指标（直到代码修复落地——这是一个故意的权衡，而不是无声的损坏）：

```yaml
# 紧急：直到源代码修复落地，删除整个指标
metric_relabel_configs:
  - source_labels: [__name__]
    regex: http_requests_total
    action: drop
```

### 应用程序在生产环境中发出调试指标

**告知**：在顶部你不认识的指标。在源代码中搜索——通常是一个 `_details` 或 `_per_request` 调试指标，开发者忘记禁用。

**修复**：在抓取时完全删除：
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: my_app_request_details
    action: drop
```

向团队开一个工单，从代码中删除它。

### 应用程序发出的标签与目标标签冲突

**告知**：一个作业的时间序列计数是它应有的几倍。查看一个时间序列，你看到既是应用程序发出的 `instance=...`，又是目标 `instance=...` 冲突成了奇怪的东西（Prometheus 将冲突的一个重命名为 `exported_instance`）。

**修复**：正确的修复方法是**在应用程序中**——停止从代码中发出 `instance`/`node`/`host`；它们属于抓取目标。确认 `honor_labels` 是 `false`（默认值），以便目标标签获胜。

如果你需要一个抓取时临时措施，你可能会删除标签*仅*在它**完全重复**目标标签时——这是唯一安全的 `labeldrop`，因为目标标签仍然提供唯一性。将范围严格限制为重复的名称，并且**永远不要包括 `pod`**（或任何其他唯一性来源的标签）：

```yaml
# 仅用于应用程序重复的目标标签的临时措施。
# 删除 `exported_*` 冲突——不包括 pod，pod 使 K8s 时间序列唯一。
metric_relabel_configs:
  - regex: exported_(instance|node|host)
    action: labeldrop
```

然后目标标签从 `relabel_configs` 清洁地应用。优先修复应用程序。

### 联邦放大基数

**告知**：一个联邦的 Prometheus 或 Mimir 全局视图中的时间序列远多于预期。每个源都有自己的 `cluster` / `region` 标签，倍增。

**修复**：这通常是预期的——联邦设计保留了源标签。如果时间序列计数过高，请联邦聚合的记录规则，而不是原始指标：

```yaml
- job_name: federate
  honor_labels: true
  metrics_path: /federate
  params:
    'match[]':
      - '{__name__=~".*:.*"}'  # 记录规则命名约定
```

---

## 修复决策树

```
确认基数火灾
│
├── 需要立即止血（生产 OOM，摄取 429s）
│   └── 通过 metric_relabel_configs 删除整个违规指标 (action: drop on __name__)
│       (Alloy/Agent 也适用——语法相同)
│       不要 `labeldrop` 一个区分性标签——它会破坏数据，参见“一条规则”。
│       然后安排正确的修复。
│
├── 这是一个 Grafana Cloud 活跃时间序列账单问题，而不是性能问题
│   ├── 基数是结构性的，你无法修复应用程序
│   │   └── 路由到 `adaptive-metrics` 技能（摄取后聚合规则——安全的方法）
│   └── 你想要按指标 DPM 分解
│       └── 路由到 `dpm-finder` 技能
│
├── 这是一个可修复的应用程序错误（无界标签，生产环境中的调试指标）
│   ├── 短期：在抓取时删除整个指标，或通过 Adaptive Metrics 聚合
│   └── 长期：在代码中修复；路由到 `prometheus-label-strategy` 获取设计指导
│
├── 这是直方图基数
│   ├── 在源处减少底层直方图的标签（每个标签节省 14×）
│   ├── 如果合适，减少桶数量
│   └── 考虑原生直方图进行高分辨率延迟跟踪
│
└── 这是波动（部署驱动）
    ├── 停止从应用程序代码中发出 `version`/`git_sha`/`instance`
    ├── 保持 `pod`——永远不要删除它；如果 pod 级时间序列过于昂贵，使用 Adaptive Metrics
    └── 验证 K8s SD 重命名规则不会映射 `uid` 或其他易失性字段
```

---

## 紧急删除模式（可复制粘贴）

这些都是**安全**的抓取时紧急操作：删除一个*整个*不需要的指标。它们不会合并不同的时间序列，因此不会损坏数据。

⚠️ 这里故意**不进行区分性标签的 `labeldrop`**，也**不进行值归一化的重标签**。两者都会合并不同的序列，并破坏 `rate()`/DPM（参见[单一规则](#before-you-remediate-the-one-rule)）。为了在不丢弃整个指标的情况下减少基数，请修复源数据或使用**自适应指标**（路由到 `adaptive-metrics`）。唯一安全的 `labeldrop` 是移除一个与目标标签*完全重复*的标签（例如 `exported_instance`）——参见[应用发出的标签与目标标签冲突](#app-emitted-labels-colliding-with-target-labels)。

对于 Prometheus `scrape_configs`：

```yaml
metric_relabel_configs:
  # 完全丢弃一个特定的坏指标
  - source_labels: [__name__]
    regex: bad_metric_name
    action: drop

  # 通过名称前缀丢弃一组调试/临时指标
  - source_labels: [__name__]
    regex: debug_.*
    action: drop
```

对于 Grafana Alloy (`prometheus.relabel` 组件)：

```alloy
prometheus.relabel "drop_bad_metric" {
  forward_to = [prometheus.remote_write.default.receiver]

  rule {
    source_labels = ["__name__"]
    regex = "bad_metric_name"
    action = "drop"
  }
}
```

**始终先在测试环境中测试**，并优先修复源数据或使用自适应指标，而不是在抓取时进行丢弃。

---

## 何时移交

- **"现在设计一个标签策略，以避免再次发生这种情况"** → `prometheus-label-strategy`
- **"我们需要保留这些指标但降低成本"** → `adaptive-metrics`
- **"哪个指标在 DPM 方面最昂贵？"** → `dpm-finder`
- **"编写 PromQL 查询以查找这个"** → `promql`
- **"在 Alloy 中配置此内容"** → `alloy`
- **"为什么我的 Loki 运行缓慢？"** → `loki-label-analyzer`（不同系统，但属于同一问题类别）

这项技能的职责是**在压力下进行诊断**。预防、设计和摄取后成本优化属于其他领域。
