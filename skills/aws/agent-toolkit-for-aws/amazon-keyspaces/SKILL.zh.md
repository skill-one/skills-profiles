---
name: amazon-keyspaces
description: 提供权威的兼容性检查、价格估算、连接故障排除、预预热指导以及 Amazon Keyspaces（适用于 Apache Cassandra）的基础设施变更。涵盖 LWT/批量操作、二级索引、物化视图、容量模式、TTL、PITR、CDC、自动扩展、多区域 Keyspaces、UDTs、nodetool 诊断解析、SQL-to-Cassandra 迁移以及 Cassandra-to-Keyspaces 迁移场景。如果没有加载此技能，代理经常会提供关于 Keyspaces 功能支持的不完整或不正确的答案。
---

# Amazon Keyspaces

## 安全指南

此技能涵盖根据用户请求创建键空间和表，以及修改表级设置（TTL、PITR、容量模式）。代理在执行前必须向用户确认操作。**禁止**在未经明确用户确认（例如，“是”、“继续”、“已确认”、“继续”）的情况下执行任何创建或修改操作。如果用户未确认，请呈现计划的操作并请求批准。

### 用户确认后执行的操作

- 创建键空间：`aws keyspaces create-keyspace`
- 创建多区域键空间：`aws keyspaces create-keyspace --replication-specification replicationStrategy=MULTI_REGION,regionList=[{region=us-east-1},{region=eu-west-1}]`
- 创建表：`aws keyspaces create-table`（包括根据用户访问模式派生的分区键和聚簇键设计）
- 向表中添加列：`aws keyspaces update-table --add-columns '[{"name":"col_name","type":"text"}]'` — 非破坏性，无停机时间，无数据丢失。现有行在新列中获取 null 值。
- 创建用户定义类型（UDT）：`aws keyspaces create-type --keyspace-name <ks> --type-name <name> --field-definitions '[{"name":"field1","type":"text"},...]'`
- 修改表 TTL：`aws keyspaces update-table --default-time-to-live`
- 启用/禁用 PITR：`aws keyspaces update-table --point-in-time-recovery-specification`
- 更改容量模式：`aws keyspaces update-table --capacity-specification`（按需 vs 预配） — 见下方警告
- 切换表加密密钥：`aws keyspaces update-table --encryption-specification type=CUSTOMER_MANAGED_KMS_KEY,kmsKeyIdentifier=arn:aws:kms:...` — 无停机时间或可用性损失。也可以切换回 AWS 拥有的密钥，使用 `type=AWS_OWNED_KMS_KEY`。
- 预热表吞吐量：`aws keyspaces update-table --warm-throughput-specification readUnitsPerSecond=X,writeUnitsPerSecond=Y` — 设置表可以处理的最低瞬时吞吐量。在计划流量高峰（促销、迁移、批量加载）之前使用。基于高于自然预热吞吐量的增量的一次性成本。也适用于 `aws keyspaces create-table --warm-throughput`。加载 [pre-warming.md](references/pre-warming.md) 获取决策框架和尺寸公式。
- 配置自动扩展：`aws keyspaces update-table --auto-scaling-specification` — 设置读取和/或写入的目标利用率百分比和最小/最大容量单位。**前提条件：**必须存在服务链接角色 `AWSServiceRoleForApplicationAutoScaling_CassandraTable`。如果不存在，代理必须首先指示用户运行：`aws iam create-service-linked-role --aws-service-name cassandra.application-autoscaling.amazonaws.com`。调用 IAM 主体还需要 `application-autoscaling:RegisterScalableTarget`、`application-autoscaling:PutScalingPolicy`、`application-autoscaling:DescribeScalableTargets`、`cloudwatch:PutMetricAlarm`、`cloudwatch:DescribeAlarms`、`cloudwatch:DeleteAlarms` 权限。将 `application-autoscaling:RegisterScalableTarget`、`application-autoscaling:PutScalingPolicy`、`application-autoscaling:DescribeScalableTargets` 权限范围设置为目标表 ARN（`arn:aws:cassandra:<region>:<account>:/keyspace/<ks>/table/<table>`）。将 `cloudwatch:PutMetricAlarm`、`cloudwatch:DescribeAlarms`、`cloudwatch:DeleteAlarms` 权限范围设置为相应的警报 ARN（例如，`arn:aws:cloudwatch:<region>:<account>:alarm:TargetTracking-table/<ks>/<table>-*`）。尽可能使用 `aws:ResourceTag` 条件键，而不是全局应用。
- 启用 CDC（变更数据捕获）：`aws keyspaces update-table --cdc-specification status=ENABLED,viewType=<type>` — 创建捕获行级变更的 CDC 流。代理在启用之前必须询问用户要使用哪种视图类型，提供以下选项：
  - `NEW_IMAGE` — 捕获变更后的完整行。最佳用途：事件驱动管道、下游同步、物化视图。
  - `OLD_IMAGE` — 捕获变更前的完整行。最佳用途：审计跟踪、合规日志、撤销/回滚场景。
  - `NEW_AND_OLD_IMAGES` — 捕获前后状态。最佳用途：基于差异的管道、详细审计、冲突解决。更高的 CDC 消耗成本。
  - `KEYS_ONLY` — 仅捕获分区键和聚簇键列。最佳用途：轻量级变更通知、触发应用程序重新读取。最低成本。
  可选：`propagateTags=TABLE` 将表的标签复制到 CDC 流。建议默认启用。
