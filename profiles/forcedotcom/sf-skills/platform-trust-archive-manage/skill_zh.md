# Salesforce 存档

通过其 Connect API 和 `ArchiveActivity` 元数据对象操作 Salesforce 存档（也称为 Trusted Services Archive）。本技能涵盖如何搜索和恢复存档记录、运行分析器、处理 RTBF 删除和 PII 掩码、检查存储，以及——最常被忽略的部分——如何从 `ArchiveActivity` 中读取存档作业状态，并使用作业的 Id + 类型下载其日志。

## 范围

- **在范围内**：调用 `/platform/data-resilience/archive/` 下的 Archive Connect API 操作；通过 SOQL/Connect 查询 `ArchiveActivity` 对象；将作业的 `ArchiveActivity` 记录与其日志下载端点相关联；每个异步操作的写入后验证模式。
- **超出范围**：定义存档策略 / `ArchivePolicyDefinition` 元数据；构建 UI；生成基于存档数据的流程（`ArchiveActivity` **不可** Flow 查询——参见注意事项）；与附加组件无关的通用备份/导出工具。

---

## 必需的输入

在执行前收集或推断：

- **操作意图**：搜索（这也是查看存档记录的方式）、解档、分析、掩码、RTBF、存储检查或作业状态/日志查找。
- **目标 sObject** (`sobjectName`)：搜索和解档时必需。
- **过滤器**：搜索和解档需要 `sobjectName` + 至少一个过滤器。
- **用于日志下载**：已完成并生成日志的作业的 `requestId`（一个 `ArchiveActivity` Id，`8qv…` 前缀），以及 `reportType` = 该活动的 `Type`。

前提条件（如果调用返回不允许错误，则确认或向用户展示）：
- **组织** 必须启用 Salesforce 存档。每个操作都以此为基础。
- 每个操作都需要在组织权限之上特定的**用户权限**——见下方的权限表。没有单一的“存档管理员”角色；访问权限按功能划分。

---

## 权限

每个操作首先要求组织必须启用 Salesforce 存档。在此基础上，每个功能都由一个独特的**用户权限**控制。如果用户没有权限进行调用，则会失败并返回“不允许”错误——将错误与下方的缺失权限进行匹配。

| 操作 | 需要的用户权限 |
|-----------|--------------------------|
| `search-archived-records`, `get-search-archived-records-next-page` | `ViewSearchPage`（存档搜索）——**不是** `ViewArchivedRecords` |
| `search-archived-records-with-sharing-rules` | `ViewArchivedRecords` |
| `unarchive-records` | `UnarchiveSdk` |
| `forget-archived-records`（RTBF）+ `get-rtbf-status` | `Rtbf` |
| `mask-archived-records` + `get-masking-status` | `Rtbf`（掩码共享相同的 `Rtbf` 权限——**不是** 分离的授权） |
| `run-analyzer`, `get-analyzer-report`, `get-archive-storage-used` | `ArchiveAnalyzer` |
| `get-execution-details-stream-url`, `get-failed-records-stream-url` | `ViewActivitiesPage`（存档活动） |

---

## 工作流

所有步骤在任务内按顺序执行。第一次接触该区域时，请阅读参考文件。

1. **确定操作并阅读合同**——不要依赖对存档 API 的通用了解，其合同并不明显。加载 `references/connect-api-operations.md` 以获取每个 Archive Connect API 操作的精确请求/响应形状、必需输入和每个操作的注意事项。在构建任何调用之前（例如 `dateRanges` 复数与单数、`isSuccess` 标志与 HTTP 状态、`url: null` 表示无日志）执行此操作。

2. **对于作业状态/监控，阅读数据模型**——当任务涉及存档作业、失败、进度、计数或日志时，加载 `references/archive-activity-entity.md` 以获取 `ArchiveActivity` 字段参考及其与 Connect API 的链接。通过 SOQL 或 Connect 查询 `ArchiveActivity`——**不是** Flow。对于端到端示例（查找失败/进行中的作业，然后下载它们的执行详情和失败记录日志），加载 `examples/monitor-failed-jobs.md`。

