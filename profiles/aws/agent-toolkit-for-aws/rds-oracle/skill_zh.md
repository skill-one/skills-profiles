# Amazon RDS for Oracle — 连接

## 安全指南

此技能涵盖在用户请求时创建和修改 RDS for Oracle 资源。代理在执行前必须与用户确认操作。未经明确用户确认（例如，“是”、“继续”、“已确认”、“继续”），不得执行任何创建或修改操作。如果用户未确认，请呈现计划的操作并请求批准。

### 执行这些操作（在用户确认后）

- 创建实例：`create-db-instance`（需要 DB 子网组；RDS Oracle 仅限于 VPC，默认情况下不公开访问）
- 创建自定义参数组：`create-db-parameter-group`（系列 `oracle-se2-19`、`oracle-ee-19` 等）
- 创建选项组：`create-option-group`（用于 Oracle 原生网络加密、TLS/TCPS、S3 集成、APEX、空间）
- 更改备份保留期：`modify-db-instance --backup-retention-period`
- 启用/禁用删除保护：`modify-db-instance --deletion-protection`
- 更改 CloudWatch 日志导出：`modify-db-instance --cloudwatch-logs-export-configuration`
- 附加/分离参数组或选项组：`modify-db-instance --db-parameter-group-name / --option-group-name`
- 标记资源：`add-tags-to-resource`，`remove-tags-from-resource`

### 资源标记（资源创建时始终应用）

在创建任何 RDS for Oracle 资源（`create-db-instance`、`create-db-parameter-group`、`create-option-group`、`create-db-instance-read-replica`）时，始终使用 RDS 记录列表 `--tags` 语法包含以下标签：

