# ElastiCache

ElastiCache 是一个模块化的工具包，组织为一系列子技能。每个子技能处理 ElastiCache 工作的特定领域。下方的路由器将用户意图匹配到正确的子技能，然后仅加载该子技能所需的引用。

## 该技能的工作原理

1. 将用户的请求与下方注册表中的语义类别进行匹配。基于意义而非精确措辞进行匹配（“帮助我确定使用哪些数据结构”即使没有“模式”这个词也会匹配 `data-modeling`）。
2. **歧义消除**：如果用户的意图匹配多个子技能，按顺序应用以下规则：
   - 如果存在 `.elasticache/requirements.json` 且 `infrastructure.endpoint` 已设置，优先选择 `monitoring` 或 `data-modeling`（用户已有缓存）。
   - 如果不存在缓存（没有 requirements.json 或没有 endpoint），优先选择 `requirements`。
   - 如果仍然模糊，问一个澄清问题：“您是想设置新东西，还是排错现有东西？”
3. 在推荐引擎或部署模型之前，检查 Guardrails 部分。
4. 阅读 `references/{sub-skill-id}/instructions.md` 以获取匹配的子技能。如果相对路径下找不到该文件，请检查您的提示或环境中的技能目录绝对路径，并使用 `{skill-directory}/references/{sub-skill-id}/instructions.md` 重试。
5. 如果请求涉及多个子技能，按管道顺序执行它们。
6. 如果某个子技能需要上游上下文（引擎、部署模型、endpoint）而会话内存中尚未包含，则首先路由到上游子技能。
7. 如果没有子技能匹配，则首先激活 `requirements`。
8. 如果脚本或 CLI 调用失败，向用户显示错误并建议具体的修复方案，然后再重试。

## 子技能注册表

每个条目包含：一个 ID（`references/` 下的目录名）、领域描述、用于匹配的语义类别以及上游/下游依赖关系。

| ID | 名称 | 领域 | 语义类别 | 上游 | 下游 |
|----|------|------|----------|------|------|
| `requirements` | 解决方案匹配 | 通过工作区扫描和结构化访谈收集工作负载、堆栈、规模、延迟、持久性、预算。决定 ElastiCache 是否是合适的服务，并附带路由推荐。 | 我需要缓存、加快我的应用速度、减少数据库负载、降低 Bedrock 成本、我应该使用 ElastiCache 吗、什么最适合我的工作负载、评估缓存选项、ElastiCache 与 X 对比、Valkey 与 X 对比、模糊的新工作负载 | — | `setup`、`data-modeling`、`genai`、`monitoring`、`migration` |
| `setup` | 创建和连接 | 资源分配、连接性、安全性、身份验证、IaC、部署选择。以最低的摩擦度将用户引导至可工作的缓存。涵盖引擎选择、无服务器与基于节点、VPC、TLS、RBAC/IAM、跳主机/SSM 隧道、CLI/SDK/CloudFormation/CDK/Terraform 启动器。 | 创建缓存、设置 ElastiCache、资源分配、Valkey 集群、连接 Lambda/ECS/EKS/EC2、VPC、安全组、TLS、RBAC、IAM 身份验证、跳主机、SSM 隧道、CloudFormation、CDK、Terraform、引擎选择、无服务器与基于节点、备份、快照、恢复、导出 | `requirements`（可选） | `data-modeling`、`genai`、`monitoring` |
| `data-modeling` | 应用模式 | 选择数据结构、键模式、TTL 策略、失效策略和客户端代码，适用于非 AI 模式：缓存旁路、会话存储、速率限制、排行榜、计数器、发布/订阅、流、购物车、作业队列、活动源。 | 会话存储、速率限制、排行榜、缓存旁路、查询缓存、计数器、流、发布/订阅、购物车、作业队列、活动源、键模式、TTL、失效、数据结构 | `setup`（缓存必须存在） | `monitoring` |
| `genai` | AI 和向量工作负载 | 将请求分类为模式 1（普通缓存）、模式 2（语义响应缓存）或模式 3（完整向量搜索）。选择 Valkey 并在需要服务器端向量相似性时强制使用基于节点的 Valkey 8.2 或更高版本（推荐 9.0）。涵盖语义缓存、代理内存、RAG 检索、推荐、个性化、AI 代理的会话/持久化以及框架连接（Strands、mem0、LangChain）。 | 语义缓存、RAG、代理内存、会话内存、向量搜索、嵌入、推荐、个性化、Bedrock 延迟、Bedrock 成本、LLM 缓存、Strands、mem0、LangChain、会话历史、AI 会话存储、嵌入提供者、框架集成 | `setup`（缓存必须存在） | `monitoring` |
| `monitoring` | 运行和观察 | 使用指标首先诊断性能、成本和可靠性，然后推荐最小的变更。涵盖仪表板、警报、日志交付、成本报告、事件路由、故障排除高 CPU / 内存 / 复制延迟 / 连接峰值 / 低命中率 / 热键 / 大键 / 插槽不平衡 / 延迟峰值根本原因。 | 缓存速度慢、成本过高、命中率低、高 CPU、内存压力、复制延迟、连接峰值、仪表板、警报、CloudWatch、成本比较、故障排除、热键、不均匀的碎片负载、单个节点固定、大键、内存膨胀、哪个键最大、键空间分布、前缀分析、按租户的成本归因、内存不平衡、单个碎片已满、插槽内存偏差、延迟峰值、慢命令事件、延迟增加的根本原因 | — | `setup`、`migration` |
| `migration` | 引擎和平台迁移 | 选择迁移路径和预迁移、验证、切换和回滚的顺序。涵盖自管理 Redis → ElastiCache、Redis OSS → Valkey、基于节点 ↔ 无服务器、版本升级。实施严格的迁移前验证门禁。 | 迁移、Redis OSS 到 Valkey、自管理到 ElastiCache、基于节点到无服务器、无服务器到基于节点、引擎升级、版本升级、零停机切换、回滚 | — | `setup`、`monitoring` |

