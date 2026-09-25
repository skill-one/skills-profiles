# ClickHouse 管理的 Postgres RCA

## 何时使用

当用户报告 ClickHouse 管理的 Postgres 实例出现性能下降、高 CPU 占用率、低吞吐量、缓存抖动或任何无法解释的问题时触发。

## 您可以访问的内容

`https://api.clickhouse.cloud` 上的两个 API（使用 ClickHouse Cloud API 密钥/密钥对进行 HTTP Basic 认证）：

- **Prometheus 指标** — Prometheus 标签下的操作 `postgresInstancePrometheusGet`。返回 Prometheus 说明格式。一个 Postgres 服务的系统和工作负载指标。
- **慢查询模式** — Postgres 标签下的操作 `slowQueryPatternsGetList`。返回规范化查询模式的每个摘要延迟、IO 和调用统计信息。**Beta 版本。**

两个端点都需要 `organizationId` 和 `serviceId` 作为路径参数。用户必须提供这两个参数，以及 API 密钥/密钥对。

## 您无法访问的内容

- 查询计划 / EXPLAIN 输出。
- 每个表的扫描类型计数器（`seq_scan` / `idx_scan`）。
- 自动清理或最后一次 ANALYZE 时间戳。

从 IO 和时间信号中推断原因，而不是从计划树中推断。

## 工作流程

六个步骤，按顺序执行。不要跳过步骤。

步骤 2 和 3 仅共享认证 — 它们之间没有数据依赖关系。并行运行它们（后台 curl，`&` + `wait`）以将顺序的 ~2 秒墙时间减少到 ~1 秒。

### 1. 发现活 API 的形状

这些端点是 Beta 版本 — 路径、参数和 JSON 字段名可能会发生变化。遵循 `rules/openapi-discovery.md` 来：

1. 从 `https://api.clickhouse.cloud/v1` 获取 OpenAPI 规范。
2. 通过 `operationId` 定位两个操作：
   - `postgresInstancePrometheusGet`（Prometheus 标签）
   - `slowQueryPatternsGetList`（Postgres 标签）
3. 解析它们的路径模板、必需的查询参数，以及（对于慢查询端点）响应模式。
4. 从模式属性描述中构建会话范围的角色映射：`{ 语义角色 → 实际字段名 }`。

在后续的请求和引用中使用解析后的名称。永远不要从内存中硬编码字段名。

### 2. 一次抓取 Prometheus 以获取系统仪表板

遵循 `rules/prometheus-scrape.md`。**一次抓取，不等待。** 您要的是不需要差值的仪表板（当前值）：`CacheHitRatio`、`ActiveConnections`、`MemoryUsedPercent`、`FilesystemUsedPercent`。

一个 `CacheHitRatio` 远低于 ~95% 的工作负载应该适合缓存，这是一个独立的真实信号。`ActiveConnections` 向连接池上限上升是一个独立的真实信号。这些不需要变化率。

第二次抓取用于计数器差值是 **可选的**，仅在步骤 4 筛分指向写拥塞时使用（此时死锁和回滚 *速率* 很重要，慢查询模式 API 不能替代）。对于读路径情况（最常见的 RCA 形状），单个抓取就足够了。

### 3. 拉取顶级慢查询模式

请求慢查询模式。遵循 `rules/slow-query-patterns-fields.md` 了解重要的字段以及如何读取它们。这是主要的诊断 — 它返回您请求的窗口内每个模式的累积总计数（调用次数、运行时间、块、行），这是您原本从两个 Prom 抓取中推导出的“变化率”数据 — 但按查询且无需等待。

如果没有模式返回有意义的 `totalDurationUs`，报告可能被夸大或问题不是查询型的。停止并告诉用户您查看了什么。

### 4. 筛分：选择正确的启发式方法

遵循 `rules/triage.md`。将 Prom + 慢查询信号与其中一个启发式形状匹配。每个形状都指向一个特定的启发式文件：

- `rules/heuristic-full-scan.md` — 读路径全扫描。
- `rules/heuristic-hot-loop.md` — N+1 / 应用程序中的热循环。
- `rules/heuristic-write-congestion.md` — 死锁、慢写、高回滚率。

如果信号没有干净地匹配任何形状，不要编造假设。展示顶级模式并询问用户他们认出了哪个工作负载。欢迎作为 PR 提交新的启发式方法。

### 5. 推断，然后建议

使用 `rules/output-template.md` 中的格式。始终包括：症状、证据、假设（注意您无法从表面排除的任何替代原因）、短期修复和长期跟进。

### 6. 不要应用修复

遵循 `rules/recommend-only.md`。永远不要运行 DDL。永远不要调用 `pg_cancel_backend` 或 `pg_terminate_backend`。写出建议，解释原因，并让人类应用它。

## 完整编译文档

要获取包含每个规则在单个上下文中展开的完整指南：`AGENTS.md`。
