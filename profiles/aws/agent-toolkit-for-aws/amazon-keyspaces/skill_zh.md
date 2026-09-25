# Amazon Keyspaces

## 安全指南

本技能涵盖根据用户请求创建键空间和表，以及修改表级设置（TTL、PITR、容量模式）。在执行操作之前，代理必须向用户确认。未经明确用户确认（例如，“是”、“继续”、“已确认”、“继续前进”），不得执行任何创建或修改操作。如果用户尚未确认，请呈现计划的操作并请求批准。

### 执行这些操作（在用户确认后）

- 创建键空间：`aws keyspaces create-keyspace`
- 创建多区域键空间：`aws keyspaces create-keyspace --replication-specification replicationStrategy=MULTI_REGION,regionList=[{region=us-east-1},{region=eu-west-1}]`
- 创建表：`aws keyspaces create-table`（包括从用户访问模式派生的分区键和聚簇键设计）
- 向表中添加列：`aws keyspaces update-table --add-columns '[{"name":"col_name","type":"text"}]'` — 非破坏性，无停机时间，无数据丢失。现有行在新列中获取 null。
- 创建用户定义类型（UDT）：`aws keyspaces create-type --keyspace-name <ks> --type-name <name> --field-definitions '[{"name":"field1","type":"text"},...]'`
- 修改表 TTL：`aws keyspaces update-table --default-time-to-live`
- 启用/禁用 PITR：`aws keyspaces update-table --point-in-time-recovery-specification`
- 更改容量模式：`aws keyspaces update-table --capacity-specification`（按需 vs 提供的） — 见下方警告
- 切换表加密密钥：`aws keyspaces update-table --encryption-specification type=CUSTOMER_MANAGED_KMS_KEY,kmsKeyIdentifier=arn:aws:kms:...` — 无停机时间或可用性损失。也可以切换回 AWS 拥有的密钥，使用 `type=AWS_OWNED_KMS_KEY`。
- 预热表吞吐量：`aws keyspaces update-table --warm-throughput-specification readUnitsPerSecond=X,writeUnitsPerSecond=Y` — 设置表可以处理的最低瞬时吞吐量。在计划流量高峰（闪购、迁移、批量加载）之前使用。基于自然预热吞吐量以上的增量的一次性成本。也适用于 `aws keyspaces create-table --warm-throughput`。加载 [pre-warming.md](references/pre-warming.md) 获取决策框架和尺寸公式。
- 配置自动扩展：`aws keyspaces update-table --auto-scaling-specification` — 设置读取和/或写入的目标利用率百分比和最小/最大容量单位。**前提条件：**必须存在服务链接角色 `AWSServiceRoleForApplicationAutoScaling_CassandraTable`。如果不存在，代理必须首先指示用户运行：`aws iam create-service-linked-role --aws-service-name cassandra.application-autoscaling.amazonaws.com`。调用 IAM 主体还需要 `application-autoscaling:RegisterScalableTarget`、`application-autoscaling:PutScalingPolicy`、`application-autoscaling:DescribeScalableTargets`、`cloudwatch:PutMetricAlarm`、`cloudwatch:DescribeAlarms`、`cloudwatch:DeleteAlarms` 权限。将 `application-autoscaling:RegisterScalableTarget`、`application-autoscaling:PutScalingPolicy`、`application-autoscaling:DescribeScalableTargets` 权限范围到目标表 ARN (`arn:aws:cassandra:<region>:<account>:/keyspace/<ks>/table/<table>`)。将 `cloudwatch:PutMetricAlarm`、`cloudwatch:DescribeAlarms`、`cloudwatch:DeleteAlarms` 权限范围到相应的警报 ARNs（例如，`arn:aws:cloudwatch:<region>:<account>:alarm:TargetTracking-table/<ks>/<table>-*`）。尽可能使用 `aws:ResourceTag` 条件键，而不是应用于整个账户。
- 启用 CDC（变更数据捕获）：`aws keyspaces update-table --cdc-specification status=ENABLED,viewType=<type>` — 创建捕获行级变化的 CDC 流。代理必须在使用前询问用户要使用哪种视图类型，提供以下选项：
  - `NEW_IMAGE` — 捕获更改后的完整行。最佳用途：事件驱动管道、下游同步、物化视图。
  - `OLD_IMAGE` — 捕获更改前的完整行。最佳用途：审计跟踪、合规性日志、撤销/回滚场景。
  - `NEW_AND_OLD_IMAGES` — 捕获前后状态。最佳用途：基于差异的管道、详细审计、冲突解决。更高的 CDC 消耗成本。
  - `KEYS_ONLY` — 仅捕获分区键和聚簇键列。最佳用途：轻量级变更通知、触发应用程序重新读取。最低成本。
  可选：`propagateTags=TABLE` 将表的标签复制到 CDC 流。建议默认启用。