## 管道顺序

子技能独立运行，但常见的多步骤流程遵循以下管道：

- `requirements` → `setup` → (`data-modeling` | `genai`) → `monitoring`
- `migration` → `setup` → `monitoring`
- `monitoring` → `setup` | `migration`（如果指标指示）

## 状态传递：requirements.json

`.elasticache/requirements.json` 是跨子技能状态的单源真理。每个子技能在启动时读取它，并在完成工作后写入其部分。写入前读取；合并，不要覆盖。

| 部分 | 所有者 | 关键字段 |
|------|--------|----------|
| 顶层 | `requirements` | `engine`、`deployment_model`、`region`、`runtime`、`patterns`、`use_case`、`vpc_id`、`subnet_ids`、`security_group_ids` |
| `infrastructure` | `setup` | `cache_name`、`resource_id`、`engine_version`、`topology`、`endpoint`、`port`、`auth_model`、`tls`、`client_library`、`execution_path`、`access_mode`、`tunnel_instance_id`、`embedding_provider`、`embedding_model`、`embedding_dim`、`embedding_module` |
| `genai` | `genai` | `mode`、`mode_2_path`、`framework` |
| `migration` | `migration` | `source_type`、`source_host`、`migration_path`、`cutover_status` |

> **所有权说明**：`deployment_model` 由 `requirements` 在初始访谈期间设置。`migration` 可能会在引擎或部署模型切换后更新它（例如，基于节点到无服务器）。

requirements.json 应在顶层包含 `"schema_version": 1` 和 `"last_updated": "<ISO timestamp>"`。每个写入 requirements.json 的子技能都必须更新 `last_updated`。如果 `last_updated` 超过 7 天，请警告用户缓存状态可能已过时。

requirements.json 跟踪一个活动缓存。如果用户在同一项目中处理多个缓存，请在读取或写入状态之前确认哪个缓存是活动的。

当子技能需要上游上下文（引擎、endpoint、auth_model）时，首先检查 requirements.json。如果字段为 `null` 或文件不存在，则路由到上游子技能。

## 全局规则（适用于每个子技能）

1. **执行路径**。将 AWS CLI、SDK（boto3）、CloudFormation 或 CDK 作为控制平面工作的主要路径。将 valkey-py 作为数据平面工作的主要路径。

2. **响应深度**。对于“我应该”或“哪个”问题，提供摘要（2-3 句话）。默认情况下提供标准（建议 + 配置 + 代码 + 下一步操作）。对于“为什么”或“比较所有”问题，提供专家（完整的决策矩阵，包括替代方案、成本、安全注意事项）。根据用户请求进行升级；切勿未经提示降级。

