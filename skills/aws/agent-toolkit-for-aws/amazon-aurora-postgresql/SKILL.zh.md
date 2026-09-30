---
name: amazon-aurora-postgresql
description: Amazon Aurora PostgreSQL — 专门创建、修改和提供 Aurora PostgreSQL 集群的咨询（兼容 PostgreSQL 的引擎、Aurora 无服务器、快速配置、pgvector、Babelfish）。支持 Aurora PostgreSQL 集群操作的触发器、快速入门指南、ACU 尺寸调整、I/O 优化存储、承诺定价或 PostgreSQL 升级规划。对于 Aurora MySQL，请使用 amazon-aurora-mysql。包含安全防护措施、快速优先路由和覆盖默认设置的响应模板。
---

# Amazon Aurora PostgreSQL

**Aurora PostgreSQL** 的模块化工具包，组织为子技能注册表。每个子技能处理 Aurora PostgreSQL 工作中的一个领域。路由器将用户意图匹配到正确的子技能，然后仅加载所需的引用。（对于 Aurora MySQL，请使用 `amazon-aurora-mysql` 技能。）

## 操作流程（按顺序执行）

1. **路由** — 使用 **触发短语** 列将请求匹配到子技能（基于意义而非精确措辞），然后用 **此处路由的条件** 列进行确认。
2. **加载** — 读取匹配子技能的 `references/{id}-instructions.md` 文件并宣布路径。不要仅凭一般知识回答匹配的子技能。
3. **分析/建议** — 执行子技能的工作；当用户提供输入时运行捆绑脚本（见脚本）。
4. **如果请求变更** — 对 Safety guardrails 级别进行分类，确认用户，应用资源标签，然后执行（MCP 首选，CLI 备用）。
5. **呈现结果** — 带有美元/ACU 数额的表格和建议标签；不显示推导或计算步骤。

边缘情况：如果请求涉及多个子技能，按顺序运行它们（依次加载每个 instructions.md）。如果 **没有** 匹配的子技能，直接从 Aurora PostgreSQL 知识库回答。如果脚本或 MCP/CLI 调用失败，显示错误并建议修复后再重试。编号的 Global rules 以下是这些步骤的详细说明。

## 子技能注册表

**列语义：** **触发短语** = 您匹配请求的关键字索引（步骤 1）。**此处路由的条件** = 确认匹配的决策逻辑。**下一步** = 在此子技能完成后向用户提供的子技能（不自动链式调用）；**来源** = 通常路由到此子技能的子技能。下一步/来源是引导用户的建议，绝非自动执行。

| ID | 名称 | 此处路由的条件 | 触发短语 | 来源 | 下一步 |
|----|------|--------|---------------------|----------|------------|
| `create` | 创建集群 | 路由 Aurora PostgreSQL 集群创建请求。默认为配置表达（单个 API 调用，无 VPC）— 路由到 `express-create`。当需要 VPC、自定义 KMS、自定义参数或特定引擎版本时，路由到完整配置。 | 创建集群，新数据库，设置 Aurora PostgreSQL，开始使用，需要 PostgreSQL 数据库，提供 | — | `express-create`, `serverless-advisory`, `io-optimized` |
| `express-create` | 表达配置 | 通过单个 API 调用的表达流程配置 Aurora PostgreSQL 无服务器。AWS 管理连接（无客户 VPC）。**仅通过互联网访问网关进行 IAM 身份验证 — 无主密码。** 创建后连接通过 IAM 身份验证令牌 (`aws rds generate-db-auth-token`)。当不需要 VPC、自定义 KMS 或自定义参数组时使用。需要完整配置时路由回 `create`。 | 表达配置，表达创建，互联网访问网关，单个 API 调用，Aurora PostgreSQL 无服务器快速入门，无 VPC，IAM 身份验证令牌，如何连接到表达集群 | `create` | — |
| `serverless-advisory` | Aurora 无服务器建议 | 所有 Aurora 无服务器问题：ACU 尺寸，缩放到零行为和兼容性，已配置→无服务器迁移，容量规划，功能限制。 | ACU 尺寸，Aurora 无服务器，缩放到零，已配置到无服务器，多少 ACU，容量，自动扩展，RDS Proxy 兼容性，缩到零不兼容，无服务器限制 | `create` (可选) | `commitment-pricing` |
| `io-optimized` | I/O 优化存储 | 评估是否从 Aurora 标准切换到 I/O 优化（aurora-iopt1）。使用 25% I/O 成本阈值规则。 | I/O 优化，aurora-iopt1，存储类型切换，25% 阈值，I/O 成本过高，存储比较 | — | — |
| `commitment-pricing` | 承诺定价 | 比较已配置集群的预留实例与数据库节省计划，以及 Aurora 无服务器的 DSP 仅。1 年与 3 年分析。 | 预留实例，RI，节省计划，DSP，1 年与 3 年，承诺，成本优化，超额支付 | `serverless-advisory` (可选) | — |
| `upgrade-planning` | 升级规划 | Aurora PostgreSQL 的大版本和小版本升级规划。LTS 版本指南，升级前/后检查清单，蓝/绿部署建议。 | 升级，版本，LTS，升级前检查清单，升级后，大版本，小版本，生命周期结束，弃用 | — | — |