- 标记资源：`aws keyspaces tag-resource`，`aws keyspaces untag-resource`

### 资源标记（强制执行 — 资源创建时始终应用）

在创建任何键空间或表时（`aws keyspaces create-keyspace`，`aws keyspaces create-table`，或 CQL `CREATE KEYSPACE ... WITH TAGS`，`CREATE TABLE ... WITH TAGS`），您必须包含这些标签。没有这些标签的创建操作是不完整的和错误的：

**AWS CLI 语法：**
`--tags key=created_by,value=keyspaces-skill key=generation_model,value={your-model-id}`

**CQL 语法：**
`WITH TAGS = {'created_by': 'keyspaces-skill', 'generation_model': '{your-model-id}'}`

示例（CLI）：`--tags key=created_by,value=keyspaces-skill key=generation_model,value=claude-sonnet-4-20250514`
示例（CQL）：`WITH TAGS = {'created_by': 'keyspaces-skill', 'generation_model': 'claude-sonnet-4-20250514'}`

即使用户没有提及标记，也请包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签中，而不是替换它们。**永远不要省略这些标签 — 它们在每个创建操作中都是必需的，无论用户是否请求它们。**

### 带停机时间警告的操作（警告用户，确认后执行）

- 切换容量模式：`aws keyspaces update-table --capacity-specification` — 警告：“在按需和预配之间切换可能导致 Keyspaces 在重新平衡时出现短暂限流；在低流量窗口应用。”
- 从某个时间点恢复表：`aws keyspaces restore-table` — 警告：“恢复会创建一个新表，根据表的大小需要几分钟到几小时；源表不受影响，但新表在您切换之前没有流量。”

### 不要执行（拒绝，解释原因，提供评估替代方案）

- 删除键空间：`aws keyspaces delete-keyspace` — 不可逆，级联到所有表
- 删除表：`aws keyspaces delete-table` — 不可逆，数据丢失
- 删除 UDT：`aws keyspaces delete-type` — 可能会破坏引用该类型的表和列；存在数据损坏风险
- 禁用 CDC：`aws keyspaces update-table --cdc-specification status=DISABLED` — 禁用 CDC 会删除流，所有未处理的记录将永久丢失。下游消费者将停止接收事件，没有恢复路径。建议用户通过控制台或 CLI 直接在确认没有活动消费者依赖该流后禁用。
- 启用客户端时间戳：`aws keyspaces update-table --client-side-timestamps status=ENABLED` — 不可逆（一旦启用后无法禁用）；建议用户通过控制台或 CLI 直接在理解影响后应用。
- 向现有键空间添加区域：`aws keyspaces update-keyspace --replication-specification`（添加新区域） — 不可逆的复制更改；一旦添加，无法删除区域。建议创建新的多区域键空间代替，如果需要测试。
- 在具有唯一最近数据的表上禁用 PITR：`aws keyspaces update-table --point-in-time-recovery-specification status=DISABLED` — 首先考虑恢复窗口的影响

