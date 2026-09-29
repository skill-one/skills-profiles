---
name: dms-schema-conversion
description: 处理完整的 DMS 模式转换生命周期，包括创建迁移项目、将数据库模式转换为目标引擎、运行兼容性评估、导航元数据树、将转换后的 DDL 导出到 S3、将模式更改应用到目标数据库，以及在不同数据库引擎之间转换 SQL 语句。在使用 AWS DMS 模式转换迁移异构引擎的数据库模式时适用。
---

# DMS Schema转换

## 概述

此技能处理DMS Schema转换的完整生命周期——从首次设置到在现有项目上运行转换。

> 建议使用AWS MCP服务器以实现流程简化、审计日志和可观察性。当MCP服务器不可用时，所有操作都可以通过AWS CLI直接执行。

**关键文档：**

- [DMS Schema转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html) — 将操作范围限定为特定对象
- [DMS Schema转换中的转换规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-transformation-rules.html) — 在转换过程中重命名模式、表、列

**全局约束：** 您必须获取并阅读任何相关文档，然后才能采取行动——不要依赖记忆来处理任何参考材料（选择规则、转换规则、故障排除指南、网络配置等）。文档包含特定于供应商的详细信息，这些信息在不同的引擎和API版本之间会发生变化。

---

## 边界控制——此技能的文件存放位置（MCP与本地安装）

此技能可以通过两种方式加载，并且它们从不同的位置解析技能自身的捆绑文件。在读取参考之前，请确定技能是如何加载的：

- **通过AWS MCP `retrieve_skill` 工具加载：** 技能未安装在本地文件系统中。您必须使用带有`file`参数的`retrieve_skill`来获取每个参考（例如`file="references/setup-wizard.md"`）。不要在本地`file_read`这些路径——它们不存在于磁盘上。
- **本地安装**（例如`.kiro/skills/dms-schema-conversion/`或`~/.claude/skills/dms-schema-conversion/`）：使用相对路径从本地技能目录读取文件。

此区别仅适用于技能自身的打包文件。用户数据和会话工件始终从用户的当前工作目录读取和写入。切勿通过`retrieve_skill`获取或写入客户数据。

---

## 验证依赖项

开始之前，检查AWS CLI命令是否可以执行。

**约束：**

- 您必须验证可以运行AWS CLI命令（通过MCP服务器工具或直接通过shell）
- 如果没有可用的执行方法，您必须通知客户并询问是否继续
- 您必须询问客户要使用哪个AWS区域——不要尝试从STS响应中推断它（它不包含区域字段）。如果客户不确定，建议检查`AWS_DEFAULT_REGION`环境变量或他们正在使用的`--region`标志。

---

## 项目选择

检查现有的迁移项目：

```
aws dms describe-migration-projects
```