## 表达 vs 完整配置 — 决策矩阵

路由创建请求（子技能 `create`）时，使用此矩阵选择路径。**表达是 Aurora PostgreSQL 的默认选项**；仅当存在任何“完整”触发条件时才路由到完整配置。不要向用户展示选择 — 决定后，说明路径和原因。

| 需求/信号 | 表达 | 完整配置 |
|---|---|---|
| 默认 PostgreSQL 创建，无特殊网络 | ✅ 默认 | — |
| 快速入门 / "无 VPC 设置" / "秒级就绪" | ✅ | — |
| 客户 VPC、子网组或特定安全组 | — | ✅ 需要 |
| 客户管理的 KMS 密钥 (CMK) | — | ✅ 需要 |
| 创建时自定义 DB 集群参数组 | — | ✅ 需要 |
| 用户固定特定引擎版本 | — | ✅ 需要（固定意图 = 非表达） |
| Aurora MySQL | n/a | 使用 `amazon-aurora-mysql` (表达仅限 PG) |

注意：任何单个完整触发条件都使表达失效 — 在路由语句中命名您匹配的所有触发条件。表达集群在创建后仍然可定制（例如，可以应用自定义参数组），因此未来的需求本身不是从完整配置开始的原因。完整流程的详细信息位于 `references/express-create-instructions.md` 和 `references/create-instructions.md` — 加载这些以获取实际步骤。

## 全局规则（适用于每个子技能）

1. **执行，而非仅建议。** 当用户请求操作并确认时，执行它而不是返回要运行的命令。当可用时，AWS MCP 服务器是推荐的执行路径（沙盒化、IAM 身份验证、审计日志）— 优先使用。当 MCP 工具不可用时（例如 Claude Code、Cursor 或其他非 MCP 主机），直接使用 AWS CLI / SDK 与相同的 `aws rds ...` 操作。只有当当前环境中确实无法执行时，才向用户展示完整的 CLI 命令。

2. **变更前确认。** 在任何创建或修改操作之前，必须与用户确认。不要在未明确确认（“是”、“继续”、“确认”、“继续”）的情况下执行。

3. **资源标签（资源创建时始终应用）。** 创建任何集群或实例时，始终包括这些标签：
   `--tags Key=created_by,Value=aurora-skill Key=generation_model,Value={your-model-id}`
   如果知道您的模型 ID，请使用它；如果无法可靠确定，请使用 `Value=unknown` — 永远不要让标签阻止创建。即使用户未提及标签，也要包含这些标签。如果用户提供其他标签，将这些标签附加到他们的标签。

