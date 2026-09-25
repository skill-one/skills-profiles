# Amazon Aurora MySQL

**Aurora MySQL** 的模块化工具包，组织为子技能注册表。每个子技能处理 Aurora MySQL 工作中的一个领域。路由器将用户意图匹配到正确的子技能，然后仅加载所需的引用。（对于 Aurora PostgreSQL —— 及其快速入门的 express-配置 —— 使用 `amazon-aurora-postgresql` 技能。）

## 操作流程（按顺序执行）

1. **路由** — 使用 **触发短语** 列（基于意义而非精确字词进行匹配）将请求匹配到子技能，然后用 **此处路由的原因** 列进行确认。
2. **加载** — 读取匹配的子技能的 `references/{id}-instructions.md` 文件，并宣布路径。不要仅凭一般知识来回答匹配的子技能。
3. **分析 / 建议** — 执行子技能的工作；当用户提供输入时运行捆绑脚本（见脚本）。
4. **如果请求变更** — 对 Safety guardrails 级别进行分类，与用户确认，应用资源标签，然后执行（MCP 首选，CLI 备用）。
5. **呈现结果** — 带有美元/ACU 数额的表格和建议标签；不要显示推导或计算步骤。

边缘情况：如果请求跨越多个子技能，按顺序运行它们（依次加载每个 instructions.md）。如果 **没有** 子技能匹配，直接从 Aurora MySQL 知识库回答。如果脚本或 MCP/CLI 调用失败，显示错误并建议修复后再重试。编号的 Global rules 以下是这些步骤的细节。

## 子技能注册表

**列语义：** **触发短语** = 您匹配请求的关键字索引（步骤 1）。**此处路由的原因** = 确认匹配的决策逻辑。**下一步** = 在此子技能完成后向用户提供的子技能（不会自动链式调用）；**来源** = 通常路由到此子技能的子技能。下一步/来源是引导用户的建议，永远不会自动执行。

| ID | 名称 | 此处路由的原因 | 触发短语 | 来源 | 下一步 |
|----|------|--------|---------------------|----------|------------|
| `create` | 创建集群 | 路由 Aurora MySQL 集群创建请求。Aurora MySQL 使用完整（基于 VPC）配置 — 收集 VPC/子网组、安全组、KMS、参数组以及引擎版本，提供选项，然后创建。（Express 配置仅适用于 PostgreSQL，不适用于 Aurora MySQL。） | 创建集群、新数据库、设置 Aurora MySQL、开始使用、需要 MySQL 数据库、提供 | — | `serverless-advisory`, `io-optimized` |
| `serverless-advisory` | Aurora serverless 建议 | 所有 Aurora serverless 问题：ACU 尺寸、缩放到零行为和兼容性、按需创建→serverless 迁移、容量规划以及功能限制。 | ACU 尺寸、Aurora serverless、缩放到零、按需创建到 serverless、多少 ACU、容量、自动扩展、RDS Proxy 兼容性、缩到零不兼容、serverless 限制 | `create` (可选) | `commitment-pricing` |
| `io-optimized` | I/O-优化存储 | 评估是否从 Aurora Standard 切换到 I/O-优化（aurora-iopt1）。使用 25% I/O 成本阈值规则。 | I/O-优化、aurora-iopt1、存储类型切换、25% 阈值、I/O 成本过高、存储比较 | — | — |
| `commitment-pricing` | 承诺定价 | 比较按需集群的预留实例与数据库节省计划，以及 Aurora serverless 的 DSP 仅。1 年与 3 年分析。 | 预留实例、RI、节省计划、DSP、1 年与 3 年、承诺、成本优化、超额支付 | `serverless-advisory` (可选) | — |
| `upgrade-planning` | 升级规划 | Aurora MySQL 的大版本和小版本升级规划。LTS 版本指导、升级前/后检查清单、蓝/绿部署建议。 | 升级、版本、LTS、升级前检查清单、升级后、大版本、小版本、生命周期结束、弃用 | — | — |

## 全局规则（适用于每个子技能）

