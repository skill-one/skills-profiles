# Prometheus 核心指标问题排查工具

您是诊断实时 Prometheus 核心指标问题的专家。当用户报告 Prometheus 性能、内存或成本问题时，如果怀疑与核心指标有关，请使用此指南进行系统性的分诊。

这项技能是**诊断和操作**性的。对于模式设计和预防，请路由到 `prometheus-label-strategy`。

---

## 在您进行修复之前：一条规则

在压力下，诱人的做法是在抓取时 `labeldrop` 高核心指标的标签。**不要这样做**。您不能在抓取时删除任何使时间序列唯一的标签——不是 `pod`，不是 `instance`，不是任何能区分一个真实时间序列与其他时间序列的标签。它看起来像是止住了出血；实际上它**破坏了数据**：

- 来自不同时间序列的计数器重置被合并 → `rate()` 和 `increase()` 返回垃圾值，通常 *异常高*。
- 多个样本在同一抓取周期落在同一时间序列上 → 出现重复样本/顺序错误，并且 DPM **膨胀**，而不是减少。
- 破坏是静默的（没有配置错误），并且不会在数据中留下任何错误原因的证据。几周后有人问“为什么我的 DPM 这么高 / 为什么 `rate()` 异常？”而没有任何线索。

唯一安全的修复措施是：

1. **删除一个*整个*不需要的指标** (`action: drop` on `__name__`) — 您正在丢弃整个指标，而不是合并不同的时间序列。
2. **修复源** — 停止发出坏标签的应用程序（无界 `path`、`user_id` 等的真实修复方法）。
3. **自适应指标** — 对于您在源处无法修复的时间序列上的结构化核心指标。它正确聚合（计数器重置感知、可审计、可逆）。这是降低 `pod` 标签成本的正确方法。路由到 `adaptive-metrics`。

在下面，所有提到“删除一个标签”的地方，请通过这条规则理解：删除整个指标，修复源，或使用自适应指标——永远不要 `labeldrop` 一个区分性标签。

---

## 症状 → 可能的原因