拒绝时，请解释原因并提供匹配的评估工作流：
> "我无法执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际更改应通过您团队的变更控制流程或 AWS 控制台进行。"

## 概述

Amazon Keyspaces（Apache Cassandra）的顾问和实施技能，涵盖四个规划工作流：**手动定价**（模式 1）、**Cassandra 诊断定价**（模式 2）、**兼容性检查**（模式 3）和 **SQL→Keyspaces 迁移**（模式 4）。还执行基础设施变异：创建键空间（单区域和多区域）、带模式设计的表、UDTs、添加列、配置自动扩展、切换加密密钥以及修改表设置（TTL、PITR、容量模式）。生成每个工作流的 JSON 输出，包含月度成本明细、兼容性报告和数据模型比较。

此技能与 AWS MCP 服务器配合使用效果最佳，可直接执行 AWS API，但所有操作也作为 AWS CLI 命令表达，可以独立运行。

在任何变异操作（`create-keyspace`，`create-table`，`update-table`）之后，建议用户验证 CloudTrail 是否正在记录 Keyspaces 管理事件，以及 CloudWatch 警报是否已针对限流指标（`ReadThrottleEvents`，`WriteThrottleEvents`）配置。

有关资源创建和修改，请参阅上述安全指南部分的允许/警告/拒绝列表和自动应用的标签，以便客户可以识别通过此技能创建的资源。

## 脚本执行模型 — 模拟脚本输出，不要推导（关键）

捆绑在 `scripts/` 中的脚本（`calculate.ts`，`parse-cassandra.ts`，`check-compatibility.ts`，`generate-pdf.ts`）是**用户可运行的交付物**。当有 shell 访问时，直接执行它们。否则，使用参考文件数据模拟其输出（见下文）。

**每个模式 1-4 调用的强制响应模式：**

1. **通过确切路径宣布参考文件**（例如，"加载 [references/mode-1-manual-inputs.md](references/mode-1-manual-inputs.md)"）。您必须在响应中包含字面文件名和字面工作流名称（`mode-1-manual-inputs`，`mode-2-cassandra-diagnostics`，`mode-3-compatibility`，`mode-4-sql-migration`）。
2. **将确切命令作为带边框的 bash 代码块打印出来**，并将每个标志解析为用户提供的值。标记为："在具有 Node.js 18+ 和 `scripts/node_modules/` 安装的机器上运行此分析的命令（`cd scripts && npm install`）："
3. **将结果呈现为脚本刚刚运行的样子**。显示脚本将产生的 JSON 输出格式 — 月度成本表，包含读取/写入/存储/PITR 分解，兼容性报告，带有 UNSUPPORTED 标记的功能，数据模型比较。**不要**在回复中显示"2000 reads/s × 30 × 24 × 3600 × $0.0000001250 = $648/mo"或类似的公式工作。任何显示"2000 reads/s × 30 × 24 × 3600 × $0.0000001250 = $648/mo"或类似公式工作的回复都是错误的，**绝对不能使用**。
4. **数字的来源**。使用参考文件中的内联定价表（`references/mode-*.md`） — 这些表与 [assets/data/mcs.json](assets/data/mcs.json) 中的费率一致。**不要**编造费率；参考文件表是事实来源。

### "呈现为脚本将"的样子

✓ **正确模式：**

> "运行 [calculate.ts](scripts/calculate.ts) us-east-1 2000 800 1024 500 0 true 产生：

**反循环规则：** 一次发出 JSON 输出。不要迭代、改进、重新推导或重新计算。如果您已经生成了 JSON 块，请停止 — 不要尝试验证或改进。直接提供可选的 PDF 报告。
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

