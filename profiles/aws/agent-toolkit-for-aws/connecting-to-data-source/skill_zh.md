# 连接到数据源

将外部数据源注册到 AWS Glue 中，以便下游技能（数据湖导入）可以从其中移动数据。Glue 连接存储一个数据源的网络安全配置、驱动程序和凭证引用。每个数据源创建一次，可在多个作业中重用。

## 哲学思想

**连接是一个命名管道，而不是一个管道。** 此技能生成一个经过测试、可重用的 Glue 连接。它不会移动数据。

## 常见任务

连接时必须使用 AWS MCP 服务器工具执行命令——它们提供验证、沙盒执行和审计日志。如果 MCP 不可用，则仅回退到 AWS CLI。执行每个步骤之前必须向用户解释。

## 工作流程

### 1. 验证依赖项和上下文

- 必须检查 AWS MCP 工具或 AWS CLI 是否可用，并在缺失时通知用户
- 必须确认目标 AWS 区域，并使用 `aws sts get-caller-identity` 验证凭证

### 2. 对源进行分类

询问用户他们想要连接到哪种类型的源，或根据提示推断：

| 用户说... | 源类型 | 连接类型 | 参考 |
|---|---|---|---|
| "Oracle"、"SQL Server"、"Postgres"、"MySQL"、"RDS <引擎>" | JDBC 数据库 | `JDBC` | [jdbc-setup.md](references/jdbc-setup.md) |
| "Redshift"、"我的集群"、"我在 AWS 上的数据仓库" | Redshift | `JDBC` | [jdbc-setup.md](references/jdbc-setup.md) (Redshift 部分) |
| "Snowflake" | Snowflake | `SNOWFLAKE` | [snowflake-setup.md](references/snowflake-setup.md) |
| "BigQuery"、"Google analytics warehouse" | BigQuery | `BIGQUERY` | [bigquery-setup.md](references/bigquery-setup.md) |

如果用户命名为 DynamoDB 或本地文件，则停止并告诉他们：DynamoDB 由 Glue 直接读取，无需连接，本地文件属于 ingesting-into-data-lake 技能的本地上传工作流。

### 3. 从用户那里收集连接提示

必须要求用户提供提示——不要猜测。

**对于所有源：**

- 期望的连接名称（小写，连字符：`oracle-prod-sales`、`snowflake-analytics`）
- 现有的 Secrets Manager 密钥，或创建一个
- 源是否可以从 Glue VPC 访问（相同、对等、VPN、Direct Connect）

**JDBC：** 主机名/端点、端口、数据库、是否为 RDS/Aurora/自管理、IAM DB 身份验证是否启用（Aurora/RDS MySQL/Postgres）、是否需要 SSL。

**Snowflake：** 账户标识符、仓库、角色、默认数据库、身份验证（密码、密钥对、OAuth）。

**BigQuery：** GCP 项目 ID、位置、是否已提供服务账户 JSON。

### 4. 发现现有连接和候选源

在创建之前检查一下。

**现有的 Glue 连接：**

```bash
aws glue get-connections --filter ConnectionType=<TYPE> --region <REGION>
```

如果存在合适的连接，请确认并跳到步骤 7。

**账户中的候选源**（仅限 JDBC/Redshift）：

- RDS：`aws rds describe-db-instances`
- Aurora：`aws rds describe-db-clusters`
- Redshift：`aws redshift describe-clusters`

向用户展示候选源；让他们选择。参见 [discovery.md](references/discovery.md)。

### 5. 注册凭证

必须鼓励使用 AWS Secrets Manager 而不是明文密码。在支持的地方应优先选择 IAM 数据库身份验证（Aurora/RDS MySQL 和 PostgreSQL、Redshift）。参见 [credential-security.md](references/credential-security.md)。

- 创建新的 Secrets Manager 密钥之前必须与用户确认
- 绝不能将明文凭证写入聊天或日志
- 对于 IAM DB 身份验证，不需要密钥

### 6. 创建 Glue 连接

遵循源特定的参考以获取连接属性：

```bash
aws glue create-connection --connection-input '<JSON>' --region <REGION>
```

私有源需要 `PhysicalConnectionRequirements`（SubnetId、SecurityGroupIdList、AvailabilityZone）。参见 [network-setup.md](references/network-setup.md)。

### 7. 测试连接

必须测试后再交接。测试是两阶段的：快速 API 检查，然后是引擎级验证。

#### 阶段 A：Glue TestConnection（网络和凭证合理性检查）

