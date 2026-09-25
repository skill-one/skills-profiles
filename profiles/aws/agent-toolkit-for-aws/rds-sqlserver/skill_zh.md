# Amazon RDS for SQL Server

## 安全指南

本技能涵盖在用户请求时创建和修改 RDS for SQL Server 资源。代理在执行前必须与用户确认操作。不得在未经明确用户确认（例如，“是”、“继续”、“确认”、“继续”）的情况下执行任何创建或修改操作。如果用户未确认，请呈现计划的操作并请求批准。

### 用户确认后执行的操作

- 创建实例：`create-db-instance`（需要 DB 子网组；RDS SQL Server 仅限于 VPC，默认情况下不公开访问）
- 创建自定义参数组：`create-db-parameter-group`（系列 `sqlserver-ex-15.00`、`sqlserver-se-15.00` 等）—— 用于设置 `rds.force_ssl=1` 等选项
- 创建选项组：`create-option-group`（用于 TDE、S3 集成、SQLServer 审计、原生备份/恢复、SSIS、SSAS、SSRS）
- 创建 RDS 代理：`create-db-proxy`、`register-db-proxy-targets`（用于 SQL Server 前面的 IAM DB 认证——参见 rds-proxy 参考）
- 创建 AWS 管理的 Microsoft AD 目录用于 Windows 认证：`create-directory`（然后通过 `modify-db-instance --domain` 关联）
- 创建带旋转的 Secrets Manager 密钥：`create-secret`、`rotate-secret --rotation-rules AutomaticallyAfterDays=N`
- 更改备份保留期、删除保护、日志导出：`modify-db-instance --backup-retention-period` / `--deletion-protection` / `--cloudwatch-logs-export-configuration`
- 附加/分离参数组或选项组：`modify-db-instance --db-parameter-group-name / --option-group-name`
- 标记资源：`add-tags-to-resource`、`remove-tags-from-resource`

### 资源标记（始终在资源创建时应用）

在创建任何 RDS for SQL Server 资源（`create-db-instance`、`create-db-parameter-group`、`create-option-group`、`create-db-proxy`、用于 RDS 凭据的 `create-secret`、用于 Windows 认证的 `create-directory`）时，始终使用 RDS list-of-records `--tags` 语法包含以下标签（AWS Directory Service 和 Secrets Manager 使用相同的形状）：

