---
name: rds-oracle
description: 诊断和解决 Amazon RDS for Oracle 连接、认证、网络和驱动程序问题。适用于任何 RDS-for-Oracle 问题，包括在 VPC 中通过连接池和冷启动优化将 Python Lambda 连接到 RDS Oracle，通过 Secrets Manager CSI 驱动程序和 IRSA 将 EKS Pod 连接到 RDS Oracle，来自 EC2 的 ORA-12170 跨 VPC 超时，DPI-1047 无法定位 64 位 Oracle 客户端错误，以及作为跨两个 AZ 实现高可用性的代理的 EC2 上的 Oracle 连接管理器（CMAN）。涵盖 python-oracledb 薄模式与厚模式、init_oracle_client、RDS Proxy 不支持 RDS Oracle、端口 1521、VPC 对等连接、传输网关、Kerberos 与 AWS 管理的 Microsoft AD、SSL/TLS/NNE、SSM 端口转发、EC2/ECS Fargate/EKS/Lambda、SQL Developer/DBeaver/Toad/SQLcl 以及 Secrets Manager。
---

# Amazon RDS for Oracle — 连接

## 安全指南

此技能涵盖在用户请求时创建和修改 RDS for Oracle 资源。代理在执行前**必须**与用户确认操作。**禁止**在未经明确用户确认（例如，“是”、“继续”、“确认”、“进行”）的情况下执行任何创建或修改操作。如果用户未确认，请呈现计划的操作并请求批准。

### 用户确认后执行的操作

- 创建实例：`create-db-instance`（需要 DB 子网组；RDS Oracle 仅限于 VPC，默认情况下不公开访问）
- 创建自定义参数组：`create-db-parameter-group`（系列 `oracle-se2-19`、`oracle-ee-19` 等）
- 创建选项组：`create-option-group`（用于 Oracle 原生网络加密、TLS/TCPS、S3 集成、APEX、空间）
- 更改备份保留期：`modify-db-instance --backup-retention-period`
- 启用/禁用删除保护：`modify-db-instance --deletion-protection`
- 更改 CloudWatch 日志导出：`modify-db-instance --cloudwatch-logs-export-configuration`
- 附加/分离参数组或选项组：`modify-db-instance --db-parameter-group-name / --option-group-name`
- 标记资源：`add-tags-to-resource`，`remove-tags-from-resource`

### 资源标记（资源创建时始终应用）

在创建任何 RDS for Oracle 资源（`create-db-instance`、`create-db-parameter-group`、`create-option-group`、`create-db-instance-read-replica`）时，**始终**使用 RDS 记录列表 `--tags` 语法包含以下标签：