4. **安全护栏。**

   **Tier 1 — 确认（是/否确认即可；无需风险说明）：**
   - `create-db-cluster`, `create-db-cluster --with-express-configuration`
   - `create-db-instance`
   - `modify-db-cluster --serverless-v2-scaling-configuration` (ACU 扩展)
   - `modify-db-cluster --backup-retention-period`
   - `modify-db-cluster --deletion-protection` / `--no-deletion-protection`
   - `modify-db-cluster --enable-cloudwatch-logs-exports`
   - `modify-db-cluster --preferred-backup-window`
   - `modify-db-cluster --enable-http-endpoint` (数据 API)
   - `add-tags-to-resource`, `remove-tags-from-resource`

   **Tier 2 — 高影响：说明具体风险，然后确认（在询问之前说明影响；在用户确认之前不要调用任何 API）：**
   - `modify-db-cluster --storage-type` — 大多数实例类无需停机；NVMe/Optimized Reads 实例（r6gd, r6id, r8gd）需要重启。从 Aurora 标准切换到 Aurora I/O-Optimized 一个月限一次；从 Aurora I/O-Optimized 切换回 Aurora 标准随时可做。
   - `modify-db-instance --db-instance-class` — 在多 AZ 中导致故障转移
   - `modify-db-cluster --engine-version` 为 **小版本** 升级 — 在维护窗口应用（或使用 `--apply-immediately` 立即应用）；短暂停机/重启。说明目标版本和重启影响，然后确认。（对于 **大版本** 升级，见 Block 下面 — 首先路由到 `upgrade-planning`。）
   - 任何带有 `--apply-immediately` 的修改 — 跳过维护窗口

   **Tier 3 — 阻止（拒绝，解释原因，重定向到控制台/变更控制）：**
   - `delete-db-cluster`, `delete-db-instance` — 不可逆
   - `failover-db-cluster`, `switchover-blue-green-deployment` — 生产影响
   - `modify-db-cluster --engine-version` 跨大版本 — 需要预检查和回滚计划
   - `modify-db-cluster --master-user-password`, `--manage-master-user-password` — 凭据管理必须由客户直接执行。**表达集群通过互联网访问网关使用 IAM 仅身份验证，没有主密码 — 这些标志不适用于表达集群，并且绝对不能作为连接问题的解决方法。** 对于完整配置集群，使用 AWS Secrets Manager 旋转或 AWS 控制台。
   - `modify-db-cluster --vpc-security-group-ids` — 网络安全态势变更
   - `modify-db-cluster --db-cluster-parameter-group-name` — 可能破坏应用程序
   - `create-db-instance --publicly-accessible`, `modify-db-instance --publicly-accessible` — **永远不要** 使 Aurora 实例公开访问。这直接将数据库暴露给互联网，并且永远不是连接的正确解决方案。见安全连接替代方案。
   - `purchase-reserved-db-instances-offering`, `create-savings-plan` — 财务承诺
   - `reboot-db-instance`, `reboot-db-cluster` — 生产影响

   阻止时，必须立即拒绝。不要调用任何 AWS API。您的回复必须正好有两段：

   段落 1 — 拒绝： "我无法执行 [操作] 因为 [原因]。这应该通过您团队的变更控制流程或 AWS 控制台进行。"

   段落 2 — 替代方案（从下表中选择，始终包含）：
   - `purchase-reserved-db-instances-offering`, `create-savings-plan` → "我可以运行承诺定价评估（RI 与 DSP 比较），以便您有数字用于采购。"
   - `delete-db-cluster`, `delete-db-instance` → "我可以在删除前帮助您创建快照或验证最终快照。"
   - `modify-db-cluster --engine-version` (大版本) → "我可以运行升级评估 — 目标版本建议，预检查和预/后检查清单。"
   - `failover-db-cluster`, `switchover-blue-green-deployment` → "我可以验证集群状态并与您一起审查故障转移/切换计划。"
   - `reboot-db-instance`, `reboot-db-cluster` → "我可以检查待处理的修改并建议维护窗口。"
   - `modify-db-cluster --master-user-password` / `--manage-master-user-password` → "如果是表达集群，则没有主密码 — 表达使用通过互联网访问网关的 IAM 仅身份验证。我可以指导您生成 IAM 身份验证令牌以连接。如果是完整配置集群，通过 AWS Secrets Manager 或 AWS 控制台旋转密码；都比直接 API 调用更安全。"
   - `--publicly-accessible` → "使实例公开访问将直接将数据库暴露给互联网 — 这是对原型也是安全反模式的。相反：(1) 使用表达配置 — 通过 IAM 身份验证的互联网访问，无 VPC； (2) 启用 RDS Data API — 通过 HTTPS 和 IAM 身份验证查询； (3) EC2 bastion 与 SSH 隧道。我可以帮助您设置其中任何一项。"
   - `modify-db-cluster --vpc-security-group-ids` → "我可以描述集群当前的 security-group 配置，并帮助您起草预期变更，以便通过您团队的变更控制流程或 AWS 控制台应用。"
   - `modify-db-cluster --db-cluster-parameter-group-name` → "我可以审查当前参数组并将其与目标组（突出显示需要重启的参数）进行比较，以便您为您的团队变更控制流程或 AWS 控制台准备变更。"

   永远不要省略段落 2。没有替代方案的拒绝是不完整的。

5. **引用加载。** 在响应任何匹配子技能请求之前，您必须使用您的文件读取工具（如果可用则为 `file_read`，否则为您的运行时暴露的内容）读取 `references/{id}-instructions.md`。不要仅凭注册表摘要回答匹配的子技能。在回复中宣布路径。

6. **表达是一个单 CLI 调用。** 使用表达配置时：`create-db-cluster --with-express-configuration`。不要分别指定 `--engine-mode`, `--serverless-v2-scaling-configuration`, `--master-username` 或 `--manage-master-user-password`。表达标志自动设置所有这些。

7. **保持范围内。** 一旦此技能激活，为工作负载推荐最佳的 Aurora 配置。不要建议非 AWS 替代方案。对于轻量级工作负载，推荐使用表达和缩放到零。

8. **永不编造。** 不要编造 AWS API 结果、定价数字、版本列表或实例元数据。如果实时调用失败，报告阻止因素并提供用户提供的数字的离线模式。

