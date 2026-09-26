# Amazon RDS for Db2

## 概述

Amazon RDS for Db2 是一个托管的 IBM Db2 LUW 服务。RDS for Db2 是托管的——你不能 SSH 到主机、安装代理或运行 C/COBOL 的无墙外存储过程。Java 存储过程通过 `sqlj.install_jar` 工作。这项技能涵盖了操作员生命周期：使用 IBM 许可证进行配置、客户端安装和 TLS 连接、从 Linux/AIX/Windows/z/OS/AS400 上的自管理 Db2 迁移、S3 备份和恢复、多 AZ 和跨区域备用副本，以及替换 SYSCTRL/SYSMAINT 权限的 RDSADMIN 存储过程。

它还涵盖了六个额外的安全和操作领域：客户管理的 KMS 密钥（BYOK）、自管理的 Active Directory 与 Kerberos 身份验证、Db2 审计到 S3、代码页和排序规则选择（EBCDIC、CCSID）、最低 IAM 权限，以及 EC2/RDS 并置以实现 Multi-AZ 延迟和故障转移。

建议使用 AWS MCP 服务器，但不是必需的；所有操作都以 AWS CLI 语法表示，无论是否安装了 AWS MCP 服务器都可以运行。

路由到匹配的子技能参考。仅加载匹配的参考。

## 常见任务

### 验证依赖项

在执行 RDS for Db2 工作流之前，确认所需的工具是否存在。暂时不要运行安装程序或 API 调用。

- 每个针对 RDS API 调用的 AWS CLI v2
- 通过托管机制（IAM 角色、实例配置文件、`ada credentials update`）提供的 AWS 凭证——不是粘贴的凭证
- 客户端安装：`bash`/`curl` 访问，以 root 和 `db2inst1` 身份运行
- 空间隙安装：连接到互联网的机器 + 目标具有 S3、SSM、Secrets Manager 的 VPC 端点
- 主机迁移：z/OS 访问、IBM ADB2GEN 许可证、Python 3
- BYOK / 客户端管理的 KMS：`openssl`（用于封装导入的密钥材料）和 `jq`（用于解析 `get-parameters-for-import` 输出）
- 自管理的 Active Directory + Kerberos：客户端上的 `realmd`、`sssd`、`adcli`、`krb5-workstation`，以及有效的 Kerberos 票据（`kinit` 生成 TGT——用 `klist` 检查）
- Kerberos JDBC 测试：一个 JDK 和 Db2 JDBC 驱动程序 `db2jcc4.jar` v4.33+（较早的驱动程序版本缺少 `securityMechanism=11` Kerberos 支持）

**约束：**

- 代理必须在运行任何安装或 AWS API 命令之前检查依赖项。
- 代理必须不提示用户粘贴凭证，因为凭证必须通过 IAM 角色或实例配置文件流式传输。
- 代理必须告诉用户哪些依赖项缺失，并且必须尊重用户中止的决定。
- 代理必须解释每个步骤执行什么、为什么以及将调用哪个工具——在调用它之前。

### 分类和路由

将用户的问题映射到正确的子技能参考，然后仅加载该文件。

