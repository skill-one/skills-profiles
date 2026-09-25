# DMS Schema Conversion

## 概述

此技能处理 DMS Schema Conversion 的完整生命周期——从首次设置到在现有项目上运行转换。

> 建议使用 AWS MCP 服务器以实现流程简化、审计日志和可观察性。当 MCP 服务器不可用时，所有操作都可以通过 AWS CLI 直接执行。

**关键文档：**

- [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html) — 将操作范围限定为特定对象
- [DMS Schema Conversion 中的转换规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-transformation-rules.html) — 在转换过程中重命名模式、表、列

**全局约束：** 您必须先获取并阅读相关联的文档，然后才能采取行动——不要依赖记忆来处理任何参考材料（选择规则、转换规则、故障排除指南、网络配置等）。文档包含特定于供应商的详细信息，这些信息在不同的引擎和 API 版本之间会发生变化。

---

## 护栏——此技能自己的文件存放位置（MCP 与本地安装）

此技能可以通过两种方式加载，它们从不同的位置解析技能自己的捆绑文件。在读取参考之前，确定技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载：** 技能未安装在本地文件系统中。您必须使用 `retrieve_skill` 并带有 `file` 参数来获取每个参考（例如 `file="references/setup-wizard.md"`）。不要在本地 `file_read` 这些路径——它们不存在于磁盘上。
- **本地安装**（例如 `.kiro/skills/dms-schema-conversion/` 或 `~/.claude/skills/dms-schema-conversion/`）：使用相对路径从本地技能目录读取文件。

此区别仅适用于技能自己的捆绑文件。用户数据和会话工件始终从用户的当前工作目录读取和写入。切勿通过 `retrieve_skill` 获取或写入客户数据。

---

## 验证依赖项

在开始之前，检查是否可以执行 AWS CLI 命令。

**约束：**

- 您必须验证是否可以运行 AWS CLI 命令（通过 MCP 服务器工具或直接通过 shell）
- 如果没有可用的执行方法，您必须通知客户并询问是否继续
- 您必须询问客户要使用哪个 AWS 区域——不要尝试从 STS 响应中推断它（它不包含区域字段）。如果客户不确定，建议检查 `AWS_DEFAULT_REGION` 环境变量或他们正在使用的 `--region` 标志。

---

## 项目选择

检查现有的迁移项目：

```
aws dms describe-migration-projects
```

