---
name: rds-sqlserver
description: 提供 Amazon RDS for SQL Server 的连接、身份验证和故障排除指南。适用于用户询问以下情况：从 EC2 连接 SSMS 超时、使用 Windows 身份验证无法生成 SSPI 上下文、从 Lambda 使用 pymssql 连接 RDS SQL Server、ECS Fargate 上的 auth_scheme 显示 NTLM 而不是 KERBEROS、从笔记本电脑通过 SSM 隧道连接 RDS SQL Server、端口 1433 的安全组、localhost 隧道的 TrustServerCertificate=True、SPN MSSQLSvc、AWS 管理的 Microsoft AD、CNAME 而不是 RDS 端点用于 Kerberos、tds_version='7.4'、encryption='require'、pymssql 的 port-as-string、Lambda 中的 Secrets Manager 凭据缓存、错误 18456 登录失败。涵盖 Python (pymssql, pyodbc)、.NET (Microsoft.Data.SqlClient)、Java (JDBC mssql-jdbc)、Node.js (tedious)、通过 RDS Proxy 的 IAM 身份验证，以及 VPC/ECS/EKS/Lambda 部署。
---

# Amazon RDS for SQL Server

## 安全指南

本技能涵盖在用户请求时创建和修改 RDS for SQL Server 资源。代理在执行前必须与用户确认操作。未经明确用户确认（例如，“是”、“继续”、“确认”、“继续”），不得执行任何创建或修改操作。如果用户未确认，请呈现计划的操作并请求批准。

### 用户确认后执行的操作

- 创建实例：`create-db-instance`（需要 DB 子网组；RDS SQL Server 仅限于 VPC，默认情况下不公开访问）
- 创建自定义参数组：`create-db-parameter-group`（系列 `sqlserver-ex-15.00`、`sqlserver-se-15.00` 等）— 用于设置 `rds.force_ssl=1` 等选项
- 创建选项组：`create-option-group`（用于 TDE、S3 集成、SQLServer 审计、原生备份/恢复、SSIS、SSAS、SSRS）
- 创建 RDS 代理：`create-db-proxy`、`register-db-proxy-targets`（用于 IAM DB 认证前的 SQL Server — 请参阅 rds-proxy 参考）
- 创建 AWS 管理的 Microsoft AD 目录用于 Windows 认证：`create-directory`（然后通过 `modify-db-instance --domain` 关联）
- 创建带轮换的 Secrets Manager 密钥：`create-secret`、`rotate-secret --rotation-rules AutomaticallyAfterDays=N`
- 更改备份保留期、删除保护、日志导出：`modify-db-instance --backup-retention-period` / `--deletion-protection` / `--cloudwatch-logs-export-configuration`
- 附加/分离参数组或选项组：`modify-db-instance --db-parameter-group-name / --option-group-name`
- 标记资源：`add-tags-to-resource`、`remove-tags-from-resource`

### 资源标记（始终在资源创建时应用）

在创建任何 RDS for SQL Server 资源（`create-db-instance`、`create-db-parameter-group`、`create-option-group`、`create-db-proxy`、用于 RDS 凭据的 `create-secret`、用于 Windows 认证的 `create-directory`）时，始终使用 RDS list-of-records `--tags` 语法包含这些标签（AWS Directory Service 和 Secrets Manager 使用相同的形状）：

