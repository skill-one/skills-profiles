# 远程监控查询技能

将此技能用作任何可能从远程监控数据中获取答案的调查、调试或数据问题的入口点。它帮助您确定相关信号所在的**位置**（指标、日志、跟踪、RUM），并告诉您在查询前**需要加载哪些参考文件**。

## 加载参考文件

在查询前，加载所选支柱的参考文件：

| 柱 | 加载这些文件 |
|---|---|
| 日志 | `references/dataprime-reference.md` + `references/logs-querying.md` |
| 跨度 / 跟踪 | `references/dataprime-reference.md` + `references/spans-querying.md` |
| 指标 | `references/promql-guidelines.md` + `references/metrics-querying.md` |
| RUM（前端） | `references/dataprime-reference.md` + `references/logs-querying.md` + `references/rum-querying.md` + `references/rum-fields.md` |
| 仅 DataPrime 语法 | `references/dataprime-reference.md` |

---

## 安全性

所有查询命令（`cx logs`、`cx spans`、`cx metrics`、`cx dataprime`、`cx search-fields`）都是只读的，并在 `--read-only` 模式下工作。它们永远不会修改数据，并且可以自由运行，无需 `--yes`。

---

## 快速路由指南

使用此表格解决明显情况下某个支柱是明显首选的情况：

| 问题类型 | 首选 | 备选 |
|---|---|---|
| UI 行为、页面加载、前端错误 | RUM | 跟踪（如果与后端相关） |
| 端点延迟、吞吐量、错误率 | 指标 | 跟踪（用于每个请求的详细信息） |
| 服务间依赖关系、请求流 | 跟踪 | 日志（用于调试输出） |
| 具体错误消息、堆栈跟踪 | 日志 | 跟踪（用于请求上下文） |
| 基础设施健康（CPU、内存、磁盘） | 指标 | - |
| 业务事件（购买、注册） | 取决于 - 请参阅发现工作流 | - |

对于**模糊问题**（例如，“用户上周花了多少钱？”），信号可能存在于任何支柱中。请遵循下方的发现工作流。

---

## 发现工作流

当答案可能存在于多个支柱中时，并行运行发现以找到最佳来源。

### 第 1 步：搜索指标

检查是否存在相关指标：

```bash
cx metrics search --name '*transaction*'
cx metrics search --name '*payment*'
cx metrics search --name '*revenue*'
cx metrics search --description "total purchase amount"
```

如果找到匹配的指标，加载 `references/promql-guidelines.md` + `references/metrics-querying.md` 并继续。

### 第 2 步：搜索日志和跨度字段

使用语义字段搜索查找相关的 DataPrime 路径：

```bash
cx search-fields "transaction amount" --dataset logs
cx search-fields "payment total" --dataset spans
cx search-fields "purchase value" --dataset logs --limit 10
```

如果您知道应该出现在数据中的具体值，但不知道哪个字段包含它，请使用值搜索。它返回匹配的字段键以及样本值，这还可以让您推断字段的类型（字符串、数值、枚举等）：

```bash
cx search-fields "payment_failed" -s value --dataset logs
cx search-fields "grpc.status.UNAVAILABLE" -s value --dataset spans
cx search-fields "eu-west-1" -s value --dataset all
```

**要求：** `cx search-fields` 需要一个 Coralogix API 密钥或活动配置文件上的 OAuth。如果凭证缺失，提示用户运行 `cx profiles add <name>`。

如果找到匹配字段：
- 对于 **日志**：加载 `references/dataprime-reference.md` + `references/logs-querying.md`
- 对于 **跨度**：加载 `references/dataprime-reference.md` + `references/spans-querying.md`

### 第 3 步：搜索代码库

当发现结果模糊或您需要验证指标/字段实际代表什么时，搜索代码库：

- 查找指标注册代码（例如，`prometheus.NewCounter`、`metrics.record`）
- 查找发出字段的日志语句（例如，`logger.info("transaction", ...)`）
- 查找跨度属性（例如，`span.setAttribute("purchase.amount", ...)`）

这确认了语义含义，并帮助您选择正确的支柱。

### 第 4 步：选择并查询