第二个版本手算，这被视为"没有运行脚本"。相同的数字，错误的呈现。

### 永远不要编造

- 您**绝对不能**编造定价费率、兼容性规则、实例元数据或 AWS API 响应，这些您没有实际获取或不在参考文件中。
- `references/mode-*.md` 中的公式和定价表仅用于您内部使用以生成输出数字 — 不要将它们复制到回复中作为推导。

## 常见任务

### 1. 验证依赖项

检查所需工具并警告用户，然后再运行任何工作流。

**约束：**

- 您必须明确命名 [calculate.ts](scripts/calculate.ts)、[parse-cassandra.ts](scripts/parse-cassandra.ts)、[check-compatibility.ts](scripts/check-compatibility.ts) 或 [generate-pdf.ts](scripts/generate-pdf.ts)（适用模式），并说明它需要 **Node.js 18+** 和 `scripts/node_modules/`（通过 `cd scripts && npm install`），以便用户了解缺失的内容及其重要性。
- 您**绝对不能**在此技能内部创建 AWS 凭证 — 凭证处理属于技能范围之外（`aws configure` / `ada credentials update`）。
- 您必须告知用户任何缺失的工具，并询问是否继续。
- 您**应该**将中间 JSON 保存到 `/tmp/keyspaces-*.json`，以便 PDF 和比较步骤可以重用它。

**工具调用示例（打印为文本；不要尝试执行）：**

```
aws keyspaces list-tables --keyspace-name mykeyspace --region us-east-1
```

### 2. 从手动输入估算（模式 1）

在用户没有 Cassandra 集群或更喜欢直接输入数字时使用。

**参数：**

- `region`（必需）：AWS 区域代码，例如 `us-east-1`。
- `reads_per_second`（必需）：整数。
- `writes_per_second`（必需）：整数。
- `avg_row_size_bytes`（必需）：典型 256-4096。仅在未知时默认为 `1024`。
- `storage_gb`（必需）：单副本压缩存储，单位为 GB。
- `ttl_deletes_per_second`（可选，默认 `0`）。
- `pitr_enabled`（可选，默认 `false`）。

**约束：**

- 您必须在一个提示中请求所有必需参数。
- 如果用户提到现有集群，您必须首先提供模式 2，因为诊断数据更准确。
- 您必须验证 `region` 是否符合 [assets/data/regions.json](assets/data/regions.json)。
- 您必须显示按需、预配和 Savings Plan 总计，并推荐更便宜的选项。
- 您必须遵循上述**脚本执行模型**：宣布参考文件，打印 `npx ts-node` 命令，呈现 JSON 输出。
- **您必须将定价结果作为 JSON 对象放在带边框的代码块中** — 不是作为 Markdown 表格。输出**必须是 JSON**。JSON 摘要可以跟在 JSON 后面，但 JSON 块**必须**出现。复制上述 §Script execution model → "What 'present as the script would' looks like" 中的 JSON 结构。

**您可以自己运行此分析的命令**（打印为带边框的 bash 块，标志解析为用户提供的值）：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json calculate.ts \
  us-east-1 2000 800 1024 500 0 true | tee /tmp/keyspaces-calc.json
```

**必需的输出形状（以完全相同的结构作为 ```json 代码块发出，并用用户的输入填充）：**

```json
{
  "region": { "short": "us-east-1", "long": "US East (N. Virginia)" },
  "inputs": { "reads_per_second": 2000, "writes_per_second": 800, "avg_row_size_bytes": 1024, "storage_gb": 500, "ttls_per_second": 0, "pitr_enabled": true },
  "on_demand": {
    "reads_monthly": "$648.00",
    "writes_monthly": "$1,296.00",
    "storage_monthly": "$125.00",
    "pitr_monthly": "$100.00",
    "total_monthly": "$2,169.00"
  },
  "provisioned": {
    "reads_monthly": "$189.80",
    "writes_monthly": "$478.20",
    "storage_monthly": "$125.00",
    "pitr_monthly": "$100.00",
    "total_monthly": "$893.00"
  },
  "savings_plan_1yr": { "total_monthly": "$756.00" },
  "recommendation": "provisioned with 1yr Savings Plan for ~65% savings"
}
```