| 用户说 | 子技能 | 加载 |
|---|---|---|
| 创建 / 配置 / 参数组 / IBM 客户 ID / IBM 站点 ID / 许可证管理器 / BYOL / GovCloud | 配置 | [配置.md](references/配置.md) |
| 连接 / SQL30082N / SQL1531N / DSN / CLP / Python / Java / CloudShell / 空间隙 | 连接性 | [连接性.md](references/连接性.md) |
| SSL / TLS / GSKit / 证书 / 信任存储 / bundle.pem | 连接性-TLS | [连接性-TLS.md](references/连接性-TLS.md) |
| Python 驱动程序 / JDBC / 笔记本电脑 / 多实例 / db2_use | 连接驱动程序 | [连接驱动程序.md](references/连接驱动程序.md) |
| 迁移 / DMS / Q Replication / IIDR / AIX / Windows / AS400 / 预检查 | 迁移 | [迁移.md](references/迁移.md) |
| z/OS / 主机 / ADB2GEN / 模式转换 | 主机迁移 | [主机迁移.md](references/主机迁移.md) |
| 代码页 / 排序规则 / CCSID / EBCDIC / UTF-8 / CODEUNITS32 / 地区 | 代码页和排序规则 | [代码页-排序规则.md](references/代码页-排序规则.md) |
| 快照 / 备份 / 恢复 / 滚前 / PiTR / S3 集成 | 备份恢复 | [备份恢复.md](references/备份恢复.md) |
| Multi-AZ / 备用副本 / 读副本 / HADR / 跨区域 / 故障转移 | 高可用性灾难恢复 | [高可用性灾难恢复.md](references/高可用性灾难恢复.md) |
| 参数组 / RDSADMIN / 扩展 / 存储 / CloudWatch / 注册变量 | 操作 | [操作.md](references/操作.md) |
| BYOK / 客户端管理的 KMS / 带你自己的密钥 / 导入的密钥材料 / 多区域密钥 | BYOK | [BYOK-KMS.md](references/BYOK-KMS.md) |
| Active Directory / Kerberos / 域加入 / 自管理的 Active Directory / kinit / SPN / 域 | AD-Kerberos | [AD-Kerberos.md](references/AD-Kerberos.md) |
| 审计 / DB2_AUDIT / 审计策略 / 审计到 S3 / 选项组 | Db2-审计 | [Db2-审计.md](references/Db2-审计.md) |
| 最低 IAM / 最小权限 / IAM 策略 / 信任策略 / 权限 | 最低 IAM | [最低 IAM.md](references/最低 IAM.md) |
| 并置 / 共置 / EC2 应用延迟 / ASG / ALB / 故障转移路由 | 并置 | [并置.md](references/并置.md) |

**约束：**

- 代理必须仅读取与用户问题匹配的参考文件，以保持上下文集中。
- 代理必须不编造 RDSADMIN 存储过程签名，因为错误的参数顺序将在运行时失败——始终引用参考文件中的签名。
- 当答案来自博客时，代理必须引用源博客 URL，以便用户可以验证具体信息。
- 如果问题跨越两个子技能（例如，“使用近乎零停机时间从 z/OS 迁移 Db2”或“BYOK 加上跨区域备用副本”），代理应加载每个匹配的参考并将它们组合起来。

### 执行工作流

一旦路由，向用户提供一个基于参考文件的具体、可运行的答案。

参数获取：

- 所有必需参数（区域、实例标识符、源/目标 ARN、S3 桶、前缀、`--master-username` 值）必须在单个消息中提前收集。
- 必须指定参数格式：区域 `us-east-1` 风格；实例标识符 `^[a-zA-Z][a-zA-Z0-9-]{0,62}$`；ARN `arn:aws:rds:<region>:<account>:db:<name>`；S3 桶 3–63 个字符小写。
- 代理必须通过直接输入、JSON/YAML 文件路径或 URL 接收参数。

工具使用：

- 使用 AWS CLI 进行 RDS 操作（示例：`aws rds create-db-instance-read-replica --db-instance-identifier <name> --source-db-instance-identifier <arn> --replica-mode mounted --region <dr-region>`）。每个操作都以 AWS CLI 语法表示，因此无论是否安装了 AWS MCP 服务器都可以运行。
- 使用捆绑脚本——[db2-driver.sh](scripts/db2-driver.sh)、[db2client-configure.sh](scripts/db2client-configure.sh)、[db2client-airgap.sh](scripts/db2client-airgap.sh)、[functions.sh](scripts/functions.sh)——而不是重写安装步骤。
- 将迁移计划、升级计划、验证报告写入在运行时在工作目录中创建的本地 `artifacts/<app-name>/` 目录（这是一个运行时输出位置，不是随技能一起分发的部分）。

**约束：**

