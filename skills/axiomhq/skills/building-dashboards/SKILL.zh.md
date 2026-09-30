---
name: building-dashboards
description: 通过 API 设计和构建 Axiom 仪表板。涵盖图表类型、APL 和指标/MPL 查询模式、智能过滤器、布局和配置选项。在创建仪表板、从 Splunk 迁移或配置图表选项时使用。
---

# 构建仪表盘

## 哲学

1. **决策优先。** 每个面板都回答一个能导向行动的问题。
2. **概览 → 下钻 → 证据。** 从宏观开始，点击/筛选后缩小范围，最终以原始日志结束。
3. **速率和分位数优于平均值。** 平均值会掩盖问题；p95/p99 会暴露它们。
4. **简洁胜过繁杂。** 每个面板只问一个问题。无图表垃圾。
5. **用数据验证。** 不要猜测字段——先发现模式。
6. **按需计算或推迟。** 如果面板无法计算，用记录阻塞性质的 `Note` 替代它。永远不要用不同的量替代，即使已披露。参见 [按需计算或推迟](#compute-or-defer)。

---

## 入口

| 从...开始 | 工作流 |
|---------------|----------|
| **模糊描述** | 摄取 → 检查数据集类型 → 设计蓝图（APL 或 MPL）→ 每个面板的查询 → 部署 |
| **模板** | 选择模板 → 自定义数据集/服务/环境 → 部署 |
| **Splunk 仪表盘** | 提取 SPL → 通过 spl-to-apl 翻译 → 映射到图表类型 → 部署 |
| **Grafana 仪表盘** | 项目规范面板 (`expr`, `legendFormat`, `unit`, `title`, `description`) → PromQL 翻译 → 映射图表类型 → 部署。参见 [reference/grafana-migration.md](./reference/grafana-migration.md)。 |
| **探索** | 使用 axiom-sre 发现模式/信号 → 产品化为面板 |

---

## 摄取：首先问什么

1. **受众与决策**
   - 紧急响应分派？（快速刷新，错误聚焦）
   - 团队健康？（每日趋势，SLO 追踪）
   - 执行报告？（每周摘要，高层级）

2. **范围**
   - 服务、环境、区域、集群、端点？
   - 单一服务还是跨服务视图？

3. **数据集类型。** 运行 `scripts/metrics/datasets <deploy>` 并检查 `kind`。
   - `otel:metrics:v1` → 指标数据集，遵循 **指标路径**。
   - 其他任何类型 → 事件/日志数据集，遵循 **APL 路径**。

   > **永远不要在指标数据集上运行 `getschema`。** 它会无错误地返回 0 行。

   **APL 路径：** 使用 `['dataset'] | where _time between (ago(1h) .. now()) | getschema` 发现字段。继续步骤 4–5。

   **指标路径：**
   - `scripts/metrics/metrics-spec <deploy> <dataset>` — 任何 MPL 查询前都必须执行。
   - `scripts/metrics/metrics-info <deploy> <dataset> metrics | tags | tags <tag> values` 用于发现。
   - 如果发现为空，使用 `--start` 7 天前重试（稀疏指标）。
   - `find-metrics <value>` 搜索标签 *值*，不是指标名称——仅在与已知实体名称一起使用时使用。
   - 跳转到 **指标/MPL 蓝图**。

4. **金信号**（APL 路径）
   - 流量：每秒请求数，每分钟事件数
   - 错误：错误率，5xx 计数
   - 延迟：p50，p95，p99 持续时间
   - 饱和度：CPU，内存，队列深度，连接数

5. **下钻维度**（APL 路径）
   - 用户按什么过滤/分组？（服务，路由，状态，Pod，customer_id）

---

## 仪表盘蓝图

选择与数据集类型匹配的蓝图。

### APL 蓝图（事件/日志数据集）

#### 1. 一目了然（统计面板）
回答“现在是否出问题”的单个数字
- 最后 5 分钟错误率
- 最后 5 分钟 p95 延迟
- 最后 5 分钟请求率
- 适用时活跃警报

#### 2. 趋势（时间序列面板）
基于时间的模式，回答“什么发生了变化”
- 随时间变化的流量
- 随时间变化的错误率
- 随时间变化的延迟分位数
- 按状态/服务堆叠以比较

#### 3. 分解（表格/饼图面板）
回答“我应该在哪里查找”的 Top-N 分析
- 失败的 Top 10 路由
- Top 10 错误消息
- 按错误率最差的 Pod
- 按状态分布的请求

#### 4. 证据（LogStream + SmartFilter）
回答“具体发生了什么”的原始事件
- 过滤到错误的 LogStream
- SmartFilter 用于服务/环境/路由
- 为可读性投影关键字段

### Metrics/MPL 蓝图（指标数据集）

使用 `align to $__interval using …` 进行分桶——`$__interval` 由仪表盘运行时提供。硬编码的窗口会过度或不足地解析。用 `scripts/metrics/mpl-validate-chart` 验证每个管道；两者都会拒绝内联时间范围（`[1h..]`）。

例外：对于 `$__interval` 四舍五入为空桶的稀疏指标，可以使用固定更宽的窗口（例如 `1h`）；在图表上记录原因。

#### 1. 一目了然（统计面板）
当前值——“现在的状态是什么”
- 使用 `group using avg`（仪表）或 `group using last`（计数器）。
- 通过 `metrics-info … metrics <m> info` 读取指标的 `unit` 并传递给 `chart-add --unit`。比率指标（0–1）在 MPL 中使用 `| map * 100` 之前需要 `--unit "%"`。

#### 2. 趋势（时间序列面板）
随时间变化的趋势——“什么发生了变化”
- `align to $__interval using avg|sum|last`。
- 仅按低基数标签分组（每张图表 ≤10 系列）。
- 在 `--name` 中嵌入单位（`"P95 延迟 (ms)"`, `"内存 (MiB)"`）；在 MPL 中缩放量级（`| map / 1048576` 将字节 → MiB）。

#### 3. 分解（时间序列或表格面板）
按实体详细说明——“我应该在哪里查找”
- 按实体（主机、Pod、服务）分解指标。
- 过滤以保持系列数量可控。
- 每个面板一个维度；不要过度加载单个图表。

#### 4. 实体状态（时间序列或表格面板）
布尔/状态指标——回答“什么已开启/关闭/活跃”
- 使用 `align to $__interval using last`。
- 稀疏状态指标可能需要固定更宽的间隔（1h+）。

---

## 必需的图表结构

每个图表需要一个唯一的 kebab-case `id`（`error-rate`, `p95-latency`）；每个布局 `i` 都必须匹配一个。将相同的 id 传递给 `chart-add --id` 和 `layout-pack <id>:…`。`dashboard-assemble` 在发出前会交叉检查。

---

## 图表单位配置

将友好的单位字符串传递给 `chart-add --unit`（`"%"`, `"s"`, `"ms"`, `"B"`, `"req/s"`）。脚本根据图表类型选择 `unit` 枚举 + `customUnits` 后缀。`customUnits` 是一个标签，不是格式化器——在 MPL 中缩放量级（`| map / 1048576` 将字节 → MiB，`| map / 1000000` 将字节 → MB，`| map * 100` 将 0–1 比率 → 百分比）。对于指标图表，从 `metrics-info … metrics <m> info` 读取源单位并通过。内部（高级选项代理可能合并 `jq`）：[reference/chart-config.md](./reference/chart-config.md)。

---

## 按需计算或推迟

每个面板要么计算请求的量，要么用记录阻塞性质的 `Note` 替代。永远不要用不同的量替代——免责声明不会到达处理数字的人。

推迟模板（使用 `chart-add --type Note`）：

```
**推迟——阻塞原因：** <一句话原因>。

**原始规范：** <面板应计算的量，维度，单位>。

**取消阻塞：** <指向修复的指针>。
```

常见阻塞：MPL 解析器限制，缺少没有反向标签等效项的标签，缺少没有 OTel 重命名匹配的指标。完整理由：[reference/design-playbook.md § 替换请求的量](./reference/design-playbook.md#substituting-a-different-quantity-for-the-asked-one)。

---

## 图表类型

| 类型          | 当…时                                                | 关键约束                                                       |
|---------------|-----------------------------------------------------|----------------------------------------------------------------------|
| 统计          | 单个 KPI，当前值                           | 查询必须返回一行。                                           |
| 时间序列      | 基于时间的趋势，分位数叠加               | `bin_auto(_time)`；`percentiles_array()` 用于多分位数。       |
| 表格         | Top-N 列表，分解                             | 用 `top N` 绑定；通过 `project` 控制列。                   |
| 饼图         | ≤6 类别的总额分率                    | 聚合到 ≤6 个切片；永远不要高基数。                      |
| LogStream     | 原始事件检查                                | `take 100–500`；`project-keep` 保留相关字段；硬过滤。      |
| Heatmap       | 分布/延迟密度                      | `summarize histogram(field, buckets) by bin_auto(_time)`。            |
| 散点图        | 每组关联两个指标                     | `summarize avg(x), avg(y) by group`。                                 |
| SmartFilter   | 交互式过滤条                              | 每个面板查询需要 `declare query_parameters`。参见 `reference/smartfilter.md`。 |
| Monitor List  | 监控状态显示                              | 无 APL — 在 UI 中选择监控。                                      |
| Note          | Markdown 上下文，标题，运行手册链接            | `chart-add --type Note --text "<md>"`。                               |

每类型 APL 配方：`reference/chart-cookbook.md`。

---

## 图表配置

`chart-add` 覆盖常见路径（类型，id，名称，查询，数据集，单位，sparkline）。对于它不暴露的选项——`aggChartOpts` 变体在时间序列，`tableSettings.columns` 在表格/LogStream，`hideHeader` 等——从 `chart-add` 输出开始，并使用 `jq` 合并额外的字段。有关完整选项集，参见 `reference/chart-config.md`，以及合并任何定制内容之前的拒绝字段列表。

---

## APL 模式

### 时间过滤

仪表盘图表查询继承时间来自选择器——省略 `_time` 过滤。临时查询（Axiom 查询选项卡，`axiom-sre`）需要显式的 `where _time between (ago(1h) .. now())`。

### 分桶大小选择

使用 `bin_auto(_time)`——它会调整到仪表盘时间窗口。手动 `bin(_time, …)` 仅在非标准情况下合理（例如匹配上游批处理间隔）；记录原因。

### 基数限制

用 `top N` 或过滤器绑定 `summarize … by …`。对高基数字段的无限制分组（`user_id`, `trace_id`）会导致爆炸。

```apl
| summarize count() by route | top 10 by count_   // 有界
| summarize count() by user_id                    // 无界 — 避免
```

### 字段转义
带点的字段需要括号表示：

```apl
| where ['kubernetes.pod.name'] == "frontend"
```

字段名中带点（非层级）需要转义：

```apl
| where ['kubernetes.labels.app\\.kubernetes\\.io/name'] == "frontend"
```

### 配方

流量，错误率，延迟分位数，以及其他金信号 APL 配方：`reference/chart-cookbook.md`。

---

## 布局组合

`layout-pack` 按行主序将图表打包到 12 列网格中，使用每类型的默认值（统计 3×3，时间序列 6×4，表格 6×5，LogStream 12×6，Note 12×2）。需要时用 `id:WxH` 覆盖。部分蓝图：`reference/layout-recipes.md`。命名和面板排序约定：`reference/design-playbook.md`。

---

## 仪表盘设置

### 刷新率

`dashboard-assemble --refresh oncall|team|exec` (60/300/900s) 或传递显式整数（≥60）。短刷新 + 长时间范围 = 昂贵的查询；为执行/每周板选择较长的端。

### 共享

API 令牌仅创建共享仪表盘（`owner: "X-AXIOM-EVERYONE"`）；不支持私有仪表盘。用户级数据可见性仍由数据集权限强制执行。

### URL 时间范围参数

`?t_qr=24h`（快速范围），`?t_ts=...&t_te=...`（自定义），`?t_against=-1d`（比较）

---

## 设置

工具，先决条件和 `~/.axiom.toml` 配置：参见 `README.md`。使用 `scripts/setup` 验证。

---

## 部署

### 脚本

| 脚本 | 用法 |
|--------|-------|
| `scripts/chart-add --type <T> --id <id> --name <n> [--apl <q> \| --mpl <q> --dataset <d>] [--unit <u>]` | **向 stdout 发出一个单个图表 JSON**。分割 APL vs MPL；MPL 查询会检查内联时间范围；按图表类型应用单位字段。 |
| `scripts/layout-pack <id>:<Type\|WxH> ...` | **向 stdout 发出一个布局 JSON 数组**。按行主序到 12 列网格；类型名称映射到默认大小。 |
| `scripts/dashboard-assemble --name … --datasets … --layout F.json [opts] CHART_FILES…` | **从图表文件 + 布局组合一个完整的仪表盘 JSON**。拥有封装（`owner`, `schemaVersion`, `qr-` 前缀，`refreshTime` 验证，id 交叉检查）。 |
| `scripts/dashboard-list <deploy>` | 列出所有仪表盘 |
| `scripts/dashboard-get <deploy> <id>` | 获取仪表盘 JSON |
| `scripts/dashboard-validate <file>` | 验证 JSON 结构 |
| `scripts/dashboard-create <deploy> <file>` | 创建仪表盘 |
| `scripts/dashboard-update <deploy> <id> <file>` | 更新（需要版本） |
| `scripts/dashboard-chart-patch <deploy> <id> <chart-id> <patch-file> (--version <version> \| --overwrite)` | 补丁单个图表 |
| `scripts/dashboard-copy <deploy> <id>` | 克隆仪表盘 |
| `scripts/dashboard-link <deploy> <id>` | 获取可共享的 URL |
| `scripts/dashboard-delete <deploy> <id>` | 删除（带确认） |
| `scripts/axiom-api <deploy> <method> <path>` | **仪表盘/应用 API 仅**（重写为 `app.*`）。对于数据/指标端点使用 `scripts/metrics/axiom-api` |
| `scripts/metrics/axiom-api <deploy> <method> <path>` | **数据/指标 API**（支持 `AXIOM_URL_OVERRIDE` 用于边缘路由） |
| `scripts/metrics/datasets <deploy>` | 列出具有 `kind` 和边缘部署的数据集 |
| `scripts/metrics/metrics-spec <deploy> <dataset>` | 获取 MPL 查询规范 |
| `scripts/metrics/metrics-info <deploy> <dataset> ...` | 发现指标，标签和值 |
| `scripts/metrics/metrics-query <deploy> <mpl> <start> <end>` | 执行指标查询（原始——无 `$__interval` 注入） |
| `scripts/metrics/mpl-validate-chart <deploy> '<MPL>' [start] [end] [--interval D]` | **验证图表 MPL 管道。** 自动注入 `param $__interval: Duration;` 和 `-p __interval=…`；拒绝内联时间范围。在编写图表查询时使用此代替原始 `metrics-query`。 |

> 两个 `axiom-api` 脚本不可互换。`scripts/axiom-api` 用于仪表盘应用 API；`scripts/metrics/axiom-api` 用于数据/指标端点和边缘路由。错误一个 → 404。

### 针对性图表更新

当更改单个现有图表且仪表盘布局，元数据和其他图表应保持不变时，使用 `scripts/dashboard-chart-patch`。它调用 `PATCH /v2/dashboards/uid/{uid}/charts/{chartId}` 并在 `chart` 请求字段下使用 JSON 合并补丁。

补丁文件仅包含要更改的图表字段：

```json
{
  "name": "Error Rate (5m)",
  "query": { "apl": "['logs'] | summarize errors=countif(status >= 500)" },
  "config": { "stale": null }
}
```

`null` 删除现有字段。嵌套对象递归合并。如果 `id` 在补丁中存在，它必须匹配 `<chart-id>` 路径参数。服务器在保存之前验证完整的仪表盘。

使用 `--version <version>` 进行乐观并发控制后获取仪表盘（使用 `dashboard-get`）。仅当需要最后写入者胜利行为时使用 `--overwrite`。继续使用 `dashboard-update` 进行布局更改，多图表编辑，仪表盘元数据，所有者，刷新间隔或时间窗口更新。

### 工作流

`chart-add`，`layout-pack` 和 `dashboard-assemble` 拥有 JSON 形状。每个图表都存在于其临时文件中；没有任何图表形状重新进入代理的上下文。

1. 发现模式（`axiom-sre` / `getschema` 用于事件；`metrics-spec` + `metrics-info` 用于指标）。
2. 编写每个面板查询。通过 `axiom-sre` 验证 APL（带显式时间过滤）；通过 `scripts/metrics/mpl-validate-chart` 验证 MPL。
3. `chart-add --type … --apl '<APL>'` *或* `chart-add --type … --mpl '<MPL>' --dataset <name>` 每个图表，重定向到其自己的文件。
4. `layout-pack <id>:<Type|WxH> …` 用于布局（id 在显示顺序中）。
5. `dashboard-assemble --name … --datasets … --layout LAYOUT CHART_FILES…` 组合。
6. `dashboard-validate` 然后 `dashboard-create`（或 `dashboard-update`）。
7. `dashboard-link` 用于 URL — 永远不要手动构造。

---

## 兄弟技能集成

- **spl-to-apl** — Splunk SPL → APL (`timechart` → TimeSeries, `stats` → Statistic/Table)。参见 `reference/splunk-migration.md`。
- **axiom-sre** — 通过 `getschema` 进行模式发现，基线探索。
- **query-metrics** — 指标数据集/标签/值发现；相同的脚本已作为 `scripts/metrics/` 下的组件提供。

---

## 模板

使用 `chart-add` + `layout-pack` + `dashboard-assemble` 组合。预构建的模板保留在 `reference/templates/` 下 (`blank.json`, `service-overview.json`, `service-overview-with-filters.json`, `api-health.json`) 以供遗留使用；`dashboard-from-template` 可实例化它们，但假设特定的字段名 (`service`, `status`, `route`, `duration_ms`) 并需要 `sed` 修复。优先为新工作使用组合方式。

---

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `getschema` 返回 0 行 | 数据集是 `otel:metrics:v1` | 使用 `scripts/metrics/metrics-info` 进行指标发现。 |
| 指标发现返回空结果 | 24 小时默认窗口之外的稀疏指标 | 使用 `--start` 7 天前的参数重试。 |
| 指标 API 调用返回 404 | 使用了 `scripts/axiom-api`（仪表板）而不是 `scripts/metrics/axiom-api` | 使用 `scripts/metrics/axiom-api` 进行 `/v1/query/*` 和 `/v1/datasets`。 |
| 统计显示 `1` 而不是 `100%`（对于 0-1 比率） | `Percent` 枚举不自动乘以 100 | 在 MPL 中使用 `\| map * 100`，然后 `chart-add --unit "%"`。 |
| OTel 直方图图表显示无意义的内容 | 直方图对齐为标量 | 使用 `bucket … using interpolate_cumulative_histogram`（或每 `temporality` 使用 `_delta`）。参见 [promql-to-mpl.md § 直方图转换](./reference/promql-to-mpl.md#histogram-translation-histogram_quantile--bucket--using-interpolate__histogram)。 |
| Grafana 迁移的筛选/分组在错误的数据子集上 | 未使用 `description` 读取 `expr`，反之亦然 | 在编写前投影所有五个面板字段；参见 [reference/grafana-migration.md](./reference/grafana-migration.md)。 |
| PromQL 指标名未找到 | 跳过了 OTel 重命名规则 | 移除 `_total`，分解直方图，标准化单位；使用 `metrics-info` 验证。标签需要反向标签发现。参见 [grafana-migration.md § 名称映射](./reference/grafana-migration.md#name-mapping-promql--otel-ingest)。 |
| MPL 图表在维度上聚合，而 PromQL 在筛选/分组上 | 在转换过程中丢失了选择器或 `by(...)` | 每个 `{label=…}` → `where`；每个 `by(…)` → `group by`。参见 [reference/promql-to-mpl.md](./reference/promql-to-mpl.md)。 |
| 面板发送了与请求不同的数量 | 替换而不是延迟 | 用记录阻塞性质的 `Note` 替换。参见 [Compute or Defer](#compute-or-defer)。 |
| 403 "创建私有仪表板" | API 令牌仅创建共享仪表板 | 将 `owner` 留为 `dashboard-assemble` 的默认值 (`X-AXIOM-EVERYONE`)。 |

---

## 参考

- `reference/chart-config.md` — 所有图表配置选项（JSON）
- `reference/metrics-mpl.md` — 指标/MPL 图表合同和发现脚本
- `reference/smartfilter.md` — SmartFilter/FilterBar 完整配置
- `reference/chart-cookbook.md` — 每种图表类型的 APL 模式
- `reference/layout-recipes.md` — 网格布局和部分蓝图
- `reference/splunk-migration.md` — Splunk 面板 → Axiom 映射
- `reference/grafana-migration.md` — Grafana 面板 → Axiom 映射（规范投影，PromQL→MPL 指针，OTel 重命名规则）
- `reference/promql-to-mpl.md` — PromQL → MPL 转换规则（选择器，分组，比率，直方图，反向标签发现）
- `reference/design-playbook.md` — 决策优先设计原则
- `reference/templates/` — 可直接使用的仪表板 JSON 文件

对于 APL 语法：https://axiom.co/docs/apl/introduction