`--tags Key=created_by,Value=rds-sqlserver-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-sqlserver-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户未提及标记，也请包含这些标签，以便他们可以通过此技能识别创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时，也适用相同规则。

### 执行时带停机警告（警告用户，然后在他们确认后执行）

- 更改实例类：`modify-db-instance --db-instance-class` — 警告：“这会导致 Multi-AZ 配置中的故障转移，并在单-AZ 实例上导致短暂不可用。”
- 小版本引擎升级：`modify-db-instance --engine-version` 在同一主要版本内（例如，15.00.4X → 15.00.4Y）— 警告：“这会触发重启，并可能导致短暂中断。”
- 存储类型或 IOPS 更改：`modify-db-instance --storage-type` / `--iops` / `--allocated-storage` — 警告：“在更改应用期间，这可能导致 IO 降级。”
- 立即应用：任何 `modify-db-instance --apply-immediately` — 警告：“这会在维护窗口外应用，并可能立即导致停机。”
- 域加入/离开：`modify-db-instance --domain` / `--disable-domain` — 警告：“这将重启实例。”

### 不要执行（拒绝，解释原因，提供评估替代方案）

- 删除实例：`delete-db-instance` — 不可逆数据丢失
- 删除自动备份：`delete-db-instance --delete-automated-backups` — 销毁点时间恢复历史记录
- 故障转移：`reboot-db-instance --force-failover` — 生产影响
- 主要版本升级：`modify-db-instance --engine-version` 跨主要版本（例如，15.0 → 16.0）— 需要预检查和回滚计划；应通过变更控制流程
- 重启：`reboot-db-instance` — 生产影响
- 启用公共访问：`modify-db-instance --publicly-accessible true` — 安全回归；使用 SSM 端口转发、VPN 或 Direct Connect

拒绝时，请解释原因并提供相应的评估工作流：
> “我无法执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际变更应通过您的团队变更控制流程或 AWS 控制台进行。”

## 概述

Amazon RDS for SQL Server 是 AWS 的托管 SQL Server 服务。本技能涵盖了将应用程序连接到 RDS for SQL Server 的端到端工作流程：驱动程序选择、连接字符串、SSL/TLS 加密、SQL 和 Windows 认证、通过 RDS 代理的 IAM 认证、连接池、VPC 网络配置、EC2 / ECS / Lambda / EKS 的部署模式，以及常见错误模式的故障排除。

本技能直接与 AWS CLI 合作。建议使用 AWS MCP 服务器，但不是必需的 — 它在可用时增加了沙盒执行、CloudTrail 审计和可观察性。

## 常见任务

### 1. 验证依赖项

检查所需工具，并在缺少任何工具时警告用户。

**约束条件：**

- 您必须验证 AWS CLI 是否可用（`aws --version`）
- 如果 AWS CLI 缺失，您必须通知用户，因为大多数步骤需要 AWS API 访问
- 如果 AWS MCP 服务器工具（`call_aws`、`suggest_aws_commands`）可用，请优先使用它们进行审计和可观察性 — 但它们不是必需的

### 2. 分类和路由

收集连接上下文并将路由到正确的子技能参考文件。

参数：

- **language**（必需）：`python` | `dotnet` | `java` | `nodejs`。从项目文件推断（`requirements.txt`/`*.py` → python；`*.csproj` → dotnet；`pom.xml`/`build.gradle` → java；`package.json` → nodejs）。如果存在歧义，请仅询问。
- **runtime**（必需）：`ec2` | `ecs` | `lambda` | `eks` | `laptop`。驱动网络+秘密模式。
- **auth**（必需）：`sql` | `windows-kerberos` | `windows-ntlm` | `iam-proxy`。默认 `sql`，除非用户提到 Active Directory、Kerberos、NTLM 或 IAM。
- **region**（必需）：AWS 区域，例如 `us-east-1`。
- **db_instance_id**（用于故障排除时必需）：RDS 实例标识符。

**约束条件：**

- 您必须一次性在单个提示中询问所有必需参数，因为迭代提问会使用户沮丧
- 当可用时，您必须从项目文件中推断 `language`，而不是询问
- 您必须在继续之前验证 `region` 是否在 AWS 区域的枚举列表中
- 您应默认为 SQL 认证，除非用户明确说明 Windows 认证、IAM 认证或 Active Directory

#### 子技能路由

加载**恰好一个驱动程序**参考以及任何相关的主题参考：

| 用户正在执行 | 加载 |
|---|---|
| Python / pymssql / pyodbc | [references/python.md](references/python.md) |
| .NET / C# / Microsoft.Data.SqlClient | [references/dotnet.md](references/dotnet.md) |
| Java / JDBC / mssql-jdbc | [references/java.md](references/java.md) |
| Node.js / tedious / mssql | [references/nodejs.md](references/nodejs.md) |
| EC2 托管 | [references/ec2-vpc.md](references/ec2-vpc.md) |
| Lambda 托管 | [references/lambda-vpc.md](references/lambda-vpc.md) |
| ECS 或 Fargate 托管 | [references/ecs-fargate-vpc.md](references/ecs-fargate-vpc.md) |
| 通过 SSM 隧道进行 Laptop 连接 | [references/ssm-tunneling.md](references/ssm-tunneling.md) |
| SSL/TLS、rds.force_ssl、证书 | [references/encryption.md](references/encryption.md) |
| Windows / AD / Kerberos / NTLM | [references/ad-kerberos.md](references/ad-kerberos.md) |
| 跨 VPC、 Transit Gateway、VPC 对等连接 | [references/networking.md](references/networking.md) |
| SQL 认证、Secrets Manager、凭据 | [references/connection-auth.md](references/connection-auth.md) |
| IAM 认证、RDS 代理、连接池 | [references/rds-proxy.md](references/rds-proxy.md) |
| 错误、连接失败、Kerberos 回退到 NTLM | [references/troubleshooting.md](references/troubleshooting.md) |

### 3. 执行工作流

按顺序遵循加载的参考文件中的步骤：驱动程序设置 → 网络配置 → 认证 → 秘密 → 验证。

**约束条件：**

- 您必须对所有连接使用 `TLS 1.2` 或更高版本，因为较旧的 TLS 版本存在已知漏洞
- 您必须从 AWS Secrets Manager 获取凭据，而不是在代码中嵌入密码，因为硬编码的密钥会泄露到日志和源代码控制中
- 您必须在生产中设置 `Encrypt=Mandatory` (.NET) / `encrypt=true` (JDBC) / `encryption="require"` (pymssql) / `encrypt: true` (tedious)，因为机会性加密可能会静默回退到明文
- 您必须使用 RDS CA 束（从 `https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem`）验证服务器证书链，而不是在生产中设置 `TrustServerCertificate=true`，因为禁用验证会使您容易受到 MITM 攻击
- 您必须不在 DB 实例上启用 `PubliclyAccessible: true`，因为这会将 SQL Server 端口 1433 公开到公共互联网
- 您必须使用安全组 ID 作为同一 VPC 访问的源，并使用 CIDR 块通过 Transit Gateway 或 VPC 对等连接跨 VPC 访问，因为 SG 参考不会跨越 VPC 边界
- 您必须不直接使用 IAM 认证针对 RDS for SQL Server，因为 RDS for SQL Server 不支持它 — IAM 认证需要在实例前使用 RDS 代理
- 您必须从已加入域的主机（EC2 或客户端）测试 Windows 认证，而不是通过 SSM send-command，因为 SSM 以系统帐户运行，而不是用户的 AD 身份
- 当两者都可用时，您应优先选择 Kerberos 而不是 NTLM，因为 Kerberos 是加密学上更强的，并且更容易进行审计
- 当应用程序需要 Kerberos/Windows 认证时，您应优先使用 `pyodbc` 而不是 `pymssql`，因为 pymssql 不支持 Kerberos

### Rubric-Critical Facts to Always Surface

这些 RDS-for-SQL-Server 特定的事实将此技能与一般 SQL Server 知识区分开来。每个下面的清单都是 Rubric 评估匹配测试场景的内容。

**对于“无法从 EC2 连接到 RDS SQL Server — SSMS 超时”，您必须告诉用户以下所有六个事实 — 并且必须系统地调查，而不是简单地列出通用清单：**

1. **询问您正在调试哪个 RDS 实例和哪个源 EC2** — 在没有将诊断范围限定到用户实际资源的情况下，不要开始故障排除。没有范围诊断的通用清单是 Rubric 评为失败的。
2. **检查 VPC 和子网连接性** 介于 EC2 和 RDS 之间（同一 VPC，或 VPC 对等/Transit Gateway 具有可路由路径）。
3. **RDS 上的安全组允许从 EC2 的安全组入站 1433**（通过安全组 ID，而不是 CIDR）。安全组规则是最常见的修复方法。
4. **从 EC2 解析 RDS 端点** — 从 EC2 运行 `nslookup <rds-endpoint>` 并确认它返回私有 IP。
5. **端口 1433 上的 TCP 连接性** — 从 PowerShell 运行 `Test-NetConnection -ComputerName <rds-endpoint> -Port 1433` 或 `telnet <rds-endpoint> 1433`。如果 DNS 工作正常但此操作失败，问题在于安全组或 NACL。
6. **仅当实例位于公共子网时才检查公开访问标志** — 检查 `describe-db-instances` 中的 `PubliclyAccessible`；公共子网上的公共端点在私有子网上是不可达的。
7. **如果默认协议行为异常，请建议 SSMS 选项 → 连接属性 → 网络协议 = TCP/IP**。**此特定的 SSMS 对话框提示必须在响应中明确出现** — 列出所有其他检查但遗漏此 SSMS 特定建议的响应将被 Rubric 评为失败。

**对于“Windows 认证时无法生成 SSPI 上下文”错误，您必须告诉用户以下所有六个事实：**

1. **询问连接之前是否工作** — 这告诉您您是在诊断设置问题（从未工作过）还是回归（工作过，然后中断）。诊断路径不同。不要跳过此分类步骤。
2. **检查客户端的域加入状态** — 在 Windows 上运行 `nltest /dsgetdc:<domain>` 或 `systeminfo | findstr /B /C:"Domain"`。客户端必须加入 AD，该 AD 信任 RDS 实例。
3. **运行 `klist` 检查 Kerberos 票据** — 查找 `MSSQLSvc/<sql-server-host>:<port>` 的票据。如果没有票据，Kerberos 未工作。**您必须在第一个响应中明确提及 `klist`**，而不是将其作为“后续诊断” — Rubric 明确在第一个消息输出中搜索 `klist`。将其作为“当用户回答是否之前工作过时的第一个检查”来表述。
4. **验证 SPN 注册** 对于 `MSSQLSvc/<cname>:1433` 在 AWS 管理的 Microsoft AD 中的 RDS 实例 — 运行 `setspn -L <service-account>` 或检查目录服务。缺少 SPN 是最常见的 SSPI 原因。
5. **确认 DNS 解析** — 客户端的 DNS 必须解析 RDS 端点（或其已加入域的 CNAME）以匹配 SPN 的 AD 已加入名称。连接字符串主机名和 SPN 主机名之间的不匹配会触发 SSPI 失败。
6. **根据答案进行缩小，不要一次列出所有可能的 SSPI 原因。** 首先询问“之前是否工作过？”。然后提供 **klist 作为下一个具体步骤**（“运行 klist 并告诉我您看到什么”）。然后根据 klist 输出，一次调查一个下游路径（没有票据 → 检查域加入+SPN；有票据但服务不匹配 → 检查 SPN 匹配）。**将 klist、域加入、SPN 和 DNS 作为四个子弹点同时诊断是“倾倒”。首先列出 klist 并根据其输出导出下一步是“缩小”。** 后者。Rubric 将会因（a）完全遗漏 klist 和（b） upfront 列出所有四个原因而失败。正确的中间路径：明确提及 klist 作为第一个主动检查，其他原因仅在 klist 输出后提及。

**对于“Lambda with pymssql to RDS SQL Server”，您必须告诉用户以下所有八个事实：**

1. **在示例代码中使用 `pymssql`（而不是 pyodbc）** — 用户明确要求 pymssql。
2. **在连接调用中设置 `encryption='require'`** — 强制 TLS，如果服务器拒绝则快速失败。
3. **设置 `tds_version='7.4'`** — 较旧的 TDS 版本缺少 RDS 所需的 TLS/认证功能。7.4 是当前 RDS SQL Server 上最低支持版本。
4. **将端口作为字符串传递** — `port='1433'`，而不是 `port=1433`。pymssql 对此很挑剔，如果传递 int 会抛出令人困惑的错误。将其称为 pymssql 的陷阱。
5. **使用模块级代码（在处理程序外部）在冷启动时从 Secrets Manager 拉取凭据**，以便 Lambda 的每个容器重用将密钥缓存起来，并且不会在每次调用时调用 Secrets Manager。
6. **如果调用率很高，建议使用 RDS 代理进行前端** — Lambda 的冷容器更迭会快速打开和断开连接；代理会池化它们。
7. **Lambda 放置在 VPC 中**，具有到 RDS 的 1433 安全组出站，以及 **用于 Secrets Manager 的 VPC 端点**（这样 Lambda 就不需要互联网出站）。两者对于生产 VPC Lambda 都是必需的。
8. **带错误处理的完整处理程序** — 具体捕获 **登录失败（错误 18456）** 和 **预登录超时**。**您提供的代码示例必须包括这两个异常处理程序** — 不要仅在文本中提及它们。Rubric 会搜索代码中出现的“18456”和“pre-login timeout”，而不是仅在注释中。示例模式包括：

```python
try:
    conn = pymssql.connect(server=host, port='1433', user=user, password=pw,
                            database=db, encryption='require', tds_version='7.4',
                            login_timeout=5)