3. **会话内存**。跟踪区域、VPC、引擎、部署模型、auth_model、计算运行时和语言。跨子技能传递。不要重新询问。如果用户覆盖了某个值，请更新所有位置。从工作区扫描或 IaC 推断的值必须在做出高风险决策（引擎、部署模型、安全态势）之前重新确认；低风险推断（语言、框架、区域）可以作为默认值静默使用。

4. **来源优先级**。始终首先从技能本地文件回答（子技能引用，然后是 `scripts/`）。除非本地文件无法回答查询，否则不要获取外部文档或网络搜索。当本地文件不足时，回退到官方 AWS 文档：https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/（用于功能）和 https://aws.amazon.com/elasticache/pricing/（用于定价）。切勿编造价格点或版本约束。如果用户引用了 Valkey 或 Redis 版本、功能或定价层，而本地文件未涵盖，则回退到 https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ 再回答。不要根据可能过时的本地内容进行推断。

5. **新鲜度免责声明**。在输出定价、版本约束或功能可用性时，包含一行免责声明：“当前定价请参阅 https://aws.amazon.com/elasticache/pricing/。当前功能可用性请参阅 https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/。”

6. **连接安全**。切勿在模块级别（文件顶部、导入时）创建 Valkey/Redis 客户端。在函数内或首次使用时初始化连接。模块级连接会导致在导入模块之前无法访问缓存的应用程序崩溃。

7. **代码环境**。在所有命令和 shebang 中使用 `python3`（而不是 `python`）。不要在应用程序代码中生成 `pip install` 或 `pytest` 命令。优先使用代理的文件写入工具而不是 shell 重定向来写入文件。

8. **输入验证（仅限写操作）**。在运行任何使用用户提供值（缓存名称、区域、子网 ID、安全组 ID、VPC ID、KMS 密钥、快照名称）的创建、修改或删除 CLI 命令或 SDK 调用时，使用 `scripts/input_validator.py` 进行验证。运行 `python3 scripts/input_validator.py cache_name=<val> region=<val> ...` 或将 `validate_all` 作为库导入。对于只读操作（描述、列出），不良输入无害，可以跳过验证。

9. **资源标记（始终在资源创建时应用）**。在创建任何缓存（`create-serverless-cache`、`create-replication-group`、`create-cache-cluster`）时，始终包含以下标签：

   `--tags Key=managed_by,Value=aws-skills Key=skill,Value=elasticache Key=skill_version,Value=1.0.0 Key=created_by,Value=elasticache-skill Key=generation_model,Value={your-model-id}`

   示例：`--tags Key=managed_by,Value=aws-skills Key=skill,Value=elasticache Key=skill_version,Value=1.0.0 Key=created_by,Value=elasticache-skill Key=generation_model,Value=claude-sonnet-4-20250514`

   将 `generation_model` 设置为您自己的模型标识符。即使用户没有提到标记，也要包含这些标签。如果用户提供了其他标签，请将这些标签附加到他们的标签，而不是替换它们。

## 引用加载

仅在当前回合的答案需要时加载额外的引用。

按需指针（非预加载；在触发适用时获取）：

- `references/shared-ux/production-readiness.md` — 当用户询问他们的缓存是否准备好用于生产，或设置完成后用户想进入生产时
- `references/shared-ux/action-safety.md` — 在任何破坏性操作之前（风险级别、永不自动执行列表）
- `references/shared-ux/error-remediation.md` — 当用户遇到特定的 ElastiCache 错误代码（MOVED、CROSSSLOT、CLUSTERDOWN、MULTI/EXEC+IAM 等）
- `references/shared-foundation/boundary-doc.md` — 当用户询问此技能涵盖的内容
- `references/shared-foundation/attribution.md` — 在生成 CLI 命令、SDK 代码或 IaC 模板时
- `references/shared-foundation/architecture-diagrams.md` — 当用户请求架构图或视觉参考时
- `references/shared-runtime/lambda.md` — 当从 Lambda 连接时（冷启动注意事项、IAM 身份验证代码、懒加载）
- `references/shared-runtime/ecs.md` — 当从 ECS 连接时（SIGTERM 关闭、连接池耗尽、任务定义）
- `references/shared-runtime/eks.md` — 当从 EKS 连接时（IRSA、服务网格绕过、SecurityGroupPolicy CRD）
- `references/shared-runtime/api-gateway.md` — 当与 API Gateway 集成时（没有直接路径、缓存层比较）
- `references/shared-runtime/rds-acceleration.md` — 当缓存 RDS/Aurora 查询时（雷声效应、冲击保护、失效）
- `references/shared-runtime/secret-injection.md` — 当用户询问每个计算平台的凭证管理时
- `references/shared-security/encryption-defaults.md` — 当向现有未加密集群添加加密时（TLS 两步迁移、静态加密）
- `references/shared-security/config-guardrails.md` — 当用户希望持续合规监控时（AWS Config 规则、自定义 Lambda 规则）
- `references/shared-security/vpc-patterns.md` — 当调试端口/安全组问题时（端口 6380 无服务器读取器、反模式）