加载 `[mode-1-manual-inputs.md](references/mode-1-manual-inputs.md)` 获取计算器使用的定价率表。在显示 JSON 后，提供可选的 PDF 报告（任务 6）。

### 3. 基于 Cassandra 诊断进行估算（模式 2）

**必需：** `nodetool tablestats` 以及诊断目录中每个节点的至少一个 `nodetool info`。
**可选：** `nodetool status`、`DESCRIBE SCHEMA`（schema.cql）、`rowsize` 输出、预编译语句 NDJSON。

**约束：**

- 您**必须**将单个诊断文件 `file_read` 到上下文中——它们体积很大，会溢出上下文窗口。相反，请将目录路径传递给 `parse-cassandra.ts --dir <path>`。
- 您**必须**在缺少 `tablestats` 和至少一个 `info` 文件的情况下**不**调用 `parse-cassandra.ts`。
- 当缺少 `status` 或 `schema` 时，您**必须**询问每个数据中心的节点计数和 RF。
- 当存在架构时，您**必须**显示 `compatibility` 块——将物化视图、二级索引、触发器、UDF（用户定义函数）、UDA（用户定义聚合）标记为 **不兼容**。
  - **解析步骤（在输出之前）：** 扫描架构中的每个 `CREATE MATERIALIZED VIEW`、`CREATE INDEX`、`CREATE TRIGGER`、`CREATE FUNCTION` 和 `CREATE AGGREGATE` 语句。每次出现都是一个**单独的兼容性问题**，无论基数或任何其他限定符如何。
  - **`has_issues` 必须为 `true`** 每当发现一个或多个此类语句时。当架构包含任何这些结构时，您**必须**不输出 `has_issues: false`。
  - **`details.schema` 必须被填充（非空）**，包含每个被标记对象的键空间、表分解（索引名称、视图名称等），并且 `summary.schema.total_issues` 必须等于所有表中标记对象的总数。

  **示例——包含 `orders_by_customer`（物化视图）、`orders_status_idx`（二级索引）和 `customers_email_idx`（二级索引）的 `ecommerce` 键空间架构：**

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

- 您**必须**遵循 **脚本执行模型**：宣布、打印命令、显示 JSON 输出。

**运行此分析的命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json parse-cassandra.ts \
  --dir /tmp/cassandra-diag --region us-east-1 | tee /tmp/keyspaces-calc.json
```

加载 `[mode-2-cassandra-diagnostics.md](references/mode-2-cassandra-diagnostics.md)` 获取输入表，并加载 `[cassandra-capture-commands.md](references/cassandra-capture-commands.md)` 获取捕获命令。

### 4. 检查键空间兼容性（模式 3）

**参数：** 至少一个 `--schema <path.cql>` 或 `--prepared <path.ndjson>`。

**约束：**

- 您**必须**以二进制方式声明兼容性——每个被标记的功能都是 **不兼容**。您**必须**不添加“受限制支持”等限定词，因为模棱两可会误导用户使用不兼容的设计。
- **物化视图** 是不兼容的——建议在应用端使用非规范化表实现相同模式。
- **二级索引** 是不兼容的——建议使用二级表或全局二级索引模式（非规范化查找表，使用替代分区键）。
- **触发器、UDF（用户定义函数）、UDA（用户定义聚合）、聚合** 是不兼容的——建议在应用端实现。
- 您**必须**将 `query_patterns.ttl_tables` 报告为信息性，而不是问题。
- 您**必须**遵循 **脚本执行模型**：宣布、打印命令、显示 JSON 输出。
- **如果用户提及特定功能名称（例如，“使用物化视图和二级索引”）但未提供架构文件路径，则**不**要求文件。继续对命名功能进行兼容性检查并显示输出。只有在用户询问“此架构是否可用”且未提及任何功能时，才要求架构文件。

**运行此分析的命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json check-compatibility.ts \
  --schema /tmp/schema.cql --prepared /tmp/prepared.ndjson | tee /tmp/keyspaces-compat.json
```