| 症状 | 可能的原因 | 首要行动 |
|---|---|---|
| Prometheus OOMKilled 或内存线性增长 | 活跃时间序列增长（通常来自新的坏指标或标签） | [活跃时间序列分诊](#步骤-1-活跃时间序列分诊) |
| 单个 PromQL 查询缓慢或 OOMs 查询器 | 查询中的一个或多个指标具有高核心指标 | [按查询深入分析](#步骤-3-按指标深入分析) |
| 远程写入延迟，WAL 增长 | 样本吞吐量激增——时间序列计数 OR 抓取间隔改变 | [活跃时间序列分诊](#步骤-1-活跃时间序列分诊) + 检查抓取间隔 |
| `429 Too Many Samples` / `out of bounds` 错误 | 达到 Mimir/Cortex 每租户时间序列限制 | [按指标深入分析](#步骤-3-按指标深入分析)，找到新的违规者 |
| Grafana Cloud 活跃时间序列账单激增 | 新指标、新标签或发布导致波动 | [按指标深入分析](#步骤-3-按指标深入分析) + 波动检查 |
| Grafana Cloud DPM 账单激增但活跃时间序列平稳 | 抓取间隔缩短，OR 远程写入发送重复数据 | DPM 端问题——路由到 `dpm-finder` |
| 部署后出现 `series_limit_per_user` 错误 | 应用程序更改引入了新的坏标签 | [最近更改差异](#步骤-4-最近更改差异) |
| 时间序列计数增长然后在每次重启时重置 | 来自易失性标签值的系列波动 | [波动诊断](#步骤-5-波动诊断) |

---

## 步骤 1：活跃时间序列分诊

### 获取标题数字

```promql
# 本地 Prometheus 中的总活跃时间序列
prometheus_tsdb_head_series

# 或对于 Mimir / Grafana Cloud 指标（每个租户）
cortex_ingester_memory_series{user="<tenant>"}
```

与最近的历史比较：
```promql
# 过去 7 天的增长
deriv(prometheus_tsdb_head_series[7d]) * 86400
```

在稳定的应用程序上，每天增长率 > 几 % 是一个危险信号。

### 使用 TSDB 状态端点

Prometheus 暴露了一个内置的核心指标分解：

```bash
curl -s http://prometheus:9090/api/v1/status/tsdb | jq
```

返回：
- `seriesCountByMetricName` — 按时间序列计数排序的顶级指标
- `labelValueCountByLabelName` — 按唯一值计数排序的顶级标签
- `memoryInBytesByLabelName` — 按内存占用排序的顶级标签
- `seriesCountByLabelValuePair` — 按时间序列计数排序的顶级标签值对

这通常是找到“哪个指标 / 哪个标签是问题”的最快路径。

对于 Grafana Cloud：
```bash
# 相同端点，针对每个租户的 Mimir 进行身份验证
curl -s -u "<user>:<token>" \
  "https://prometheus-prod-XX.grafana.net/api/prom/api/v1/status/tsdb" | jq
```

---

## 步骤 2：阅读输出

### 按时间序列计数排序的顶级指标

```json
"seriesCountByMetricName": [
  { "name": "http_request_duration_seconds_bucket", "value": 184320 },
  { "name": "go_gc_duration_seconds",               "value": 80 },
  ...
]
```

**启发式方法**：
- 顶部的一个直方图 (`_bucket`) 几乎总是答案——这些有一个 14× 的乘数（桶计数 + 3）。修复通常是在源处**减少底层直方图的标签**（在仪器代码中），而不是在抓取时剥离它们，也不触摸桶本身。
- 顶级 5 中的一个您不认识的指标 → 在代码库中 grep 它；它很可能是一个新的功能标志或发到生产环境的调试指标
- 同一个指标在多个变体下出现 (`_total`、`_count`、`_sum`) — 那是一个直方图或汇总，将所有变体一起计算以获得真实影响

### 按唯一值计数排序的顶级标签

```json
"labelValueCountByLabelName": [
  { "name": "url",       "value": 84210 },
  { "name": "trace_id",  "value": 41000 },
  { "name": "pod",       "value": 1820 }
]
```

**危险信号**：
- 任何具有 >10K 个唯一值的标签几乎肯定是错误。唯一的例外是大规模舰队中故意每个目标标签。
- `trace_id`、`request_id`、`session_id`、`query`、`email`、`path`、`url` — 这些永远不应该是标签。它们应该放在示例中、日志或跟踪中。
- `pod` 具有数千个值 — 查看 [波动诊断](#步骤-5-波动诊断)；最近的波动通常会使此数字膨胀

---

## 步骤 3：按指标深入分析

一旦您确定了一个可疑指标，找出哪个标签是负责的。

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

### 找到一个标签的顶级标签值

```promql
# http_requests_total 的前 20 个路径值
topk(20,
  count by (path) (http_requests_total)
)
```

如果您看到 UUID、哈希、时间戳或数字 ID 在顶级值中 → 该标签从源处具有无界值。

### 按指标分组的时间序列计数

```promql
# 按实例的系列-实例分解——如果 uneven，一个实例在行为异常
sum by (job, instance) ({__name__=~"my_metric.*"})
```

---

## 步骤 4：最近更改差异

如果核心指标火灾是最近开始的，原因几乎总是最近的更改。将当前与之前进行比较。

### 指标的当前值与昨天的列表

通过 Grafana Cloud 核心指标仪表板，或：
```promql
# 当前指标
group by (__name__) ({__name__!=""})

# 与上周（偏移）比较
group by (__name__) ({__name__!=""} offset 7d)
```

外部比较。一个新指标在 `seriesCountByMetricName` 的顶部附近，而一周前没有 → 那就是您的违规者。

### 与部署相关联

```promql
# 活跃时间序列与 build_info 相关
prometheus_tsdb_head_series
# 叠加：
changes(app_build_info[1d])
```

时间序列计数与部署对齐的垂直步骤是结论性的。

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

一个创建率实质性超过删除率，并持续存在，意味着核心指标正在单向上升。常见原因：

| 原因 | 告知 |
|---|---|
| Pod 展开发出 `pod` 标签 | 波动尖峰与部署时间对齐；影响 pod-discovered 抓取 |
| 每个指标上的 `version` / `git_sha` / `image_tag` 标签 | 在许多指标上每个部署的波动尖峰 |
| `instance` 中的易失性主机名 | 云自动缩放事件时间 |
| 错误：动态标签名称 | 波动无限上升，永远不会达到平台期 |
| 应用程序错误发出作为标签的新 UUID | 线性无界增长，没有部署相关性 |

### 波动对内存的影响

```promql
# 一个波动驱动的头块包含旧时间序列，直到 tsdb 压缩
prometheus_tsdb_head_chunks
go_memstats_heap_inuse_bytes{job="prometheus"}
```

重启 Prometheus 会删除波动的系列，但这不是一个修复。修复是在源处。

---

## 常见元凶画廊

### 直方图爆炸

**告知**：`*_bucket` 指标在 `seriesCountByMetricName` 的顶部。乘数 ≈ 14×。

**修复**：
1. 首先，在源处**减少直方图的标签**——每个删除的标签节省 14× 时间序列。在仪器代码中修剪 `path`、`method` 或 `status_code`（不要在抓取时 `labeldrop` 它们——那会合并不同的直方图并损坏桶）。对于您无法更改的 Grafana Cloud 中的系列，使用自适应指标进行聚合。
2. 然后，如果合适，减少桶计数。
3. 对于高分辨率延迟跟踪，考虑**原生直方图**（Prometheus 2.40+）——单个稀疏系列取代了桶家族。

### kube-state-metrics 标签爆炸

**告知**：`kube_pod_labels` 或 `kube_pod_annotations` 在顶部，`label_*` 或 `annotation_*` 标签驱动核心指标。

**修复**：使用 `--metric-labels-allowlist` 和 `--metric-annotations-allowlist` 配置 kube-state-metrics。默认情况下，它发出 *所有* 标签和注解作为系列。

```yaml
# kube-state-metrics 标志
--metric-labels-allowlist=pods=[app,team,version]
--metric-annotations-allowlist=pods=[checksum/config]
```

### 来自新端点的路径 / 路由爆炸

**告知**：`http_requests_total`（或框架等效项）在一夜之间增长了 10×+。`topk(20, count by (path) (http_requests_total))` 显示了数百个 `/users/123456`-样式的值。

**修复**：真正的修复是在应用程序代码中**模板路径**（`/users/:id`）——将用户路由到 `prometheus-label-strategy`。对于 Grafana Cloud 中的系列，**自适应指标**可以正确聚合 `path` —— 路由到 `adaptive-metrics`。

不要用重标签“替换”规则来“规范化”`path`——在抓取时将 `/users/123`、`/users/456`、… 折叠成一个 `/users/:id` 值会合并不同的时间序列并产生重复样本错误和损坏的 `rate()`。合并必须在源处（模板化）或在摄取后（自适应指标）发生，永远不会在抓取时发生。

如果您必须立即停止生产火（生产 OOM、摄取 429s），并且模板化尚未可部署，唯一安全的抓取时操作是删除**整个**违规指标（直到代码修复落地才会丢失它——这是一个故意的权衡，而不是无声的损坏）：

```yaml
# 紧急：直到源代码模板化之前删除整个指标
metric_relabel_configs:
  - source_labels: [__name__]
    regex: http_requests_total
    action: drop
```

### 应用程序在生产中发出调试指标

**告知**：在顶部的一个您不认识的指标。在源代码中 grep —— 通常是一个 `_details` 或 `_per_request` 调试指标，开发人员忘记阻止它。

**修复**：在抓取时完全删除：
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: my_app_request_details
    action: drop
```

向团队开一个工单，从代码中删除它。

### 应用程序发出的标签与目标标签冲突

**告知**：一个作业的时间序列计数是它应该的几 ×。查看一个时间序列，您看到既是应用程序发出的 `instance=...` 又是目标 `instance=...` 冲突成了奇怪的东西（Prometheus 将冲突的一个重命名为 `exported_instance`）。

**修复**：正确的修复是在**应用程序**中——停止从代码中发出 `instance`/`node`/`host`；它们属于抓取目标。确认 `honor_labels` 是 `false`（默认值），以便目标标签获胜。

如果您需要一个抓取时临时措施，您可能只删除标签，仅当它**精确地重复**一个目标标签时——这是唯一安全的 `labeldrop`，因为目标标签仍然提供唯一性。将范围严格限制到重复的名称，并且**永远不要包括 `pod`**（或任何其他是唯一性来源的标签）：

```yaml
# 仅用于应用程序重复的目标标签的临时措施。
# 删除 `exported_*` 冲突——不包括 pod，pod 使 K8s 时间序列唯一。
metric_relabel_configs:
  - regex: exported_(instance|node|host)
    action: labeldrop
```

然后目标标签从 `relabel_configs` 清洁地应用。优先修复应用程序。

### 联邦放大核心指标

**告知**：一个联邦的 Prometheus 或 Mimir 全局视图中的时间序列比预期多得多。每个源都有自己的 `cluster` / `region` 标签，乘以。

**修复**：这通常是预期的——联邦设计上保留了源标签。如果时间序列计数过高，请联邦聚合的记录规则，而不是原始指标：

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
核心指标火灾确认
│
├── 需要立即止血（生产 OOM，摄取 429s）
│   └── 通过 metric_relabel_configs 完全删除违规指标 (action: drop on __name__)
│       (Alloy/Agent 也适用——语法相同)
│       不要 `labeldrop` 一个区分性标签——它会破坏数据，参见“一条规则”。
│       然后安排正确的修复。
│
├── 这是一个 Grafana Cloud 活跃时间序列账单问题，而不是性能问题
│   ├── 核心指标是结构性的，您无法修复应用程序
│   │   └── 路由到 `adaptive-metrics` 技能（摄取后聚合规则——安全的方法）
│   └── 您希望按指标 DPM 分解
│       └── 路由到 `dpm-finder` 技能
│
├── 这是一个可修复的应用程序错误（无界标签，生产中的调试指标）
│   ├── 短期：在抓取时删除整个指标，或通过 Adaptive Metrics 聚合
│   └── 长期：在代码中修复；路由到 `prometheus-label-strategy` 获取设计指导
│
├── 这是直方图核心指标
│   ├── 在源处减少底层直方图的标签（每个标签节省 14×）
│   ├── 如果合适，减少桶计数
│   └── 考虑原生直方图进行高分辨率延迟跟踪
│
└── 这是波动（部署驱动）
    ├── 停止从应用程序代码中发出 `version`/`git_sha`/`instance`（使用 info-metric 提供版本）
    ├── 保留 `pod`——永远不要删除它；如果 pod 级时间序列过于昂贵，使用 Adaptive Metrics
    └── 验证 K8s SD 重标签规则不会映射 `uid` 或其他易失性字段
```

---

## 紧急删除模式（可复制粘贴）

这些都是**安全的**抓取时紧急操作：删除一个*整个*不需要的指标。它们不会合并不同的时间序列，因此不会破坏数据。

> ⚠️ 有意**不包含**区分性标签的 `labeldrop` 和**不包含**值规范化重标签。两者都会合并不同的时间序列并破坏 `rate()`/DPM（参见 [一条规则](#before-you-remediate-the-one-rule)）。要减少核心指标*而不*删除整个指标，修复源或使用 **Adaptive Metrics**（路由到 `adaptive-metrics`）。唯一安全的 `labeldrop` 是删除一个标签，该标签*精确地重复*一个目标标签（例如 `exported_instance`）——参见 [应用程序发出的标签与目标标签冲突](#app-emitted-labels-colliding-with-target-labels)。

对于 Prometheus `scrape_configs`：

```yaml
metric_relabel_configs:
  # 完全删除一个特定的坏指标
  - source_labels: [__name__]
    regex: bad_metric_name
    action: drop

  # 通过名称前缀删除一组调试/临时指标
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

**始终在暂存环境中测试**，并且优先修复源或使用 Adaptive Metrics 而不是任何抓取时删除。

---

## 何时移交

- **“现在设计一个标签策略，以防止这种情况再次发生”** → `prometheus-label-strategy`
- **“我们需要保留这些指标但降低成本”** → `adaptive-metrics`
- **“哪个指标在 DPM 方面是最昂贵的？”** → `dpm-finder`
- **“编写 PromQL 来找到这个”** → `promql`
- **“在 Alloy 中配置此内容”** → `alloy`
- **“为什么我的 Loki 慢？”** → `loki-label-analyzer`（不同系统，但问题是同一系列）

这项技能的赛道是**在压力下进行诊断**。预防、设计和摄取后成本优化存在于其他地方。