> **文件夹约定**：`references/` 包含 10 个文件夹。6 个与子技能匹配（`requirements`、`setup`、`data-modeling`、`genai`、`monitoring`、`migration`）并作为路由目的地。4 个 `shared-*` 文件夹（`shared-foundation`、`shared-ux`、`shared-security`、`shared-runtime`）是跨领域材料，按需加载，不是路由目的地。

## Guardrails

| 优先级 | 规则 |
|--------|------|
| CRITICAL | **向量搜索必须使用基于节点的 Valkey 8.2 或更高版本。** 无服务器不支持向量搜索。切勿为向量搜索建议无服务器。无论哪个子技能激活，都必须应用此规则。 |
| CRITICAL | **不要编造价格点或版本约束。** 精确情况下使用 `scripts/price_calculator.py` 和当前 AWS 文档。 |
| HIGH | **不要**在用户需要持久性、复制、RBAC 或 IAM 身份验证、有序集合、流、发布/订阅或向量搜索时推荐 Memcached。 |
| HIGH | **不要**假设本地笔记本电脑访问直接工作。ElastiCache 以 VPC 为中心；在需要时解释 VPC、隧道或跳主机访问。 |
| STANDARD | **不要**在每次提及通用 Redis 时触发。当用户显然在询问 AWS、托管缓存、迁移、连接性、定价、操作或 AWS 服务集成时才触发。 |
| STANDARD | 对于 AWS 上下文中的模糊“缓存”请求，激活此技能并从 `requirements` 开始。 |

## 产品真相

- ElastiCache 无服务器部署在分钟内完成，并移除了基础设施管理。
- Valkey 无服务器定价比其他支持的引擎低 33%；基于节点的 Valkey 定价低 20%。
- 无服务器缓存始终启用传输中加密（无法禁用）。
- IAM 身份验证适用于所有 ElastiCache Valkey 版本（7.2 是 ElastiCache 上的基础 Valkey 版本）和 Redis OSS 7.0+。
- Valkey 版本阶梯：7.2（基础）、8.0（每个节点 20% 更多数据（容量改进）、每插槽指标）、8.1（布隆过滤器、COMMANDLOG、SET IFEQ、通过新哈希表减少 20% 内存（效率改进））、8.2（向量搜索）、9.0（推荐新集群的默认值）。除非特定功能另有指示，否则建议新集群使用 Valkey 9.0。
- 向量搜索适用于 8.2 或更高版本的基于节点的集群（推荐 9.0）。
- 全球数据存储仅适用于基于节点的集群。它不支持 IPv6 或本地区域。全球数据存储支持 AUTH 和 RBAC。跨区域故障转移必须手动提升（跨区域自动故障转移不可用）。所有集群都必须在全局数据存储中启用静态加密，但每个集群可以每个区域使用不同的 KMS 密钥。
- 从自管理 Redis 到 ElastiCache 的在线迁移需要：（源）AUTH 必须未启用、`protected-mode` 设置为 `no`、复制和管理命令不得重命名（例如，`sync`、`psync`、`info`、`config`、`command`、`cluster`）；（目标）传输中加密禁用、Multi-AZ 启用、引擎版本 Redis OSS 5.0.6+ 或 Valkey 7.2+、不属于全局数据存储、数据分层禁用。源和目标之间的碎片数量必须匹配。所有源 Redis 实例必须使用相同的端口。不支持无服务器缓存的在线迁移（仅基于节点目标）。有关完整清单，请参阅 `references/migration/topology-validation.md`。