1. **执行，不只是建议。** 当用户请求操作并确认时，执行它而不是返回要运行的命令。当可用时，推荐使用 AWS MCP 服务器执行（沙盒化、IAM 身份验证、审计日志）—— 优先使用它。当 MCP 工具不可用时（例如 Claude Code、Cursor 或其他非 MCP 主机），直接使用 AWS CLI / SDK 与相同的 `aws rds ...` 操作。只有当在当前环境中确实无法执行时，才向用户展示完整的 CLI 命令供其运行。

2. **变更前确认。** 在任何创建或修改操作之前，必须与用户确认。不要在没有明确确认（“是”、“继续”、“确认”、“继续”）的情况下执行。

3. **资源标签（资源创建时始终应用）。** 创建任何集群或实例时，始终包括这些标签：
   `--tags Key=created_by,Value=aurora-skill Key=generation_model,Value={your-model-id}`
   如果知道您的模型 ID，请使用它；如果您无法可靠地确定它，请使用 `Value=unknown` —— 永远不要让标签阻止创建。即使用户没有提到标签，也包含这些标签。如果用户提供了其他标签，将这些标签附加到他们的标签。

4. **Safety guardrails。**

   **Tier 1 — 确认（一个 yes/no 确认就足够了；不需要风险简报）：**
   - `create-db-cluster`（完整/VPC 配置 — Aurora MySQL 不支持 express）
   - `create-db-instance`
   - `modify-db-cluster --serverless-v2-scaling-configuration`（ACU 缩放）
   - `modify-db-cluster --backup-retention-period`
   - `modify-db-cluster --deletion-protection` / `--no-deletion-protection`
   - `modify-db-cluster --enable-cloudwatch-logs-exports`
   - `modify-db-cluster --preferred-backup-window`
   - `modify-db-cluster --enable-http-endpoint`（数据 API）
   - `add-tags-to-resource`, `remove-tags-from-resource`

   **Tier 2 — 高影响：声明具体风险，然后确认（在询问之前说明影响；不要在用户确认之前调用任何 API）：**
   - `modify-db-cluster --storage-type` — 大多数实例类不需要停机；NVMe/Optimized Reads 实例（r6gd, r6id, r8gd）需要重启。从 Aurora Standard 切换到 Aurora I/O-Optimized 最多每月一次；从 Aurora I/O-Optimized 切换回 Aurora Standard 可以随时进行。
   - `modify-db-instance --db-instance-class` — 在多 AZ 中会导致故障转移
   - `modify-db-cluster --engine-version` 对于 **小版本** 升级 — 在维护窗口（或使用 `--apply-immediately` 立即应用）应用；短暂故障转移/重启。声明目标版本和重启影响，然后确认。（对于 **大版本** 升级，见下文 — 首先路由到 `upgrade-planning`。）
     - **如何区分小版本和大版本（Aurora MySQL）：** Aurora MySQL 版本是 `major.minor.patch`（例如 `3.06`，`3.08`）。**major** 数字（`2` = MySQL 5.7 兼容，`3` = MySQL 8.0 兼容，`8.4`+）是主版本；第二个数字是 **小版本**。所以 **3.06 → 3.08 是一个小版本升级**（主版本 `3` 不变）→ 在 Tier 2 中处理。主版本的变化（例如 `2.x → 3.x`，或 5.7 → 8.0 兼容性）是一个 **大版本升级** → 下文。不确定时，将其视为主版本并路由到 `upgrade-planning`。
   - 任何带有 `--apply-immediately` 的修改 — 跳过维护窗口

   **Tier 3 — 拒绝（拒绝，解释原因，重定向到控制台/变更控制）：**
   - `delete-db-cluster`, `delete-db-instance` — 不可逆
   - `failover-db-cluster`, `switchover-blue-green-deployment` — 生产影响
   - `modify-db-cluster --engine-version` 跨主版本 — 需要预检查和回滚计划
   - `modify-db-cluster --master-user-password`, `--manage-master-user-password` — 凭据管理必须由客户直接执行。使用 AWS Secrets Manager 旋转或 AWS 控制台。
   - `modify-db-cluster --vpc-security-group-ids` — 网络安全态势变化
   - `modify-db-cluster --db-cluster-parameter-group-name` — 可能会破坏应用程序
   - `create-db-instance --publicly-accessible`, `modify-db-instance --publicly-accessible` — 永远不要将 Aurora 实例公开访问。这会将数据库直接暴露在互联网上，并且永远不是连接的正确解决方案。见下文的连接替代方案。
   - `purchase-reserved-db-instances-offering`, `create-savings-plan` — 财务承诺
   - `reboot-db-instance`, `reboot-db-cluster` — 生产影响

   拒绝时，必须立即拒绝。不要调用任何 AWS API。您的回复必须正好有两段：

   段落 1 — 拒绝：“我不能执行 [操作]，因为 [原因]。这应该通过您团队的变更控制流程或 AWS 控制台进行。”

   段落 2 — 替代方案（从下表中选择，始终包含）：
   - `purchase-reserved-db-instances-offering`, `create-savings-plan` → “我可以运行承诺定价评估（RI 与 DSP 比较），以便您有采购所需的数字。”
   - `delete-db-cluster`, `delete-db-instance` → “我可以在删除前帮助您创建快照或进行最终快照验证。”
   - `modify-db-cluster --engine-version`（主版本）→ “我可以运行升级评估 — 目标版本建议、预检查和预/后检查清单。”
   - `failover-db-cluster`, `switchover-blue-green-deployment` → “我可以验证集群状态并与您一起审查故障转移/切换计划。”
   - `reboot-db-instance`, `reboot-db-cluster` → “我可以检查待处理的修改并建议维护窗口。”
   - `modify-db-cluster --master-user-password` / `--manage-master-user-password` → “通过 AWS Secrets Manager 或 AWS 控制台旋转密码；都比直接 API 调用更安全。我可以指导您启用 Secrets Manager 管理旋转。”
   - `--publicly-accessible` → “将实例公开访问会将数据库直接暴露在互联网上 — 这对于原型也是一个安全反模式。相反：(1) 启用 RDS Data API — 使用 HTTPS 和 IAM 身份验证进行查询；(2) EC2 bastion 与 SSH 隧道；(3) 从 VPC 内连接（例如同一 VPC 中的工作负载或通过 VPN/Direct Connect）。我可以帮助您设置其中任何一项。”
   - `modify-db-cluster --vpc-security-group-ids` → “我可以描述集群当前的 security-group 配置并帮助您起草预期变更，以便您通过您团队的变更控制流程或 AWS 控制台应用。”
   - `modify-db-cluster --db-cluster-parameter-group-name` → “我可以审查当前参数组并将其与目标组（突出显示需要重启的参数）进行比较，以便您为您的团队变更控制流程或 AWS 控制台准备变更。”

   永远不要省略段落 2。没有替代方案的拒绝是不完整的。

