# 只读库存

## 目的

在不进行修改的情况下，构建一个有证据支持的 PlanetScale 数据库清单。

## 允许的操作

默认允许：

- 列出组织、数据库、分支、键空间、区域和大小。
- 读取分支元数据。
- 读取 webhook 配置。
- 读取模式建议。
- 通过 MCP 或 API 读取查询洞察、异常和查询模式。
- 读取流量预算和规则。
- 读取 Postgres 角色和非秘密角色元数据。
- 读取备份计划和恢复元数据。
- 读取分支模式。
- 使用 Connections CLI 视图检查实时连接/会话元数据。
- 检查框架、ORM、迁移、SQL 标记和连接配置的存储库文件。
- 检查 Terraform 或其他基础设施即代码定义的 PlanetScale 角色、备份、备份策略、Postgres 参数和支持的扩展。

需要明确批准的操作：

- 任何创建、更新、删除、启用、禁用、重置、部署、恢复、提升、强制或应用操作。
- 任何 SQL 变更操作。
- 任何除非操作员明确要求凭证工作的会发出新凭证的命令。

## 接口和文档基础

基于官方文档而不是猜测来验证每个命令和端点。PlanetScale 发布了代理可读的文档：

- 文档索引：https://planetscale.com/docs/llms.txt
- 任何文档页面作为 Markdown：将其 URL 添加 `.md`
- API 参考：https://planetscale.com/docs/openapi.yaml (OpenAPI 3.0)

在调用它之前，在 API 参考中验证端点路径。来自未验证路径的 404 是错误的路径，不是发现；不要将其记录为平台状态，也不要从它得出“未配置”的结论。

已验证接口注释（当命令失败时重新检查文档）：

- `pscale database show <database> --org <org>` — 组织是一个标志，不是位置参数。
- `pscale api <path>` 接受组织相对路径，例如 `organizations/{org}/databases/{db}/branches/{branch}` — 没有 `get` 子命令，也没有 `/v1/` 前缀。使用 `-Q key=value` 标志传递查询参数；在路径中嵌入 `?`/`&` 会在 shell 通配符下中断。
- `pscale webhook list <database> --org <org>` — 数据库是位置参数。`pscale backup list <database> <branch>` 需要分支。
- `pscale branch connections top <database> <branch>` — 实时只读会话清单适用于 Postgres 和 Vitess，通过保留的管理连接。除非操作员明确批准该操作，否则不要取消查询或终止连接。
- 查询洞察是公共 API。实时查询遥测：`.../branches/{branch}/insights`（每个模式的统计数据；支持 `from`/`to`/`period`，`q`，`sort`，`dir`，`tablet_type`，`type`，`fields` 和分页）。同一分支路径下的相关端点：`insights/errors`，`insights/anomalies`，`insights/tags`，`insights/tags/summaries`，`insights/{fingerprint}`（单个执行），`insights/{fingerprint}/summary` 和 `insights/{fingerprint}/traffic/budgets`。`query-patterns` 路径返回生成的报告元数据，而不是实时模式。
- 流量预算：`.../branches/{branch}/traffic/budgets`。CLI 没有 `pscale traffic-control budget list`；使用 API 进行清单。
- Postgres 角色通过 `.../branches/{branch}/roles` 列出；通过 ID 获取单个角色，而不是名称（`pscale role get <db> <branch> <role-id>`）。
- IP 限制：数据库级 `organizations/{org}/databases/{db}/cidrs`。分支级 IP 限制路径无效。
- 模式建议：数据库级 `.../databases/{db}/schema-recommendations`（分支级路径无效）。当前请求 `page=2` 即使响应报告 `next_page` 也会返回 404；使用数据库对象的 `open_schema_recommendations_count` 作为权威总数，将返回的页面视为样本，并在报告中说明项目列表仅涵盖总数的一部分。
- PITR 状态和分支级备份策略没有验证的读取路径；从 `pscale backup list` 和数据库级备份策略记录备份态势，并将 PITR 标记为“本次运行未评估”而不是探测路径。
- 列表端点分页；在报告计数之前耗尽分页参数（上述模式建议的情况除外）。