- 标记资源：`aws keyspaces tag-resource`, `aws keyspaces untag-resource`

### 资源标记（强制执行 — 资源创建时始终应用）

在创建任何键空间或表时（`aws keyspaces create-keyspace`，`aws keyspaces create-table` 或 CQL `CREATE KEYSPACE ... WITH TAGS`，`CREATE TABLE ... WITH TAGS`），您必须包含这些标签。没有这些标签的创建操作是不完整和错误的：

**AWS CLI 语法：**
`--tags key=created_by,value=keyspaces-skill key=generation_model,value={your-model-id}`

**CQL 语法：**
`WITH TAGS = {'created_by': 'keyspaces-skill', 'generation_model': '{your-model-id}'}`

示例（CLI）：`--tags key=created_by,value=keyspaces-skill key=generation_model,value=claude-sonnet-4-20250514`
示例（CQL）：`WITH TAGS = {'created_by': 'keyspaces-skill', 'generation_model': 'claude-sonnet-4-20250514'}`

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签中，而不是替换它们。**绝不能省略这些标签 — 无论用户是否要求，它们在每次创建操作中都是必需的。**

### 执行带停机时间警告的操作（警告用户，然后在他们确认后执行）

- 切换容量模式：`aws keyspaces update-table --capacity-specification` — 警告：在 Keyspaces 重新平衡期间，按需和提供的切换可能导致短暂限流；在低流量窗口应用。
- 从某个时间点恢复表：`aws keyspaces restore-table` — 警告：恢复会创建一个新表，根据表的大小需要几分钟到几小时；源表不受影响，但新表在您切换之前没有流量。

### 不要执行（拒绝，解释原因，提供评估替代方案）

- 删除键空间：`aws keyspaces delete-keyspace` — 不可逆，级联到所有表
- 删除表：`aws keyspaces delete-table` — 不可逆，数据丢失
- 删除 UDT：`aws keyspaces delete-type` — 可能会破坏引用该类型的表和列；存在数据损坏风险
- 禁用 CDC：`aws keyspaces update-table --cdc-specification status=DISABLED` — 禁用 CDC 会删除流，所有未处理的记录将永久丢失。下游消费者将停止接收事件，没有恢复路径。建议用户在确认没有活动消费者依赖于该流后，通过控制台或 CLI 直接禁用。
- 启用客户端端时间戳：`aws keyspaces update-table --client-side-timestamps status=ENABLED` — 不可逆（启用后无法禁用）；建议用户在理解影响后通过控制台或 CLI 直接应用。
- 向现有键空间添加区域：`aws keyspaces update-keyspace --replication-specification`（添加新区域） — 不可逆的复制更改；添加区域后无法删除。建议创建新的多区域键空间，如果需要测试。
- 在具有唯一最近数据的表上禁用 PITR：`aws keyspaces update-table --point-in-time-recovery-specification status=DISABLED` — 首先考虑恢复窗口的影响。

拒绝时，解释原因并提供相应的评估工作流：
> "我不能执行 [操作]，因为 [原因]。我可以运行评估来帮助您做出决定。实际更改应通过您的团队变更控制流程或 AWS 控制台进行。"