- 当行为确定时，代理必须给出确切的 CLI 命令，而不是描述，例如“启用 Multi-AZ”。
- 代理必须通过 IAM 角色或实例配置文件获取 AWS 凭证，并且必须不提示用户粘贴凭证。
- 当答案来自已发布材料时，代理必须引用源博客或文档 URL，以便用户可以验证它。
- 代理必须将长格式工件写入本地 `artifacts/<app-name>/` 目录（在运行时在工作目录中创建），以便工作空间可检查。
- 当请求的操作在管理的 RDS for Db2 上不受支持时，代理必须明确说明限制——不要使用“有限支持”或“需要特殊配置”等模糊说法——并提供受支持的替代方案（例如，无墙外 C/COBOL 存储过程不受支持；通过 `sqlj.install_jar` 将它们重写为 Java，或重写为 SQL PL）。
- AWS MCP 服务器是建议的，但不是必需的。当使用 MCP 服务器时，请优先使用内联 JSON 字符串而不是 `call_aws` 的位置文件系统参数；这只是针对 MCP 路径的指导，不是要求。永远不要将 `call_aws` 或 `run_script` 视为执行操作的唯一方式——AWS CLI 命令单独起作用。

### 资源标记（资源创建时始终应用）

在创建任何 RDS for Db2 资源（`create-db-instance`、`create-db-parameter-group`、`create-db-cluster` 用于 Multi-AZ 部署、`create-db-instance-read-replica` 用于备用副本）时，始终使用 RDS list-of-records `--tags` 语法包含这些标签：

`--tags Key=created_by,Value=rds-db2-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=rds-db2-skill Key=generation_model,Value=claude-sonnet-4-20250514`

相同的约定适用于此技能创建的每个资源，包括 BYOK 加密的实例（`create-db-instance --storage-encrypted --kms-key-id ...`）、审计选项组（`create-option-group`）和客户端管理的 KMS 密钥（`kms create-key`，按照 KMS 标签语法标记）。

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签，而不是替换它们。在通过 `add-tags-to-resource` 对现有资源进行标记时，也适用相同的约定。

## RDS 管理的事实，代理必须始终显示

这些 RDS-for-Db2 特定的事实使此技能与一般的 IBM Db2 知识区分开来。通常，一般-Db2 答案会省略 RDS 管理的约束（无墙外 C/COBOL、Secrets Manager 旋转副作用、`rdsadmin.*` 存储过程）和 AWS 本地迁移工具的细微差别（DMS z/OS 限制、ADB2GEN 与 SCT）。

**对于“为灾难恢复创建跨区域备用副本”，你必须告诉用户以下所有六个事实：**

1. **使用 `aws rds create-db-instance-read-replica`** 并带有 `--replica-mode mounted` 和跨区域源 ARN——Db2 跨区域备用副本使用**挂载副本模式**，而不是事务性读副本模式。
2. **源先决条件：源实例上启用自动备份**（备份保留期 > 0）。
3. **目标区域先决条件：在命令运行之前在目标区域创建自定义参数组**。
4. **目标区域先决条件：目标区域中可用的 KMS 密钥**（多区域 KMS 密钥或目标区域客户端管理的 KMS 密钥）。
5. **状态先决条件：所有数据库处于 `active` 状态，没有挂起的重新启动**，没有许可证模型阻止跨区域副本。
6. **解释挂载与事务性区别**——挂载副本不接受来自应用程序的读取或 SQL；它们纯粹作为灾难恢复备用副本存在，可以提升。不要建议读卸载用例。

**对于“从 S3 恢复 Db2 备份（多部分，N 个文件）”，你必须告诉用户以下所有六个事实——永远不要省略任何过程名称：**

1. **通过 `aws rds add-role-to-db-instance` 附加上载 S3 访问的 IAM 角色** 使用 `--feature-name S3_INTEGRATION`。
2. **通过 `rdsadmin.set_configuration` 设置恢复性能参数**——在开始恢复之前调整 `USE_STREAMING_RESTORE`、`RESTORE_DATABASE_NUM_BUFFERS` 和 `PARALLELISM`。
3. **调用 `rdsadmin.restore_database`** 并以以下确切顺序提供五个参数：数据库名称、恢复模式（`OFFLINE` 或 `ONLINE`）、S3 前缀、S3 桶和区域。多文件（多部分）备份由共享前缀处理——没有单独的多部分标志参数。（签名：`rdsadmin.restore_database(dbname, type, prefix, bucket, region)`。）
4. **对于 `ONLINE` 恢复模式，随后调用 `rdsadmin.rollforward_database`** 以重放存档日志，然后 `rdsadmin.complete_rollforward` 以完成。`OFFLINE` 恢复不需要回滚。
5. **使用 `rdsadmin.get_task_status` 监控进度**——每个 `rdsadmin` 过程都返回一个您可以轮询的任务 ID。
6. **如果 S3 没有来自私有子网的互联网出口，则警告 S3 VPC 端点**，并警告**源备份和 RDS 实例引擎版本之间的 Db2 版本兼容性**（向前兼容，不是向后兼容）。