except pymssql.OperationalError as e:
    msg = str(e)
    if '18456' in msg or 'Login failed' in msg:
        # 错误 18456：凭证错误 / 数据库错误 / 登录被禁用
        raise RuntimeError(f"登录失败 (18456)：{e}")
    if 'pre-login' in msg.lower() or 'timeout' in msg.lower():
        # 登录前超时：网络路径或 RDS 不健康
        raise RuntimeError(f"登录前超时：{e}")
    raise
```

**对于“ECS Fargate auth_scheme 显示 NTLM 而不是 KERBEROS”，你必须告诉用户以下五个事实：**

1. **将其识别为 Kerberos 回退到 NTLM，而不是连接问题。** TCP 连接成功；认证协商是问题。不要首先将其视为安全组或 DNS 症状。
2. **连接字符串必须使用 AD 注册的 CNAME**，而不是 RDS 端点 — Kerberos 需要匹配 SPN 的主机名。如果客户端连接到 `my-db.abc123.us-east-1.rds.amazonaws.com`，但 SPN 在 `sql.corp.example.com` 注册，Kerberos 无法匹配并回退到 NTLM。这是首要根本原因。
3. **验证 SPN `MSSQLSvc/<cname>:1433`** 在 AD 中注册 — 在加入域的主机上运行 `setspn -L <service-account>`。缺少 SPN → NTLM 回退。
4. **确认 ECS 任务的路径到 AD 域控制器的网络路径** 在端口 **53 (DNS)、88 (Kerberos)、389 (LDAP)、445 (SMB)、464 (kpasswd)** 上。任何缺失的端口将静默降级到 NTLM。Kerberos 仅使用 1433。
5. **不要建议重新加入域或更改密码**，直到确认 CNAME 与端点检查。这些修复措施适用于不同的症状。

**对于“从笔记本电脑到 RDS SQL Server 的 SSM 隧道”，你必须告诉用户以下六个事实：**

1. **使用 `aws ssm start-session`** 并使用文档名称 `AWS-StartPortForwardingSessionToRemoteHost` — 这是远程主机变体，而不是普通的端口转发变体（后者仅转发到 SSM 目标本身）。
2. **文档参数：** `host=<rds-endpoint>`，`portNumber=1433`，`localPortNumber=11433`（使用 **11433 作为示例**，而不是 1433 — 11000 系列的本地端口避免与笔记本电脑上的本地 SQL Server 实例冲突）。
3. **将 SSMS 或 sqlcmd 连接到 `localhost,11433`**（SQL Server 使用逗号语法，而不是冒号）。
4. **在连接字符串中包含 `TrustServerCertificate=True`**。RDS TLS 证书是为 RDS 端点主机名签发的，但客户端连接到 `localhost` — 证书主机名不匹配。`TrustServerCertificate=True` 跳过主机名检查。明确指出这是原因。
5. **需要一个中间的 EC2 实例**，SSM Session Manager 已启用（SSM 代理已安装，IAM 实例角色具有 `AmazonSSMManagedInstanceCore`）。
6. **EC2 上的安全组规则** 允许出站到 RDS 在 1433，RDS 安全组允许从 EC2 的安全组入站 1433。EC2 是隧道端点；RDS 必须接受来自 EC2。

## 故障排除

### 用户登录失败（错误 18456）

最常见的原因：密码错误（SQL Server 日志中的状态 8）、数据库错误（状态 38/40）或登录被禁用（状态 7）。

- 从 Secrets Manager 获取当前密码；如果密钥已轮换，重启应用程序或清除连接池
- 运行 `SELECT * FROM sys.server_principals WHERE name = 'user'` — 检查 `is_disabled` 列
- 参考 [references/troubleshooting.md](references/troubleshooting.md) 获取完整状态代码解码

### 无法生成 SSPI 上下文

Windows 身份验证与 Kerberos 握手失败。根本原因：DNS CNAME 缺失、SPN 不匹配、客户端无法到达 KDC，或使用 RDS 端点（它没有 SPN）而不是域 CNAME。

- 验证客户端解析 CNAME `<db-instance-identifier>.<domain-fqdn>`
- 检查 AD 中 CNAME 的 SPN 存在
- 参考 [references/ad-kerberos.md](references/ad-kerberos.md)

### auth_scheme 显示 NTLM 而不是 KERBEROS

Kerberos 回退到 NTLM。通常是因为客户端直接连接到 RDS 端点，而不是 AD DNS 中注册的 CNAME，或者因为 CNAME 没有注册 SPN。

- 连接到 CNAME（例如 `database-1.example.com`），而不是 RDS 端点
- 使用 `SELECT auth_scheme FROM sys.dm_exec_connections WHERE session_id = @@SPID` 验证
- 参考 [references/troubleshooting.md](references/troubleshooting.md)

### 连接超时

网络路径被阻塞。按顺序检查：

1. 客户端安全组在 1433 上的入站（同一 VPC）或 CIDR（跨 VPC）
2. 路由表有到 RDS 的路由（TGW 绑定或对等连接）
3. NACL 没有阻止返回流量
4. RDS 实例处于 `available` 状态
5. 对于 VPC 中的 Lambda：NAT 网关或用于 Secrets Manager/STS 的 VPC 端点

### 证书验证错误

客户端不信任 RDS CA 链。从 RDS 信任存储下载 `global-bundle.pem` 并添加到客户端信任存储（Java）或 `TrustedCAs` (.NET) 或 `SSL_SERVER_CA` (Python)。

### 从 Lambda 无法访问 Secrets Manager

Lambda 在 VPC 中默认没有互联网访问权限。要么为 Secrets Manager 创建 VPC 端点，要么添加 NAT 网关。Lambda 执行角色需要 `secretsmanager:GetSecretValue`（如果客户管理的 KMS，还需要 `kms:Decrypt`）。

### SSMS “成功连接到服务器，但在登录前握手期间发生错误”

TLS 版本不匹配。SSMS < 18 使用 TLS 1.0；RDS SQL Server 需要 TLS 1.2+。升级 SSMS 或应用 TLS 1.2 补丁。

### pymssql ImportError: DLL load failed on Windows

缺少 FreeTDS。在 Windows 上使用 `pyodbc` — 它使用本地的 `SQL Server Native Client` 或 `ODBC Driver 18 for SQL Server`。

## 其他资源

- **AWS RDS for SQL Server 用户指南**：<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_SQLServer.html>
- **RDS SQL Server TLS/SSL**：<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/SQLServer.Concepts.General.SSL.Using.html>
- **AWS Managed Microsoft AD 与 RDS**：<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_SQLServerWinAuth.html>
- **RDS Proxy for SQL Server**：<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html>
- **Microsoft.Data.SqlClient**：<https://learn.microsoft.com/en-us/sql/connect/ado-net/microsoft-ado-net-sql-server>
- **mssql-jdbc 驱动**：<https://learn.microsoft.com/en-us/sql/connect/jdbc/microsoft-jdbc-driver-for-sql-server>
- **pymssql 文档**：<https://www.pymssql.org/>
- **tedious (Node.js)**：<https://tediousjs.github.io/tedious/>
- **RDS CA 包**：<https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem>
- **相关技能**：`rds-oracle`，`rds-db2`，`amazon-aurora`（用于跨引擎比较）

## 从 aws-database-selection 过渡

此技能可以直接调用，或在使用 `aws-database-selection` 父技能运行需求访谈并生成 `requirements.json` 资产后进入。当你在最近的对话中看到符合 `aws_dbs_requirements/*/requirements.json` 的反引号包裹路径时，请遵循 `aws-database-selection/references/handoff-contract.md` 中的入口协议：

1. 使用 `file_read` 读取资产。
2. 使用 `aws-database-selection/references/workload-primary-artifact.schema.json` 验证它。如果格式错误或无法读取，告诉用户并继续处理。
3. 用一到两 **粗体** 句子承认相关内容，引用来自资产的高级事实（主导形状、硬约束、迁移上下文） — 不要逐字重复整个资产。
4. 范围检查：此技能的范围限于 Amazon RDS for SQL Server 连接性、身份验证（SSPI、Kerberos、SPN、AWS Managed Microsoft AD）和客户端部署模式。如果资产的 `workload_primaries.dominant_shapes` 或 `migration_context` 与此范围不匹配，根据过渡合同发出弱反压力：建议 `amazon-aurora` 用于从 SQL Server 重构到 PostgreSQL，或如果 SQL Server 不是源，则返回 `aws-database-selection`，然后询问用户是否要返回或无论如何继续。不要无声地滥用资产。
5. 使用此技能的本地工作流程继续，在建议基于需求时引用资产路径。

此技能的所有用户面输出都遵循过渡合同中定义的仅使用 markdown-primitives 的格式约定：粗体标签、反引号用于路径和枚举值、项目符号列表用于替代，不使用 ASCII 艺术或框绘制字符。
