---
name: rds-db2
description: 提供、连接、迁移和操作 Amazon RDS for Db2。适用于使用 IBM 客户和站点 ID 进行配置（License Manager、BYOL、GovCloud），通过 TLS 连接，在 Secrets Manager 旋转后修复 SQL30082N，从 Db2 LUW（Linux、AIX、Windows、AS400）或 z/OS 大型机（ADB2GEN、Q Replication）迁移，选择代码页/排序（EBCDIC、CCSID），S3 备份/恢复，多可用区（Multi-AZ）和跨区域热备副本，RDSADMIN 程序，客户管理的 KMS BYOK，自管理的 Active Directory Kerberos，Db2 审计到 S3，最低 IAM 权限，或同址部署。
---

# Amazon RDS for Db2

## 概述

Amazon RDS for Db2 是一个托管的 IBM Db2 LUW 服务。RDS for Db2 是托管的——你不能 SSH 到主机、安装代理或运行 C/COBOL 的无墙外存储过程。Java 存储过程通过 `sqlj.install_jar` 工作。这项技能涵盖了操作员生命周期：使用 IBM 许可证进行配置、客户端安装和 TLS 连接、从 Linux/AIX/Windows/z/OS/AS400 上的自管理 Db2 迁移、S3 备份和恢复、Multi-AZ 和跨区域备用副本，以及替换 SYSCTRL/SYSMAINT 权限的 RDSADMIN 存储过程。

它还涵盖了六个额外的安全和操作领域：客户管理的 KMS 密钥（BYOK）、自管理的 Active Directory 与 Kerberos 身份验证、Db2 审计到 S3、代码页和排序规则选择（EBCDIC、CCSID）、最低 IAM 权限，以及 EC2/RDS 并置以实现 Multi-AZ 延迟和故障转移。

推荐使用 AWS MCP 服务器，但不是必需的；所有操作都以 AWS CLI 语法表达，无论是否安装了 AWS MCP 服务器都可以运行。

匹配的子技能路由参考。仅加载匹配的参考。

## 常见任务

### 验证依赖项

在执行 RDS for Db2 工作流之前，确认所需的工具存在。现在不要运行安装程序或 API 调用。

- 每个针对 RDS API 调用的 AWS CLI v2
- 通过托管机制（IAM 角色、实例配置文件、`ada credentials update`）获取 AWS 凭证——不是粘贴的凭证
- 客户端安装：`bash`/`curl` 访问，以 root 和 `db2inst1` 身份运行
- 空气间隙安装：联网的机器 + 目标具有 S3、SSM、Secrets Manager 的 VPC 端点
- 主机迁移：z/OS 访问、IBM ADB2GEN 许可证、Python 3
- BYOK / 客户端管理的 KMS：`openssl`（用于封装导入的密钥材料）和 `jq`（用于解析 `get-parameters-for-import` 输出）
- 自管理的 Active Directory + Kerberos：客户端上的 `realmd`、`sssd`、`adcli`、`krb5-workstation`，以及有效的 Kerberos 票据（`kinit` 生成 TGT——用 `klist` 检查）
- Kerberos JDBC 测试：一个 JDK 和 Db2 JDBC 驱动 `db2jcc4.jar` v4.33+（较早的驱动版本缺少 `securityMechanism=11` Kerberos 支持）

**约束：**

- 代理在运行任何安装或 AWS API 命令之前必须检查依赖项。
- 代理不得提示用户粘贴凭证，因为凭证必须通过 IAM 角色或实例配置文件流式传输。
- 代理必须告诉用户哪些依赖项缺失，并必须尊重用户中止的决定。
- 代理必须在调用它之前解释每个步骤它做什么、为什么做以及将调用哪个工具。

### 分类和路由

将用户的问题映射到正确的子技能参考，然后仅加载该文件。