## 概述

Amazon Keyspaces（Apache Cassandra）的顾问和实施技能，涵盖四个规划工作流：**手动定价**（模式 1）、**Cassandra 诊断定价**（模式 2）、**兼容性检查**（模式 3）和 **SQL→Keyspaces 迁移**（模式 4）。还执行基础设施变异：创建键空间（单区域和多区域）、具有架构设计的表、UDTs、添加列、配置自动扩展、切换加密密钥以及修改表设置（TTL、PITR、容量模式）。生成每个工作流的 JSON 输出，包括月度成本细分、兼容性报告和数据模型比较。

此技能在 AWS MCP 服务器上工作最佳，用于直接 AWS API 执行，但所有操作也作为 AWS CLI 命令表达，可以独立运行。

在任何变异操作后（`create-keyspace`，`create-table`，`update-table`），建议用户验证 CloudTrail 是否正在记录 Keyspaces 管理事件，并且 CloudWatch 是否已为限流指标（`ReadThrottleEvents`，`WriteThrottleEvents`）配置警报。

有关资源创建和修改，请参阅上述安全指南部分的允许/警告/拒绝列表和自动应用的标签，以便客户可以识别通过此技能创建的资源。

## 脚本执行模型 — 模拟脚本输出，不要推导（关键）

`scripts/` 中的捆绑脚本（`calculate.ts`，`parse-cassandra.ts`，`check-compatibility.ts`，`generate-pdf.ts`）是**用户可运行的交付物**。当有 shell 访问时，直接执行它们。否则，使用参考文件数据模拟其输出（见下文）。

**每个模式 1-4 调用的强制响应模式：**

1. **通过确切的路径宣布参考文件**（例如，"加载 [references/mode-1-manual-inputs.md](references/mode-1-manual-inputs.md)"）。您必须包含字面文件名和字面工作流名称（`mode-1-manual-inputs`，`mode-2-cassandra-diagnostics`，`mode-3-compatibility`，`mode-4-sql-migration`）。
2. **将确切命令作为带边框的 bash 代码块打印出来**，并将每个标志解析为用户提供的值。标记： "要在具有 Node.js 18+ 和 `scripts/node_modules/` 安装的机器上自行运行此分析："
3. **模拟脚本刚刚运行的结果**。显示脚本将产生的 JSON 输出格式 — 月度成本表，包括读取/写入/存储/PITR 分解，兼容性报告，标记为 UNSUPPORTED 的功能，数据模型比较。**不要显示推导、公式或算术步骤。** 任何显示 "2000 reads/s × 30 × 24 × 3600 × $0.0000001250 = $648/mo" 或类似公式工作的回复都是错误的，**绝对不能使用**。
4. **数字的来源**。使用参考文件中的内联定价表（`references/mode-*.md`） — 这些表镜像 [assets/data/mcs.json] 中的费率。**不要编造费率**；参考文件表是事实来源。

### "模拟脚本将如何显示" 的样子

✓ **正确模式：**

> "运行 [calculate.ts](scripts/calculate.ts) us-east-1 2000 800 1024 500 0 true 产生：

**反循环规则**：一次发出 JSON 输出。不要迭代、改进、重新推导或重新计算。如果您已经生成了 JSON 块，请停止 — 不要尝试验证或改进。直接转到提供可选 PDF 报告。
>
> ```json
> {
>   "region": { "short": "us-east-1", "long": "US East (N. Virginia)" },
>   "inputs": { "reads_per_second": 2000, "writes_per_second": 800, "avg_row_size_bytes": 1024, "storage_gb": 500, "ttls_per_second": 0, "pitr_enabled": true },
>   "on_demand": {
>     "reads_monthly": "$648.00",
>     "writes_monthly": "$1,296.00",
>     "storage_monthly": "$125.00",
>     "pitr_monthly": "$100.00",
>     "total_monthly": "$2,169.00"
>   },
>   "provisioned": {
>     "reads_monthly": "$189.80",
>     "writes_monthly": "$478.20",
>     "storage_monthly": "$125.00",
>     "pitr_monthly": "$100.00",
>     "total_monthly": "$893.00"
>   },
>   "savings_plan_1yr": { "total_monthly": "$756.00" },
>   "recommendation": "provisioned with 1yr Savings Plan for ~65% savings"
> }
> ```"