根据发现结果，选择信号最清晰的支柱，加载其参考文件（请参阅 [加载参考文件](#loading-references)），然后进行查询。

---

## 备选和转向

**如果初始路由未产生结果，请转向另一个支柱。**

示例转向路径：
- 指标为空 → 尝试跟踪（每个请求的数据）或日志（事件记录）
- 日志为空 → 尝试跟踪（结构化跨度属性）或指标（聚合计数器）
- 跟踪为空 → 尝试日志（基于文本的调试输出）

不要在失败一次后停止。在得出数据不存在的结论前，至少尝试两个支柱。

---

## CLI 命令参考

| 命令 | 目的 | 使用时机 |
|---|---|---|
| `cx schema` | 输出完整的命令树为 JSON | 发现所有可用命令及其标志 |
| `cx metrics search --name <pattern>` | 通过名称查找指标 | 指标发现的第一步 |
| `cx metrics search --description <text>` | 语义指标搜索 | 当您知道想要什么但不知道名称时 |
| `cx search-fields "<text>" --dataset logs` | 通过描述查找日志字段 | 基于日志的问题发现 |
| `cx search-fields "<text>" --dataset spans` | 通过描述查找跨度字段 | 基于跟踪的问题发现 |
| `cx search-fields "<value>" -s value --dataset logs` | 查找包含已知值的日志字段 | 当您知道值但不知道哪个日志字段包含它 — 还可从返回值推断字段类型 |
| `cx search-fields "<value>" -s value --dataset spans` | 查找包含已知值的跨度字段 | 当您知道值但不知道哪个跨度属性包含它 |
| `cx search-fields "<value>" -s value --dataset all` | 同上，跨日志和跨度 | 当您希望同时搜索日志和跨度时 |
| `cx spans "filter $l.serviceName == '<service>'" --limit 10` | 通过服务搜索跨度 | 当调查特定服务时 |
| `cx dataprime list` | 列出 DataPrime 命令/函数 | 当构建日志或跨度查询时 |
| `cx dashboards search "<description>"` | 通过自然语言描述查找现有仪表板 | 在创建新仪表板前 — 检查是否已存在 |
| `cx dashboards query-search --description "<text>"` | 查找查询涵盖某个主题的仪表板组件 | 发现某个主题已被如何监控 |
| `cx dashboards query-search --field "<field-path>"` | 查找引用特定字段的组件 | 为已知字段重用现有的 PromQL/DataPrime 模式 |

---

## 示例

### 示例 1：业务问题（模糊来源）

**问题：** “用户上周在平台上花了多少钱？”

**方法：**
1. 搜索指标：`cx metrics search --name '*revenue*'` 和 `cx metrics search --name '*transaction*'`
2. 搜索日志字段：`cx search-fields "transaction amount" --dataset logs`
3. 搜索跨度字段：`cx search-fields "payment total" --dataset spans`
4. 如果存在类似 `payment_total_usd` 的指标，加载指标参考文件并运行范围查询
5. 如果只有日志包含数据，加载日志参考文件并使用 DataPrime 聚合
6. 如果跟踪有 `purchase.amount` 属性，加载跨度参考文件

### 示例 2：延迟问题（明确首选）

**问题：** “结账路由的平均延迟是多少？”

**方法：**
1. 首先尝试指标：`cx metrics search --name '*checkout*latency*'` 或 `cx metrics search --name '*http*duration*'`
2. 如果存在直方图指标，加载指标参考文件并使用 `histogram_quantile`
3. 如果没有指标，转向跟踪：加载跨度参考文件并聚合跨度持续时间

### 示例 3：前端性能（RUM）

**问题：** “为什么用户的仪表板页面加载缓慢？”

**方法：**
1. 这显然是一个 RUM 问题 - 加载 `references/rum-querying.md` + `references/rum-fields.md` + `references/logs-querying.md` + `references/dataprime-reference.md`
2. 查询 Web Vitals 和页面加载时间
3. 如果 RUM 显示后端调用缓慢，转向跨度参考文件以查看 API 调用

### 示例 4：错误调查（日志 + 跟踪）

**问题：** “为什么用户在支付端点收到 500 错误？”

**方法：**
1. 检查错误率指标 → 加载指标参考文件
2. 搜索错误日志 → 加载日志参考文件
3. 获取失败请求的跟踪 → 加载跨度参考文件
4. 交叉参考：在日志中查找跟踪 ID，然后获取完整跟踪以查找根本原因

---

## 超越调查

并非所有问题都能通过查询数据解决。如果用户的意图是操作而非调查，请路由到相应的流程技能：

| 用户意图 | 路由到 |
|---|---|
| 降低成本、检查使用量、TCO 政策 | `cx-cost-optimization` |
| 分配案例、谁被通知、案例时间线 | `cx-cases` |
| SLO 状态、错误预算、服务级目标 | `cx-slos` |
| 设置监控、Webhook、通知 | `cx-observability-setup` |
| 配置解析规则、增强、E2M | `cx-data-pipeline` |
| 访问审计、API 密钥、用户管理 | `cx-platform-admin` |
| 创建或管理仪表板 | `cx-dashboards` |
| 查找或搜索现有仪表板 | `cx-search-dashboard` |

---

## 关键原则

- **查询前加载参考文件**：首先检查 [加载参考文件](#loading-references) 表
- **查询前发现**：始终运行搜索/发现以找到正确来源
- **并行发现**：对于模糊问题，同时搜索指标、日志和跨度
- **用代码验证**：当不确定指标或字段代表什么时，检查代码库
- **失败时转向**：如果一个支柱为空，在放弃前尝试另一个支柱