| 用户说 | 子技能 | 加载 |
|---|---|---|
| create / provision / parameter group / IBM customer ID / IBM site ID / License Manager / BYOL / GovCloud | provisioning | [provisioning.md](references/provisioning.md) |
| connect / SQL30082N / SQL1531N / DSN / CLP / Python / Java / CloudShell / airgap | connectivity | [connectivity.md](references/connectivity.md) |
| SSL / TLS / GSKit / certificate / truststore / bundle.pem | connectivity-tls | [connectivity-tls.md](references/connectivity-tls.md) |
| Python driver / JDBC / laptop / multi-instance / db2_use | connection drivers | [connection-drivers.md](references/connection-drivers.md) |
| migrate / DMS / Q Replication / IIDR / AIX / Windows / AS400 / precheck | migration | [migration.md](references/migration.md) |
| z/OS / mainframe / ADB2GEN / schema conversion | mainframe-migration | [mainframe-migration.md](references/mainframe-migration.md) |
| code page / collation / CCSID / EBCDIC / UTF-8 / CODEUNITS32 / territory | code page & collation | [code-page-collation.md](references/code-page-collation.md) |
| snapshot / backup / restore / rollforward / PiTR / S3 integration | backup-restore | [backup-restore.md](references/backup-restore.md) |
| Multi-AZ / standby replica / read replica / HADR / cross-region / failover | ha-dr | [ha-dr.md](references/ha-dr.md) |
| parameter group / RDSADMIN / scale / storage / CloudWatch / registry variable | operations | [operations.md](references/operations.md) |
| BYOK / customer-managed KMS / bring your own key / imported key material / multi-region key | byok | [byok-kms.md](references/byok-kms.md) |
| Active Directory / Kerberos / domain join / self-managed AD / kinit / SPN / realm | ad-kerberos | [ad-kerberos.md](references/ad-kerberos.md) |
| audit / DB2_AUDIT / audit policy / audit to S3 / option group | db2-audit | [db2-audit.md](references/db2-audit.md) |
| minimum IAM / least privilege / IAM policy / trust policy / permissions | minimum-iam | [minimum-iam.md](references/minimum-iam.md) |
| colocation / co-locate / EC2 app latency / ASG / ALB / failover routing | colocation | [colocation.md](references/colocation.md) |

**约束：**

- 代理必须仅读取与用户问题匹配的参考文件，以保持上下文集中。
- 代理不得编造 RDSADMIN 存储过程签名，因为错误的参数顺序将在运行时失败——始终引用参考文件中的签名。
- 当答案来自博客时，代理必须引用源博客 URL，以便用户可以验证具体内容。
- 如果一个问题跨越两个子技能（例如，“migrate z/OS with near-zero downtime”，或“BYOK plus cross-region standby”），代理应该加载每个匹配的参考并将它们组合起来。

### 执行工作流

一旦路由，给用户提供一个基于参考文件的具体、可运行的答案。

参数获取：

- 所有必需参数（区域、实例标识符、源/目标 ARN、S3 存储桶、前缀、`--master-username` 值）必须在单个消息中提前收集。
- 必须指定参数格式：区域 `us-east-1` 风格；实例标识符 `^[a-zA-Z][a-zA-Z0-9-]{0,62}$`；ARN `arn:aws:rds:<region>:<account>:db:<name>`；S3 存储桶 3–63 个字符小写。
- 代理必须通过直接输入、JSON/YAML 文件路径或 URL 接收参数。

工具使用：

- 使用 AWS CLI 进行 RDS 操作（示例：`aws rds create-db-instance-read-replica --db-instance-identifier <name> --source-db-instance-identifier <arn> --replica-mode mounted --region <dr-region>`）。每个操作都以 AWS CLI 语法表达，因此无论是否安装了 AWS MCP 服务器都可以运行。
- 使用捆绑脚本——[db2-driver.sh](scripts/db2-driver.sh)、[db2client-configure.sh](scripts/db2client-configure.sh)、[db2client-airgap.sh](scripts/db2client-airgap.sh)、[functions.sh](scripts/functions.sh)——而不是重写安装步骤。
- 将迁移计划、升级计划、验证报告写入在运行时在工作目录中创建的本地 `artifacts/<app-name>/` 目录（这是一个运行时输出位置，不是随技能一起分发的部分）。

**约束：**