将访问失败（403、缺失的 token 范围、超时）记录在操作员的内部运行日志中。它们不是发现，也不进入客户报告（参见 `../planetscale-customer-report-template/SKILL.md`）。

## 库存清单

### 数据库身份

记录：

- 组织。
- 数据库。
- 分支。
- 引擎：Vitess 或 Postgres。
- 区域和云提供商。
- 生产/开发分支状态。
- 分支保护和安全工作流状态。
- 大小和集群形状。

### 分支和模式工作流

对于 Vitess，记录：

- 生产分支。
- 生产分支和暂存分支是否启用了安全迁移。
- 打开的部署请求。
- 部署请求批准设置。
- 待处理的模式更改。
- 分支策略是否有一个启用了安全迁移的暂存分支。

对于 Postgres，记录：

- 分支列表。
- 分支是否是从备份或空创建的。
- 模式更改是否由手动管理、通过迁移或通过 ORM 管理。
- 是否使用单独的分支进行迁移测试。
- 团队是否期望 Vitess 风格的部署请求；如果是，请标记 Postgres 分支不以相同的方式使用部署请求。

### 可观察性

记录：

- 洞察的可用性。
- 是否存在查询标签。
- 出现哪些标签。
- 是否存在高基数标签。
- 是否启用完整/原始查询收集。
- 活跃异常。
- 高延迟、高读取行数、高错误率或高执行次数的查询模式。
- 当洞察界面暴露时，Postgres CPU 密集型查询模式和 Vitess vindex-usage 数据。
- 应用部署标识符是否在评论或标签中可见。

### 建议

记录：

- 打开的模式建议。
- 建议类型。
- 影响的表/查询。
- 提议的 DDL 或操作。
- 是否存在分支/部署工作流来安全地评估它。
- 建议是否可以作为应用代码、ORM 迁移或数据库 DDL 实现。

### webhook 和自动化

记录：

- 配置的 webhook。
- 订阅的事件。
- 启用状态。
- 最后一次交付成功或失败。
- 目标类别：Slack、PagerDuty、内部自动化、CI、代理队列、未知。
- 是否记录或实现了 webhook 签名验证。
- webhook 处理是否幂等和异步。

### Postgres 流量控制

仅适用于 Postgres，记录：

- 现有的预算和规则。
- 预算模式：关闭、警告、强制。
- 限制：速率、容量、突发、并发、警告阈值。
- 按指纹、键空间、查询类型或标签的规则。
- 规则是否与有意义的 SQLCommenter 标签相关联。
- 是否有任何生产预算处于强制模式。

### Postgres 安全性

仅适用于 Postgres，记录：

- 应用角色使用情况。
- 应用是否使用默认角色。
- 应用角色是否是最小权限。
- 是否为应用角色启用了 pg_strict。
- 是否为适当的负载使用 PgBouncer。
- 在活动事件期间，实时连接是否显示阻塞、事务中的空闲会话或连接饱和。
- 是否配置了私有连接性和 IP 限制。
- 备份保留和 PITR 是否满足客户的恢复预期。

### Vitess 安全性

仅适用于 Vitess，记录：

- 安全迁移状态。
- 部署请求工作流。
- 管理员批准要求。
- 受门禁保护的部署使用。
- 模式回滚可用性。
- 分支和键空间拓扑。
- 分片/vschema 状态。
- 分片查询模式是否使用相关的 vindex。
- 备份和恢复态势。

## 证据格式

对于每个发现，包括证据：

- 来源：MCP、CLI、API、仪表板观察到、只读 SQL、存储库文件。
- 使用的路径或命令。
- 时间戳。
- 原始值或简洁摘录。
- 置信度：高、中、低。

## 输出

返回：

- 库存表。
- 缺失证据表。
- 风险标志。
- 建议下次运行的技能。

结束：

“未应用任何更改。”