```bash
aws glue test-connection --connection-name <NAME> --region <REGION>
```

这验证了 Glue 是否可以到达源并验证凭证。它不能证明连接与用户计划使用的查询引擎端到端工作。

#### 阶段 B：引擎级验证

TestConnection 通过后，通过运行一个最小查询来验证连接是否与用户预期的引擎工作：

- **Glue ETL（默认）：** 运行一个读取一行数据的烟雾测试 Glue 作业。参见 [troubleshooting.md](references/troubleshooting.md)。
- **Athena：** 如果用户计划通过 Athena 使用联邦连接进行查询，运行 `SELECT 1` 通过 Athena 连接以确认基于 Lambda 的连接器可以到达源。
- **Glue Crawler：** 如果用户计划爬取源，在单个表上运行一个测试爬取。

阶段 B 捕获 TestConnection 遗漏的问题：作业运行时的驱动程序兼容性、目录配置、Spark 级别的序列化、特定于引擎的身份验证流程（例如，Snowflake `SNOWFLAKE` 类型在 ETL 中工作，但在 JDBC 爬取器中不工作）。

在两个阶段都成功后，告诉用户连接名称已准备好用于 `ingesting-into-data-lake`。在任一阶段失败时，进入步骤 8。

### 8. 故障排除（仅在测试失败时）

按顺序诊断：网络、凭证、驱动程序。参见 [troubleshooting.md](references/troubleshooting.md)。

**约束：**

- 在归咎于凭证之前，必须检查 VPC 路由、安全组和 S3 VPC 端点
- 必须验证 Glue 角色可以读取 Secrets Manager 密钥
- 在未经用户确认的情况下，绝不能旋转凭证

## 参数路由

- 无参数：交互式地执行步骤 1-7
- 源类型关键字（例如，`snowflake`、`oracle`）：跳到步骤 2 并预填类型
- 现有连接名称：跳到步骤 7（测试），如果失败则跳到步骤 8
- 主机名或 RDS 端点：跳到步骤 4 并预填候选源

## 注意事项

- Glue 的 `SNOWFLAKE` 连接类型与 Snowflake 配置的 `JDBC` 不同。对于 Spark ETL 作业，必须使用 `SNOWFLAKE`；不要使用 JDBC。
- 连接名称是不可变的。请谨慎选择。
- `PhysicalConnectionRequirements.AvailabilityZone` 必须与子网的 AZ 匹配，否则连接在作业运行时失败，而不是在创建时。
- IAM 数据库身份验证令牌在 15 分钟内过期。Glue 作业在每次连接时生成一个新令牌；不要缓存。
- 在私有源连接使用的 VPC 中必须存在 S3 VPC 网关端点。没有它，Glue 作业无法读取其脚本或将结果写入 S3。

## 故障排除

| 错误 | 可能的原因 | 解决方法 |
|---|---|---|
| `Connect timed out` | VPC 路由、SG 规则或 NAT 网关缺失 | 参见 [troubleshooting.md](references/troubleshooting.md) |
| `Access denied for user` / `ORA-01017` | 凭证错误、Secrets Manager 访问缺失或 IAM DB 身份验证配置错误 | 参见 [troubleshooting.md](references/troubleshooting.md) |
| `No suitable driver found` | 自定义驱动程序 JAR 未设置或类名错误 | 参见 [troubleshooting.md](references/troubleshooting.md) |
| `SSL handshake failed` | Glue 和源之间的 `JDBC_ENFORCE_SSL` 不匹配 | 参见 [troubleshooting.md](references/troubleshooting.md) |
| `UnableToFindVpcEndpoint` | S3 VPC 端点缺失 | 在连接的 VPC 中创建 S3 网关端点 |

## 参考

- [jdbc-setup.md](references/jdbc-setup.md) -- Oracle、SQL Server、PostgreSQL、MySQL、RDS、Redshift
- [snowflake-setup.md](references/snowflake-setup.md) -- Glue `SNOWFLAKE` 类型、身份验证模式
- [bigquery-setup.md](references/bigquery-setup.md) -- Glue `BIGQUERY` 类型、GCP 服务账户
- [discovery.md](references/discovery.md) -- 查找现有连接和候选源
- [credential-security.md](references/credential-security.md) -- Secrets Manager 和 IAM DB 身份验证
- [network-setup.md](references/network-setup.md) -- VPC、子网、安全组、端点
- [troubleshooting.md](references/troubleshooting.md) -- 连接错误和诊断流程