- 当行为确定时，代理必须给出确切的 CLI 命令，而不是描述，例如“启用 Multi-AZ”。
- 代理必须通过 IAM 角色或实例配置文件获取 AWS 凭证，并且不得提示用户粘贴凭证。
- 当答案来自已发布材料时，代理必须引用源博客或文档 URL，以便用户可以验证它。
- 代理必须将长格式工件写入本地 `artifacts/<app-name>/` 目录（在运行时在工作目录中创建），以便工作空间可检查。
- 当请求的操作在托管的 RDS for Db2 上不受支持时，代理必须明确说明限制——不要使用“有限支持”或“需要特殊配置”等模糊说法——并提供受支持的替代方案（例如，无墙外 C/COBOL 存储过程不受支持；通过 `sqlj.install_jar` 将它们重写为 Java，或重写为 SQL PL）。
- 推荐 AWS MCP 服务器，但不是必需的。当使用 MCP 服务器时，优先使用内联 JSON 字符串而不是 `call_aws` 的位置文件系统参数；这是针对 MCP 路径的指导，不是要求。永远不要将 `call_aws` 或 `run_script` 视为执行操作的唯一方式——AWS CLI 命令单独运行始终有效。

### 资源标记（在资源创建时始终应用）

在创建任何 RDS for Db2 资源（`create-db-instance`、`create-db-parameter-group`、`create-db-cluster` 用于 Multi-AZ 部署、`create-db-instance-read-replica` 用于备用副本）时，始终使用 RDS list-of-records `--tags` 语法包含这些标签：

`--tags Key=created_by,Value=rds-db2-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-db2-skill Key=generation_model,Value=claude-sonnet-4-20250514`

相同的约定适用于此技能创建的每个资源，包括 BYOK 加密的实例（`create-db-instance --storage-encrypted --kms-key-id ...`）、审计选项组（`create-option-group`）和客户管理的 KMS 密钥（`kms create-key`，按照 KMS 标签语法标记为 `--tags TagKey=created_by,TagValue=rds-db2-skill TagKey=generation_model,TagValue={your-model-id}`）。

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也适用相同的约定。

## 代理必须始终显示的 RDS 管理事实

这些 RDS-for-Db2 特定的事实是此技能与通用 IBM Db2 知识的区别。通用 Db2 答案通常省略 RDS 管理限制（无墙外 C/COBOL、Secrets Manager 旋转副作用、`rdsadmin.*` 存储过程）和 AWS 原生迁移工具的细微差别（DMS z/OS 限制、ADB2GEN 与 SCT）。

**对于“为灾难恢复创建跨区域备用副本”，你必须告诉用户以下所有六个事实：**

1. **使用 `aws rds create-db-instance-read-replica`** 并带有 `--replica-mode mounted` 和跨区域源 ARN——Db2 跨区域备用使用 **mounted 复制模式**，而不是事务性读副本模式。
2. **源先决条件：源实例上启用自动备份**（备份保留期 > 0）。
3. **目标区域先决条件：在命令运行之前在目标区域创建自定义参数组**。
4. **目标区域先决条件：目标区域中有可用的 KMS 密钥**（多区域 KMS 密钥或目标区域的客户管理 KMS 密钥）。
5. **状态先决条件：所有数据库处于 `active` 状态，没有挂起的重新启动**，没有许可证模型限制跨区域副本。
6. **解释 mounted 与事务性区别**——mounted 复本不接受来自应用程序的读取或 SQL；它们纯粹作为灾难恢复备用存在，可以被提升。不要建议读卸载用例。

**对于“从 S3 恢复 Db2 备份（多部分、N 个文件）”，你必须告诉用户以下所有六个事实——永远不要遗漏任何过程名称：**

