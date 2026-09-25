# 迁移到 Amazon Redshift

## 这个技能是什么

这个技能是**AI指导，而非执行框架**。它完全是**Markdown知识**（规则、映射、模式、最佳实践）——**没有可执行代码**。所有执行——转换、发现/迁移/验证运行器、依赖项和基础设施——**你（AI）在运行时根据这些知识生成**，并根据客户的特定环境进行定制。

原则：**知识优于发送的代码 → 减少漂移，客户无需运行或依赖任何内容，可靠的一次性结果。** 不要寻找pyproject、工具包、编排引擎或发送的脚本——按设计没有这些；你生成执行。

> **运行时：** 这个技能**无论是否使用AWS MCP服务器**都能工作——步骤指导使用AWS CLI语法。建议**使用AWS MCP服务器运行**，以便进行沙盒执行和审计日志记录；如果没有，AI将在主机shell上运行生成的脚本（假设Bash、Python 3和AWS CLI + 凭据）。不要假设仅MCP的工具可用。

## 源路由

这个技能将支持的**源数据仓库迁移到Amazon Redshift**。首先识别**源系统**，然后在`references/<source>/`下加载该源的知识：

- **Teradata (Vantage)** → `references/teradata/` — 支持的（以下所有引用）。
- *其他源（例如Snowflake、Oracle）—— 不支持；准备好时，每个源都会作为自己的`references/<source>/`集添加。*

**工作流程与源无关**（发现 → 转换 → 迁移 → 验证 → 性能 → 报告）；只有**转换知识**与源相关。以下是Teradata集。

## 何时使用

- 将Teradata系统（Vantage）迁移到Amazon Redshift。
- 将Teradata DDL、SQL、存储过程、宏或BTEQ转换为Redshift/RSQL。
- 评估Teradata→Redshift迁移的复杂性和工作量。

## 运行原则

- **发现阶段对源数据库严格只读（SELECT-only）**。永远不要更改生产状态：没有DDL/DML，并且永远不要启用日志记录（`BEGIN/REPLACE QUERY LOGGING`）。如果DBQL为空，将其标记为`unavailable`，并回退到始终开启的`DBC.AMPUsageV`——参见`references/teradata/discovery-queries.md`。
- **技能提供知识；你生成执行**。阅读`references/`进行推理和转换——直接应用`references/teradata/conversion-rules.md`中的规则进行转换，并根据环境生成发现/迁移/验证运行器（以及来自`references/teradata/discovery-queries.md`的可读-only发现收集器）。
- **生成，不要假设框架**。假设环境有Bash、Python 3和AWS CLI + 凭据。任何生成的脚本需要的Python库（`teradatasql`、`boto3`等）都会在运行时通过`pip install`安装——固定确切版本。Teradata **TTU**（BTEQ/TPT）是**仅限Linux/Windows——不适用于macOS**；优先使用**WRITE_NOS** + **`teradatasql`**（跨平台，无需客户端）进行发现/提取，除非存在TTU/Linux主机。
- **凭据：** 使用**只读**Teradata用户；优先使用IAM角色而不是IAM用户。对于**生产环境**，从**AWS Secrets Manager或Systems Manager Parameter Store**引用凭据。对于**仅限本地开发**，可以使用git忽略的`.env`文件或配置文件——永远不要提交它。永远不要硬编码或回显密钥。在可移植包中，引用**同位置的凭据文件**，并附带`credentials.env.example`模板——真实文件被git忽略。
- **将状态保存在文件中**。所有生成的输出都放在用户工作目录下git忽略的`output/`中；保持`output/state.md`最新，以便工作可恢复。

## 工作流程（阶段）

按顺序运行；每个阶段的`result/`都为下一个阶段提供输入（参见`references/teradata/orchestration.md`）。

1. **发现**——源清单。→ `references/teradata/discovery-queries.md`（只读收集SQL + AI生成的BTEQ驱动模板）→ `output/discovery/result/inventory.json`
2. **转换**——架构 + 代码。直接应用转换规则，标记需要手动重写的长尾部分，并从引用中修复Redshift错误。→ `references/teradata/conversion-rules.md`、`references/teradata/data-type-mapping.md`、`references/teradata/architecture-mapping.md`、`references/teradata/stored-procedure-migration.md`、`references/teradata/bteq-to-rsql.md`、`references/teradata/common-errors.md`
3. **数据迁移**——提取 → S3 → COPY，可重启。→ `references/teradata/data-migration-patterns.md`
4. **验证**——计数/聚合/采样。→ `references/teradata/validation-patterns.md`
5. **性能**——基线与Redshift对比；目标大小。→ `references/teradata/performance.md`、`references/teradata/sizing.md`
6. **报告**——汇总所有阶段。→ `references/teradata/reporting.md`

## 转换（AI如何应用）