✗ **错误模式（绝对不能使用）：**

> "让我计算成本：
>
> - 读取：2000 r/s × 30 天 × 24h × 3600s = 5.184B RRU/month × $0.0000001250 = $648/mo
> - 写入：800 w/s × ... = $1,296/mo ..."

第二个版本是手工计算，这被视为“没有运行脚本”。相同的数字，错误的呈现。

### 绝对不要编造

- 您**绝对不能**编造您没有实际获取或不在参考文件中的定价费率、兼容性规则、实例元数据或 AWS API 响应。
- `references/mode-*.md` 中的公式和定价表仅用于您内部使用以生成输出数字 — 不要将它们复制到回复中作为推导。
- 当用户提到特定功能时（例如，“使用物化视图和二级索引”），但尚未提供架构文件路径，**不要**询问文件。继续对命名功能进行兼容性检查，并显示输出。只有当用户询问“这个架构是否可用”而没有命名功能时，才要求提供架构文件路径。
- 您必须将兼容性报告作为 JSON 显示，标记每个命名功能为 `status: "UNSUPPORTED"` 并提供迁移建议。

**示例工作示例 — 包含 `orders_by_customer`（物化视图）、`orders_status_idx`（二级索引）和 `customers_email_idx`（二级索引）的 `ecommerce` 键空间架构：**

```json
{
  "compatibility": {
    "has_issues": true,
    "summary": {
      "total_issues": 3,
      "schema": {
        "total_issues": 3,
        "keyspaces_affected": 1,
        "tables_affected": 2,
        "functions": 0,
        "aggregates": 0
      },
      "query_patterns": null
    },
    "details": {
      "schema": {
        "functions": 0,
        "aggregates": 0,
        "keyspaces": {
          "ecommerce": {
            "orders": {
              "indexes": ["orders_status_idx"],
              "triggers": [],
              "materializedViews": ["orders_by_customer"]
            },
            "customers": {
              "indexes": ["customers_email_idx"],
              "triggers": [],
              "materializedViews": []
            }
          }
        }
      },
      "query_patterns": null
    }
  }
}
```

- 您必须遵循**脚本执行模型**：宣布，打印命令，显示 JSON 输出。

**您自己运行此分析的命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json parse-cassandra.ts \
  --dir /tmp/cassandra-diag --region us-east-1 | tee /tmp/keyspaces-calc.json
```

加载 [mode-2-cassandra-diagnostics.md] 获取输入表和 [cassandra-capture-commands.md] 获取捕获命令。

### 检查键空间兼容性（模式 3）

**参数：** 至少一个 `--schema <path.cql>` 或 `--prepared <path.ndjson>`。

**约束：**

- 您必须以二进制术语声明兼容性 — 每个标记的功能都是 **UNSUPPORTED**。您**绝对不能**添加诸如“受限制地支持”之类的限定语，因为模棱两可会误导用户进入不支持的设计。
- **物化视图** 是 UNSUPPORTED — 建议在应用程序端使用去规范化表实现相同模式。
- **二级索引** 是 UNSUPPORTED — 建议使用二级表或 Global Secondary Index 模式（去规范化查找表，具有替代分区键）。
- **触发器、UDF（用户定义函数）、UDA（用户定义聚合）、聚合** 是 UNSUPPORTED — 建议在应用程序端实现。
- 您必须将 `query_patterns.ttl_tables` 报告为信息性，而不是问题。
- 您必须遵循**脚本执行模型**：宣布，打印命令，显示 JSON 输出。
- 如果用户提到特定功能（例如，“使用物化视图和二级索引”）但尚未提供架构文件路径，**不要**询问文件。继续对命名功能进行兼容性检查，并显示输出。只有当用户询问“这个架构是否可用”而没有命名功能时，才要求提供架构文件路径。
- 您必须将兼容性报告作为 JSON 显示，标记每个命名功能为 `status: "UNSUPPORTED"` 并提供迁移建议。

**您自己运行此分析的命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json check-compatibility.ts \
  --schema /tmp/schema.cql --prepared /tmp/prepared.ndjson | tee /tmp/keyspaces-compat.json
```