1. **通过 `aws rds add-role-to-db-instance` 附着具有 S3 访问的 IAM 角色** 使用 `--feature-name S3_INTEGRATION`。
2. **通过 `rdsadmin.set_configuration` 设置恢复性能参数**——在开始恢复之前调整 `USE_STREAMING_RESTORE`、`RESTORE_DATABASE_NUM_BUFFERS` 和 `PARALLELISM`。
3. **调用 `rdsadmin.restore_database`** 并以以下确切顺序使用五个参数：数据库名称、恢复模式（`OFFLINE` 或 `ONLINE`）、S3 前缀、S3 存储桶和区域。多文件（多部分）备份由共享前缀处理——没有单独的多部分标志参数。（签名：`rdsadmin.restore_database(dbname, type, prefix, bucket, region)`。）
4. **对于 `ONLINE` 恢复模式，随后调用 `rdsadmin.rollforward_database`** 以重放归档日志，然后 `rdsadmin.complete_rollforward` 以完成。`OFFLINE` 恢复不需要回滚。
5. **使用 `rdsadmin.get_task_status` 监控进度**——每个 `rdsadmin` 过程返回一个您可以轮询的任务 ID。
6. **如果没有来自私有子网的互联网出站连接，则警告 S3 的 VPC 端点**，并警告**源备份和 RDS 实例引擎版本之间的 Db2 版本兼容性**（向前兼容，不是向后兼容）。

**对于“C/COBOL 无墙外存储过程——将它们迁移到 RDS for Db2？”（提升和迁移），你必须告诉用户以下所有四个事实：**

1. **C 和 COBOL 的无墙外存储过程在 RDS for Db2 上不受支持。** 将其声明为未经修饰的“不受支持”——不要用“有限支持”或“需要特殊配置”来缓和。
2. **RDS for Db2 上的所有例程都必须是墙外的。** 这是一个托管服务的架构约束，不是标志。
3. **支持 Java 存储过程**——通过 `sqlj.install_jar` 安装。C/COBOL SP 应该被**重写为 Java 或 SQL PL**（Db2 的过程 SQL，相当于 Oracle 的 PL/SQL）。
4. **提供帮助识别哪些 SP 是无墙外的**，并按调用频率优先考虑重写（热点代码路径优先）。

**对于“使用近零停机时间将 Db2 for z/OS 迁移到 RDS for Db2”，你必须告诉用户以下所有五个事实：**

1. **对于从 z/OS 的近零停机时间，使用 Q Replication（IBM IIDR）、Qlik Replicate 或 Precisely**——这些是支持 Db2 for z/OS 作为源并将流式传输到 RDS for Db2 的 CDC 工具。
2. **AWS DMS 仅支持从 Db2 for z/OS 的全加载。** DMS 不支持从 z/OS 源的 CDC。使用 DMS 进行一次性批量加载，而不是用于近零停机时间的切换。
3. **使用 ADB2GEN 进行 z/OS 的模式转换。** AWS SCT 不支持 Db2 for z/OS 作为源——这是一个常见的陷阱。不要建议使用 SCT 作为 z/OS 源。
4. **代码页转换（EBCDIC → UTF-8）是主要的迁移风险。** 在切换前计划明确的排序规则和代码页映射——无声数据损坏是故障模式。
5. **在目标 RDS 实例上计划明确的排序规则选择**以匹配 z/OS 源的语义排序。

**对于“SQL30082N — USERNAME AND/OR PASSWORD INVALID”与 RDS 管理的主用户（用户没有更改它），你必须告诉用户以下所有四个事实：**

1. **在之前可以正常连接后几乎总是意味着主密码在 Secrets Manager 中旋转了。** RDS for Db2 按照 Secrets Manager 的计划旋转主密码——使用缓存的密码的客户端即使他们自己这边没有改变也会开始出现 SQL30082N。
2. **修复：运行 `db2_use <instance-id>`**（从 `functions.sh` / 捆绑的辅助工具）。这将从 Secrets Manager 获取当前密码，并将 `~/.db2env` 重写为新的值。
3. **替代方案：`db2_test_connection`** 以验证辅助工具的修复是否端到端工作。
4. **如果 `db2_use` 没有安装**，用户需要使用 `aws secretsmanager get-secret-value` 拉取当前密码并手动更新他们的本地凭证缓存。不要告诉他们旋转密码——密码旋转是导致问题的原因。

**对于“BYOK / 客户端管理的 KMS 密钥用于 RDS for Db2”，你必须告诉用户以下所有六个事实：**