3. **构建并发送调用**——每个操作都是一个 `{method, path, body}` REST 调用。使用您的环境提供的任何 Connect/REST API 工具（一个调用 Connect/REST API 的 MCP 服务器、`sf` CLI 或任何 REST 客户端）发送它。两条路径规则至关重要（完整的每个操作合同在 `references/connect-api-operations.md` 中）：

   - **本技能中的操作名称**不是 URL 路径。`search-archived-records`、`unarchive-records` 等是标签；永远不要将它们放入路径。使用下面的短路径字面量（每个相对于基本 `/platform/data-resilience/archive`）。将操作名称作为路径段（例如 `/…/archive/search-archived-records`）会返回 **404**。
   - **路径在 `/platform/data-resilience/archive/…` 处停止——这里没有 `/connect` 段**，尽管这是一个 Connect API。在此处返回 **404 / `NOT_FOUND` 意味着路径错误，而不是存档被禁用**——在确定附加组件缺失之前修复路径。

   | 操作 | 方法 + 路径 | 备注 |
   |-----------|---------------|-------|
   | `search-archived-records` | `POST /search` | 需要 `sobjectName` + ≥1 过滤器 |
   | 搜索下一页 | `GET /search/next/{scrollId}` | 当 `scroll_id == "-1"` 时停止 |
   | 搜索带共享规则 | `POST /search/with-sharing-rules` | 使用 `filtersJson` 对象映射 |
   | `unarchive-records` | `POST /unarchive` | `sobjectName` + 过滤器 |
   | 运行分析器 / 报告 | `POST /analyzer/run` · `GET /analyzer/report` | |
   | 忘记 / RTBF + 状态 | `POST /rtbf` · `GET /rtbf/{requestId}` | |
   | 掩码 + 状态 | `POST /mask` · `GET /mask/{requestId}` | |
   | 存储使用 | `GET /storage/archive-used` | |
   | 执行详情 / 失败记录日志 | `GET /log/execution-details-stream-url` · `GET /log/failed-records-stream-url` | 查询参数 `requestId`, `reportType` |

   使用 `sf` CLI 时，在路径前缀 `/services/data/v67.0`；某些 MCP/REST 工具使用裸路径并自己添加版本（工具依赖——见参考）。然后遵循合同：对于搜索，提供 `sobjectName` + ≥1 过滤器；对于日期过滤，使用复数 `dateRanges` 数组 `{field, from, to}`，包含完整的 ISO-8601 日期时间。

4. **根据正确的信号分支**——某些操作返回 HTTP 201 并带有请求级别的成功标志（`body.statusCode`, `body.isSuccess`）。阅读 `references/connect-api-operations.md` 以获取每个操作应信任的信号；永远不要假设 HTTP 状态本身意味着成功。

5. **每次写入后验证**——重新读取状态以确认效果（见下方的写入后验证表）。异步操作（分析器、RTBF、掩码）返回您必须轮询的请求 ID。

---

## 写入后验证