没有要运行的转换器——直接应用`references/teradata/conversion-rules.md`中的规则（结合类型/架构/存储过程/BTEQ引用）：将确定性规则应用于理解良好的批量内容，**标记需要手动重写的结构**并附带建议的重写，为每个对象分配**置信度**，并使用`references/teradata/common-errors.md`修复任何Redshift错误。参考文档是单一事实来源；`conversion-rules.md`包含输入→输出的黄金示例以进行匹配。

## 执行模式（连接性）

- **连接**——你的主机可以访问Teradata/Redshift → 在本地运行生成的脚本。
- **断开连接**——不能 → 在`output/<phase>/`下生成自包含包（脚本 + 同位置的凭据模板 + 相对`result/` + `run-instructions.md`）；操作员在可访问的主机上运行它，并将`result/`复制回来。复制的`result/`是持久的状态——读取它（+ `state.md`）并继续。

## 项目工作区布局（每个迁移运行）

```
<project-workspace>/
  migration-config.yaml          # 操作员编写：端点、范围、策略
  .gitignore                     # 忽略output/
  output/                        # 所有生成内容（git忽略）
    state.md                     # 进度游标
    discovery/   …  result/inventory.json
    conversion/  …  result/{ddl,sql,procedures,rsql}/  manual_review.json
    data_migration/ … result/{extract,load,templates}/  migration_manifest.json
    validation/  …  result/validation_report.json
    performance/ …  result/{perf_baseline,perf_compare}.json
    reporting/      result/migration_report.md
```

## 安全注意事项

- **没有发送的代码或依赖项。** 这个技能是纯文本——客户不会运行它生成的任何内容。AI生成的任何运行器都必须固定依赖项确切版本，验证/清理输入（文件路径、SQL、shell参数），并且永远不要打印或记录凭据、密钥或PII。
- **最小权限 + 临时凭据。** 使用**只读**Teradata用户进行发现。在AWS中优先使用**IAM角色而不是IAM用户**，并优先使用**IAM认证而不是用户名/密码**。将密钥保存在**AWS Secrets Manager / Parameter Store**——永远不要硬编码、回显或提交它们（凭据文件被git忽略；只发送`*.example`模板）。
- **传输中/静态数据。** 使用TLS连接到两个引擎；在加密的S3存储桶（SSE）中暂存提取（具有最小权限的存储桶策略）；通过`COPY … IAM_ROLE`（不是访问密钥）加载。在目标Redshift集群上启用加密。
- **爆炸半径。** 发现按设计是**只读**的。迁移写入目标——首先在**丢弃/非生产Redshift**上验证，并且在没有操作员明确确认的情况下，永远不要将生成的写入路径指向生产环境。
- **无密钥泄露在工件中。** 生成的`output/…`（清单、报告、`state.md`）**必须**不嵌入凭据或操作员在`migration-config.yaml`中提供的端点之外的端点。
- **COPY `IAM_ROLE`加固。** 将角色的策略范围限制为特定的暂存前缀（而不是全局`s3:*`），并在其信任策略中包含条件键（`aws:SourceAccount` / `aws:SourceArn`，或`sts:ExternalId`用于跨账户）以防止混淆代理假设——按Redshift IAM角色授权最佳实践。
- **日志记录和监控。** 启用CloudTrail（暂存存储桶上的S3数据事件 + Redshift管理事件）、Redshift审计日志记录（连接/用户活动日志到S3或CloudWatch），并在迁移期间在COPY失败或暂存存储桶异常访问期间启用CloudWatch警报。

AWS MCP服务器（推荐运行时）额外提供生成的脚本的沙盒执行和审计日志记录。

## 参考（专业知识）

| 文件 | 主题 |
|------|-------|
| `references/teradata/orchestration.md` | 阶段工作流程 + 状态模型 |
| `references/teradata/conversion-rules.md` | 72条转换规则（事实来源） |
| `references/teradata/data-type-mapping.md` | TD→RS类型映射 |
| `references/teradata/architecture-mapping.md` | PI→DISTKEY, PPI→SORTKEY, Join Index→MV |
| `references/teradata/stored-procedure-migration.md` | SP → PL/pgSQL |
| `references/teradata/bteq-to-rsql.md` | BTEQ → RSQL |
| `references/teradata/common-errors.md` | 常见Redshift错误 + 修复 |
| `references/teradata/discovery-queries.md` | DBC系统视图清单查询 |
| `references/teradata/data-migration-patterns.md` | COPY/TPT/微批处理/检查点 |
| `references/teradata/validation-patterns.md` | 行计数/聚合/采样比较 |
| `references/teradata/performance.md` | 代表性查询提取 + 比较 |
| `references/teradata/sizing.md` | RG节点类型 + 从源配置文件获取计数 |
| `references/teradata/reporting.md` | 迁移状态报告生成 |