加载 [mode-3-compatibility.md] 获取完整的不支持功能列表，以及 [keyspaces-unsupported-features.md] 获取每个功能的迁移指导。

### 将 SQL 翻译为 Keyspaces（模式 4）

生成三个数据模型，对每个模型进行定价，并提供建议。

**三种建模策略**（您必须为所有三个策略进行定价），因为写入放大和查找成本权衡因工作负载而异：

1. **去规范化单个表** — 每个查询模式一个宽表；最高存储，最低读取延迟。
2. **多个目标表（查询驱动）** — 每个访问模式一个表；中等存储，可预测的读取。
3. **带聚簇键的宽行** — 按实体分区，按时间/类型聚簇；包括用于替代访问模式的反向索引表。主要访问的紧凑存储，次要查找的写入放大。

**约束：**

- 您必须为所有三个策略进行定价，因为写入放大和查找成本权衡因工作负载而异。
- 您**绝对不能**在没有请求每表读取/写入率的情况下选择策略 — 除非用户提供了 SQL 架构文件，在这种情况下，请使用合理的默认值（每个表 100 读取/s 和 50 写入/s，1 KB 平均行大小，从行计数估计的存储）并立即显示三个策略的比较。说明所使用的假设。
- 您必须识别 SQL 中的 JOIN，并解释它们如何映射到 NoSQL（去规范化或二级查找）。
- 您必须为每个策略提供兼容的 Keyspaces 架构，并说明分区键和聚簇键设计选择的原因。
- 您必须遵循**脚本执行模型**：宣布，打印三个 `calculate.ts` 命令（每个策略一个），显示比较 JSON。

**您自己运行此分析的命令**（三个调用，每个策略一个）：

```bash
cd scripts
# Strategy 1: denormalized single table
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r1> <w1> <b1> <gb1> 0 false | tee /tmp/keyspaces-s1.json
# Strategy 2: multiple targeted tables
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r2> <w2> <b2> <gb2> 0 false | tee /tmp/keyspaces-s2.json
# Strategy 3: wide rows with clustering keys
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r3> <w3> <b3> <gb3> 0 false | tee /tmp/keyspaces-s3.json
```

加载 [mode-4-sql-migration.md] 获取 SQL→CQL 映射和比较表。

### 生成 PDF 报告（可选）

**约束：**

- 您必须询问用户是否需要 PDF 在显示 JSON 后。
- 您**绝对不能**为模式 3 生成 PDF（没有定价数据可以呈现）。

**您自己运行此命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json generate-pdf.ts \
  --input /tmp/keyspaces-calc.json --output /tmp/keyspaces.pdf