- **如果恰好存在一个项目** → 询问客户：“找到迁移项目 `<name>`。您想使用它，还是创建一个新的？” 如果他们确认，请存储 `migration_project_identifier` 并继续到 [操作菜单](#actions-menu)。如果他们想要一个新的，请运行设置向导。
- **如果存在多个项目** → 列出它们并要求客户选择一个，或者提供创建新项目的选项。存储 `migration_project_identifier`，继续到 [操作菜单](#actions-menu)。
- **如果不存在项目** → 询问：“未找到迁移项目。您想创建一个吗？” 如果是，加载 [setup-wizard.md](references/setup-wizard.md) 并从第 1 阶段运行完整的设置向导。向导完成后，运行 [自动导入](#auto-import)，然后继续到 [操作菜单](#actions-menu)。

---

## 自动导入

> 此部分仅在设置向导创建新项目后运行。不要对现有项目运行。

1. 构建选择规则以从源服务器导入 **所有模式**。对于 `server-name`，请使用数据提供程序标识符（ARN 中的短 ID，例如 `JIFET2LUZJEJZPDYSOSGANOA2M`）或数据提供程序设置中的字面值 `ServerName`（例如，对于离线源为 `"offline"`）。对于 SQL Server，您必须将 `database-name` 包含在对象定位器中。有关 JSON 格式，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

2. 运行 `start-metadata-model-import` 并带有 `--origin SOURCE --refresh` 以及步骤 1 中的选择规则。从响应中提取 `RequestIdentifier`。

3. 使用 DMS 等待器等待导入完成：

   ```
   aws dms wait metadata-model-imported \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每 30 秒轮询一次 `describe-metadata-model-imports`，并带有 `--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或 **FAILED**（通过响应中的 `Error` 字段检查错误）。

4. **显示发现的模式：** 成功后，在根级别使用 `--origin SOURCE` 调用 `describe-metadata-model-children` 以列出导入的模式/数据库。向客户展示发现的名称，以便他们确认已建立正确的数据库连接：
   > “导入完成。我发现了以下模式/数据库： `<list>`。这看起来正确吗？”

5. 继续到 [操作菜单](#actions-menu)。

---

## 操作菜单

如果可用，请使用结构化选择工具（例如 `AskUserQuestion`）来呈现操作菜单——这为客户提供了一个可点击/可选择的列表。

**对于 SQL Server → PostgreSQL/Aurora PostgreSQL 项目**（作为单个选择问题“您想做什么？”呈现）：

1. **转换数据库** — 将模式对象转换为目标引擎（还会生成一个转换评估报告）
2. **评估数据库** — 运行兼容性评估（还会生成一个转换评估报告）
3. **转换语句** — 转换单个 SQL 语句
4. **清理** — 删除迁移项目和相关的 DMS 资源

**对于所有其他引擎组合**（作为单个选择问题“您想做什么？”呈现）：

1. **转换数据库** — 将模式对象转换为目标引擎（还会生成一个转换评估报告）
2. **评估数据库** — 运行兼容性评估（还会生成一个转换评估报告）
3. **处理树** — 浏览元数据模型树
4. **清理** — 删除迁移项目和相关的 DMS 资源

客户始终可以通过“其他”键输入自定义请求（例如，“处理树”、“显示数据库统计信息”或“退出”）。如果客户选择“其他”并描述了此技能涵盖的操作，请相应处理。

每次操作完成后，都通过再次显示相同的选择来返回此菜单。

> **关于元数据加载的说明：** `start-metadata-model-import`（带有 `Refresh=false`）、`start-metadata-model-assessment` 和 `start-metadata-model-conversion` 都会加载作用域对象源树的元数据。如果当前会话中已经为给定子树导入元数据，则不需要重新导入——这些操作将使用已加载的内容。

---

### 转换数据库

1. **询问要转换什么：** 询问客户他们想转换什么（例如，“所有模式”、“模式 public”、“以 PROD_ 开头的表”）。

2. **构建选择规则：** 将客户的自然语言转换为选择规则 JSON。有关格式、通配符和特定于供应商定位器的信息，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

3. **运行转换：** 调用 `start-metadata-model-conversion` 并带有迁移项目和选择规则。从响应中提取 `RequestIdentifier`。

4. **等待完成：** 使用 DMS 等待器等待：

   ```
   aws dms wait metadata-model-converted \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每 30 秒轮询一次 `describe-metadata-model-conversions`，并带有 `--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或 **FAILED**（通过响应中的 `Error` 字段检查错误）。

5. **导出转换评估报告：** 转换成功后，使用选择规则（使用 `rule-action: "explicit"`）调用 `export-metadata-model-assessment`（此 API 需要显式规则，而不是 `include`）。向客户提供 S3 链接，用于 PDF 和 CSV 报告（`PdfReport.S3ObjectKey` 和 `CsvReport.S3ObjectKey`）。

6. **显示摘要：** 使用 `aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv` 从 S3 下载摘要 CSV。向客户展示其内容——显示每个类别的对象数量、自动转换的对象数量以及每个复杂级别具有操作项的对象数量。

7. **转换后子菜单：** 显示摘要后，显示选项。如果目标是实时目标（不是虚拟的），则仅显示“应用到目标”：
   > “您想接下来做什么？
   > 1. **修复操作项** — 审查和修复转换评估报告中的操作项
   > 2. **导出为脚本** — 将转换的 DDL 导出为 SQL 脚本到 S3
   > 3. **应用到目标** — 将转换的对象应用到目标数据库（仅限实时目标）
   > 4. **返回** — 返回到操作菜单"

   - **修复操作项：** 加载 [action-items.md](references/action-items.md) 并遵循那里的修复工作流。
   - **导出为脚本：** 运行 `aws dms start-metadata-model-export-as-script --migration-project-identifier <migration_project_identifier> --origin TARGET --selection-rules '<json>'`。提取 `RequestIdentifier`。通过 `aws dms wait metadata-model-exported-as-script --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。完成时提供 S3 链接。
   - **应用到目标：** 运行 `aws dms start-metadata-model-export-to-target --migration-project-identifier <migration_project_identifier> --selection-rules '<json>'`。如果客户确认，可以可选地传递 `--overwrite-extension-pack`。提取 `RequestIdentifier`。通过 `aws dms wait metadata-model-exported-to-target --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。完成后通知客户。
   - **返回：** 返回到 [操作菜单](#actions-menu)。

完成后，询问客户他们想接下来做什么。

---

### 评估数据库

评估分析转换复杂度并生成转换评估报告**而不实际转换任何对象**。当客户希望在提交转换之前了解迁移工作量时，请使用此功能。

> **重要提示：** 如果客户已在相同的作用域上运行了转换，则不需要单独的评估——转换已经生成了转换评估报告。通知客户：“您已经从之前运行的转换中获得了转换评估报告。您想让我显示该报告，还是想在一个不同的作用域上重新运行评估？”

1. **询问要评估什么：** 询问客户他们想评估什么（例如，“所有模式”、“模式 pg_catalog”、“以 PROD_ 开头的表”）。

2. **构建选择规则：** 将客户的自然语言转换为选择规则 JSON。有关格式、通配符和特定于供应商定位器的信息，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

3. **运行评估：** 调用 `start-metadata-model-assessment` 并带有迁移项目和选择规则。从响应中提取 `RequestIdentifier`。

4. **等待完成：** 使用 DMS 等待器等待：

   ```
   aws dms wait metadata-model-assessed \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每 30 秒轮询一次 `describe-metadata-model-assessments`，并带有 `--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或 **FAILED**（检查错误）。

5. **导出转换评估报告：** 成功后，使用相同的选择规则调用 `export-metadata-model-assessment`。向客户提供 S3 链接，用于 PDF 和 CSV 报告（`PdfReport.S3ObjectKey` 和 `CsvReport.S3ObjectKey`）。报告包含转换复杂度统计信息、操作项和估计的工作量。

6. **显示摘要：** 使用 `aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv` 从 S3 下载摘要 CSV。向客户展示其内容——显示每个类别的对象数量、自动转换的对象数量以及每个复杂级别具有操作项的对象数量。

7. **提供修复操作项的选项：** 询问客户：
   > “您想让我帮助修复操作项吗？”

   如果是，加载 [action-items.md](references/action-items.md) 并遵循那里的修复工作流。

完成后，询问客户他们想接下来做什么。

---

### 审查操作项

加载 [action-items.md](references/action-items.md) 并遵循那里的工作流。

完成后，询问客户他们想接下来做什么。

---

### 处理树

元数据树以分层方式表示数据库模式。它包含两种类型的元素：

- **对象** — 实际的数据库对象（表、函数、视图、序列、索引），它们具有 SQL 定义
- **类别** — 虚拟分组容器（“模式”、“表”、“函数”），它们用于组织对象以进行导航，但没有 SQL 定义

树使用按需加载——元数据仅在导入时从数据库检索。有关详细信息，请参阅 [导航元数据模型](https://docs.aws.amazon.com/dms/latest/userguide/sc-metadata-model.html#sc-metadata-model-navigating)。

**导航使用两个 API：**

- `describe-metadata-model-children` — 返回给定节点的子项，每个子项都有自己的 `SelectionRules` 以进行更深入的钻取
- `describe-metadata-model` — 返回特定对象的名称、类型和 SQL 定义

这两个 API 都需要 `--origin SOURCE` 或 `--origin TARGET`，并且只接受 `explicit` 选择规则。

1. **显示树根：** 使用针对根级别的选择规则并带有 `--origin SOURCE` 调用 `describe-metadata-model-children`。如果树为空，则自动运行元数据导入（与 [自动导入](#auto-import) 相同），然后重新显示树根。

2. **导航：** 响应中的每个子项都有 `MetadataModelName` 和 `SelectionRules`。向客户展示子项并询问他们想做什么：
   - **显示子项** — 通过调用 `describe-metadata-model-children` 并使用子项的 `SelectionRules` 作为 `--selection-rules` 参数来钻取子项
   - **显示定义** — 显示选定对象的 DDL（见步骤 3）。仅适用于对象，不适用于类别。
   - **返回** — 返回到父节点
   - **退出树** — 返回到操作菜单

3. **显示定义：** 使用子项的 `SelectionRules` 并带有 `--origin SOURCE` 调用 `describe-metadata-model`。响应包括 `Definition`（源 DDL）和 `TargetMetadataModels`（转换后对应对象的列表及其各自的 `SelectionRules`）。要获取目标 DDL，请再次调用 `describe-metadata-model`，并使用来自 `TargetMetadataModels[0]` 的 `SelectionRules`，并带有 `--origin TARGET`。清晰地标记为 **源** 和 **目标** 向客户展示。

4. **从数据库刷新：** 如果客户要求刷新，请使用针对当前树位置的选择规则、`--origin SOURCE --refresh` 运行 `start-metadata-model-import`。提取 `RequestIdentifier`。通过 `aws dms wait metadata-model-imported --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。刷新完成后，重新显示当前节点的子项。

完成后，询问客户他们想接下来做什么。

---

### 转换语句

> **限制：** 此功能仅适用于 **SQL Server → PostgreSQL/Aurora PostgreSQL** 迁移项目。不要为任何其他源/目标引擎组合提供或显示此选项。

1. **确定上下文：** 导航元数据树以找到目标位置。对于 SQL Server，这是服务器 → 数据库 → 模式；对于其他引擎，这是服务器 → 模式。使用 `describe-metadata-model-children` 钻取节点，直到达到模式级别。让客户选择模式（或对于 SQL Server，数据库 + 模式）。如果树为空，请要求客户手动提供位置。

2. **获取 SQL 语句：** 询问客户他们想转换的 SQL 语句。

3. **为模式构建选择规则：** 构建针对模式位置的选择规则。有关格式和特定于供应商定位器的信息，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

4. **创建元数据模型：** 生成一个唯一的模型名称（例如，`statement-<timestamp>`）。调用 `start-metadata-model-creation` 并带有：
   - `--selection-rules` — 步骤 3 中的模式选择规则
   - `--metadata-model-name` — 生成的模型名称
   - `--properties '{"StatementProperties": {"Definition": "<sql_statement>"}}'`

   从响应中提取 `RequestIdentifier`。通过 `aws dms wait metadata-model-created --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。

5. **为语句构建选择规则：** 构建针对特定语句的选择规则。有关格式，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)——使用 `statement-name` 设置为模型名称。

6. **转换创建的模型：** 调用 `start-metadata-model-conversion` 并带有步骤 5 中的语句选择规则。提取 `RequestIdentifier`。通过 `aws dms wait metadata-model-converted --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。

7. **显示转换结果：** 使用步骤 5 中的语句选择规则并带有 `--origin SOURCE` 调用 `describe-metadata-model`。从响应中，提取 `TargetMetadataModels[0].SelectionRules`。然后使用这些目标选择规则并带有 `--origin TARGET` 再次调用 `describe-metadata-model`。清晰地向客户展示转换后的 SQL，来自 `Definition` 字段。

8. **导出转换评估报告：** 调用 `export-metadata-model-assessment` 并使用 **源** 选择规则（来自步骤 5）。向客户提供 PDF 和 CSV 报告的 S3 链接。

完成后，询问客户他们想接下来做什么。

---

### 数据库统计信息

当客户询问其源数据库统计信息时——例如对象数量、对象类型、模式大小或一般概述——请运行评估并显示结果作为简洁的摘要。

1. **构建选择规则** 基于客户的范围。如果他们指定特定的模式或对象，请相应地作用域。如果没有指定范围，则默认为源服务器上的所有模式（通配符 `%`）。有关 JSON 格式，请参阅 [DMS Schema Conversion 中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

2. **运行评估：** 调用 `start-metadata-model-assessment` 并带有迁移项目和选择规则。有关执行详细信息，请参阅 [schema-conversion-operations.md](references/schema-conversion-operations.md)。

3. **等待完成** 使用 DMS 等待器或如 [schema-conversion-operations.md](references/schema-conversion-operations.md) 中所述的回退轮询。

4. **导出转换评估报告：** 使用相同的选择规则调用 `export-metadata-model-assessment`。

5. **下载并仅显示客户请求的内容：** 使用 `aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv` 从 S3 下载摘要 CSV：

   报告包含许多数据点。仅显示客户请求的信息——不要显示整个报告。例如：
   - 如果他们询问“有多少表？” → 仅显示表计数
   - 如果他们询问关于特定模式 → 仅显示该模式的统计信息

6. **提供下一步操作：** 询问他们是否想查看转换复杂度或继续转换。

**约束：**

- 如果客户指定了范围，请使用它。如果没有，则默认为所有模式。
- 仅显示客户请求的内容——不要使用未请求的数据淹没客户。
- 以清晰、表格化的格式显示统计信息。

完成后，询问客户他们想接下来做什么。

---

### 清理

删除迁移项目及其关联的 DMS 资源。资源必须按依赖顺序删除。

1. **与客户确认：** 列出将要删除的资源并要求确认：

   ```
   aws dms describe-migration-projects --filter Name=migration-project-identifier,Values=<migration_project_identifier>
   ```

   显示项目名称、源/目标数据提供程序和实例配置文件。

2. **删除迁移项目:**

   ```
   aws dms delete-migration-project \
     --migration-project-identifier <migration_project_identifier>
   ```

3. **删除数据提供程序：** 删除源和目标数据提供程序：

   ```
   aws dms delete-data-provider \
     --data-provider-identifier <source_data_provider_identifier>
   aws dms delete-data-provider \
     --data-provider-identifier <target_data_provider_identifier>
   ```

4. **删除实例配置文件:**

   ```
   aws dms delete-instance-profile \
     --instance-profile-identifier <instance_profile_identifier>
   ```

5. **删除子网组:**

   ```
   aws dms delete-replication-subnet-group \
     --replication-subnet-group-identifier <subnet_group_identifier>
   ```

6. **确认完成：** 通知客户所有 DMS Schema Conversion 资源已被删除。

**约束：**

- 您必须在使用任何资源之前获得客户明确的确认。
- 您必须按顺序删除：首先删除迁移项目，然后删除数据提供程序，然后删除实例配置文件，然后删除子网组——以错误顺序删除将由于依赖关系而失败。
- 您绝不能删除底层基础设施（VPC、子网、安全组、RDS 实例、Secrets Manager 密钥）——这些不在 DMS Schema Conversion 清理范围内。

完成后，询问客户他们想接下来做什么。

---

## 取消意识

在任何运行中的异步操作期间，如果客户请求取消，请参考 [cancel-operations.md](references/cancel-operations.md) 以获取正确的取消命令映射。

---

## 安全注意事项

- **凭证：** 所有数据库凭证都存储在 AWS Secrets Manager 中。切勿将凭证嵌入数据提供程序设置或记录到输出中。
- **静态加密：** S3 存储桶使用 SSE-S3 加密（默认）。DMS Schema Conversion 不支持 SSE-KMS。
- **传输中加密：** 在线连接应使用 `require` 或更强的 SSL 模式。`none` 仅用于隔离的测试环境。
- **IAM 最小权限：** 所有 IAM 角色使用混淆代理条件密钥（`aws:SourceAccount`、`aws:SourceArn`）并作用域资源 ARN。
- **网络访问：** DMS 实例配置文件在具有安全组限制的 VPC 子网中运行。
- 请参阅 [DMS 安全最佳实践](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Security.html) 以获取更多指导。

---

## 错误处理

当任何操作失败或返回错误时，请加载 [troubleshooting.md](references/troubleshooting.md) 并遵循其指导来诊断和解决问题。用 plain language 向客户解释错误，并提供选项：重试、尝试不同的操作或退出。
