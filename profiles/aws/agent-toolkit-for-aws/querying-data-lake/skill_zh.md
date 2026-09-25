# 查询数据湖

在 Amazon Athena 上执行 SQL 查询，支持默认目录和联邦目录（Glue、S3 表、Redshift），可选择工作组、语句分类和错误恢复。

## 概述

执行和管理 Athena SQL 查询，支持默认目录和联邦目录。选择工作组、解析目标资源（将模糊引用委托给 `finding-data-lake-assets`）、对语句进行分类以确保安全，并报告成本和数据扫描量。使用 AWS MCP 服务器进行沙盒执行和审计日志记录；当 MCP 服务器不可用时，相同的 AWS CLI 命令可直接使用。

**参数获取约束：**

- 必须接受一个可选参数：SQL 文本、命名查询名称、工作组名称、目录名称或 `profile TABLE_NAME`
- 必须接受参数作为直接文本或指向包含 SQL 的文件的指针
- 如果未设置目标 AWS 区域，必须要求用户输入
- 在执行任何非简单查询之前，必须确认输出 S3 位置
- 必须尊重用户在任何步骤中中止的决定

## 常见任务

### 1. 验证依赖项

在运行查询之前检查所需的工具和 AWS 访问权限。

**约束：**

- 必须验证 AWS MCP 服务器工具是否可用（`aws___call_aws`），并在可用时通过它们运行查询；如果 MCP 服务器不可用，则仅回退到 AWS CLI
- 不允许回退到 shell 或 Bash 执行查询——结果必须通过 MCP 工具或 `aws athena` CLI 捕获，以便跟踪输出位置和成本
- 必须使用 `aws sts get-caller-identity` 确认凭证，并告知用户任何缺失的工具

### 2. 解析工作组

检查调用者身份，列出工作组，自动选择最佳工作组（参见 [workgroup-selection.md](references/workgroup-selection.md)）。

**约束：**

- 在提交任何查询之前必须选择工作组（防止输出位置错误）
- 必须向用户展示所选工作组及其输出位置
- 在失败时，不允许自动升级到不同工作组，除非用户确认

### 3. 解析目标资源

如果用户通过名称、业务概念（“我们的季度报告”、“销售数据”）、S3 路径或未指定表的目录引用表，则委托给 `finding-data-lake-assets` 返回具体的 `database.table`（如果目录非默认，则返回目录）。

**约束：**

- 不允许尝试使用 `athena list-data-catalogs` 或通过迭代 `get-tables` 解析模糊资源引用——这些会忽略联邦目录并浪费令牌
- 仅当用户提供完全限定引用（确切的 `database.table`）或希望按原样执行的原始 SQL 时，才应跳过此步骤
- 在构建查询之前必须明确声明解析的资源：“在 [目录] 中找到 [表]。将用于查询。”
- 应默认为默认 Glue 目录，除非用户提到“联邦”、“Redshift”、“S3 表”或 `finding-data-lake-assets` 返回不同的目录

### 4. 发现架构

对于分析查询，应在构建最终查询之前对目标表进行剖析。必须将样本行（`SELECT ... LIMIT 5`）作为剖析的一部分展示。

### 5. 构建查询

表寻址取决于目录类型：

- 默认 Glue 目录：`database.table`（对于单目录查询，省略目录前缀）。在跨目录查询中，用 `"awsdatacatalog".database.table` 限定默认目录表
- 注册的数据源：`datasource.database.table`
- 未注册的 Glue 目录：`"catalog/subcatalog".database.table`

### 6. 分类和执行

在执行之前对 SQL 语句进行分类：

| 语句 | 行为 |
|---|---|
| `SELECT`、`SHOW`、`DESCRIBE`、`EXPLAIN` | 安全——执行 |
| `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER`、`CREATE`、`TRUNCATE`、`MERGE` | 具有破坏性——警告用户并要求明确确认 |
| 不确定 | 视为具有破坏性；确认 |

示例工具调用（通过 AWS MCP 服务器）：

```
aws___call_aws(command="aws athena start-query-execution --work-group <WORKGROUP_NAME> --query-string '<sql>' --query-execution-context Database=<db>")
```

对于联邦或 S3 表目录，也在执行上下文中设置 `Catalog=<CATALOG_PATH>`（例如 `Catalog=s3tablescatalog/<BUCKET_NAME>`）。

**约束：**

- 在执行时必须警告用户，如果目标是 Redshift 联邦的（“没有分区裁剪——每个查询扫描整个表”）
- 在执行跨目录连接之前必须警告用户（“跨目录连接会产生网络开销，可能很慢”）
- 在执行之前必须确认输出 S3 位置
- 在执行之前必须解释正在调用的工具
- 必须尊重用户中止的决定

### 7. 展示和恢复

展示结果，包括成本、扫描的数据量、持续时间和可操作的见解。在失败时，列出可用的工作组并让用户选择要重试的工作组。

### 参数路由

按以下顺序解析；在第一个匹配项处停止：

1. 包含 SQL 关键字（`SELECT`、`SHOW`、`DESCRIBE`、`INSERT` 等）——SQL 文本，直接执行
2. `profile TABLE_NAME` —— 运行全面的表剖析（参见 [query-patterns.md](references/query-patterns.md)）
3. 匹配已知的命名查询——查找并执行
4. 匹配已知的工作组——显示工作组状态和最近查询
5. 匹配已知的目录——委托给 `exploring-data-catalog` 以枚举数据库和表
6. 无参数——显示最近的查询活动和可用表

### 原则

- 执行前始终选择工作组（防止输出位置错误）
- 在运行分析查询之前剖析不熟悉的表
- 在结果中展示成本，以便用户建立成本意识
- 对于大型表上的探索性查询建议使用 `LIMIT`
- 不要询问具有明显答案的领域问题，但始终确认与安全相关的操作（工作组切换、输出位置更改、非 `SELECT` 语句）

## 故障排除

| 错误 | 原因 | 解决方法 |
|---|---|---|
| Redshift 标识符错误，大小写混合 | Redshift 联邦名称仅小写 | 将标识符小写化 |
| `CatalogId` 验证失败 | 传递了 ARN 而不是目录名称 | 传递目录名称，而不是 ARN |
| 跨目录 `information_schema` 返回空结果 | 缺少目录限定符 | 使用目录限定路径：`"catalog".information_schema.tables` |
| 查询因输出位置错误而失败 | 工作组未配置输出位置 | 选择具有输出位置的不同工作组，或配置一个 |
| 未确认即执行具有破坏性的语句 | 跳过了语句分类 | 始终分类 `INSERT`/`UPDATE`/`DELETE`/`DROP`/`ALTER`/`CREATE`/`TRUNCATE`/`MERGE` 并确认 |

## 其他资源

- [工作组选择逻辑](references/workgroup-selection.md)
- [常见查询模式](references/query-patterns.md)
- [Athena 最佳实践](https://docs.aws.amazon.com/athena/latest/ug/performance-tuning.html)
- [Athena 联邦查询](https://docs.aws.amazon.com/athena/latest/ug/connect-to-a-data-source.html)