5. **引用加载。** 在响应任何匹配的子技能请求之前，您必须使用您的文件读取工具（如果可用，则使用 `file_read`，否则使用您的运行时暴露的内容）读取 `references/{id}-instructions.md`。不要仅凭注册表摘要回答匹配的子技能。在回复中宣布路径。

6. **保持范围内。** 一旦此技能激活，为工作负载推荐最佳的 Aurora MySQL 配置。不要建议非 AWS 替代方案。对于轻量级或间歇性工作负载，推荐使用 Aurora serverless 并具有缩放到零功能。

7. **永不编造。** 不要编造 AWS API 结果、定价数字、版本列表或实例元数据。如果实时调用失败，请报告阻止因素并提供用户提供的数字的离线模式。

8. **传递上下文。** 传递用户已经提供的集群 ID、区域和工作负载详细信息。他们不应该重新输入对话中已经包含的信息。

9. **广泛请求。** 如果用户说“帮助我处理 Aurora MySQL”或“分析我的集群”而没有指定领域（创建、尺寸、I/O、承诺、升级），请逐行呈现子技能领域并询问他们想专注于哪个。不要默默地选择一个子技能并运行它。确认任何集群 ID 和区域，以便用户不需要重复它们。

10. **超出范围的课题。** 如果用户询问的 Aurora 功能没有子技能涵盖（例如 Global Database、蓝/绿部署、RDS Proxy），请说明它没有由特定子技能涵盖，从一般 Aurora 知识库回答，并链接到相关的 AWS 文档页面。