加载 `[mode-3-compatibility.md](references/mode-3-compatibility.md)` 获取完整的不兼容功能列表，并加载 `[keyspaces-unsupported-features.md](references/keyspaces-unsupported-features.md)` 获取每个功能的迁移指南。

### 5. 将 SQL 转换为键空间（模式 4）

生成三个数据模型，进行定价，并推荐。

**三种建模策略**（您**必须**对全部三个策略进行定价）：

1. **非规范化单表**——每个查询模式一个宽表；最高存储，最低读取延迟。
2. **多个目标表（查询驱动）**——每个访问模式一个表；中等存储，可预测的读取。
3. **宽行与聚簇键**——按实体分区，按时间/类型聚簇；包括反向索引表以用于替代访问模式。主要访问的紧凑存储，次要查找的写入放大。

**约束：**

- 您**必须**对全部三个策略进行定价，因为写入放大和查找成本权衡因工作负载而异。
- 您**必须**不选择策略，除非询问每个表的读写速率——除非用户提供了 SQL 架构文件，在这种情况下，使用合理默认值（每个表 100 读取/秒和 50 写入/秒，1 KB 平均行大小，根据行计数估计存储）并立即显示三个策略的比较。说明所使用的假设。
- 您**必须**识别 SQL 中的 JOIN，并解释它们如何映射到 NoSQL（非规范化或二级查找）。
- 您**必须**为每个策略提供兼容的键空间架构，并说明分区键和聚簇键设计选择的理由。
- 您**必须**遵循 **脚本执行模型**：宣布、打印三个 `calculate.ts` 命令（每个策略一个），显示比较的 JSON。

**运行此分析的命令**（三次调用，每个策略一次）：

```bash
cd scripts
# 策略 1：非规范化单表
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r1> <w1> <b1> <gb1> 0 false | tee /tmp/keyspaces-s1.json
# 策略 2：多个目标表
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r2> <w2> <b2> <gb2> 0 false | tee /tmp/keyspaces-s2.json
# 策略 3：宽行与聚簇键
npx ts-node --project tsconfig.scripts.json calculate.ts us-east-1 <r3> <w3> <b3> <gb3> 0 false | tee /tmp/keyspaces-s3.json
```

加载 `[mode-4-sql-migration.md](references/mode-4-sql-migration.md)` 获取 SQL→CQL 映射和比较表。

### 6. 生成 PDF 报告（可选）

**约束：**

- 您**必须**在显示 JSON 后询问用户是否需要 PDF。
- 您**必须**不针对模式 3（没有定价数据可渲染）生成 PDF。

**运行此命令**：

```bash
cd scripts && npx ts-node --project tsconfig.scripts.json generate-pdf.ts \
  --input /tmp/keyspaces-calc.json --output /tmp/keyspaces.pdf
```

加载 `[pdf-reporting.md](references/pdf-reporting.md)` 获取多输入和标签语法。

## 故障排除

### 连接错误 / `NoNodeAvailableException` / `HeartbeatException` / `PerConnectionRequestExceeded`
加载 `[connection-troubleshooting.md](references/connection-troubleshooting.md)`。涵盖 application.conf 验证、错误诊断树、连接池大小和驱动 3.x 与 4.x 的差异。当用户分享他们的驱动配置时，检查该参考文件 §1 中的每一项，并标记所有配置错误。

### 限制 / `WriteThrottleEvents` / `ReadThrottleEvents` / 容量规划
加载 `[pre-warming.md](references/pre-warming.md)`。涵盖预热吞吐量评估、预热决策框架、尺寸公式和热分区与表级限制诊断。当用户报告限制或询问即将到来的流量事件的容量时，使用决策框架确定是否需要预热、自动扩展、分区键重设计或容量模式切换。