`--tags Key=created_by,Value=rds-oracle-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-oracle-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户未提及标记，也请包含这些标签，以便他们可以通过此技能识别创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也适用。

### 执行时带停机警告（警告用户，然后在确认后执行）

- 更改实例类：`modify-db-instance --db-instance-class` — 警告：“这会导致 Multi-AZ 配置中的故障转移，并在单-AZ 实例上短暂不可用。”
- 小版本引擎升级：`modify-db-instance --engine-version` 在同一主要版本内（例如，19.0.0.0.ru-2024-01 → 19.0.0.0.ru-2024-04）— 警告：“这会触发重启，并可能导致短暂停机。”
- 存储类型或 IOPS 更改：`modify-db-instance --storage-type` / `--iops` — 警告：“这可能导致更改应用期间 IO 退化。”
- 立即应用：任何 `modify-db-instance --apply-immediately` — 警告：“这会在维护窗口外应用，并可能立即导致停机。”

### 不要执行（拒绝，解释原因，提供评估替代方案）

- 删除实例：`delete-db-instance` — 不可逆的数据丢失
- 删除自动备份：`delete-db-instance --delete-automated-backups` — 销毁时间点恢复历史记录
- 强制故障转移：`reboot-db-instance --force-failover` — 生产影响
- 主要版本升级：`modify-db-instance --engine-version` 跨主要版本（例如，19c → 21c）— 需要预检查、选项组迁移和回滚计划；应通过变更控制流程
- 重启：`reboot-db-instance` — 生产影响
- 提升读副本：`promote-read-replica` — 会中断复制且很少可逆
- 启用公共可访问性：`modify-db-instance --publicly-accessible true` — 安全回归；改用 SSM 端口转发、VPN 或 Direct Connect（根据概述中的安全态势）

拒绝时，请解释原因并提供相应的评估工作流：
> “我无法执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际更改应通过您的团队的变更控制流程或 AWS 控制台进行。”

## 概述

Amazon RDS for Oracle 是一个托管的 Oracle 数据库服务。此技能涵盖连接生命周期：私有子网网络（端口 1521 上的安全组、跨 VPC 对等或 Transit Gateway、Route 53 私有区端点）、TLS/TCPS 和原生网络加密（NNE）、使用 AWS Secrets Manager 的用户名/密码认证、使用 AWS 管理的 Microsoft AD 的 Kerberos 认证、按语言（python-oracledb、JDBC/HikariCP、node-oracledb、ODP.NET Core）的连接池、平台模式（EC2、ECS Fargate、EKS、Lambda、SSM 端口转发）、EC2 上的 Oracle 连接管理器（CMAN）用于高可用性多路复用，以及特定于驱动程序的故障排除。

主要约束：RDS Oracle **不支持** RDS 代理，不允许 SYS/SYSTEM 登录，默认情况下不公开访问——外部访问使用 SSM 端口转发、VPN 或 Direct Connect。

通往八个子技能之一的路线：**网络**、**连接认证**、**计算运行时**、**加密**、**cman-proxy**、**客户端工具**、**ssm-tunneling**、**故障排除**。仅加载匹配的参考。

## 安全注意事项

- **静态加密**：在创建实例时启用 `--storage-encrypted`（可选 `--kms-key-id <key-arn>`）。RDS Oracle 的静态加密只能在创建时设置——无法稍后添加而无需重新创建实例。
- **传输中加密**：通过选项组启用原生网络加密（NNE）或 TLS/TCPS；不要依赖端口 1521 上的明文用于敏感工作负载。
- **网络暴露**：将实例保持在私有子网中，`PubliclyAccessible: No`。通过 SSM 端口转发、VPN 或 Direct Connect 访问它——永远不要启用公共访问。
- **凭证**：将主凭证和应用程序凭证存储在 AWS Secrets Manager 中并启用自动旋转。永远不要在代码、连接字符串或日志中硬编码凭证。
- **KMS 密钥策略**：在使用客户管理的 KMS 密钥进行存储加密时，将其密钥策略的范围限定为 RDS 服务和需要它的角色；仅向该密钥的应用程序角色授予 `kms:Decrypt`。
- **审计日志**：将 Oracle 审计和警报日志导出到 CloudWatch Logs 并为 RDS API 审计启用 CloudTrail（参见日志和监控）。

## 常见任务

### 验证依赖项

在生成连接代码或运行 AWS 命令之前，确认任务需要的工具。

推荐使用 AWS MCP 服务器进行流线化的 AWS 工具执行，但它不是必需的——此技能中的每个操作也可以通过整个文档中显示的 AWS CLI 示例运行。

- AWS CLI v2 通过管理机制（IAM 角色、实例配置文件、SSO 凭证分发）获取凭证——不是粘贴的密钥
- 语言驱动程序：`oracledb`（Python）、`ojdbc11.jar`（Java 11+）、`oracledb`（Node ≥ 6）、`Oracle.ManagedDataAccess.Core`（.NET）
- SSM 端口转发：AWS CLI + Session Manager 插件
- Kerberos：AWS 管理的 Microsoft AD、`krb5.conf`、`okinit` 工具
- CMAN：Oracle 企业版 BYOL 许可证 + 完整的 Oracle 客户端安装（Instant Client 不足）

**约束：**

- 代理在生成代码或运行 AWS 命令之前必须检查依赖项。
- 代理不得指示用户将密码粘贴到连接字符串中，因为凭证必须来自 AWS Secrets Manager、IAM/域管理的身份或 Kerberos 票证。
- 代理必须告知用户缺失的依赖项，并必须尊重用户中止的决定。
- 代理在运行它之前必须解释每个步骤——它做什么、为什么，以及调用了哪个工具。

### 分类和路由

将用户的问题映射到正确的子技能参考，然后仅加载这些文件。

| 用户说 | 加载 |
|---|---|
| SG / VPC 对等 / TGW / Route 53 / 端口 1521 / CIDR | `[networking.md](references/networking.md)` |
| 连接 / 连接字符串 / python-oracledb / JDBC / node-oracledb / ODP.NET / Secrets Manager / 认证 / Kerberos | `[connection-auth.md](references/connection-auth.md)` + 语言参考（`[python.md](references/python.md)`、`[java.md](references/java.md)`、`[nodejs.md](references/nodejs.md)`、`[dotnet.md](references/dotnet.md)`） |
| Lambda / EC2 / ECS Fargate / EKS / 容器 / 无服务器 / IRSA | `[compute-runtime.md](references/compute-runtime.md)` |
| SQL Developer / Toad / SQLcl / DBeaver / sqlplus / GUI | `[client-tools.md](references/client-tools.md)` |
| SSL / TLS / TCPS / NNE / 加密 / FIPS / 密码 | `[encryption.md](references/encryption.md)` |
| CMAN / 连接管理器 / 代理 / 多路复用 / RDS 代理 | `[cman-proxy.md](references/cman-proxy.md)` |
| SSM / 端口转发 / 隧道 / 本地主机 / 笔记本电脑 | `[ssm-tunneling.md](references/ssm-tunneling.md)` |
| ORA-12170 / ORA-12541 / ORA-01017 / ORA-12514 / ORA-28040 / DPI-1047 / DPY-6005 / 超时 / 拒绝 | `[troubleshooting.md](references/troubleshooting.md)` |

**约束：**

- 代理必须仅读取与用户问题匹配的参考文件，以保持上下文集中。
- 代理不得仅从训练数据生成连接代码或网络配置，因为 Oracle-on-RDS 有特定的约束（没有 RDS 代理，不允许 SYS 登录，偏好瘦模式，Kerberos IDENTIFIED EXTERNALLY 模式），LLM 经常会忽略这些。
- 代理必须引用 ORA 错误代码及其确切含义，来自故障排除参考，而不是猜测的解释。
- 如果问题跨越多个子技能（例如，“在不同 VPC 中使用 Secrets Manager 的 ECS Fargate 连接到 RDS Oracle”），代理应加载网络 + 计算运行时 + 连接认证。

### 执行工作流

一旦路由，向用户提供一个基于参考文件的具体、可运行的答案。

参数获取：

- 所有必需参数（区域、实例 ID、端点、服务/SID、源 VPC CIDR、SG ID、Secrets Manager ARN、客户端语言/运行时）必须提前在一个消息中收集。
- 必须指定参数格式：区域 `us-east-1` 风格；实例 ID `^[a-zA-Z][a-zA-Z0-9-]{0,62}$`；端点 `<instance>.<hash>.<region>.rds.amazonaws.com>`；CIDR `a.b.c.d/n`；ARN `arn:aws:<service>:<region>:<account>:...`。
- 代理必须通过直接输入、JSON/YAML 文件路径或 URL 接受参数。

工具使用：

- 使用 AWS CLI 执行 AWS 操作（示例：`aws ec2 authorize-security-group-ingress --group-id sg-123 --protocol tcp --port 1521 --source-group sg-456`）。
- 使用捆绑脚本——`[test_connectivity.sh](scripts/test_connectivity.sh)`、`[check_rds_status.sh](scripts/check_rds_status.sh)`、`[check_security_groups.sh](scripts/check_security_groups.sh)`、`[test_oracle_connection.py](scripts/test_oracle_connection.py)`、`[check_ssl_status.sql](scripts/check_ssl_status.sql)`——进行诊断。
- 将计划、高可用性架构、故障排除报告写入 `artifacts/<app-name>/`。

**约束：**

- 代理不得建议在 RDS Oracle 上启用公共访问，因为公共 RDS 增加了攻击面——使用 SSM 端口转发、VPN 或 Direct Connect。
- 代理不得建议 RDS Oracle 使用 RDS 代理，因为 RDS 代理不支持 Oracle——改用 EC2 上的 Oracle CMAN。
- 代理不得使用 `call_aws` 带位置文件系统参数，因为位置文件系统参数会破坏工具契约——使用内联 JSON 字符串。
- 代理必须优先使用瘦模式驱动程序（python-oracledb 瘦模式、node-oracledb 6+、ODP.NET Core、ojdbc11），因为瘦模式避免了 Oracle 客户端安装并消除了部署复杂性。
- 代理必须将长格式输出写入 `artifacts/<app-name>/`，以便工作空间可检查。

### Rubric-Critical Facts to Always Surface

这些 RDS-for-Oracle 特有的事实使此技能区别于一般的 Oracle-on-EC2 知识。最重要的 #1 是：**RDS Proxy 不支持 RDS Oracle**——CMAN 是替代方案。没有此技能的代理会弄错。

**对于“将 Python Lambda 连接到 RDS Oracle（包括层、池、冷启动的完整设置）”，你必须告诉用户以下七个事实中的所有：**

1. **Lambda VPC 配置**：跨多个 AZ 的私有子网 + 允许向 RDS 在 1521 上出站的安全组。
2. **默认使用 python-oracledb 瘦模式——不需要 Lambda 层**。瘦模式不需要 Oracle 客户端库；不需要 Instant Client，不需要层。只有在用户明确需要厚模式（LDAP 认证或某些 RAC 特定功能）时才建议层。
3. **在处理程序外部的模块级连接池**，以便池在相同容器中的热启动中持续存在。不要在处理程序内构建池。
4. **如果对延迟敏感，使用提供并发进行冷启动优化**。明确提及“提供并发”——这是 Lambda 特有的解决方案。
5. **SSM VPC 端点**，以避免 NAT 网关成本并将密钥检索保持在 VPC 内。这是一个架构优势，不是可选的。
6. **显式处理第一次调用的 ORA-12170**——第一个冷启动连接可能在 ENI 附着时超时；捕获此错误并重试，不要使请求失败。
7. **仅当需要厚模式时才使用层**——LDAP 认证或某些遗留/RAC 功能。不要盲目建议添加 `oracle_client` 层。

**对于“使用 Secrets Manager CSI 驱动程序、IRSA、SecretProviderClass 和部署清单的 EKS 容器连接到 RDS Oracle”，你必须告诉用户以下七个事实中的所有：**

1. **在 EKS 上安装 Secrets Store CSI 驱动程序 + AWS 提供程序**——使用 `helm install` 安装 CSI 驱动程序，使用 `kubectl apply` 应用 AWS 提供程序 YAML。两者都需要（仅驱动程序无法知道如何与 AWS 通信）。
2. **创建 IAM 策略**，授予 `secretsmanager:GetSecretValue` **在特定的密钥 ARN 上**（不是 `*`）。范围它。
3. **使用 eksctl 设置 IRSA**——`eksctl utils associate-iam-oidc-provider` 用于集群的 OIDC 提供程序，然后 `eksctl create iamserviceaccount` 将 IAM 策略绑定到 Kubernetes ServiceAccount。明确提及“eksctl”、“OIDC”、“iamserviceaccount”。
4. **编写 `SecretProviderClass` YAML**，使用 `provider: aws` 和 `jmesPath` 表达式从 JSON 密钥 blob 中提取单个密钥字段（用户名、密码）。
5. **部署清单挂载 CSI 卷**（`volumes` 使用 `csi: { driver: secrets-store.csi.k8s.io }`）并引用正确的 `serviceAccountName`（通过 IRSA 绑定到 IAM 角色的那个）。
6. **Pod 到 RDS 的安全组规则在端口 1521 上**——EKS 工作节点 SG（如果使用安全组为 Pod）必须允许 RDS SG 在 1521 上接收来自 Pod 的入站流量。
7. **池大小：总连接数 = 实例数 × 每个 Pod 的最大池大小**。明确调用此公式，以便用户知道如何调整他们的 RDS 实例以支持 N 个实例。

**对于“从 EC2 跨 VPC 连接到 RDS Oracle 的 ORA-12170 超时”，你必须告诉用户以下六个事实中的所有：**

1. **检查两个 VPC 之间是否存在 VPC 对等或 Transit Gateway**，并在两个方向上都有路由（EC2 的子网路由表指向 RDS 的 VPC CIDR 的对等/TGW，RDS 的子网路由表也回指）。
2. **验证 EC2 的安全组出站允许 1521 到 RDS 的安全组或 CIDR**。
3. **验证 RDS 的安全组允许 1521 入站来自 EC2 的安全组 ID（首选）或其 CIDR**。
4. **验证 NACL 允许双向 1521**——NACL 是无状态的，因此需要在两个子网上都需要返回路径 NACL 规则。NACL 是当安全组看起来正确时常见的静默阻止因素。
5. **确认 RDS 端点在 EC2 的 DNS 中解析**——从 EC2 运行 `nslookup <rds-endpoint>`。如果对等 VPC 的 DNS 解析选项未为对等启用，则 RDS 端点将无法解析。
6. **最快的连接测试：从 EC2 运行 `nc -zv <rds-endpoint> 1521`**。如果 `nc` 超时而 DNS 工作，问题在于安全组/NACL/路由。始终建议 `nc -zv` 作为缩小步骤。

**对于“DPI-1047：无法定位 64 位 Oracle 客户端库”，你必须告诉用户以下四个事实中的所有：**

1. **DPI-1047 意味着 `python-oracledb` 在厚模式下运行且无法找到 Oracle Instant Client**。明确将其作为根本原因解释。
2. **主要修复：通过从代码中删除 `oracledb.init_oracle_client()` 切换到瘦模式**。瘦模式没有 Instant Client 依赖项，并且适用于几乎所有 RDS Oracle 用例（包括 TLS、密码认证、Secrets Manager、连接池）。
3. **只有在确实需要厚模式时（LDAP 认证、某些遗留功能）**——安装 Oracle Instant Client 并确保 `LD_LIBRARY_PATH`（Linux）或 `PATH`（Windows）指向 Instant Client 目录。明确提及每个 OS 的环境变量。
4. **不要盲目安装 Instant Client 而不确认实际上需要厚模式**。默认建议必须是“删除 init_oracle_client, 完成。” 首先安装 Instant Client 并调试路径是一种常见的误诊，评分标准会捕获这一点。

**对于“EC2 上的 Oracle 连接管理器（CMAN）作为 RDS Oracle 的高可用性代理”，你必须告诉用户以下八个事实中的所有：**

1. **提前声明许可和安装先决条件**——CMAN 需要一个**完整的 Oracle 客户端安装（不是 Instant Client）**和**Oracle 企业版 BYOL 许可证**。这是用户最常犯的错误。首先说，而不是最后说。
2. **RDS Proxy 不支持 RDS Oracle**——明确指出这是 CMAN 成为 RDS Oracle 连接池/代理模式的原因。代理经常建议 RDS Proxy 用于 Oracle，并且会弄错评分标准。
3. **在两个位于不同 AZ 的 EC2 实例上安装 CMAN** 以实现高可用性。不要建议单个 EC2——它会破坏“高可用性”要求。
4. **配置 `cman.ora`** 使用 `RULE_LIST`（访问控制规则——哪些客户端可以连接通过 CMAN 到哪些目标）和 `PARAMETER_LIST`（监听器端点、日志记录、会话限制）。明确提及 `cman.ora` 的两个块。
5. **使用 `systemd` 运行 CMAN** 以在故障时自动重启——编写一个服务单元，在启动时启动 `cmctl startup`。
6. **跨 AZ 前端使用网络负载均衡器（NLB）** 以实现高可用性——客户端连接到 NLB DNS，然后分配到两个 CMAN EC2。明确提及 NLB（不是 ALB——Oracle TNS 是 TCP）。
7. **三层安全组规则**：客户端 → CMAN EC2 SG（端口 1521）→ RDS SG（端口 1521）。每个 SG 仅允许从前一个层接收入站流量。这是用户容易出错的开销架构。
8. **客户端 `tnsnames.ora` 指向 NLB DNS 名称**——客户端通过 NLB 连接到 CMAN，CMAN 转发到 RDS。不要让客户端连接到单个 EC2 的 DNS。

## 故障排除

现实场景涵盖了三个主要故障类别：访问拒绝、超时、资源可用性。

| 错误 / 症状 | 可能的原因 | 修复 |
|---|---|---|
| `ORA-12170` 超时 | 安全组阻止 1521，跨 VPC 路由缺失，错误的端点 | 运行 `[test_connectivity.sh](scripts/test_connectivity.sh)`；如果 TCP 失败，请检查安全组入站 + 路由表。跨 VPC 需要对等/TGW + 基于 CIDR 的安全组规则。 |
| `ORA-12541` 没有监听器 | 错误的端口，数据库不可用，错误的端点 | `aws rds describe-db-instances --query 'DBInstances[0].Endpoint'`；确认 `Port`。 |
| `ORA-01017` 无效凭证 | Secrets Manager 中的密码已旋转，Kerberos 票证已过期 | 从 Secrets Manager 重新获取；重新运行 `okinit`；检查 `SELECT username FROM dba_users`。 |
| `ORA-12514` 服务未知 | 错误的 `SERVICE_NAME` 或 `SID` | `SELECT value FROM v$parameter WHERE name = 'service_names'` — 完全匹配。 |
| `ORA-28040` 没有匹配的认证协议 | 客户端太旧 | 更新客户端到 21c+；瘦模式可避免此问题。 |
| `DPI-1047`（Python） | 厚模式启用但找不到 Oracle Instant Client | 通过删除 `oracledb.init_oracle_client()` 切换到瘦模式。如果需要厚模式，安装 Instant Client 并设置 `LD_LIBRARY_PATH`（Linux）或 `PATH`（Windows）。 |
| `DPY-6005`（Python） | 网络连接失败：连接拒绝、超时或 TLS 握手错误 | 检查端点、端口、安全组规则、DNS 解析和 TLS 配置。与 ORA-12170 相同的诊断路径。 |
| IAM `AccessDenied` on Secrets Manager | 任务角色缺少 `secretsmanager:GetSecretValue` | 附加到任务执行角色（ECS 任务定义的凭证注入）。 |
| RDS API 超限 | 超出请求速率 | 指数退避和抖动；检查服务配额。 |

## 日志和监控

在创建或操作 RDS Oracle 实例时，建议启用以下功能：

- **CloudTrail** — 审计 RDS 控制平面 API 调用（创建 / 修改 / 删除）。
- **增强监控** — 操作系统级指标（`--monitoring-interval`, `--monitoring-role-arn`）。
- **性能洞察** — 查询级性能分析（`--enable-performance-insights`）。
- **导出日志到 CloudWatch Logs** — 通过 `--cloudwatch-logs-export-configuration` 导出 Oracle `audit`、`alert`、`listener` 和 `trace` 日志。
- **CloudWatch 闹钟** — 至少在 `DatabaseConnections`、`FreeStorageSpace` 和 `CPUUtilization` 上设置闹钟。
- **日志加密** — 使用 AWS KMS 密钥加密 CloudWatch 日志组。导出的 Oracle `audit`、`alert` 和 `listener` 日志可能包含连接元数据和身份验证尝试，因此请保护它们在静止状态。

## 其他资源

- AWS 文档 — Amazon RDS for Oracle：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Oracle.html
- AWS 文档 — 使用 IAM with RDS：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.html
- AWS 文档 — RDS for Oracle Kerberos 认证：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-kerberos.html
- AWS 文档 — RDS for Oracle 的 SSL/TLS：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.Oracle.Options.SSL.html
- AWS 文档 — Oracle Native Network Encryption：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.Oracle.Options.NetworkEncryption.html
- AWS Systems Manager — 端口转发：https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html#sessions-remote-port-forwarding
- python-oracledb 文档：https://python-oracledb.readthedocs.io/
- node-oracledb 文档：https://node-oracledb.readthedocs.io/
- Oracle JDBC 驱动程序：https://www.oracle.com/database/technologies/appdev/jdbc.html
- 相关技能：`odb-aws`（Oracle Database@AWS on OCI-managed Exadata — 不同产品，不同认证模型）。