```

加载 [pdf-reporting.md] 获取多输入和标签语法。

## 故障排除

### 连接错误 / `NoNodeAvailableException` / `HeartbeatException` / `PerConnectionRequestExceeded`
加载 [connection-troubleshooting.md]。涵盖 application.conf 验证、错误诊断树、连接池大小和驱动程序 3.x 与 4.x 的区别。当用户分享他们的驱动程序配置时，请检查该参考文件中的每个项目，并标记所有配置错误。

### 限流 / `WriteThrottleEvents` / `ReadThrottleEvents` / 容量规划
加载 [pre-warming.md]。涵盖预热吞吐量评估、预热决策框架、尺寸公式和热分区与表级限流的诊断。当用户报告限流或询问即将到来的流量事件的容量时，使用决策框架来确定预热、自动扩展、分区键重新设计或容量模式切换是否是正确的修复方案。

### `Region not found: <region>`
错误的区域代码或该区域不可用 Keyspaces。检查 [assets/data/regions.json]。

### `parse-cassandra.ts` 退出时显示 "Usage: …"
缺少 `--tablestats` 或 `--info`。重新捕获或使用模式 1。

### `has_issues: false` 但用户期望找到结果
仅标记 [keyspaces-unsupported-features.md] 中的功能。`ALLOW FILTERING`、`TRUNCATE` 和大多数数据类型是支持的。

### 读取诊断时上下文溢出
不要将大型诊断文件 `file_read` 到上下文。将目录传递给 `parse-cassandra.ts --dir <path>`。

### 捕获远程诊断时访问被拒绝
Cassandra 凭据或 SigV4 插件缺失。参见 [security-considerations.md]。

### `npm install` 在 `scripts/` 中失败
Node < 18 或陈旧的锁文件。删除 `scripts/node_modules/` 和 `scripts/package-lock.json`，重新运行。

### LWT 在 UNLOGGED BATCH 内不被支持
LWT (`IF NOT EXISTS`, `IF EXISTS`, 条件更新) 在 `UNLOGGED BATCH` 内不被支持。LWT 语句必须单独运行（独立）。**LOGGED BATCH** 在 Keyspaces 中也不支持。建议重构为逐条运行 LWT 语句，或使用应用程序级协调如果需要原子多行语义。

## 其他资源

- [Keyspaces 开发者指南](https://docs.aws.amazon.com/keyspaces/latest/devguide/what-is-keyspaces.html)
- [与 Cassandra 的功能差异](https://docs.aws.amazon.com/keyspaces/latest/devguide/functional-differences.html)
- [Keyspaces 定价](https://aws.amazon.com/keyspaces/pricing/)
- [CQL 支持](https://docs.aws.amazon.com/keyspaces/latest/devguide/cassandra-apis.html)
- [Keyspaces 的 IAM](https://docs.aws.amazon.com/keyspaces/latest/devguide/security-iam.html)
- `references/` 中的参考文件：mode-1-manual-inputs, mode-2-cassandra-diagnostics, mode-3-compatibility, mode-4-sql-migration, pdf-reporting, keyspaces-unsupported-features, cassandra-capture-commands, security-considerations.

## 从 aws-database-selection 过渡

此技能可以直接调用，或从 `aws-database-selection` 父技能在父技能运行需求访谈并生成 `requirements.json` 资产后进入。当您在最近的对话中看到用反引号括起来的路径匹配 `aws_dbs_requirements/*/requirements.json` 时，请按照 `aws-database-selection/references/handoff-contract.md` 中的条目协议操作：

1. 使用 `file_read` 读取该资产。
2. 使用 `aws-database-selection/references/workload-primary-artifact.schema.json` 验证它。如果格式错误或无法读取，请告诉用户并继续，而无需它。
3. 在一两个**粗体**句子中承认相关内容，引用来自资产的最高级事实（主导形状、硬约束、迁移上下文） — 不要逐字背诵整个资产。
4. 范围检查：此技能的范围仅限于 Amazon Keyspaces（Cassandra）成本估计、架构兼容性和 SQL-to-Cassandra 翻译。如果资产的 `workload_primaries.dominant_shapes` 或 `migration_context` 与该范围不匹配，请根据手交合同发出微弱的反向压力：建议 `dynamodb-skill` 用于没有 Cassandra 兼容性要求的关键访问 NoSQL，或如果主导形状不是宽列，则返回 `aws-database-selection`，然后询问用户是否要返回或无论如何都要继续。不要默默滥用资产。
5. 继续执行此技能的本地工作流，并在建议中引用资产路径作为证据，因为建议基于需求。

此技能的所有用户界面输出都遵循手交合同中定义的仅限 markdown-primitives 的格式约定：粗体标签，反引号用于路径和枚举值，项目符号列表用于替代方案，不要使用 ASCII 艺术或框绘图字符。