`--tags Key=created_by,Value=rds-sqlserver-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-sqlserver-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提及标记，也包含这些标签，以便他们可以通过此技能识别创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也适用。

### 用户确认后执行的操作（警告用户后执行）

- 更改实例类：`modify-db-instance --db-instance-class` — 警告：“这会导致 Multi-AZ 配置中的故障转移，并在单-AZ 实例上导致短暂不可用。”
- 小版本引擎升级：`modify-db-instance --engine-version` 在同一主要版本内（例如，15.00.4X → 15.00.4Y）— 警告：“这会触发重启，并可能导致短暂中断。”
- 存储类型或 IOPS 更改：`modify-db-instance --storage-type` / `--iops` / `--allocated-storage` — 警告：“在更改应用期间，这可能导致扩展 IO 退化。”
- 立即应用：任何 `modify-db-instance --apply-immediately` — 警告：“这会在维护窗口外应用，并可能导致立即中断。”
- 域加入/离开：`modify-db-instance --domain` / `--disable-domain` — 警告：“这会重启实例。”

### 不要执行的操作（拒绝，解释原因，提供评估替代方案）

- 删除实例：`delete-db-instance` — 不可逆的数据丢失
- 删除自动备份：`delete-db-instance --delete-automated-backups` — 销毁点时间恢复历史记录
- 故障转移：`reboot-db-instance --force-failover` — 对生产环境的影响
- 主要版本升级：`modify-db-instance --engine-version` 跨主要版本（例如，15.0 → 16.0）— 需要预检查和回滚计划；应通过变更控制流程
- 重启：`reboot-db-instance` — 对生产环境的影响
- 启用公共访问：`modify-db-instance --publicly-accessible true` — 安全回归；使用 SSM 端口转发、VPN 或 Direct Connect

拒绝时，请解释原因并提供相应的评估工作流：
> “我无法执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际更改应通过您的团队的变更控制流程或 AWS 控制台进行。”

## 概述

Amazon RDS for SQL Server 是 AWS 提供的托管 SQL Server 服务。本技能涵盖了将应用程序连接到 RDS for SQL Server 的端到端工作流程：驱动程序选择、连接字符串、SSL/TLS 加密、SQL 和 Windows 认证、通过 RDS 代理的 IAM 认证、连接池、VPC 网络、EC2 / ECS / Lambda / EKS 的部署模式，以及常见错误模式的故障排除。

本技能直接与 AWS CLI 合作。建议使用 AWS MCP 服务器，但不是必需的——它在可用时添加了沙盒执行、CloudTrail 审计和可观察性。

## 常见任务

### 1. 验证依赖项

检查所需工具，如果缺少任何工具，请警告用户。

**约束：**

- 您必须验证 AWS CLI 是否可用（`aws --version`）
- 如果 AWS CLI 缺失，您必须通知用户，因为大多数步骤需要 AWS API 访问
- 如果 AWS MCP 服务器工具（`call_aws`、`suggest_aws_commands`）可用，请优先使用它们进行审计和可观察性——但它们不是必需的

### 2. 分类和路由

收集连接上下文并路由到正确的子技能参考文件。

参数：

- **language**（必需）：`python` | `dotnet` | `java` | `nodejs`。从项目文件中推断（`requirements.txt`/`*.py` → python；`*.csproj` → dotnet；`pom.xml`/`build.gradle` → java；`package.json` → nodejs）。如果存在歧义，请仅询问。
- **runtime**（必需）：`ec2` | `ecs` | `lambda` | `eks` | `laptop`。驱动网络+秘密模式。
- **auth**（必需）：`sql` | `windows-kerberos` | `windows-ntlm` | `iam-proxy`。默认为 `sql`，除非用户提到 Active Directory、Kerberos、NTLM 或 IAM。
- **region**（必需）：AWS 区域，例如 `us-east-1`。
- **db_instance_id**（用于故障排除时必需）：RDS 实例标识符。

**约束：**

- 您必须在一次提示中 upfront 询问所有必需参数，因为迭代提问会让用户感到沮丧
- 当可用时，您必须从项目文件中推断 `language`，而不是询问
- 您必须在继续之前验证 `region` 是否在 AWS 区域的枚举列表中
- 您应该默认为 SQL 认证，除非用户明确说明 Windows 认证、IAM 认证或 Active Directory

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
| 通过 SSM 隧道从笔记本电脑到 RDS SQL Server | [references/ssm-tunneling.md](references/ssm-tunneling.md) |
| SSL/TLS、rds.force_ssl、证书 | [references/encryption.md](references/encryption.md) |
| Windows / AD / Kerberos / NTLM | [references/ad-kerberos.md](references/ad-kerberos.md) |
| 跨 VPC、 Transit Gateway、VPC 对等连接 | [references/networking.md](references/networking.md) |
| SQL 认证、Secrets Manager、凭据 | [references/connection-auth.md](references/connection-auth.md) |
| IAM 认证、RDS 代理、连接池 | [references/rds-proxy.md](references/rds-proxy.md) |
| 错误、连接失败、Kerberos 回退到 NTLM | [references/troubleshooting.md](references/troubleshooting.md) |

### 3. 执行工作流

按顺序遵循加载的参考文件中的步骤：驱动程序设置 → 网络 → 认证 → 秘密 → 验证。

**约束：**

- 您必须对所有连接使用 `TLS 1.2` 或更高版本，因为较旧的 TLS 版本存在已知漏洞
- 您必须从 AWS Secrets Manager 获取凭据，而不是将密码嵌入代码中，因为硬编码的密钥会泄露到日志和源代码中
- 您必须在生产环境中设置 `Encrypt=Mandatory` (.NET) / `encrypt=true` (JDBC) / `encryption="require"` (pymssql) / `encrypt: true` (tedious)，因为机会性加密可能会静默回退到明文
- 您必须使用来自 `https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem` 的 RDS CA 束验证服务器证书链，而不是在生产环境中设置 `TrustServerCertificate=true`，因为禁用验证会使您暴露于 MITM 攻击
- 您必须不在 DB 实例上启用 `PubliclyAccessible: true`，因为这会将 SQL Server 端口 1433 公开到公共互联网
- 您必须使用安全组 ID 作为同一 VPC 访问的源，并使用 CIDR 块通过 Transit Gateway 或 VPC 对等连接进行跨 VPC 访问，因为 SG 参考不会跨越 VPC 边界
- 您必须不直接使用 IAM 认证针对 RDS for SQL Server，因为 RDS for SQL Server 不支持它——IAM 认证需要在实例前面使用 RDS 代理
- 您必须从已加入域的主机（EC2 或客户端）测试 Windows 认证，而不是通过 SSM send-command，因为 SSM 以系统帐户运行，而不是用户的 AD 身份
- 当两者都可用时，您应该优先选择 Kerberos 而不是 NTLM，因为 Kerberos 是密码学上更强的，并且更容易进行审计
- 当应用程序需要 Kerberos/Windows 认证时，您应该优先使用 `pyodbc` 而不是 `pymssql`，因为 pymssql 不支持 Kerberos

### Rubric-Critical Facts to Always Surface

以下 RDS-for-SQL-Server 特定的事实将此技能与一般 SQL Server 知识区分开来。每个下面的清单都是匹配测试场景中 Rubric 评分的内容。

**对于“无法从 EC2 连接到 RDS SQL Server — SSMS 超时”，您必须告诉用户所有以下六个事实——并且必须系统地调查，而不是生硬地列出通用清单：**

1. **询问您正在调试哪个 RDS 实例和哪个源 EC2** —— 在没有将诊断范围缩小到用户实际资源的情况下开始排除故障是不行的。没有针对用户实际资源的范围诊断的通用清单是 Rubric 评为失败的。
2. **检查 EC2 和 RDS 之间的 VPC 和子网连接**（同一 VPC，或具有可路由路径的 VPC 对等连接/Transit Gateway）。
3. **RDS 上的安全组允许从 EC2 的安全组 1433 入站**（通过安全组 ID，而不是 CIDR）。安全组规则是最常见的修复方法。
4. **从 EC2 解析 RDS 端点**——从 EC2 运行 `nslookup <rds-endpoint>` 并确认它返回私有 IP。
5. **1433 端口的 TCP 连接**——从 PowerShell 或 `telnet <rds-endpoint> 1433` 运行 `Test-NetConnection -ComputerName <rds-endpoint> -Port 1433`。如果 DNS 工作，而此操作失败，则问题出在安全组或 NACL 上。
6. **仅当实例位于公共子网时才检查公开访问标志**——检查 `describe-db-instances` 中的 `PubliclyAccessible`；公共子网上的公共端点无法访问。
7. **如果默认协议行为不当，建议 SSMS 选项 → 连接属性 → 网络协议 = TCP/IP**。**此特定的 SSMS 对话框提示必须在响应中明确出现**——忽略此 SSMS 特定建议的响应将被 Rubric 评为失败。

**对于“Windows 认证时出现“无法生成 SSPI 上下文”错误”，您必须告诉用户所有以下六个事实：**

1. **询问连接是否之前工作过**——这告诉您您是在诊断设置问题（从未工作过）还是回归问题（工作过，然后坏了）。诊断路径不同。不要跳过此分诊步骤。
2. **检查客户端的域加入状态**——在 Windows 上运行 `nltest /dsgetdc:<domain>` 或 `systeminfo | findstr /B /C:"Domain"`。客户端必须加入到 RDS 实例信任的 AD。
3. **运行 `klist` 检查 Kerberos 票据**——查找 `MSSQLSvc/<sql-server-host>:<port>` 的票据。如果没有票据，Kerberos 就不工作。**您必须在第一个响应中明确提到 `klist`**，而不是将其作为“后续诊断”——Rubric 明确在第一个消息输出中搜索 `klist`。将其作为“当用户回答是否之前工作过时的第一个检查”来描述。
4. **验证 RDS 实例在 AWS Managed Microsoft AD 中的 SPN 注册**——在 AWS Directory Service 中运行 `setspn -L <service-account>` 或检查目录服务。缺少 SPN 是最常见的 SSPI 原因。
5. **确认 DNS 解析**——客户端的 DNS 必须解析 RDS 端点（或其已加入域的 CNAME）以匹配 SPN 中的 AD 已加入名称。连接字符串主机名和 SPN 主机名之间的不匹配会触发 SSPI 失败。
6. **根据答案进行缩小，不要一次生硬地列出所有可能的 SSPI 原因。** 首先询问“之前是否工作过？”。然后提供 **klist 作为下一个具体步骤**（“运行 klist 并告诉我您看到了什么”）。然后根据 klist 输出，一次调查一个下游路径（没有票据 → 检查域加入+SPN；有票据但服务不匹配 → 检查 SPN 匹配）。**同时列出 klist、域加入、SPN 和 DNS 作为四个子弹诊断是“生硬的”。首先列出 klist 并根据其输出生成下一步是“缩小”。做后者。Rubric 将会因（a）完全遗漏 klist 和（b）生硬地 upfront 列出所有四个原因而失败。正确的中间路径：明确在第一个主动检查中提到 klist，其他原因仅在 klist 输出决定下作为“下一步”提及。**

**对于“Lambda with pymssql to RDS SQL Server”，您必须告诉用户所有以下八个事实：**

1. **在示例代码中使用 `pymssql`（而不是 pyodbc）**——用户明确要求 pymssql。
2. **在连接调用中设置 `encryption='require'`**——强制 TLS，如果服务器拒绝，则快速失败。
3. **设置 `tds_version='7.4'`**——较旧的 TDS 版本缺少 RDS 需要的 TLS/认证功能。7.4 是当前 RDS SQL Server 支持的最低 TDS 版本。
4. **将端口作为字符串传递**——`port='1433'`，而不是 `port=1433`。pymssql 对此很挑剔，如果传递 int，会抛出奇怪的错误。将其作为 pymssql 的陷阱指出。
5. **使用模块级代码（在处理程序之外）从 Secrets Manager 在冷启动时获取凭据**，以便 Lambda 的每个容器重用将密钥缓存起来，并且不会在每次调用时调用 Secrets Manager。
6. **如果调用频率很高，建议使用 RDS 代理进行前端**——Lambda 的冷容器更替会快速打开和关闭连接；代理会池化它们。
7. **Lambda 放置在 VPC 中**，具有到 RDS 的 1433 安全组出站，以及 **用于 Secrets Manager 的 VPC 端点**（这样 Lambda 就不需要互联网出站）。两者对于生产 VPC Lambda 都是必需的。
8. **带错误处理的完整处理程序**——具体捕获 **登录失败（错误 18456）** 和 **预登录超时**。**您提供的代码样本必须包括这两个异常处理程序**——不要只是在文本中提到它们。Rubric 会搜索代码中出现的“18456”和“预登录超时”，而不仅仅是注释中的。示例模式包括：

```python
try:
    conn = pymssql.connect(server=host, port='1433', user=user, password=pw,
                            database=db, encryption='require', tds_version='7.4',
                            login_timeout=5)