1. **在导入自己的密钥材料时使用多区域 KMS 密钥并带有 `--origin EXTERNAL`**，以便相同的密钥 ID 和材料可以复制到灾难恢复区域。
2. **创建主体需要对密钥具有 `kms:CreateGrant` 和 `kms:DescribeKey`**，否则实例创建失败。
3. **在实例创建时设置加密** 使用 `--storage-encrypted --kms-key-id <alias|arn>`。您**不能就地加密现有的未加密实例**——执行快照 → `copy-db-snapshot --kms-key-id` → `restore-db-instance-from-db-snapshot`。
4. **对于跨区域灾难恢复，首先将多区域密钥（`kms:ReplicateKey`）复制到灾难恢复区域，然后使用副本密钥跨区域执行 `copy-db-snapshot`。**
5. **导入令牌在 24 小时后过期**——如果 `import-key-material` 在过期时失败，重新运行 `get-parameters-for-import` 以获取新的令牌和包装密钥。
6. **引用博客 DBBLOG-5188 和 [byok-kms.md](references/byok-kms.md)**；不要编造 KMS 参数名称。

**对于“在 RDS for Db2 上使用自管理的 Active Directory 与 Kerberos”，你必须告诉用户以下所有六个事实：**

1. **RDS通过`--domain-fqdn`、`--domain-ou`、`--domain-auth-secret-arn`和`--domain-dns-ips`加入您的AD** — 这是自管理的AD路径，无需AWS管理的Microsoft AD。
2. **Secrets Manager密钥使用`SELF_MANAGED_ACTIVE_DIRECTORY_USERNAME`**（仅sAMAccountName——**不能有`DOMAIN\`前缀**，否则创建失败）**和`SELF_MANAGED_ACTIVE_DIRECTORY_PASSWORD`**，由专用KMS密钥加密，资源策略信任`rds.amazonaws.com`，并由`aws:SourceArn`和`aws:SourceAccount`（混淆代理保护）保护。
3. **将九个AD权限委托给专用的服务账户，该账户限定在一个OU内；使用ADSI Edit授予`servicePrincipalName`对**User**对象的读写权限（而不是使用ADUC委托向导，该向导会过滤掉该属性）——这是最常见的失败原因。
4. **在RDS和域控制器之间打开AD端口：DNS 53、Kerberos 88和464、LDAP 389和3268，以及RPC范围49152–65535。** 缺少RPC范围是间歇性加入失败的首要原因。保持时钟偏差在5分钟以内。
5. **RDS主用户是一个本地账户，无法获取Kerberos票据。** AD用户需要`kinit`加上`GRANT CONNECT`。Kerberos JDBC使用`securityMechanism=11`和**区域特定的PEM**通过`sslCertLocation`（永远不要使用`global-bundle.pem`）。
6. **引用自管理的AD博客和[ad-kerberos.md](references/ad-kerberos.md)**；使用`describe-db-instances ... DomainMemberships`验证显示`Status: joined`。

## 故障排除

| 错误 | 原因 | 解决方法 |
|---|---|---|
| `SQL30082N` | Secrets Manager中密码已旋转 | 运行`db2_use <instance-id>`——助手会重新获取当前密码并重写`~/.db2env`。 |
| `SQL1531N` | DSN尚未缓存 | `db2 terminate`清除后重试；如果仍然失败，重新运行[db2client-configure.sh](scripts/db2client-configure.sh)。 |
| `SQL01013N` / TCP超时 | 安全组阻止50000/50443 | 检查SG入站规则——在TCP 50000（明文）或50443（SSL）上添加客户端的SG。 |
| GSKit / SSL证书错误 | RDS证书包缺失或RSA证书不是第一个 | 从RDS信任存储重新下载`<region>-bundle.pem`并重新运行`db2client-configure.sh`。 |
| 对RDSADMIN调用访问被拒绝 | IAM角色缺少`S3_INTEGRATION`功能 | `aws rds add-role-to-db-instance --feature-name S3_INTEGRATION --role-arn <role-arn> --db-instance-identifier <id>`。 |
| 恢复失败，提示"数据库在rollforward pending" | ONLINE恢复将DB置于rollforward状态 | 对每个归档日志调用`rdsadmin.rollforward_database`，然后调用`rdsadmin.complete_rollforward`。 |
| 站备副本创建失败 | 缺少先决条件 | 验证：自动备份已启用、DR区域中的自定义参数组、KMS多区域密钥、没有待处理的`rdsadmin`任务、所有数据库处于活动状态。 |
| AD域加入`Status`不是`joined` | RPC端口范围被阻止、密钥格式错误或SPN属性缺失 | 在RDS和DC之间打开RPC 49152–65535，确认密钥用户名是sAMAccountName且没有`DOMAIN\`前缀，并通过ADSI Edit授予`servicePrincipalName`在User对象上——参见[ad-kerberos.md](references/ad-kerberos.md)。 |
| `import-key-material`失败——token过期 | 导入token超过24小时 | 重新运行`get-parameters-for-import`获取新token和包装密钥，用`openssl`重新包装材料，然后重试导入——参见[byok-kms.md](references/byok-kms.md)。 |
| 来自RDS API的速率限制 | 超出API请求速率 | 指数退避带抖动；批量操作；检查服务配额。 |

## 安全注意事项

在建议任何生产RDS for Db2部署时，应暴露这些控制措施。它们整合了子技能涵盖的详细安全指南。

- **静态和传输中加密** — 始终使用`--storage-encrypted`创建实例；为密钥所有权和合规性使用客户管理的KMS密钥（BYOK），为DR使用多区域密钥。在所有连接上强制执行TLS（端口50443、`<region>-bundle.pem`）；生产环境中永远不要以明文连接。参见[byok-kms.md](references/byok-kms.md)和[connectivity-tls.md](references/connectivity-tls.md)。（指南1）
- **最小权限IAM** — 使用[minimum-iam.md](references/minimum-iam.md)中的作用域策略和信任策略；永远不要附加`*FullAccess`托管策略。作用域`iam:PassRole`，并使用资源级权限支持的所有可变语句的ARN模式。 （指南5）
- **网络隔离** — 将实例保持在私有子网中，限制安全组仅限于应用程序/源SG（永远不要`0.0.0.0/0`），并使用VPC端点进行S3/SSM/Secrets Manager，使流量保持在公共互联网之外。参见[colocation.md](references/colocation.md)。（指南5）
- **审计日志和监控** — 启用Db2审计到S3 ([db2-audit.md](references/db2-audit.md))、RDS增强监控和CloudTrail以监控RDS/KMS/Secrets Manager API调用。对失败登录和配置更改设置警报。 （指南12）
- **密钥旋转** — 使用`--manage-master-user-password`提供，以便RDS在Secrets Manager中存储和旋转主密码；永远不要嵌入明文密码。旋转后，使用`db2_use <instance-id>`刷新客户端。 （指南13）
- **备份加密和保留** — 设置备份保留期，使用您的KMS密钥加密自动和手动快照，并对任何Db2审计或备份桶应用S3桶加密以及生命周期/保留。 （指南13）

## 其他资源

### 范围内文档和博客

- AWS文档 — RDS for Db2：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_RDSDb2.html
- AWS文档 — RDS for Db2 IAM权限：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.html
- AWS文档 — RDS for Db2的Kerberos认证：https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/db2-kerberos.html
- 博客 — 从CloudShell连接到RDS for Db2：https://aws.amazon.com/blogs/database/connect-to-amazon-rds-for-db2-using-aws-cloudshell/
- 博客 — 将自管理的Db2 Linux恢复到RDS for Db2：https://aws.amazon.com/blogs/database/restore-self-managed-db2-linux-databases-in-amazon-rds-for-db2/
- 博客 — 使用Q Replication从AIX/Windows到RDS for Db2的近零停机时间迁移：https://aws.amazon.com/blogs/database/near-zero-downtime-migrations-from-self-managed-db2-on-aix-or-windows-to-amazon-rds-for-db2-using-ibm-q-replication/
- 博客 — 跨区域站备副本：https://aws.amazon.com/blogs/database/configure-amazon-rds-for-db2-standby-replicas-for-high-availability-and-faster-disaster-recovery/
- 博客 — 主机架DDL转换（z/OS到RDS for Db2）：https://aws.amazon.com/blogs/database/migrating-tables-from-ibm-db2-for-z-os-to-amazon-rds-for-db2/
- 博客 — 主机架迁移的代码页和排序规则：https://aws.amazon.com/blogs/database/choosing-the-right-code-page-and-collation-for-migration-from-mainframe-db2-to-amazon-rds-for-db2/
- 博客 — 为RDS for Db2（DBBLOG-5188）自带客户管理的KMS密钥：https://aws.amazon.com/blogs/database/bring-your-own-key-to-amazon-rds-for-db2-with-a-customer-managed-kms-key/
- 博客 — RDS for Db2的自管理Active Directory和Kerberos：https://aws.amazon.com/blogs/database/use-kerberos-authentication-with-a-self-managed-active-directory-for-amazon-rds-for-db2/

### 相关主题（引用资源，尚未路由的子技能）

这些相邻主题在本轮次中未扩展为路由引用。每个主题都可以通过以下引用资源发现。

- RDS for Db2的逆向日志传输（DBBLOG-5352）：https://aws.amazon.com/blogs/database/implement-reverse-log-shipping-for-amazon-rds-for-db2/
- 多账户连接：工作区源`04-db2-client/RDS-Db2-Multiple-Account-Connectivity/`
- Terraform配置：工作区源`04-db2-client/RDS-Db2-Terraform/`
- CIS合规性：工作区源`04-db2-client/CIS-Compliance/`
- db2mon监控：工作区源`04-db2-client/db2mon_RDS/`
- 压缩节省：工作区源`04-db2-client/Compression-Savings/`
- 迁移先决条件检查（DBBLOG-5048）：https://aws.amazon.com/blogs/database/migrate-from-ibm-db2-to-amazon-rds-for-db2-using-a-migration-prerequisite-check/
- 从S3加载数据：工作区源`04-db2-client/load-from-s3/`
- 示例Java存储过程：工作区源`04-db2-client/sample-java-sp/`

### 博客目录

已发布的RDS for Db2博客和示例工具的权威列表维护在https://github.com/aws-samples/sample-rds-db2-tools/tree/main——咨询它以获取当前博客文章和配套代码。

- 相关技能（从Db2 LUW迁移到PostgreSQL）：`rds-postgres-migration`（如果存在于语料库中）。

## 从aws-database-selection的交接

此技能可以直接调用，或可以在`aws-database-selection`父技能运行需求访谈并生成`requirements.json`工件后进入。当您在最近对话中看到匹配`aws_dbs_requirements/*/requirements.json`的引号包裹路径时，请按照`aws-database-selection/references/handoff-contract.md`中的入口协议执行：

1. 使用`file_read`读取工件。
2. 使用`aws-database-selection/references/workload-primary-artifact.schema.json`验证它。如果格式错误或无法读取，告诉用户并继续而不使用它。
3. 在一两个**粗体**句子中承认相关内容，引用工件中的高级事实（主导形状、硬约束、迁移上下文）——不要逐字重复整个工件。
4. 范围检查：此技能限定于Amazon RDS for Db2——Db2 z/OS或LUW的迁移、HADR、站备副本、SQL PL过程、Q Replication切换。如果工件的`workload_primaries.dominant_shapes`或`migration_context`与该范围不匹配，根据交接合同发出弱反压：建议`amazon-aurora`用于从Db2重构到PostgreSQL，或者如果Db2不是源，则返回`aws-database-selection`，然后询问用户是否要返回或无论如何继续。不要无声地滥用工件。
5. 使用此技能的本地工作流程继续，在建议基于需求时引用工件路径作为证据。

父`aws-database-selection`技能消费的经过策管的RDS-for-Db2选择事实位于`assets/selection-knowledge-input.json`（附带人类可读的伴侣`assets/selection-knowledge-input.md`）。这些捕获了范围内的源迁移场景、硬约束、HA/DR选项和安全领域，以结构化、可重用的形式——需要策管选择视图时读取它们，而不是重新推导。

此技能的所有用户界面输出都遵循交接合同中定义的仅使用Markdown原语格式约定：粗体标签、引号包裹路径和枚举值、用项目符号表示替代方案、不使用ASCII艺术或框画字符。