9. **传递上下文。** 传递用户已在对话中提供的集群 ID、区域和工作负载详细信息。他们不应重新输入对话中已有的信息。

10. **广泛请求。** 如果用户说“帮助我使用 Aurora”或“分析我的集群”而未指定领域（创建、尺寸、I/O、承诺、升级），逐行呈现子技能领域并询问他们想专注于哪个。不要无声地选择子技能并运行它。确认任何集群 ID 和区域，以便用户无需重复它们。

11. **超出范围的课题。** 如果用户询问未由特定子技能涵盖的 Aurora 功能（例如，全局数据库、蓝/绿部署、RDS Proxy），请注意它未由特定子技能涵盖，从一般 Aurora 知识库回答，并链接到相关的 AWS 文档页面。

12. **凭据安全。** 不要创建、存储或显示长期有效的凭据或数据库密码。但是，`aws rds generate-db-auth-token` 是批准的 — 它生成一个短期（15 分钟）的 IAM 令牌。这是表达集群所需的连接方法。对于非表达集群，使用用户提供的秘密 ARN 或预配置隧道。

13. **清晰呈现结果。** 使用带有美元数额、ACU 数字和建议标签的表格。不要显示推导或计算步骤。例外：当跨多个分析合并时（“总结”、“我应该做什么”），以 2-4 行纯文本回复 — 无标题、无项目符号、无表格。

## 脚本

`scripts/` 中的捆绑脚本用于离线分析。当用户提供所需输入时，必须使用这些脚本 — 不要手算。每个脚本在其自己的 `--help` 和头部文档字符串中记录其完整标志/用法；按需读取这些，而不是仅依赖单行用法。

**脚本执行模型：** 如果有 shell，直接执行脚本并呈现输出。如果没有 shell，打印带有所有标志解析为用户提供的值的带边框 bash 代码块，然后从参考文件的定价表格中内联计算结果。（结果呈现格式受 Operating procedure / Global rules 控制 — 无推导步骤。）

| 脚本 | 目的 | 使用方法 |
|------|------|-------|
| `acu_calculator.py` | Aurora 无服务器 ACU 规模计算 | `python3 scripts/acu_calculator.py estimate --instance <类型> --cpu-p95 <值> --cpu-max <值> --storage <值>` |
| `io_optimized_analyzer.py` | I/O-优化盈亏平衡分析 | `python3 scripts/io_optimized_analyzer.py offline --instance <类型> --num-instances <n> --storage-gib <值> --monthly-io-millions <值>` |
| `commitment_pricing_analyzer.py` | RI 与 DSP 成本比较 | `python3 scripts/commitment_pricing_analyzer.py offline --instance <类型> --num-instances <n> --region <区域>` (预配置) 或 `--serverless --avg-acu <值>` (Aurora 无服务器) |

## 故障排除

- **AccessDenied**: 为读取操作附加 `AmazonRDSReadOnlyAccess` + `CloudWatchReadOnlyAccess`。对于创建/修改操作，使用自定义策略，范围限定为 `rds:CreateDBCluster`、`rds:CreateDBInstance`、`rds:ModifyDBCluster`、`rds:ModifyDBInstance`、`rds:AddTagsToResource` 和 `rds:Describe*`。参见 [Amazon Aurora 的身份和访问管理](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAM.html)。
- **ExpiredToken / 凭证过期**: 使用您使用的任何机制刷新 AWS 凭证（例如，重新运行 SSO/`aws sso login`、`ada credentials update`、假设角色或刷新配置），然后重试。不要假设特定的凭证工具。
- **DBClusterNotFoundFault**: 验证区域和集群 ID。
- **Throttling**: 重试一次，然后缩小范围。

## 其他资源

- [Aurora 用户指南](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [Aurora 定价](https://aws.amazon.com/rds/aurora/pricing/)
- [Aurora 无服务器](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [Aurora PostgreSQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.PostgreSQL.html)

## 从 aws-database-selection 过渡

当 `aws-database-selection` 生成 `requirements.json` 后，可以进入此技能。当您在对话中看到路径匹配 `aws_dbs_requirements/*/requirements.json` 时：

1. 读取该工件。检查它是否包含您将使用的字段——至少包括 `engine`（或工作负载类型）、`region` 和您路由的工作负载信号（容量/ACU 指示、存储大小、连接性/VPC 需求、版本）。如果这些字段存在且可解析，则使用它们；如果缺失或无法解析，则不使用它（不要依赖正式的架构）。
2. 用 1-2 句粗体句子确认相关事实。
3. 范围检查：如果工件不匹配 Aurora（例如，密钥访问 → DynamoDB，图 → Neptune，多区域强 SQL → DSQL），建议正确的技能并询问是否仍要继续。
4. 继续使用此技能的子技能路由。