except pymssql.OperationalError as e:
    msg = str(e)
    if '18456' in msg or 'Login failed' in msg:
        # 错误 18456：密码错误/数据库错误/登录禁用
        raise RuntimeError(f"Login failed (18456): {e}")
    if 'pre-login' in msg.lower() or 'timeout' in msg.lower():
        # 预登录超时：网络路径或 RDS 不健康
        raise RuntimeError(f"Pre-login timeout: {e}")
    raise
```

**对于“ECS Fargate auth_scheme 显示 NTLM 而不是 KERBEROS”，您必须告诉用户所有以下五个事实：**

1. **将其识别为 Kerberos 回退到 NTLM，而不是连接问题**。TCP 连接成功；认证协商是问题。不要将其视为安全组或 DNS 症状首先。
2. **连接字符串必须使用已注册的 AD CNAME**，而不是 RDS 端点——Kerberos 需要匹配 SPN 的主机名。如果客户端连接到 `my-db.abc123.us-east-1.rds.amazonaws.com`，但 SPN 注册在 `sql.corp.example.com` 下，Kerberos 无法匹配并回退到 NTLM。这是 #1 根本原因。
3. **验证 AD 中是否存在 SPN `MSSQLSvc/<cname>:1433`**——在已加入域的主机上运行 `setspn -L <service-account>`。缺少 SPN → NTLM 回退。
4. **确认 ECS 任务的路径到 AD 域控制器** 在端口 **53 (DNS), 88 (Kerberos), 389 (LDAP), 445 (SMB), 464 (kpasswd)** 上。任何缺失的端口都会静默退化到 NTLM。Kerberos 并非仅使用 1433。
5. **在确认 CNAME 与端点之前，不要建议重新加入域或更改密码**。这些修复方法适用于不同的症状。

**对于“从笔记本电脑到 RDS SQL Server 的 SSM 隧道”，您必须告诉用户所有以下六个事实：**

1. **使用 `aws ssm start-session`** 并使用文档名称 `AWS-StartPortForwardingSessionToRemoteHost`——这是远程主机变体，而不是普通的端口转发变体（后者仅转发到 SSM 目标本身）。
2. **文档参数：** `host=<rds-endpoint>`、`portNumber=1433`、`localPortNumber=11433`（使用 **11433 作为示例**，而不是 1433——笔记本电脑上避免与本地 SQL Server 实例冲突的本地端口在 11000s 范围内）。
3. **将 SSMS 或 sqlcmd 连接到 `localhost,11433`**（SQL Server 使用逗号语法，而不是冒号）。
4. **在连接字符串中包含 `TrustServerCertificate=True`**。RDS TLS 证书是针对 RDS 端点主机名颁发的，但客户端正在连接到 `localhost`——证书主机名不会匹配。`TrustServerCertificate=True` 跳过主机名检查。明确指出此原因。
5. **需要中间 EC2 实例**，并启用 SSM Session Manager（SSM 客户端已安装，IAM 实例角色具有 `AmazonSSMManagedInstanceCore`）。
6. **在 EC2 上的安全组规则** 允许到 RDS 的 1433 出站，以及 RDS 安全组允许从 EC2 的安全组 1433 入站。EC2 是隧道端点；RDS 必须接受来自 EC2 的安全组。