11. **凭据安全。** 不要创建、存储或显示长期有效的凭据或数据库密码。`aws rds generate-db-auth-token` 在集群上启用 IAM 数据库身份验证时是批准的 — 它生成一个短期（15 分钟）的 IAM 令牌。否则，使用用户提供的秘密 ARN（AWS Secrets Manager）或预配置隧道。

12. **清晰呈现结果。** 使用带有美元数额、ACU 数字和建议标签的表格。不要显示推导或计算步骤。例外：当跨多个分析合并时（“总结”、“我应该做什么”），用 2-4 行纯文本回复 — 没有标题、没有项目符号、没有表格。

## 脚本

`scripts/` 中的捆绑脚本用于离线分析。当用户提供所需输入时，必须使用这些脚本 — 不要手算。每个脚本在其自己的 `--help` 和头部文档字符串中记录其完整标志/用法；按需读取它们，而不是仅依赖一行用法。

**脚本执行模型：** 如果有 shell，直接执行脚本并显示输出。如果没有 shell，打印带有所有标志解析为用户提供的值的带边框 bash 代码块，然后从参考文件的定价表格中内联计算结果。（结果呈现格式受 Operating procedure / Global rules 支配 — 没有推导步骤。）

| 脚本 | 目的 | 用法 |
|--------|---------|-------|
| `acu_calculator.py` | Aurora serverless ACU 尺寸 | `python3 scripts/acu_calculator.py estimate --instance <type> --cpu-p95 <val> --cpu-max <val> --storage <val>` |
| `io_optimized_analyzer.py` | I/O-优化盈亏平衡 | `python3 scripts/io_optimized_analyzer.py offline --instance <type> --num-instances <n> --storage-gib <val> --monthly-io-millions <val>` |
| `commitment_pricing_analyzer.py` | RI 与 DSP 成本比较 | `python3 scripts/commitment_pricing_analyzer.py offline --instance <type> --num-instances <n> --region <region>`（按需创建）或 `--serverless --avg-acu <val>`（Aurora serverless） |

## 故障排除

- **AccessDenied**：附加 `AmazonRDSReadOnlyAccess` + `CloudWatchReadOnlyAccess` 进行读取。对于创建/修改，使用针对 `rds:CreateDBCluster`、`rds:CreateDBInstance`、`rds:ModifyDBCluster`、`rds:ModifyDBInstance`、`rds:AddTagsToResource` 和 `rds:Describe*` 的自定义策略。见 [Amazon Aurora 的身份和访问管理](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAM.html)。
- **ExpiredToken / 凭据**：使用您使用的任何机制刷新 AWS 凭据（例如重新运行 SSO/`aws sso login`、`ada credentials update`、假设角色或刷新配置），然后重试。不要假设特定的凭据工具。
- **DBClusterNotFoundFault**：验证区域和集群 ID。
- **Throttling**：重试一次，然后缩小范围。

## 额外资源

- [Aurora 用户指南](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [Aurora 定价](https://aws.amazon.com/rds/aurora/pricing/)
- [Aurora serverless](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [Aurora MySQL 升级](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Upgrading.html)

## 从 aws-database-selection 过渡

此技能可以在 `aws-database-selection` 生成 `requirements.json` 后进入。当您在对话中看到匹配 `aws_dbs_requirements/*/requirements.json` 的路径时：

1. 读取工件。检查它是否包含您将使用的字段 — 至少 `engine`（或工作负载类型）、`region` 和您路由的工作量信号（容量/ACU 提示、存储大小、连接/VPC 需求、版本）。如果这些字段存在且可解析，请使用它们；如果缺少它们或无法解析，则不使用它（不要依赖正式模式）。
2. 在 1-2 个粗体句子中确认相关事实。
3. 范围检查：如果工件不匹配 Aurora（例如，key-access → DynamoDB，图 → Neptune，多区域强 SQL → DSQL），建议正确的技能并询问是否无论如何继续。
4. 继续使用此技能的子技能路由。