| 写入后 | 通过以下方式确认 |
|------------------|-----------|
| `run-analyzer` | 轮询 `get-analyzer-report` 直到报告被填充 |
| `unarchive-records` | 重新运行 `search-archived-records` — 确认记录已离开存档 |
| `forget-archived-records`（RTBF） | 使用返回的 `request_id` 轮询 `get-rtbf-status` |
| `mask-archived-records` | 使用返回的 `request_id` 轮询 `get-masking-status` |

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 搜索和解档需要 `sobjectName` + 至少一个过滤器 | 无过滤器的请求会以“搜索必须基于至少一个字段”被拒绝——不允许全对象操作。 |
| 日期过滤器必须是完整的 ISO-8601 日期时间（`2020-01-01T00:00:00Z`） | 日期值（`2020-01-01`）返回 `400 JSON_PARSER_ERROR`，因为该字段类型为 `xsd:dateTime`。 |
| 搜索使用 `dateRanges`（复数数组）；解档使用 `dateRange`（单数） | 它们是两个端点上真正的不同字段；使用错误的形状会静默地丢弃过滤器或返回 400。 |
| 当 `scroll_id == "-1"` 时停止分页 | 使用 `"-1"` 调用 `get-search-archived-records-next-page` 会返回 500。 |
| 日志下载需要一个真实的 `ArchiveActivity` Id 作为 `requestId` + 该活动的 `Type` 作为 `reportType` | 后端通过活动记录解析日志；不匹配的 `reportType` 返回无日志。 |
| 排除对象无法检索 | `Feed`、`History`、`Relation`、`Share` 无法搜索；文件/附件无法通过此 API 检索——不要承诺它们。 |
| 通过 SOQL/Connect 查询 `ArchiveActivity`，永远不要使用 Flow | `ArchiveActivity` 有 `isProcessEnabled=false`，因此 Flow 上的“获取记录”元素会失败并返回“您不能在流程中获取 ArchiveActivity 记录”。 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 将 HTTP 201 视为成功 | 几个操作返回 201 并带有请求级别的结果。根据 `body.statusCode`（搜索）或 `body.isSuccess`（`with-sharing-rules`）分支，而不是 HTTP 代码。 |
| 使用 `run-analyzer.isRunning` 作为信号 | 它**总是** `null`；该端点只填充 `message`。轮询 `get-analyzer-report` 以确认完成，而不是使用它。 |
| `search-archived-records-with-sharing-rules` 过滤器作为数组 | `filtersJson` 必须是 JSON 编码的**对象映射** `{"Field":"Value"`}，而不是 `{field,value}` 的数组；数组形式返回 `isSuccess:false "No valid filters provided"`。 |
| 日志 `url` 被视为存在，因为状态是 201 | `get-*-stream-url` 返回 `{url}`；`url: null` 表示未解析日志。始终检查 `url != null`。 |
| 误读 `get-archive-storage-used` | `usedStorage[]`/`availableStorage[]` 是并行的位置数组：索引 0=组织 DATA，1=组织 FILE，2=存档 RECORDS，3=存档 FILE。`availableStorage[2]`/`[3]` 是**总是 0**（存档层不计量）——这意味着“未跟踪”，而不是“已满”。 |
| 期望在 Flow 中找到 `ArchiveActivity` | 它不可 Flow 启用（`isProcessEnabled=false`）。使用 SOQL/Connect/报告。 |
| 达到解档限制 | 解档进程每个请求最多处理 ≤1000 个匹配记录，每小时/组织 ≤50 个请求，并恢复每个匹配的完整存档层次结构。 |
| RTBF/掩码限制 | `criteria` ≤10 条目（每个对象一条），每天 ≤10,000 个根记录（RTBF 和掩码共享），掩码不可逆。两者 RTBF 和掩码都由相同的 `Rtbf` 用户权限控制。 |

---

## 输出预期

这是一个知识/API 技能——它生成 API 调用及其解释结果，以及针对 `ArchiveActivity` 的 SOQL。它不会生成可部署的元数据。每个任务的交付成果：正确的操作调用、正确的成功信号分支、写入后验证确认。

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/connect-api-operations.md` | 构建任何 Archive Connect API 调用之前——每个操作的完整合同、成功信号和限制 |
| `references/archive-activity-entity.md` | 对于任何作业状态/失败/进度/日志任务——`ArchiveActivity` 字段参考及其与日志下载端点的链接 |
| `examples/monitor-failed-jobs.md` | 跟随端到端监控流程：查找失败/进行中的作业，然后下载它们的日志 |