- **如果恰好存在一个项目** → 询问客户："找到迁移项目`<name>`。您想使用它，还是创建一个新的？" 如果他们确认，请存储`migration_project_identifier`并继续到[操作菜单](#actions-menu)。如果他们想要一个新的，请运行设置向导。
- **如果存在多个项目** → 列出它们并询问客户选择一个，或者提供创建新项目的选项。存储`migration_project_identifier`，继续到[操作菜单](#actions-menu)。
- **如果不存在项目** → 询问："未找到迁移项目。您想创建一个吗？" 如果是，加载[setup-wizard.md](references/setup-wizard.md)并从第1阶段运行完整的设置向导。向导完成后，运行[自动导入](#auto-import)，然后继续到[操作菜单](#actions-menu)。

---

## 自动导入

> 此部分仅在设置向导创建新项目后运行。不要对现有项目运行。

1. 构建选择规则以从源服务器导入**所有模式**。对于`server-name`，请使用数据提供程序标识符（ARN中的短ID，例如`JIFET2LUZJEJZPDYSOSGANOA2M`）或数据提供程序设置中的字面值`ServerName`（例如，对于离线源为`"offline"`）。对于SQL Server，您必须将`database-name`包含在对象定位器中。有关JSON格式的详细信息，请参阅[DMS Schema转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

2. 运行`start-metadata-model-import`，并使用步骤1中的选择规则以及`--origin SOURCE --refresh`。从响应中提取`RequestIdentifier`。

3. 使用DMS等待器等待导入完成：

   ```
   aws dms wait metadata-model-imported \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每30秒轮询一次`describe-metadata-model-imports`，并使用`--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或**FAILED**（通过响应中的`Error`字段检查错误）。

4. **显示发现的模式：** 成功后，在根级别使用`--origin SOURCE`调用`describe-metadata-model-children`以列出导入的模式/数据库。将发现的名称呈现给客户，以便他们确认已建立正确的数据库连接：
   > "导入完成。我发现了以下模式/数据库：`<列表>`。这看起来正确吗？"

5. 继续到[操作菜单](#actions-menu)。

---

## 操作菜单

如果可用，请使用结构化选择工具（例如`AskUserQuestion`）呈现操作菜单——这为客户提供了一个可点击/可选择的列表。

**对于SQL Server → PostgreSQL/Aurora PostgreSQL项目**（作为单个选择问题"您想做什么？"呈现）：

1. **转换数据库** — 将模式对象转换为目标引擎（还会生成转换评估报告）
2. **评估数据库** — 运行兼容性评估（还会生成转换评估报告）
3. **转换语句** — 转换单个SQL语句
4. **清理** — 删除迁移项目和相关DMS资源

**对于所有其他引擎组合**（作为单个选择问题"您想做什么？"呈现）：

1. **转换数据库** — 将模式对象转换为目标引擎（还会生成转换评估报告）
2. **评估数据库** — 运行兼容性评估（还会生成转换评估报告）
3. **处理树** — 浏览元数据模型树
4. **清理** — 删除迁移项目和相关DMS资源

客户始终可以通过"其他"键入自定义请求（例如"处理树"、"显示数据库统计信息"或"退出"）。如果客户选择"其他"并描述了此技能涵盖的操作，请相应处理。

每次操作完成后，都通过再次呈现相同的选择来返回此菜单。

> **关于元数据加载的说明：** `start-metadata-model-import`（带有`Refresh=false`）、`start-metadata-model-assessment`和`start-metadata-model-conversion`都会加载作用域对象源树的元数据。如果当前会话中已经为给定子树导入元数据，则不需要重新导入——这些操作将使用已加载的内容。

---

### 转换数据库

1. **询问要转换的内容：** 询问客户他们想转换什么（例如"所有模式"、"模式public"、"以PROD_开头的表"）。

2. **构建选择规则：** 将客户的自然语言转换为选择规则JSON。有关格式、通配符和特定于供应商定位器的详细信息，请参阅[DMS Schema转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

3. **运行转换：** 使用迁移项目和选择规则调用`start-metadata-model-conversion`。从响应中提取`RequestIdentifier`。

4. **等待完成：** 使用DMS等待器等待：

   ```
   aws dms wait metadata-model-converted \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每30秒轮询一次`describe-metadata-model-conversions`，并使用`--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或**FAILED**（通过响应中的`Error`字段检查错误）。

5. **导出转换评估报告：** 转换成功后，使用选择规则（使用`rule-action: "explicit"`）调用`export-metadata-model-assessment`（此API需要显式规则，而不是`include`）。向客户提供S3链接，用于PDF和CSV报告（`PdfReport.S3ObjectKey`和`CsvReport.S3ObjectKey`）。

6. **显示摘要：** 使用`aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv`从S3下载摘要CSV。向客户展示其内容——显示每个类别的对象数量、自动转换的对象数量以及每个复杂级别具有操作项的对象数量。

7. **转换后子菜单：** 显示摘要后，显示选项。如果目标是实时目标（非虚拟），则仅显示"应用到目标"：
   > "您想接下来做什么？
   > 1. **修复操作项** — 审查和修复转换评估报告中的操作项
   > 2. **导出为脚本** — 将转换的DDL导出为SQL脚本到S3
   > 3. **应用到目标** — 将转换的对象应用到目标数据库（仅限实时目标）
   > 4. **返回** — 返回到操作菜单"

   - **修复操作项：** 加载[action-items.md](references/action-items.md)并遵循那里的修复工作流程。
   - **导出为脚本：** 运行`aws dms start-metadata-model-export-as-script --migration-project-identifier <migration_project_identifier> --origin TARGET --selection-rules '<json>'`。提取`RequestIdentifier`。通过`aws dms wait metadata-model-exported-as-script --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'`等待。完成后提供S3链接。
   - **应用到目标：** 运行`aws dms start-metadata-model-export-to-target --migration-project-identifier <migration_project_identifier> --selection-rules '<json>'`。如果客户确认，可以传递`--overwrite-extension-pack`。提取`RequestIdentifier`。通过`aws dms wait metadata-model-exported-to-target --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'`等待。完成后通知客户。
   - **返回：** 返回到[操作菜单](#actions-menu)。

完成后，询问客户他们想接下来做什么。

---

### 评估数据库

评估分析转换复杂度并生成转换评估报告**而不会**实际转换任何对象。当客户希望在提交转换之前了解迁移工作量时，请使用此功能。

> **重要提示：** 如果客户已在相同的作用域上运行了转换，则不需要单独的评估——转换已经生成了转换评估报告。通知客户："您已经从您运行的转换中获得了转换评估报告。您想让我显示该报告，还是想在一个不同的作用域上重新运行评估？"

1. **询问要评估的内容：** 询问客户他们想评估什么（例如"所有模式"、"模式pg_catalog"、"以PROD_开头的表"）。

2. **构建选择规则：** 将客户的自然语言转换为选择规则JSON。有关格式、通配符和特定于供应商定位器的详细信息，请参阅[DMS Schema转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

3. **运行评估：** 使用迁移项目和选择规则调用`start-metadata-model-assessment`。从响应中提取`RequestIdentifier`。

4. **等待完成：** 使用DMS等待器等待：

   ```
   aws dms wait metadata-model-assessed \
     --migration-project-identifier <migration_project_identifier> \
     --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'
   ```

   如果等待器失败或不可用，则回退到每30秒轮询一次`describe-metadata-model-assessments`，并使用`--filter Name=request-id,Values=<RequestIdentifier>`。终端状态：**SUCCESS**（继续）或**FAILED**（通过响应中的`Error`字段检查错误）。

5. **导出转换评估报告：** 成功后，使用相同的选择规则调用`export-metadata-model-assessment`。向客户提供S3链接，用于PDF和CSV报告（`PdfReport.S3ObjectKey`和`CsvReport.S3ObjectKey`）。报告包含转换复杂度统计信息、操作项和估计的工作量。

6. **显示摘要：** 使用`aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv`从S3下载摘要CSV。向客户展示其内容——显示每个类别的对象数量、自动转换的对象数量以及每个复杂级别具有操作项的对象数量。

7. **提供修复操作项的选项：** 询问客户：
   > "您想让我帮助修复操作项吗？"

   如果是，加载[action-items.md](references/action-items.md)并遵循那里的修复工作流程。

完成后，询问客户他们想接下来做什么。

---

### 审查操作项

加载[action-items.md](references/action-items.md)并遵循那里的工作流程。

完成后，询问客户他们想接下来做什么。

---

### 处理树

元数据树以分层方式表示数据库模式。它包含两种类型的元素：

- **对象** — 实际的数据库对象（表、函数、视图、序列、索引），它们具有SQL定义
- **类别** — 虚拟分组容器（"模式"、"表"、"函数"），它们用于导航组织对象，但没有SQL定义

树使用按需加载——元数据仅在导入时从数据库检索。有关详细信息，请参阅[导航元数据模型](https://docs.aws.amazon.com/dms/latest/userguide/sc-metadata-model.html#sc-metadata-model-navigating)。

**导航使用两个API：**

- `describe-metadata-model-children` — 返回给定节点的子节点，每个子节点都有自己的`SelectionRules`以进行更深入的挖掘
- `describe-metadata-model` — 返回特定对象的名称、类型和SQL定义

这两个API都需要`--origin SOURCE`或`--origin TARGET`，并且只接受显式选择规则。

1. **显示树根：** 使用针对根级别的选择规则和`--origin SOURCE`调用`describe-metadata-model-children`。如果树为空，则自动运行元数据导入（与[自动导入](#auto-import)相同），然后重新显示树根。

2. **导航：** 响应中的每个子节点都有`MetadataModelName`和`SelectionRules`。呈现子节点并询问客户要做什么：
   - **显示子节点** — 通过调用`describe-metadata-model-children`并使用子节点的`SelectionRules`作为`--selection-rules`参数来深入到子节点
   - **显示定义** — 显示选定对象的DDL（见步骤3）。仅适用于对象，不适用于类别。
   - **返回** — 返回到父节点
   - **退出树** — 返回到操作菜单

3. **显示定义：** 使用子节点的`SelectionRules`和`--origin SOURCE`调用`describe-metadata-model`。响应包括`Definition`（源DDL）和`TargetMetadataModels`（转换后对应对象的列表及其各自的`SelectionRules`）。要获取目标DDL，请再次调用`describe-metadata-model`，并使用`TargetMetadataModels[0]`中的`SelectionRules`以及`--origin TARGET`。清晰地标记为**源**和**目标**。

4. **从数据库刷新：** 如果客户要求刷新，请使用针对当前树位置的选择规则、`--origin SOURCE --refresh`运行`start-metadata-model-import`。提取`RequestIdentifier`。通过`aws dms wait metadata-model-imported --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'`等待。刷新完成后，重新显示当前节点的子节点。

完成后，询问客户他们想接下来做什么。

---

### 转换语句

> **限制：** 此功能仅适用于 **SQL Server → PostgreSQL/Aurora PostgreSQL** 迁移项目。请勿为任何其他源/目标引擎组合提供或显示此选项。

1. **确定上下文：** 导航元数据树以找到目标位置。对于 SQL Server，这是服务器 → 数据库 → 模式；对于其他引擎，这是服务器 → 模式。使用 `describe-metadata-model-children` 命令深入节点，直到达到模式级别。让客户选择模式（对于 SQL Server，可以选择数据库 + 模式）。如果树为空，请让客户手动提供位置。

2. **获取 SQL 语句：** 询问客户他们希望转换的 SQL 语句。

3. **构建模式选择规则：** 构建针对模式位置的选择规则。有关格式和特定于供应商的定位符，请参阅 [DMS 模式转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

4. **创建元数据模型：** 生成一个唯一的模型名称（例如，`statement-<timestamp>`）。使用以下参数调用 `start-metadata-model-creation`：
   - `--selection-rules` — 第 3 步中的模式选择规则
   - `--metadata-model-name` — 生成的模型名称
   - `--properties '{"StatementProperties": {"Definition": "<sql_statement>"}}'`

   从响应中提取 `RequestIdentifier`。使用 `aws dms wait metadata-model-created --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。

5. **构建语句选择规则：** 构建针对特定语句的选择规则。请参阅 [DMS 模式转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html) — 将 `statement-name` 设置为模型名称。

6. **转换创建的模型：** 使用第 5 步中的语句选择规则调用 `start-metadata-model-conversion`。提取 `RequestIdentifier`。使用 `aws dms wait metadata-model-converted --migration-project-identifier <id> --filter 'Name=schema-conversion-operation-id,Values=<RequestIdentifier>'` 等待。

7. **显示转换结果：** 使用第 5 步中的语句选择规则和 `--origin SOURCE` 调用 `describe-metadata-model`。从响应中提取 `TargetMetadataModels[0].SelectionRules`。然后使用这些目标选择规则和 `--origin TARGET` 调用 `describe-metadata-model`。向客户清晰地展示 `Definition` 字段中的转换后的 SQL。

8. **导出转换评估报告：** 使用第 5 步中的 **源** 选择规则调用 `export-metadata-model-assessment`。向客户提供 PDF 和 CSV 报告的 S3 链接。

完成后，询问客户下一步想做什么。

---

### 数据库统计信息

当客户询问其源数据库统计信息（例如，对象数量、对象类型、模式大小或一般概述）时，运行评估并将结果作为简洁的摘要呈现。

1. **构建选择规则：** 根据客户的范围构建选择规则。如果他们指定了特定的模式或对象，请按相应范围进行。如果没有指定范围，则默认为源服务器上的所有模式（通配符 `%`）。有关 JSON 格式，请参阅 [DMS 模式转换中的选择规则](https://docs.aws.amazon.com/dms/latest/userguide/sc-selection-rules.html)。

2. **运行评估：** 使用迁移项目和选择规则调用 `start-metadata-model-assessment`。有关执行细节，请参阅 [schema-conversion-operations.md](references/schema-conversion-operations.md)。

3. **等待完成：** 使用 DMS 等待器或 [schema-conversion-operations.md](references/schema-conversion-operations.md) 中描述的回退轮询等待。

4. **导出转换评估报告：** 使用相同的选择规则调用 `export-metadata-model-assessment`。

5. **下载并仅呈现客户请求的内容：** 从 S3 下载摘要 CSV：

   ```
   aws s3 cp s3://<bucket>/<CsvReport.S3ObjectKey> ./Summary.csv
   ```

   报告包含许多数据点。仅呈现客户请求的信息——不要显示整个报告。例如：
   - 如果他们询问“有多少表？” → 仅显示表计数
   - 如果他们询问特定模式 → 仅显示该模式的统计信息

6. **提供下一步操作：** 询问他们是否想查看转换复杂性或继续转换。

**限制：**

- 如果客户指定了范围，请使用它。如果没有，则默认为所有模式。
- 仅呈现客户请求的内容——不要用未请求的数据淹没客户。
- 以清晰的表格格式呈现统计信息。

完成后，询问客户下一步想做什么。

---

### 清理

删除迁移项目及其关联的 DMS 资源。资源必须按依赖顺序删除。

1. **与客户确认：** 列出将要删除的资源并请求确认：

   ```
   aws dms describe-migration-projects --filter Name=migration-project-identifier,Values=<migration_project_identifier>
   ```

   显示项目名称、源/目标数据提供程序和实例配置文件。

2. **删除迁移项目：**

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

4. **删除实例配置文件：**

   ```
   aws dms delete-instance-profile \
     --instance-profile-identifier <instance_profile_identifier>
   ```

5. **删除子网组：**

   ```
   aws dms delete-replication-subnet-group \
     --replication-subnet-group-identifier <subnet_group_identifier>
   ```

6. **确认完成：** 告知客户所有 DMS 模式转换资源已删除。

**限制：**

- 删除任何资源前必须获得客户的明确确认。
- 必须按顺序删除：首先删除迁移项目，然后删除数据提供程序，然后删除实例配置文件，然后删除子网组——顺序错误会导致依赖失败。
- 删除底层基础设施（VPC、子网、安全组、RDS 实例、Secrets Manager 密钥）——这些不在 DMS 模式转换清理范围内。

完成后，询问客户下一步想做什么。

---

## 取消意识

在异步操作运行期间，如果客户请求取消，请参考 [cancel-operations.md](references/cancel-operations.md) 获取正确的取消命令映射。

---

## 安全注意事项

- **凭证：** 所有数据库凭证都存储在 AWS Secrets Manager 中。切勿在数据提供程序设置中嵌入凭证或将它们记录到输出中。
- **静态加密：** S3 存储桶使用 SSE-S3 加密（默认）。DMS 模式转换不支持 SSE-KMS。
- **传输中加密：** 在线连接应使用 `require` 或更强的 SSL 模式。`none` 仅应在隔离的测试环境中使用。
- **IAM 最小权限：** 所有 IAM 角色使用混淆代理条件密钥（`aws:SourceAccount`、`aws:SourceArn`）和范围资源 ARN。
- **网络访问：** DMS 实例配置文件在具有安全组限制的 VPC 子网中运行。
- 有关更多指导，请参阅 [DMS 安全最佳实践](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Security.html)。

---

## 错误处理

当任何操作失败或返回错误时，加载 [troubleshooting.md](references/troubleshooting.md) 并遵循其指导进行诊断和解决问题。用 plain language 向客户解释错误，并提供选项：重试、尝试不同操作或退出。
