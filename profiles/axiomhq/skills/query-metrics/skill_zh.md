# 查询 Axiom 指标

所有脚本路径相对于此技能的文件夹；调用方式为 `scripts/<name>`。目标数据集必须为 `otel:metrics:v1` 类型。

设置、先决条件和 `~/.axiom.toml` 配置：参见 `README.md`。边缘部署路由是自动的——脚本读取每个数据集的 `edgeDeployment` 并路由到正确的区域端点，无需配置。

## 工作流程

1. `scripts/datasets <deploy> --kind otel:metrics:v1` — 列出指标数据集。
2. `scripts/metrics-spec` — **必须** 在编写任何查询之前使用。MPL 会不断演变；规范是事实来源。也用它来回答关于 MPL/指标的通用问题。
3. `scripts/metrics-info <deploy> <dataset> metrics` — 列出带有 `{type, temporality, unit}` 元数据的指标。在编写查询之前阅读此内容（参见 [选择查询形状](#choosing-a-query-shape)）。
4. `scripts/metrics-info <deploy> <dataset> tags [<tag> values]` — 探索过滤维度。
5. `scripts/metrics-query <deploy> '<MPL>' <start> <end>` — 执行。迭代。

如果用户指定了特定实体（服务、主机、…），`scripts/metrics-info <deploy> <dataset> find-metrics "<value>"` 会找到包含它的指标。`find-metrics` 搜索 **标签值**，而不是指标名称——不要用它进行通用发现。

## 选择查询形状

`metrics-info` 列表返回每个指标的 `{type, temporality, unit}`。在编写之前阅读这些内容——永远不要假设指标是一个简单的标量。

| 字段 | 值 | 驱动 |
|---|---|---|
| `type` | `Gauge`, `CounterMonotonic`, `CounterNonMonotonic`, `Histogram` | 需要预聚合操作符。 |
| `temporality` | `Cumulative`, `Delta`, `null` | 计数器值是运行总和还是每个间隔的增量。`null` 是 Gauge 的正常值。 |
| `unit` | UCUM 字符串 (`Cel`, `kW.h`, `s`, `%`, `[ppm]`, …) 或 `null` | 显示单位；报告结果时保留。 |

每种类型的规则（参考 `metrics-spec` 获取确切的操作符名称——它们会演变）：

- **Gauge** — 瞬时值。直接与 `avg`/`min`/`max`/`sum` 对齐。不要应用速率；你会平均瞬时值的无意义增量。
- **CounterMonotonic + Cumulative** — 运行总和（单独重置）。原始值很少是你想要的。先转换为每秒速率，**然后** 对齐/聚合。
- **CounterMonotonic + Delta** — 已经是每个间隔的。无需速率步骤即可求和/对齐。
- **CounterNonMonotonic** — 可能增加或减少（队列深度、余额）。意图不明确：速率、增量或当前值对不同问题都合理。**在做出选择之前询问用户**。
- **Histogram** — 不是标量。`align using avg` 产生无意义的结果。使用 `bucket … using` 并结合 `metrics-spec` 中的直方图函数；分位数是传递给这些函数的浮点规范，`temporality` 选择变体（`Cumulative` 与 `Delta` 插值）。参考 `metrics-spec` 获取确切的签名。
- **`temporality: null`** — “不适用于此仪器类型”（Gauge 的常态），不是“缺少数据”。

在展示数字时，附加 `unit`（将 `null` 视为无单位）。如果你在算术中组合单位不匹配的指标，请发出警告而不是静默地生成一个无意义的数字。

## 查询指标

```bash
scripts/metrics-query [-w pixels] [--pixel-per-point n] <deploy> '<MPL>' <start> <end>
```

| 参数 | 备注 |
|---|---|
| `deploy` | 来自 `~/.axiom.toml` 的名称（例如 `prod`）。 |
| `MPL` | 管道字符串。数据集从 MPL 本身解析。 |
| `start` / `end` | RFC3339 (`2025-01-01T00:00:00Z`) 或相对 (`now-1h`, `now`)。 |
| `-w` / `--chart-width <px>` | 可选。目标图表宽度（像素）；允许服务器解析 `$__interval`。 |
| `--pixel-per-point <n>` | 可选。每点的像素数（服务器默认 10）；结合 `-w` 设置桶数量。 |

**始终在 shell 中单引号 MPL 字符串。** MPL 充满了反引号；在双引号内，shell 会将其作为命令替换执行，会无声地破坏查询（或运行标识符命名的任何内容）。

**在对齐输出之前进行限制。** `group by <tag>` 返回每个标签值的一个序列，没有上限——在高基数标签的情况下会淹没输出。首先检查基数（`describe`，或 `tags <tag> values`）并优先使用 `group using <agg>` 进行探索。

示例：

```bash
scripts/metrics-query prod -w 1200 \
  '`my-dataset`:`http.server.duration` | align to $__interval using avg' \
  now-1h now

scripts/metrics-query prod -w 1200 \
  '`my-dataset`:`http.server.duration`
   | where `service.name` == "frontend" and method == "GET"
   | align to $__interval using avg
   | group by status_code using sum' \
  now-1d now
```

### 自适应分辨率 (`$__interval`)

硬编码步长（`align to 5m`）会导致在其他缩放级别上图表显示不正确——缩放时过于稀疏，缩放时过于密集。优先使用系统参数 `$__interval`，并在需要时传递图表宽度，让服务器选择步长：

```bash
scripts/metrics-query prod -w 1200 \
  '`my-dataset`:`http.server.duration` | align to $__interval using avg' \
  now-7d now
```

指标服务根据查询的时间范围和目标图表宽度计算 `$__interval`，然后将其向上**对齐**到漂亮的分辨率（从 `1s, 5s, 10s, 15s, 30s, 1m, 5m, 10m, 15m, 30m, 1h, 12h, 1d, 1w, 1M, 1Y`）。它永远不会低于指标存储的分辨率。

- **无需声明**——服务器自动注册 `$__interval`；**不要**
  添加 `param $__interval: Duration;`（边缘会转发查询原文，指标服务会注入参数）。
- **桶数量** ≈ `chart-width / pixel-per-point` (`pixel-per-point` 默认 10)。省略 `-w`，服务器会目标约 500 个桶。
- 适用于任何有效的 `Duration`，例如 `bucket to $__interval using histogram(0.5, 0.95)`。
- 设置 `-w` 为你的渲染宽度（例如 `metrics-chart` 技能的绘图宽度），以便一个桶约等于一个像素列。值会作为请求体的 `queryOptions` (`chart-width`, `pixel-per-point`) 转发。

### 参数

MPL 可以声明参数 (`param $svc: string;`)。使用重复的 `-p name=value` 传递值。脚本会应用 API 的 `param__` 前缀；值会原封不动地作为 MPL 字面量传递（字符串字面量包括它们的引号）。

```bash
scripts/metrics-query \
  -p svc='"frontend"' \
  -p window='5m' \
  prod \
  'param $svc: string; param $window: Duration;
   `otel-metrics`:`http.server.duration` | where `service.name` == $svc | align to $window using avg' \
  now-1h now
```

必需参数必须提供；可选参数可以省略。生成的请求体形状：

```json
{
  "apl": "param $svc: string; …",
  "startTime": "now-1h",
  "endTime": "now",
  "params": { "param__svc": "\"frontend\"", "param__window": "5m" }
}
```

每种类型的字面量语法位于 `metrics-spec` 中。

## 发现 (`metrics-info`)

时间范围默认为最后 24 小时；使用 `--start` / `--end` 覆盖。两者都接受 RFC3339（允许偏移）或相对 `now` / `now-<N><unit>`（`<unit>` 在 `s m h d w` 中），在客户端端解析为 RFC3339 UTC。这比 `metrics-query` **更窄**，后者将时间原样转发给服务器，因此也接受形式如 `now-1y` 的形式；在 `metrics-info` 中，任何超出 `now` / `now-<N>[smhdw]` 的内容必须已经是 RFC3339 或请求 400s。

| 命令 | 返回 |
|---|---|
| `metrics-info <d> <ds> metrics` | 所有指标，按名称键值，带有 `{type, temporality, unit}`。 |
| `metrics-info <d> <ds> metrics --by-type` | 相同的列表按 `type` 分组（客户端端重塑）。 |
| `metrics-info <d> <ds> metrics --type Gauge --type Histogram` | 过滤后的列表（可重复，OR 语义；与 `--by-type` 组合）。 |
| `metrics-info <d> <ds> metrics <metric> info` | 单个指标的 `{type, temporality, unit}`。如果不存在则非零退出。 |
| `metrics-info <d> <ds> metrics <metric> describe` | 包裹：元数据 + 所有标签 + 标签值（一次调用完成，替代 1+1+N 轮次）。标志：`--no-values`（仅标签名），`--values-limit N`（每个标签值的上限；默认 50，0 = 无限）。 |
| `metrics-info <d> <ds> metrics <metric> tags` | 特定指标携带的标签。 |
| `metrics-info <d> <ds> metrics <metric> tags <tag> values` | 该指标的标签值。 |
| `metrics-info <d> <ds> metrics <metric> tags <tag> type` | 探测标签是否为 `int`/`float`/`string`/`bool`。返回 `{type, present_types}`；如果存在多种类型则为 `mixed`，如果不存在则为 `absent`。 |
| `metrics-info <d> <ds> tags` | 数据集中的所有标签。 |
| `metrics-info <d> <ds> tags <tag> values` | 标签的所有值（跨指标）。 |
| `metrics-info <d> <ds> find-metrics "<value>"` | 携带给定标签值（不是指标名称）的指标。 |

## 错误处理

HTTP 错误返回带有 `code` 和 `message` 的 JSON；一些错误包括 `detail` 对象：

```json
{"code": 400, "message": "MPL 语法错误：…"}
```

语法错误（400）包括一个注释的源指针，列出了失败位置的有效操作符——阅读它，它通常会指出修复方法。

| 代码 | 原因 |
|---|---|
| 400 | 无效查询语法或数据集名称错误 |
| 401 | 缺少/无效认证 |
| 403 | 无权限 |
| 404 | 数据集未找到 |
| 429 | 流量限制——后退并重试；不要死循环 |
| 500 | 内部错误 |

请求在客户端端超时 120 秒（`AXIOM_MAX_TIME` 覆盖；`AXIOM_CONNECT_TIMEOUT` 为 10 秒连接超时）。

在 500 时，使用 `curl -v` 重新运行以捕获 `traceparent` / `x-axiom-trace-id` 标头并报告它——跟踪 ID 是后端团队需要调试的。

## 脚本

| 脚本 | 用法 |
|---|---|
| `scripts/setup` | 检查要求和配置。 |
| `scripts/datasets <deploy> [--kind <kind>]` | 列出带有边缘部署的数据集。 |
| `scripts/metrics-spec` | 获取 MPL 查询规范。 |
| `scripts/metrics-query [-w px] [--pixel-per-point n] <deploy> <mpl> <start> <end>` | 执行查询；使用 `$__interval` + `-w` 进行自适应分辨率。 |
| `scripts/metrics-info <deploy> <dataset> ...` | 发现指标、标签、值。 |
| `scripts/axiom-api <deploy> <method> <path> [body]` | 低级 API 调用。 |
| `scripts/resolve-url <deploy> <dataset>` | 解析到边缘部署 URL。 |

无参数运行任何脚本以获取完整用法。