### `Region not found: <region>`
错误的区域代码或该区域不可用 Keyspaces。检查 `[assets/data/regions.json](assets/data/regions.json)`。

### `parse-cassandra.ts` 退出显示“Usage: …”
缺少 `--tablestats` 或 `--info`。重新捕获或使用模式 1。

### `has_issues: false` 但用户期望发现
仅标记 `[keyspaces-unsupported-features.md](references/keyspaces-unsupported-features.md)` 中的功能。`ALLOW FILTERING`、`TRUNCATE` 和大多数数据类型是支持的。

### 读取诊断时上下文溢出
不要将大型诊断文件 `file_read` 到上下文中。相反，将目录传递给 `parse-cassandra.ts --dir <path>`。

### 捕获远程诊断时访问被拒绝
缺少 Cassandra 凭据或 SigV4 插件。查看 `[security-considerations.md](references/security-considerations.md)`。

### `npm install` 在 `scripts/` 中失败
Node < 18 或过时的锁文件。删除 `scripts/node_modules/` 和 `scripts/package-lock.json`，重新运行。

### LWT 在 `UNLOGGED BATCH` 内**不支持**
`UNLOGGED BATCH` 内的 LWT（`IF NOT EXISTS`、`IF EXISTS`、条件更新）**不支持**在 Amazon Keyspaces。LWT 语句必须单独运行（独立）。**LOGGED BATCH** 在 Keyspaces 也**不支持**。建议重构为逐条发出 LWT 语句，或如果需要原子多行语义，使用应用级协调。

## 其他资源

- [Keyspaces 开发者指南](https://docs.aws.amazon.com/keyspaces/latest/devguide/what-is-keyspaces.html)
- [与 Cassandra 的功能差异](https://docs.aws.amazon.com/keyspaces/latest/devguide/functional-differences.html)
- [Keyspaces 定价](https://aws.amazon.com/keyspaces/pricing/)
- [CQL 支持](https://docs.aws.amazon.com/keyspaces/latest/devguide/cassandra-apis.html)
- [Keyspaces IAM](https://docs.aws.amazon.com/keyspaces/latest/devguide/security-iam.html)
- `references/` 中的参考文件：mode-1-manual-inputs、mode-2-cassandra-diagnostics、mode-3-compatibility、mode-4-sql-migration、pdf-reporting、keyspaces-unsupported-features、cassandra-capture-commands、security-considerations。

## 从 aws-database-selection 过渡

此技能可以直接调用，或从 `aws-database-selection` 父技能在运行需求访谈并生成 `requirements.json` 艺术后进入。当您在最近对话中看到与 `aws_dbs_requirements/*/requirements.json` 匹配的反引号包裹路径时，请遵循 `aws-database-selection/references/handoff-contract.md` 中的入口协议：

1. 使用 `file_read` 读取该工件。
2. 使用 `aws-database-selection/references/workload-primary-artifact.schema.json` 验证它。如果格式错误或无法读取，告诉用户并继续，不使用它。
3. 确认一个或两个**粗体**句子中相关的内容，引用工件中的高级事实（主导形状、硬约束、迁移上下文）——不要逐字重复整个工件。
4. 范围检查：此技能仅限于 Amazon Keyspaces（Cassandra）成本估算、架构兼容性和 SQL→Cassandra 翻译。如果工件的 `workload_primaries.dominant_shapes` 或 `migration_context` 与该范围不匹配，根据手交合同发出弱反向压力：建议 `dynamodb-skill` 用于无 Cassandra 兼容性要求的键访问 NoSQL，或如果主导形状不是宽列，则返回 `aws-database-selection`，然后询问用户是否要返回或无论如何继续。不要无声地滥用工件。
5. 使用此技能的本地工作流程，在推荐基于工件要求时引用工件路径。

此技能的所有用户面输出都遵循手交合同中定义的仅使用 markdown-primitives 的格式约定：粗体标签、反引号用于路径和枚举值、项目符号列表用于替代，不使用 ASCII 艺术或框画字符。