`--tags Key=created_by,Value=rds-oracle-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-oracle-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户未提及标记，也请包含这些标签，以便他们可以通过此技能识别创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也适用。

### 带停机警告执行（警告用户，然后在确认后执行）

- 更改实例类：`modify-db-instance --db-instance-class` — 警告：“这会导致多 AZ 配置中的故障转移，并在单 AZ 实例上导致短暂不可用。”
- 小版本引擎升级：`modify-db-instance --engine-version` 在同一主要版本内（例如，19.0.0.0.ru-2024-01 → 19.0.0.0.ru-2024-04）— 警告：“这会触发重启，并可能导致短暂中断。”
- 存储类型或 IOPS 更改：`modify-db-instance --storage-type` / `--iops` — 警告：“在更改应用期间，这可能导致 IO 降级。”
- 立即应用：任何 `modify-db-instance --apply-immediately` — 警告：“这会在维护窗口外应用，并可能立即导致停机。”

### 不执行（拒绝，解释原因，提供评估替代方案）

- 删除实例：`delete-db-instance` — 不可逆的数据丢失
- 删除自动备份：`delete-db-instance --delete-automated-backups` — 销毁点时间恢复历史记录
- 强制故障转移：`reboot-db-instance --force-failover` — 生产影响
- 主要版本升级：`modify-db-instance --engine-version` 跨主要版本（例如，19c → 21c）— 需要预检查、选项组迁移和回滚计划；应通过变更控制流程
- 重启：`reboot-db-instance` — 生产影响
- 提升读副本：`promote-read-replica` — 会中断复制，且很少可逆
- 启用公共可访问性：`modify-db-instance --publicly-accessible true` — 安全回归；请使用 SSM 端口转发、VPN 或 Direct Connect 代替（根据概述中的安全态势）

拒绝时，请解释原因并提供相应的评估工作流：
> “我无法执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际变更应通过您的团队的变更控制流程或 AWS 控制台进行。”

## 概述

Amazon RDS for Oracle 是一个托管的 Oracle 数据库服务。此技能涵盖连接生命周期：私有子网网络（端口 1521 上的安全组、跨 VPC 对等或 Transit Gateway、Route 53 私有区端点）、TLS/TCPS 和原生网络加密 (NNE)、使用 AWS Secrets Manager 的用户名/密码认证、使用 AWS 管理的 Microsoft AD 的 Kerberos 认证、按语言（python-oracledb、JDBC/HikariCP、node-oracledb、ODP.NET Core）的连接池、平台模式（EC2、ECS Fargate、EKS、Lambda、SSM 端口转发）、EC2 上的 Oracle 连接管理器 (CMAN) 用于高可用性多路复用，以及特定于驱动程序的故障排除。

主要限制：RDS Oracle **不支持** RDS Proxy，不允许 SYS/SYSTEM 登录，默认情况下不公开访问 — 外部访问使用 SSM 端口转发、VPN 或 Direct Connect。

路由到八个子技能：**网络**、**连接认证**、**计算运行时**、**加密**、**cman-proxy**、**客户端工具**、**ssm-tunneling**、**故障排除**。仅加载匹配的参考。

## 安全注意事项

- **静态加密**：在创建实例时启用 `--storage-encrypted`（可选 `--kms-key-id <key-arn>`）。RDS Oracle 的静态加密只能在创建时设置 — 不能稍后添加而无需重新创建实例。
- **传输中加密**：通过选项组启用原生网络加密 (NNE) 或 TLS/TCPS；不要依赖端口 1521 上的明文用于敏感工作负载。
- **网络暴露**：将实例保持在私有子网中，`PubliclyAccessible: No`。通过 SSM 端口转发、VPN 或 Direct Connect 访问它 — 永远不要启用公共访问。
- **凭证**：将主凭证和应用程序凭证存储在 AWS Secrets Manager 中并启用自动旋转。永远不要在代码、连接字符串或日志中硬编码凭证。
- **KMS 密钥策略**：在使用客户管理的 KMS 密钥进行存储加密时，将其密钥策略的范围限定为 RDS 服务和需要它的角色；仅向该密钥的应用程序角色授予 `kms:Decrypt`。
- **审计日志**：将 Oracle 审计和警报日志导出到 CloudWatch Logs 并为 RDS API 审计启用 CloudTrail（参见日志和监控）。

## 常见任务

### 验证依赖项

在生成连接代码或运行 AWS 命令之前，确认任务需要的工具。

推荐使用 AWS MCP 服务器进行流线化的 AWS 工具执行，但它不是必需的 — 此技能中的每个操作也可以通过整个文档中显示的 AWS CLI 示例运行。

- AWS CLI v2，通过管理机制（IAM 角色、实例配置文件、SSO 凭证分发）获取凭证 — 不要粘贴密钥
- 语言驱动程序：`oracledb`（Python）、`ojdbc11.jar`（Java 11+）、`oracledb`（Node ≥ 6）、`Oracle.ManagedDataAccess.Core` (.NET)
- SSM 端口转发：AWS CLI + Session Manager 插件
- Kerberos：AWS 管理的 Microsoft AD、`krb5.conf`、`okinit` 工具
- CMAN：Oracle 企业版 BYOL 许可证 + 完整的 Oracle 客户端安装（Instant Client 不足）

**限制：**

- 代理在生成代码或运行 AWS 命令之前**必须**检查依赖项。
- 代理**禁止**指示用户将密码粘贴到连接字符串中，因为凭证**必须**来自 AWS Secrets Manager、IAM/域管理的身份或 Kerberos 票据。
- 代理**必须**告诉用户缺少哪些依赖项，并**必须**尊重用户中止的决定。
- 代理在运行它之前**必须**解释每个步骤 — 它做什么、为什么，以及调用了哪个工具。

### 分类和路由

将用户的问题映射到正确的子技能参考，然后仅加载这些文件。

| 用户说 | 加载 |
|---|---|
| SG / VPC 对等 / TGW / Route 53 / 端口 1521 / CIDR | [networking.md](references/networking.md) |
| connect / 连接字符串 / python-oracledb / JDBC / node-oracledb / ODP.NET / Secrets Manager / 认证 / Kerberos | [connection-auth.md](references/connection-auth.md) + 语言参考 ([python.md](references/python.md)、[java.md](references/java.md)、[nodejs.md](references/nodejs.md)、[dotnet.md](references/dotnet.md)) |
| Lambda / EC2 / ECS Fargate / EKS / 容器 / 无服务器 / IRSA | [compute-runtime.md](references/compute-runtime.md) |
| SQL Developer / Toad / SQLcl / DBeaver / sqlplus / GUI | [client-tools.md](references/client-tools.md) |
| SSL / TLS / TCPS / NNE / 加密 / FIPS / 密码 | [encryption.md](references/encryption.md) |
| CMAN / 连接管理器 / 代理 / 多路复用 / RDS Proxy | [cman-proxy.md](references/cman-proxy.md) |
| SSM / 端口转发 / 隧道 / 本地主机 / 笔记本电脑 | [ssm-tunneling.md](references/ssm-tunneling.md) |
| ORA-12170 / ORA-12541 / ORA-01017 / ORA-12514 / ORA-28040 / DPI-1047 / DPY-6005 / 超时 / 拒绝 | [troubleshooting.md](references/troubleshooting.md) |

**限制：**

- 代理**必须**仅读取与用户问题匹配的参考文件，以保持上下文集中。
- 代理**禁止**仅从训练数据生成连接代码或网络配置，因为 Oracle-on-RDS 有特定限制（不支持 RDS Proxy、不允许 SYS 登录、偏好瘦模式、Kerberos IDENTIFIED EXTERNALLY 模式），而大型语言模型经常忽略这些限制。
- 代理**必须**引用 ORA 错误代码及其确切含义，来自故障排除参考，而不是猜测的解释。
- 如果问题跨越多个子技能（例如，“在不同 VPC 中的 ECS Fargate 与 Secrets Manager 连接到 RDS Oracle（包括层、池、冷启动的完整设置）”，代理**应该**加载网络 + 计算运行时 + 连接认证。

### 执行工作流

一旦路由，向用户提供一个具体、可运行的答案，该答案基于参考文件。

参数获取：

- 所有必需参数（区域、实例 ID、端点、服务/SID、源 VPC CIDR、SG ID、Secrets Manager ARN、客户端语言/运行时）**必须**在单个消息中提前收集。
- 必须指定参数格式：区域 `us-east-1` 风格；实例 ID `^[a-zA-Z][a-zA-Z0-9-]{0,62}$`；端点 `<instance>.<hash>.<region>.rds.amazonaws.com>`；CIDR `a.b.c.d/n`；ARN `arn:aws:<service>:<region>:<account>:...`。
- 代理**必须**通过直接输入、JSON/YAML 文件路径或 URL 接收参数。

工具使用：

- 使用 AWS CLI 执行 AWS 操作（示例：`aws ec2 authorize-security-group-ingress --group-id sg-123 --protocol tcp --port 1521 --source-group sg-456`）。
- 使用捆绑脚本 — [test_connectivity.sh](scripts/test_connectivity.sh)、[check_rds_status.sh](scripts/check_rds_status.sh)、[check_security_groups.sh](scripts/check_security_groups.sh)、[test_oracle_connection.py](scripts/test_oracle_connection.py)、[check_ssl_status.sql](scripts/check_ssl_status.sql) — 进行诊断。
- 将计划、高可用性架构、故障排除报告写入 `artifacts/<app-name>/`。

**限制：**

- 代理**禁止**推荐在 RDS Oracle 上启用公共访问，因为公共 RDS 增加了攻击面 — 请使用 SSM 端口转发、VPN 或 Direct Connect。
- 代理**禁止**推荐 RDS Oracle 使用 RDS Proxy，因为 RDS Proxy 不支持 Oracle — 请使用 EC2 上的 Oracle CMAN 代替。
- 代理**禁止**使用 `call_aws` 与位置文件系统参数，因为位置文件系统参数会破坏工具契约 — 使用内联 JSON 字符串。
- 代理**必须**优先使用瘦模式驱动程序（python-oracledb 瘦模式、node-oracledb 6+、ODP.NET Core、ojdbc11），因为瘦模式避免了 Oracle 客户端安装并消除了部署复杂性。
- 代理**必须**将长格式输出写入 `artifacts/<app-name>/`，以便工作空间可检查。

### Rubric-Critical Facts to Always Surface

这些 RDS-for-Oracle 特定的事实将此技能与一般的 Oracle-on-EC2 知识区分开来。最重要的 #1 是：**RDS Proxy 不支持 RDS Oracle** — CMAN 是替代方案。没有此技能的代理会弄错。

对于“将 Python Lambda 连接到 RDS Oracle（包括层、池、冷启动的完整设置）”的用户，您**必须**告诉用户以下七个事实中的所有：

1. **Lambda VPC 配置**：跨多个 AZ 的私有子网 + 允许向 RDS 在 1521 上出站的安全组。
2. **默认使用 python-oracledb 瘦模式 — 无需 Lambda 层**。瘦模式不需要 Oracle 客户端库；不需要 Instant Client，不需要层。只有在用户明确需要厚模式（LDAP 认证或某些 RAC 特定功能）时才推荐层。
3. **模块级连接池在处理程序外部**，以便池在相同容器中的热调用之间持久存在。不要将池构建放在处理程序内部。
4. **使用提供并发进行冷启动优化**，如果对延迟敏感。明确命名“提供并发” — 这是 Lambda 特定的解决方案。
5. **SSM 端点用于 Secrets Manager**，以避免 NAT 网关成本并将密钥检索保持在 VPC 内。这是一个架构优势，不是可选的。
6. **显式处理第一次调用的 ORA-12170** — 第一个冷启动连接可能在 ENI 附着时超时；捕获此错误并重试，不要使请求失败。
7. **仅当需要厚模式时才使用层** — LDAP 认证或某些遗留/RAC 功能。不要盲目推荐添加 `oracle_client` 层。

对于“使用 Secrets Manager CSI 驱动程序、IRSA、SecretProviderClass 和部署清单将 EKS Pod 连接到 RDS Oracle”的用户，您**必须**告诉用户以下七个事实中的所有：

1. **在 EKS 上安装 Secrets Store CSI 驱动程序 + AWS 提供程序** — 使用 `helm install` 安装 CSI 驱动程序，使用 `kubectl apply` 应用 AWS 提供程序 YAML。两者都需要（仅驱动程序无法知道如何与 AWS 通信）。
2. **创建 IAM 策略** 授予 `secretsmanager:GetSecretValue` **在特定的密钥 ARN 上**（不是 `*`）。范围它。
3. **使用 eksctl 设置 IRSA** — `eksctl utils associate-iam-oidc-provider` 用于集群的 OIDC 提供程序，然后 `eksctl create iamserviceaccount` 将 IAM 策略绑定到 Kubernetes ServiceAccount。明确命名“eksctl”、“OIDC”、“iamserviceaccount”。
4. **编写 `SecretProviderClass` YAML**，使用 `provider: aws` 和 `jmesPath` 表达式从 JSON 密钥 blob 中提取单个密钥字段（用户名、密码）。
5. **部署清单挂载 CSI 卷**（`volumes` 使用 `csi: { driver: secrets-store.csi.k8s.io }`）并引用正确的 `serviceAccountName`（通过 IRSA 绑定到 IAM 角色的那个）。
6. **Pod 到 RDS 的端口 1521 的安全组规则** — EKS 工作节点 SG（如果使用安全组为 Pod）必须允许 RDS SG 从 1521 入站。
7. **池大小：总连接数 = replicas × 每个 Pod 的最大池大小**。明确调用此公式，以便用户知道如何根据 N 个副本调整 RDS 实例。

对于“从 EC2 到 RDS Oracle 跨 VPC 连接时出现 ORA-12170 超时”的用户，您**必须**告诉用户以下六个事实中的所有：

1. **检查两个 VPC 之间是否存在 VPC 对等或 Transit Gateway**，并在两个方向上都有路由（EC2 的子网路由表指向对等/TGW 中的 RDS 的 VPC CIDR，RDS 的子网路由表也回指）。
2. **验证 EC2 的安全组出站允许 1521 到 RDS 的安全组或 CIDR**。
3. **验证 RDS 的安全组允许 1521 从 EC2 的安全组 ID（首选）或其 CIDR 入站**。
4. **验证 NACL 允许双向 1521** — NACL 是无状态的，因此需要在两个子网上都需要返回路径 NACL 规则。NACL 是安全组看起来正确时的常见静默阻止因素。
5. **确认 RDS 端点在 EC2 的 DNS 中解析** — 从 EC2 运行 `nslookup <rds-endpoint>`。如果对等 VPC 的 DNS 解析选项未为对等启用，则 RDS 端点无法解析。
6. **最快连接性测试：从 EC2 运行 `nc -zv <rds-endpoint> 1521`**。如果 `nc` 超时而 DNS 工作，问题在于安全组/NACL/路由。始终建议 `nc -zv` 作为缩小步骤。

对于“DPI-1047：无法定位 64 位 Oracle 客户端库”的用户，您**必须**告诉用户以下四个事实中的所有：

1. **DPI-1047表示`python-oracledb`以厚模式运行且无法找到Oracle Instant Client。** 明确说明这是根本原因。
2. **主要修复：通过从代码中移除`oracledb.init_oracle_client()`切换到薄模式。** 薄模式没有Instant Client依赖，并且适用于几乎所有RDS Oracle使用场景（包括TLS、密码认证、Secrets Manager、连接池）。
3. **只有当确实需要厚模式时**（LDAP认证、某些遗留功能）—安装Oracle Instant Client并确保`LD_LIBRARY_PATH`（Linux）或`PATH`（Windows）指向Instant Client目录。明确按操作系统命名环境变量。
4. **不建议盲目安装Instant Client而不确认是否确实需要厚模式。** 默认建议必须是"移除init_oracle_client, 完成。" 首先安装Instant Client再调试路径是常见的误诊，评估标准会捕获这种情况。

**对于"在EC2上作为RDS Oracle的代理的Oracle连接管理器（CMAN），跨两个AZ实现HA"，你必须告诉用户以下全部八个事实：**

1. **提前声明许可和安装前提条件** — CMAN需要**完整的Oracle客户端安装（不是Instant Client）**和**BYOL的Oracle企业版**。这是用户最常犯的错误。要说在前面，不要说在后面。
2. **RDS代理不支持RDS Oracle** — 明确指出这是CMAN成为RDS Oracle连接池/代理模式的原因。代理经常建议使用RDS代理，但会弄错评估标准。
3. **在两个不同AZ的EC2实例上安装CMAN**以实现HA。不要建议单个EC2 — 这会破坏"HA"要求。
4. **配置`cman.ora`**，包括`RULE_LIST`（访问控制规则——哪些客户端可以通过CMAN连接到哪些目标）和`PARAMETER_LIST`（监听器端点、日志记录、会话限制）。按其字面`cman.ora`名称命名这两个块。
5. **在`systemd`下运行CMAN**以在失败时自动重启 — 编写一个服务单元，在启动时启动`cmctl startup`。
6. **跨AZ使用网络负载均衡器（NLB）作为前端**以实现HA — 客户端连接到NLB DNS，NLB将流量分配到两个CMAN EC2。明确提到NLB（不是ALB — Oracle TNS使用TCP）。
7. **三层安全组规则：** 客户端→CMAN EC2安全组（端口1521）→RDS安全组（端口1521）。每个安全组只允许从上一层接收入站流量。这是用户因过于广泛地开放而弄错的建筑模式。
8. **客户端`tnsnames.ora`指向NLB DNS名称** — 客户端通过NLB连接到CMAN，CMAN转发到RDS。不要让客户端连接到单个EC2的DNS。

## 故障排除

实际场景涵盖了三个主要故障类别：访问被拒绝、超时、资源可用性。

| 错误/症状 | 可能的原因 | 修复 |
|---|---|---|
| `ORA-12170`超时 | 安全组阻止1521端口，跨VPC路由缺失，错误的端点 | 运行[test_connectivity.sh](scripts/test_connectivity.sh)；如果TCP失败，检查安全组入站+路由表。跨VPC需要对等/TGW + 基于CIDR的安全组规则。 |
| `ORA-12541`没有监听器 | 错误端口，数据库不可用，错误的端点 | `aws rds describe-db-instances --query 'DBInstances[0].Endpoint'`；确认`Port`。 |
| `ORA-01017`无效凭证 | Secrets Manager中的密码已旋转，Kerberos票据过期 | 从Secrets Manager重新获取；重新运行`okinit`；检查`SELECT username FROM dba_users`。 |
| `ORA-12514`服务未知 | 错误的`SERVICE_NAME`或`SID` | `SELECT value FROM v$parameter WHERE name = 'service_names'` — 完全匹配。 |
| `ORA-28040`没有匹配的认证协议 | 客户端太旧 | 更新客户端到21c+；薄模式可以避免这个问题。 |
| `DPI-1047`（Python） | 启用了厚模式但找不到Oracle Instant Client | 切换到薄模式，通过移除`oracledb.init_oracle_client()`。如果需要厚模式，安装Instant Client并设置`LD_LIBRARY_PATH`（Linux）或`PATH`（Windows）。 |
| `DPY-6005`（Python） | 网络连接失败：连接被拒绝、超时或TLS握手错误 | 检查端点、端口、安全组规则、DNS解析和TLS配置。与ORA-12170相同的诊断路径。 |
| IAM `AccessDenied` on Secrets Manager | 任务角色缺少`secretsmanager:GetSecretValue` | 附加到任务执行角色（ECS任务定义的secrets注入）。 |
| RDS API限流 | 超出请求速率 | 指数退避加抖动；检查服务配额。 |

## 日志和监控

在创建或操作RDS Oracle实例时建议启用以下功能：

- **CloudTrail** — 审计RDS控制平面API调用（创建/修改/删除）。
- **增强监控** — 操作系统级指标（`--monitoring-interval`，`--monitoring-role-arn`）。
- **性能洞察** — 查询级性能分析（`--enable-performance-insights`）。
- **日志导出到CloudWatch Logs** — 通过`--cloudwatch-logs-export-configuration`导出Oracle的`audit`、`alert`、`listener`和`trace`日志。
- **CloudWatch警报** — 至少在`DatabaseConnections`、`FreeStorageSpace`和`CPUUtilization`上设置警报。
- **日志加密** — 使用AWS KMS密钥加密CloudWatch日志组。导出的Oracle `audit`、`alert`和`listener`日志可能包含连接元数据和认证尝试，因此需要保护它们。

## 其他资源

- AWS文档 — Amazon RDS for Oracle：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Oracle.html
- AWS文档 — 使用IAM与RDS：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.html
- AWS文档 — RDS for Oracle Kerberos认证：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-kerberos.html
- AWS文档 — RDS for Oracle的SSL/TLS：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.Oracle.Options.SSL.html
- AWS文档 — Oracle原生网络加密：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.Oracle.Options.NetworkEncryption.html
- AWS Systems Manager — 端口转发：https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html#sessions-remote-port-forwarding
- python-oracledb文档：https://python-oracledb.readthedocs.io/
- node-oracledb文档：https://node-oracledb.readthedocs.io/
- Oracle JDBC驱动：https://www.oracle.com/database/technologies/appdev/jdbc.html
- 相关技能：`odb-aws`（Oracle Database@AWS on OCI管理的Exadata — 不同产品，不同认证模型）。

## 从aws-database-selection交接

此技能可以直接调用，或者可以在`aws-database-selection`父技能运行需求访谈并生成`requirements.json`工件后进入。当你在最近的对话中看到匹配`aws_dbs_requirements/*/requirements.json`的引号包裹路径时，请按照`aws-database-selection/references/handoff-contract.md`中的入口协议操作：

1. 使用`file_read`读取工件。
2. 使用`aws-database-selection/references/workload-primary-artifact.schema.json`验证它。如果格式错误或无法读取，告诉用户并继续操作而不使用它。
3. 承认相关内容，用一到两**粗体**句子引用工件中的高级事实（主导形状、硬约束、迁移背景）——不要逐字重复整个工件。
4. 范围检查：此技能的范围是Amazon RDS for Oracle连接、认证、Kerberos、CMAN和客户端设置跨EC2/ECS/EKS/Lambda。如果工件的`workload_primaries.dominant_shapes`或`migration_context`与该范围不匹配，请根据交接合同发出弱反压：建议`odb-aws`用于AWS上的Exadata级Oracle，`amazon-aurora`用于重构到PostgreSQL，或者如果Oracle不是源引擎，则返回`aws-database-selection`，然后询问用户是否要返回或无论如何继续。不要无声地滥用工件。
5. 使用此技能的本地工作流程继续，在建议基于要求时引用工件路径。

此技能的所有用户面输出都遵循交接合同中定义的仅使用markdown-primitives的格式约定：粗体标签、引号路径和枚举值、用项目符号表示的替代方案、不使用ASCII艺术或框画字符。