**对于“C/COBOL 无墙外存储过程——迁移到 RDS for Db2？”你必须告诉用户以下所有四个事实：**

1. **C 和 COBOL 中的无墙外存储过程在 RDS for Db2 上不受支持。** 将其表述为明确的“不受支持”——不要用“有限支持”或“需要特殊配置”来模糊处理。
2. **RDS for Db2 上的所有例程都必须是封定的。** 这是一个托管服务的架构约束，而不是一个标志。
3. **支持 Java 存储过程**——通过 `sqlj.install_jar` 安装。C/COBOL SP 应该**重写为 Java 或 SQL PL**（Db2 的过程 SQL，相当于 Oracle 的 PL/SQL）。
4. **提供帮助识别哪些 SP 是无墙外的**，并按调用频率（热代码路径优先）对重写进行优先排序。

**对于“使用近乎零停机时间从 z/OS 迁移 Db2 到 RDS for Db2”，你必须告诉用户以下所有五个事实：**

1. **对于从 z/OS 的近乎零停机时间，使用 Q Replication (IBM IIDR)、Qlik Replicate 或 Precisely**——这些是支持 Db2 for z/OS 作为源将数据流到 RDS for Db2 的 CDC 工具。
2. **AWS DMS 仅支持从 Db2 for z/OS 进行 FULL LOAD。** DMS 不支持从 z/OS 源进行 CDC。使用 DMS 进行一次性批量加载，而不是用于近乎零停机时间的切换。
3. **使用 ADB2GEN 进行 z/OS 模式转换。** AWS SCT 不支持 Db2 for z/OS 作为源——这是一个常见的陷阱。不要建议使用 SCT 进行 z/OS 源。
4. **代码页转换（EBCDIC → UTF-8）是迁移的主要风险。** 在切换之前制定明确的排序规则和代码页映射计划——数据损坏是故障模式。
5. **在目标 RDS 实例上制定明确的排序规则选择**以匹配 z/OS 源的语义排序。

**对于“SQL30082N — 用户名和/或密码无效”与 RDS 管理的主用户（用户没有更改它），你必须告诉用户以下所有四个事实：**

1. **在之前可以正常连接后出现 SQL30082N 几乎总是意味着主密码在 Secrets Manager 中旋转了。** RDS for Db2 按 Secrets Manager 的计划旋转主密码——使用缓存的密码的客户端即使他们自己这边没有改变，也会开始失败。
2. **修复：运行 `db2_use <instance-id>`**（从 `functions.sh` / 捆绑的帮助程序）。这将从 Secrets Manager 获取当前密码，并使用新值重写 `~/.db2env`。
3. **替代方案：`db2_test_connection`** 以验证帮助程序是否端到端工作。
4. **如果 `db2_use` 没有安装**，用户需要使用 `aws secretsmanager get-secret-value` 拉取当前密码并手动更新他们的本地凭证缓存。不要告诉他们旋转密码——密码旋转导致了问题。

**对于“BYOK / 客户端管理的 KMS 密钥 for RDS for Db2”，你必须告诉用户以下所有六个事实：**

1. **使用多区域 KMS 密钥并带有 `--origin EXTERNAL`** 在导入你自己的密钥材料时，以便相同的密钥 ID 和材料可以复制到灾难恢复区域。
2. **创建者需要 `kms:CreateGrant` 和 `kms:DescribeKey`** 在密钥上，或者实例创建失败。
3. **加密在实例创建时设置**使用 `--storage-encrypted --kms-key-id <alias|arn>`。您**无法在原地加密现有的未加密实例**——先快照 → `copy-db-snapshot --kms-key-id` → `restore-db-instance-from-db-snapshot`。
4. **对于跨区域灾难恢复，首先将多区域密钥复制到灾难恢复区域 (`kms:ReplicateKey`)**，然后使用副本密钥跨区域复制 `copy-db-snapshot`。
5. **导入令牌在 24 小时后过期**——如果 `import-key-material` 在过期时失败，重新运行 `get-parameters-for-import` 以获取新的令牌和包装密钥。
6. **引用博客 DBBLOG-5188 和 [byok-kms.md](references/byok-kms.md)**；不要编造 KMS 参数名称。

**对于“在 RDS for Db2 上使用自管理的 Active Directory 与 Kerberos”，你必须告诉用户以下所有六个事实：**

1. **RDS 通过 `--domain-fqdn`、`--domain-ou`、`--domain-auth-secret-arn` 和 `--domain-dns-ips` 加入你的 AD**——自管理的 AD 路径，不需要 AWS 管理的 Microsoft AD。
2. **Secrets Manager 密钥使用 `SELF_MANAGED_ACTIVE_DIRECTORY_USERNAME`**（sAMAccountName 仅——**没有 `DOMAIN\` 前缀**，这会导致创建失败）**和 `SELF_MANAGED_ACTIVE_DIRECTORY_PASSWORD`**，由专用 KMS 密钥加密，具有信任 `rds.amazonaws.com` 的资源策略，由 `aws:SourceArn` 和 `aws:SourceAccount`（混淆代理保护）保护。
3. **将九个 AD 权限委派给一个专用的服务帐户**，范围到一个 OU；授予 `servicePrincipalName` 对用户对象的读写权限使用 **ADSI Edit**，而不是 ADUC 委托向导（它过滤掉该属性）——这是最常见的失败原因。
4. **在 RDS 和域控制器之间打开 AD 端口：DNS 53、Kerberos 88 和 464、LDAP 389 和 3268，以及 RPC 范围 49152–65535。** 缺少 RPC 范围是间歇性加入失败的首要原因。将时钟偏移保持在 5 分钟以内。
5. **RDS 主用户是一个本地帐户，它无法获得 Kerberos 票据。** AD 用户需要 `kinit` 加上一个 `GRANT CONNECT`。Kerberos JDBC 使用 `securityMechanism=11` 和一个**特定于区域的 PEM** 通过 `sslCertLocation`（永远不要使用 `global-bundle.pem`）。
6. **引用自管理的 AD 博客和 [ad-kerberos.md](references/ad-kerberos.md)**；用 `describe-db-instances ... DomainMemberships` 显示 `Status: joined` 来验证。

## 故障排除

| 错误 | 原因 | 修复 |
|---|---|---|
| `SQL30082N` | 密码在 Secrets Manager 中旋转 | 运行 `db2_use <instance-id>`——帮助程序重新获取当前密码并重写 `~/.db2env`。 |
| `SQL1531N` | DSN 尚未缓存 | `db2 terminate` 以清除，然后重试；如果仍然失败，重新运行 [db2client-configure.sh](scripts/db2client-configure.sh)。 |
| `SQL01013N` / TCP 超时 | 安全组阻止 50000/50443 | 检查 SG 入站规则——将客户端的 SG 添加到 TCP 50000（明文）或 50443（SSL）。 |
| GSKit / SSL 证书错误 | RDS 证书包缺失或 RSA 证书不是第一个 | 从 RDS 信任存储重新下载 `<region>-bundle.pem` 并重新运行 `db2client-configure.sh`。 |
| 对 RDSADMIN 调用访问被拒绝 | IAM 角色缺少 `S3_INTEGRATION` 功能 | `aws rds add-role-to-db-instance --feature-name S3_INTEGRATION --role-arn <role-arn> --db-instance-identifier <id>`。 |
| 恢复失败，错误为 "database in rollforward pending" | ONLINE 恢复模式将数据库置于回滚状态 | 调用每个存档日志的 `rdsadmin.rollforward_database`，然后 `rdsadmin.complete_rollforward`。 |
| 备用副本创建失败 | 缺少先决条件 | 验证：源实例上启用自动备份、DR 区域中的自定义参数组、多区域 KMS 密钥、没有挂起的 `rdsadmin` 任务、所有数据库处于 active 状态。 |
| AD 域加入 `Status` 不是 `joined` | RPC 端口范围被阻止、密钥格式错误或 SPN 属性缺失 | 打开 RDS 和 DC 之间的 RPC 49152–65535，确认密钥用户是 sAMAccountName 而没有 `DOMAIN\` 前缀，并通过 ADSI Edit 授予 `servicePrincipalName` 对用户对象的读写权限——参见 [ad-kerberos.md](references/ad-kerberos.md)。 |
| `import-key-material` 失败——令牌过期 | 导入令牌比 24 小时旧 | 重新运行 `get-parameters-for-import` 以获取新的令牌和包装密钥，使用 `openssl` 重新包装材料，然后重试导入——参见 [byok-kms.md](references/BYOK-KMS.md)。 |
| 从 RDS API 源头的限制 | 超出 API 请求速率 | 指数退避和抖动；批量操作；检查服务配额。 |

## 安全注意事项

在建议任何生产 RDS for Db2 部署时，显示这些控制。它们综合了子技能参考中涵盖的安全指南。

- **静态加密和传输加密**——始终使用 `--storage-encrypted` 创建实例；对于密钥所有权和合规性，使用客户管理的 KMS 密钥（BYOK），对于灾难恢复，使用多区域密钥。强制执行每个连接的 TLS（端口 50443、`<region>-bundle.pem`）；永远不要以明文连接到生产环境。参见 [byok-kms.md](references/byok-kms.md) 和 [connectivity-tls.md](references/connectivity-tls.md)。 (指南 1)
- **最小权限 IAM** — 使用 [minimum-iam.md](references/minimum-iam.md) 中的作用域策略和信任策略；永远不要附加 `*FullAccess` 管理策略。作用域 `iam:PassRole` 和 ARN-模式支持资源级权限的每个可变语句。 (指南 5)
- **网络隔离** — 将实例保留在私有子网中，限制安全组仅限于应用程序/源 SG（永远不要使用 `0.0.0.0/0`），并使用 VPC 端点进行 S3/SSM/Secrets Manager，以便流量保持在公共互联网之外。参见 [colocation.md](references/colocation.md)。 (指南 5)
- **审计日志和监控** — 启用 Db2 审计到 S3 ([db2-audit.md](references/db2-audit.md))、RDS 增强监控和 CloudTrail for RDS/KMS/Secrets Manager API 调用。失败登录和配置更改时触发警报。 (指南 12)
- **密钥旋转** — 使用 `--manage-master-user-password` 提供以使 RDS 在 Secrets Manager 中存储和旋转主密码；永远不要嵌入明文密码。旋转后，使用 `db2_use <instance-id>` 刷新客户端。 (指南 13)
- **备份加密和保留** — 设置备份保留期，使用您的 KMS 密钥加密自动和手动快照，并将 S3 桶加密加上生命周期/保留，任何 Db2 审计或备份桶。 (指南 13)

## 其他资源

### 范围内文档和博客

- AWS 文档 — RDS for Db2: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_RDSDb2.html
- AWS 文档 — RDS for Db2 IAM 权限: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.html
- AWS 文档 — RDS for Db2 Kerberos 身份验证: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/db2-kerberos.html
- 博客 — 从 CloudShell 连接到 RDS for Db2: https://aws.amazon.com/blogs/database/connect-to-amazon-rds-for-db2-using-aws-cloudshell/
- 博客 — 将自管理的 Db2 Linux 恢复到 RDS for Db2: https://aws.amazon.com/blogs/database/restore-self-managed-db2-linux-databases-in-amazon-rds-for-db2/
- 博客 — 使用 IBM Q Replication 从 AIX/Windows 到 RDS for Db2 的近乎零停机时间迁移: https://aws.amazon.com/blogs/database/near-zero-downtime-migrations-from-self-managed-db2-on-aix-or-windows-to-amazon-rds-for-db2-using-ibm-q-replication/
- 博客 — 跨区域备用副本: https://aws.amazon.com/blogs/database/configure-amazon-rds-for-db2-standby-replicas-for-high-availability-and-faster-disaster-recovery/
- 博客 — 主机 DDL 转换（z/OS 到 RDS for Db2）: https://aws.amazon.com/blogs/database/migrating-tables-from-ibm-db2-for-z-os-to-amazon-rds-for-db2/
- 博客 — 主机迁移的代码页和排序规则: https://aws.amazon.com/blogs/database/choosing-the-right-code-page-and-collation-for-migration-from-mainframe-db2-to-amazon-rds-for-db2/
- 博客 — 带你自己的客户管理 KMS 密钥 for RDS for Db2 (DBBLOG-5188): https://aws.amazon.com/blogs/database/bring-your-own-key-to-amazon-rds-for-db2-with-a-customer-managed-kms-key/
- 博客 — 在 RDS for Db2 上使用自管理的 Active Directory 与 Kerberos: https://aws.amazon.com/blogs/database/use-kerberos-authentication-with-a-self-managed-active-directory-for-amazon-rds-for-db2/

### 相关主题（引用资源，尚未路由的子技能）

这些相邻主题在此迭代中没有被扩展为路由参考。每个主题都可以通过引用资源发现。

- RDS for Db2 的反向日志传输 (DBBLOG-5352): https://aws.amazon.com/blogs/database/implement-reverse-log-shipping-for-amazon-rds-for-db2/
- Multi-account 连接性: 工作区源 `04-db2-client/RDS-Db2-Multiple-Account-Connectivity/`
- Terraform 提供程序: 工作区源 `04-db2-client/RDS-Db2-Terraform/`
- CIS 合规性: 工作区源 `04-db2-client/CIS-Compliance/`
- db2mon 监控: 工作区源 `04-db2-client/db2mon_RDS/`
- 压缩节省: 工作区源 `04-db2-client/Compression-Savings/`
- 迁移先决条件检查 (DBBLOG-5048): https://aws.amazon.com/blogs/database/migrate-from-ibm-db2-to-amazon-rds-for-db2-using-a-migration-prerequisite-check/
- 从 S3 加载: 工作区源 `04-db2-client/load-from-s3/`
- 示例 Java 存储过程: 工作区源 `04-db2-client/sample-java-sp/`

### 博客目录

已发布的 RDS for Db2 博客和示例工具的权威列表维护在 https://github.com/aws-samples/sample-rds-db2-tools/tree/main——咨询它以获取当前博客文章和配套代码。

- 相关技能（从 Db2 LUW 迁移到 PostgreSQL）：`rds-postgres-migration`（如果存在于语料库中）。

## 从 aws-database-selection 的交接

此技能可以直接调用，或者在 `aws-database-selection` 父技能运行要求访谈并生成 `requirements.json` 资产后进入。当你在最近的对话中看到一个用反引号括起来的路径匹配 `aws_dbs_requirements/*/requirements.json` 时，请按照 `aws-database-selection/references/handoff-contract.md` 中的条目协议：

1. 使用 `file_read` 读取该资产。
2. 使用 `aws-database-selection/references/workload-primary-artifact.schema.json` 验证它。如果格式不正确或无法读取，告诉用户并继续执行而无需它。
3. 用一到两句话承认相关内容，引用来自资产的高级事实（主导形状、硬约束、迁移上下文）——不要逐字重复整个资产。
4. 范围检查：此技能的范围是 Amazon RDS for Db2——迁移从 Db2 z/OS 或 LUW、HADR、备用副本、SQL PL 例程、Q Replication 切换。如果资产的 `workload_primaries.dominant_shapes` 或 `migration_context` 与此范围不匹配，按照手交合同发出弱反压：建议 `amazon-aurora` 用于从 Db2 重构到 PostgreSQL，或者如果 Db2 不是源，则返回到 `aws-database-selection`。不要默默地使用资产。
5. 执行此技能的本地工作流，并在建议中引用资产路径作为证据，当建议基于要求时。

父 `aws-database-selection` 技能消费的经过策划的 RDS-for-Db2 选择事实存储在 `assets/selection-knowledge-input.json`（具有人类可读的伴侣 `assets/selection-knowledge-input.md`）。这些捕获了范围内的源迁移场景、硬约束、HA/DR 选项和安全领域，以结构化、可重用的形式——当你需要策划的选择视图而不是重新推导它时，请阅读它们。

此技能的所有用户界面输出都遵循手交合同中定义的 markdown-primitives-only 格式约定：粗体标签、用反引号表示路径和枚举值、使用项目符号表示替代方案，不使用 ASCII 艺术或框绘图字符。
